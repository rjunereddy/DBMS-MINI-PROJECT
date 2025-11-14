# enhancements.py
# Add-on features: EMI calc, PDF export, graphs, notifications, foreclosure, profile editor,
# vehicle history, overdue scan, search helpers.
#
# Requires: reportlab, matplotlib
# Install: pip install reportlab matplotlib

import io
import math
import logging
# Add near other imports:
from fpdf import FPDF
from datetime import datetime, date
from tkinter import Toplevel, Frame, Label, Entry, Button, Text, Scrollbar, END, messagebox
from tkinter import ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

logger = logging.getLogger(__name__)

# ----- Utilities (EMI + amortization) -----
def calculate_emi(principal, annual_rate, tenure_months):
    monthly_rate = annual_rate / (12 * 100)
    if monthly_rate == 0:
        return round(principal / tenure_months, 2)
    emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / ((1 + monthly_rate) ** tenure_months - 1)
    return round(emi, 2)

def amortization_schedule(principal, annual_rate, tenure_months, start_date=None):
    monthly_rate = annual_rate / (12 * 100)
    emi = calculate_emi(principal, annual_rate, tenure_months)
    schedule = []
    remaining = principal
    for m in range(1, tenure_months + 1):
        interest = round(remaining * monthly_rate, 2)
        principal_paid = round(emi - interest, 2)
        if m == tenure_months:
            # adjust last payment to avoid rounding leftover
            principal_paid = round(remaining, 2)
            emi = round(principal_paid + interest, 2)
        remaining = round(remaining - principal_paid, 2)
        due_date = (start_date or date.today()).replace(day=1) if start_date else date.today()
        schedule.append({
            'month': m,
            'due_date': due_date,
            'emi': emi,
            'principal': principal_paid,
            'interest': interest,
            'remaining': remaining
        })
    return emi, schedule

# ----- EMI Calculator Window -----
def show_emi_calculator(parent=None):
    win = Toplevel(parent)
    win.title("EMI Calculator")
    win.geometry("600x500")

    Label(win, text="Principal (₹)").pack(pady=4)
    principal_e = Entry(win); principal_e.pack()
    Label(win, text="Annual Rate (%)").pack(pady=4)
    rate_e = Entry(win); rate_e.pack()
    Label(win, text="Tenure (months)").pack(pady=4)
    tenure_e = Entry(win); tenure_e.pack()

    result_label = Label(win, text="EMI: ₹0.00", font=('Arial', 12, 'bold'))
    result_label.pack(pady=8)

    tree_frame = Frame(win)
    tree_frame.pack(fill='both', expand=True, padx=8, pady=8)
    columns = ('Month','EMI','Principal','Interest','Remaining')
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=10)
    for c in columns:
        tree.heading(c, text=c)
        tree.column(c, width=100)
    tree.pack(side='left', fill='both', expand=True)
    scrollbar = Scrollbar(tree_frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    def compute():
        try:
            p = float(principal_e.get())
            r = float(rate_e.get())
            t = int(tenure_e.get())
            emi = calculate_emi(p, r, t)
            result_label.config(text=f"EMI: ₹{emi:,.2f}")
            emi_val, schedule = amortization_schedule(p, r, t, date.today())
            tree.delete(*tree.get_children())
            for s in schedule:
                tree.insert('', 'end', values=(s['month'], f"₹{s['emi']}", f"₹{s['principal']}", f"₹{s['interest']}", f"₹{s['remaining']}"))
        except Exception as e:
            messagebox.showerror("Error", f"Enter valid numbers: {e}")

    Button(win, text="Calculate", command=compute, bg='#3498db', fg='white').pack(pady=6)

# ----- PDF Export (Loan report) -----
from fpdf import FPDF
import os
from datetime import datetime
import logging
from tkinter import messagebox

logger = logging.getLogger(__name__)

def generate_loan_pdf(db, loan_id, filename=None, parent=None):
    """
    Generates a PDF with loan, customer, vehicle, installments summary using fpdf2.
    Uses a Unicode TTF (DejaVuSans.ttf) if available; otherwise falls back to ASCII 'Rs '.
    Returns path to generated file or None on failure.
    """
    try:
        loan_q = """
            SELECT l.*, c.FirstName, c.LastName, c.Phone, c.Email,
                   v.VehicleNo, v.Make, v.Model, v.Year, v.MarketValue
            FROM Loan l
            JOIN Customer c ON l.CustomerID = c.CustomerID
            JOIN Vehicle v ON l.VehicleID = v.VehicleID
            WHERE l.LoanID = %s
        """
        rows = db.execute_query(loan_q, (loan_id,))
        if not rows:
            messagebox.showerror("Error", "Loan not found")
            return None
        loan = rows[0]

        inst_q = "SELECT DueDate, TotalAmount, Status, LateFee, PaidDate FROM Installment WHERE LoanID=%s ORDER BY DueDate"
        insts = db.execute_query(inst_q, (loan_id,)) or []

        # Compose filename
        fname = filename or f"LoanReport_{loan_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf = FPDF(format='A4', unit='mm')
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Attempt to load a Unicode TTF font (DejaVuSans.ttf) from ./fonts/DejaVuSans.ttf
        fonts_folder = os.path.join(os.getcwd(), "fonts")
        dejavu_path = os.path.join(fonts_folder, "DejaVuSans.ttf")
        use_unicode_font = False
        if os.path.isfile(dejavu_path):
            try:
                # Register font for unicode (uni=True)
                pdf.add_font("DejaVu", "", dejavu_path, uni=True)
                pdf.add_font("DejaVu", "B", dejavu_path, uni=True)
                pdf.set_font("DejaVu", size=11)
                use_unicode_font = True
            except Exception:
                logger.exception("Failed to register DejaVu font, will fallback to Helvetica")
                pdf.set_font("Helvetica", size=11)
        else:
            # Try system fonts by common paths (optional) - fallback will be used if not found
            # You may add other candidate paths here if you know them, e.g. windows fonts.
            pdf.set_font("Helvetica", size=11)

        # helper for currency formatting that uses ₹ only if unicode font is available
        def money(val):
            if val is None:
                return ""
            try:
                amount = float(val)
            except Exception:
                return str(val)
            if use_unicode_font:
                return f"₹{amount:,.2f}"
            else:
                return f"Rs {amount:,.2f}"

        # Header
        pdf.set_font(pdf.font_family, style='B', size=14)
        pdf.cell(0, 10, f"Loan Report - Loan ID: {loan_id}", ln=True)
        pdf.ln(2)

        # Customer details
        if use_unicode_font:
            pdf.set_font("DejaVu", size=10)
        else:
            pdf.set_font("Helvetica", size=10)

        pdf.cell(100, 6, f"Customer: {loan.get('FirstName','')} {loan.get('LastName','')}", ln=0)
        pdf.cell(0, 6, f"Phone: {loan.get('Phone','')}", ln=1)
        pdf.cell(0, 6, f"Email: {loan.get('Email','')}", ln=1)
        pdf.ln(2)

        # Loan summary
        loan_amount = loan.get('LoanAmount') or 0
        balance = loan.get('BalanceAmount') or 0
        status = loan.get('Status') or ''
        pdf.cell(0, 6, f"Loan Amount: {money(loan_amount)}    Balance: {money(balance)}    Status: {status}", ln=1)
        pdf.ln(4)

        # Vehicle details
        pdf.cell(0, 6, f"Vehicle: {loan.get('VehicleNo','')}  -  {loan.get('Make','')} {loan.get('Model','')} ({loan.get('Year','')})", ln=1)
        mv = loan.get('MarketValue')
        if mv:
            pdf.cell(0, 6, f"Market Value: {money(mv)}", ln=1)
        pdf.ln(6)

        # Installments table header
        pdf.set_font(pdf.font_family, style='B', size=10)
        col_widths = [30, 40, 40, 30, 40]  # DueDate, Amount, Status, LateFee, PaidDate
        headers = ['Due Date', 'Amount', 'Status', 'Late Fee', 'Paid Date']
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 7, h, border=1, ln=0, align='C')
        pdf.ln()

        # Table rows
        pdf.set_font(pdf.font_family, size=9)
        for inst in insts:
            due = str(inst.get('DueDate') or '')
            amt = money(inst.get('TotalAmount')) if inst.get('TotalAmount') is not None else ''
            st = str(inst.get('Status') or '')
            lf = money(inst.get('LateFee')) if inst.get('LateFee') is not None else ''
            pd = str(inst.get('PaidDate') or '')
            row = [due, amt, st, lf, pd]
            # If a cell is too long it will wrap because of auto page break; keep it simple
            for i, cell in enumerate(row):
                # ensure cell text is string
                text = cell if isinstance(cell, str) else str(cell)
                pdf.cell(col_widths[i], 6, text, border=1)
            pdf.ln()

        pdf.ln(6)
        pdf.set_font(pdf.font_family, size=9)
        pdf.cell(0, 6, f"Generated on: {datetime.now().isoformat()}", ln=1)

        # Save PDF
        pdf.output(fname)
        messagebox.showinfo("PDF Generated", f"Loan PDF saved to {fname}")
        return fname

    except Exception as e:
        logger.exception("PDF generation (fpdf unicode-safe) failed")
        messagebox.showerror("Error", f"Failed to generate PDF: {e}")
        return None

# ----- Graph Analytics (Admin) -----
def show_admin_graphs(db, parent=None):
    try:
        win = Toplevel(parent)
        win.title("Admin Analytics")
        win.geometry("900x600")

        # Example 1: Loan status pie chart
        q = "SELECT Status, COUNT(*) as cnt FROM Loan GROUP BY Status"
        rows = db.execute_query(q)
        labels = [r['Status'] or 'Unknown' for r in rows] if rows else []
        sizes = [r['cnt'] for r in rows] if rows else []

        fig1 = plt.Figure(figsize=(4,3))
        ax1 = fig1.add_subplot(111)
        if sizes:
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax1.set_title("Loan Status Distribution")

        canvas1 = FigureCanvasTkAgg(fig1, win)
        canvas1.get_tk_widget().pack(side='left', fill='both', expand=True)

        # Example 2: Monthly collection (bar)
        q2 = """
            SELECT DATE_FORMAT(TransactionDate, '%Y-%m') as mon, SUM(DebitAmount) as amt
            FROM TransactionLogger
            WHERE TransactionType = 'EMI Payment'
            GROUP BY mon
            ORDER BY mon DESC LIMIT 12
        """
        rows2 = db.execute_query(q2)
        mon = [r['mon'] for r in rows2][::-1] if rows2 else []
        amt = [r['amt'] for r in rows2][::-1] if rows2 else []

        fig2 = plt.Figure(figsize=(4,3))
        ax2 = fig2.add_subplot(111)
        if mon:
            ax2.bar(mon, amt)
            ax2.set_xticklabels(mon, rotation=45, ha='right')
        ax2.set_title("Monthly EMI Collection")

        canvas2 = FigureCanvasTkAgg(fig2, win)
        canvas2.get_tk_widget().pack(side='right', fill='both', expand=True)

    except Exception as e:
        logger.exception("Graph display failed")
        messagebox.showerror("Error", f"Graph display failed: {e}")

# ----- Simulated notification -----
def simulate_notification(parent, title, message):
    # For demo, show messagebox and log
    logger.info("NOTIFICATION: %s - %s", title, message)
    messagebox.showinfo(title, message)

# ----- Foreclosure (transactional) -----
def foreclose_loan(db, loan_id, agent_id=None, parent=None):
    """
    Foreclose a loan: compute remaining balance, mark all installments Paid,
    update Loan status to Closed, log a transaction for remaining amount.
    """
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        # Get remaining balance
        cursor.execute("SELECT BalanceAmount FROM Loan WHERE LoanID=%s FOR UPDATE", (loan_id,))
        row = cursor.fetchone()
        if not row:
            messagebox.showerror("Error", "Loan not found")
            conn.close(); return False
        remaining = float(row[0])
        if remaining <= 0:
            messagebox.showinfo("Info", "Loan already closed or no balance")
            conn.close(); return True

        # Mark installments paid and set paid date to today (for pending/overdue)
        cursor.execute("UPDATE Installment SET Status='Paid', PaidDate=CURDATE() WHERE LoanID=%s AND Status!='Paid'", (loan_id,))

        # Update loan
        cursor.execute("UPDATE Loan SET BalanceAmount=0, Status='Closed' WHERE LoanID=%s", (loan_id,))

        # Log transaction: assume DebitAmount = remaining (customer paid), CreditAmount = 0
        cursor.execute("""INSERT INTO TransactionLogger (LoanID, DebitAmount, CreditAmount, BalanceAfterTransaction, Remarks, TransactionType)
                          VALUES (%s, %s, %s, %s, %s, %s)""",
                       (loan_id, remaining, 0, 0, 'Foreclosure payment', 'Prepayment'))

        conn.commit()
        cursor.close()
        conn.close()
        messagebox.showinfo("Success", f"Loan {loan_id} foreclosed. Amount: ₹{remaining:,.2f}")
        return True
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        logger.exception("Foreclosure failed")
        messagebox.showerror("Error", f"Failed to foreclose loan: {e}")
        return False

# ----- Customer Profile viewer/editor -----
def show_customer_profile(db, customer_id, parent=None):
    try:
        rows = db.execute_query("SELECT * FROM Customer WHERE CustomerID=%s", (customer_id,))
        if not rows:
            messagebox.showerror("Error", "Customer not found")
            return
        c = rows[0]
        win = Toplevel(parent)
        win.title("Customer Profile")
        win.geometry("500x450")

        Label(win, text=f"{c.get('FirstName','')} {c.get('LastName','')}", font=('Arial',14,'bold')).pack(pady=8)
        frame = Frame(win); frame.pack(padx=8, pady=8, fill='x')

        # Editable fields: Phone, Email, Address, City, Pincode
        fields = [('Phone','Phone'), ('Email','Email'), ('Address','Address'), ('City','City'), ('Pincode','Pincode')]
        entries = {}
        for i, (key,label_text) in enumerate(fields):
            Label(frame, text=label_text).grid(row=i, column=0, sticky='w', pady=4)
            e = Entry(frame, width=40)
            e.grid(row=i, column=1, pady=4)
            e.insert(0, c.get(key) or '')
            entries[key] = e

        def save():
            try:
                vals = tuple(entries[k].get().strip() for k,_ in fields) + (customer_id,)
                q = "UPDATE Customer SET Phone=%s, Email=%s, Address=%s, City=%s, Pincode=%s WHERE CustomerID=%s"
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute(q, vals)
                conn.commit()
                cur.close()
                conn.close()
                messagebox.showinfo("Saved", "Customer profile updated")
                win.destroy()
            except Exception as e:
                logger.exception("Save profile failed")
                messagebox.showerror("Error", f"Failed to save: {e}")

        Button(win, text="Save", command=save, bg='#27ae60', fg='white').pack(pady=8)
    except Exception as e:
        logger.exception("Profile view failed")
        messagebox.showerror("Error", f"Failed to open profile: {e}")

# ----- Vehicle history & insurance alerts -----
def show_vehicle_history(db, vehicle_no, parent=None):
    try:
        rows = db.execute_query("SELECT * FROM Vehicle WHERE VehicleNo=%s", (vehicle_no,))
        if not rows:
            messagebox.showerror("Error", "Vehicle not found")
            return
        v = rows[0]
        win = Toplevel(parent)
        win.title(f"Vehicle - {vehicle_no}")
        win.geometry("600x450")

        Label(win, text=f"{v.get('Make')} {v.get('Model')} ({v.get('Year')})", font=('Arial',12,'bold')).pack(pady=6)
        Label(win, text=f"Market Value: ₹{v.get('MarketValue'):,}").pack()
        Label(win, text=f"Insurance Expiry: {v.get('InsuranceExpiry')}").pack(pady=6)

        # days till expiry
        try:
            exp = v.get('InsuranceExpiry')
            if exp:
                days = (v.get('InsuranceExpiry') - date.today()).days if isinstance(exp, date) else None
                if isinstance(days, int):
                    if days < 30:
                        Label(win, text=f"Insurance expires in {days} days — ALERT!", fg='red').pack(pady=4)
                    else:
                        Label(win, text=f"Insurance expires in {days} days").pack(pady=4)
        except Exception:
            pass

        # Seizure history
        q = "SELECT * FROM Seizure s JOIN Loan l ON s.LoanID=l.LoanID JOIN Customer c ON l.CustomerID=c.CustomerID WHERE l.VehicleID=%s"
        # need vehicleID
        vrows = db.execute_query("SELECT VehicleID FROM Vehicle WHERE VehicleNo=%s", (vehicle_no,))
        if vrows:
            vid = vrows[0]['VehicleID']
            srows = db.execute_query("SELECT s.*, l.LoanID, CONCAT(c.FirstName,' ',c.LastName) as Customer FROM Seizure s JOIN Loan l ON s.LoanID=l.LoanID JOIN Customer c ON l.CustomerID=c.CustomerID WHERE l.VehicleID=%s", (vid,))
            if srows:
                Label(win, text="Seizure History:", font=('Arial',11,'bold')).pack(pady=6)
                txt = Text(win, height=8)
                for s in srows:
                    txt.insert(END, f"SeizureID: {s['SeizureID']} LoanID:{s['LoanID']} Date:{s['SeizureDate']} Status:{s['SeizureStatus']}\nReason:{s['Reason']}\n\n")
                txt.pack(fill='both', expand=True)
    except Exception as e:
        logger.exception("Vehicle history failed")
        messagebox.showerror("Error", f"Failed to open vehicle history: {e}")

# ----- Overdue Scan (apply late fees) -----
def run_overdue_scan(db, parent=None):
    """
    Finds overdue installments, applies late fees, updates statuses, and returns summary.
    """
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        # Find installments that are past due and not marked paid/overdue
        cur.execute("""
            SELECT InstallmentID, LoanID, DueDate, TotalAmount, Status
            FROM Installment
            WHERE DueDate < CURDATE() AND Status IN ('Pending','Partial')
        """)
        rows = cur.fetchall()
        updated = 0
        for r in rows:
            inst_id, loan_id, due, amt, status = r
            # compute late fee: 2% of amount for each month overdue (rounded)
            cur.execute("SELECT DATEDIFF(CURDATE(), DueDate) FROM Installment WHERE InstallmentID=%s", (inst_id,))
            days = cur.fetchone()[0] or 0
            months = max(1, (days + 14)//30)
            late_fee = round(min(0.02 * months, 0.20) * float(amt),2)  # capped 20%
            cur.execute("UPDATE Installment SET Status='Overdue', LateFee=%s WHERE InstallmentID=%s", (late_fee, inst_id))
            updated += 1
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("Overdue Scan", f"Marked {updated} installments as overdue and applied late fees.")
        return updated
    except Exception as e:
        try:
            conn.rollback()
        except Exception:
            pass
        logger.exception("Overdue scan failed")
        messagebox.showerror("Error", f"Overdue scan failed: {e}")
        return 0

# ----- Simple search helper used by UI (returns list of dicts) -----
def search_loans(db, term):
    t = f"%{term}%"
    q = """
        SELECT l.LoanID, CONCAT(c.FirstName,' ',c.LastName) as Customer, v.VehicleNo, l.LoanAmount, l.BalanceAmount, l.Status
        FROM Loan l
        JOIN Customer c ON l.CustomerID=c.CustomerID
        JOIN Vehicle v ON l.VehicleID=v.VehicleID
        WHERE c.FirstName LIKE %s OR c.LastName LIKE %s OR v.VehicleNo LIKE %s OR l.LoanID = %s
        ORDER BY l.LoanID DESC
    """
    # attempt numeric loan id match as well
    try:
        lid = int(term)
    except Exception:
        lid = -1
    return db.execute_query(q, (t,t,t,lid))
