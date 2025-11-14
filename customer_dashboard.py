import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from enhancements import show_customer_profile, generate_loan_pdf

class CustomerDashboard:
    def __init__(self, login_window, user, db):
        self.login_window = login_window
        self.user = user
        self.db = db
        self.customer_id = user.get('CustomerID')
        
        self.window = tk.Toplevel()
        self.window.title(f"Customer Dashboard - {user.get('FirstName','Customer')} {user.get('LastName','')}")
        self.window.geometry("1000x600")
        self.window.configure(bg='#ecf0f1')
        
        self.window.protocol("WM_DELETE_WINDOW", self.logout)
        self.window.deiconify()
        
        self.setup_ui()
        self.load_customer_data()
    
    def setup_ui(self):
        header_frame = tk.Frame(self.window, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        welcome_text = f"Welcome, {self.user.get('FirstName','')} {self.user.get('LastName','')}"
        tk.Label(header_frame, text=welcome_text, font=('Arial', 16, 'bold'), 
                fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=20)
        
        # Profile button
        profile_btn = tk.Button(header_frame, text="My Profile", command=lambda: show_customer_profile(self.db, self.customer_id, self.window),
                                bg='#16a085', fg='white', font=('Arial', 12))
        profile_btn.pack(side='right', padx=10, pady=20)
        
        # Export PDF button
        pdf_btn = tk.Button(header_frame, text="Export Loan PDF", command=self.export_my_loan_pdf,
                            bg='#2980b9', fg='white', font=('Arial', 12))
        pdf_btn.pack(side='right', padx=10, pady=20)
        
        logout_btn = tk.Button(header_frame, text="Logout", command=self.logout,
                              bg='#e74c3c', fg='white', font=('Arial', 12))
        logout_btn.pack(side='right', padx=20, pady=20)
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.loans_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.loans_frame, text="My Loans")
        
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="Payment History")
        
        self.setup_loans_tab()
        self.setup_history_tab()
    
    def setup_loans_tab(self):
        loans_container = tk.Frame(self.loans_frame, bg='white')
        loans_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(loans_container, text="My Active Loans", font=('Arial', 14, 'bold'), 
                bg='white').pack(anchor='w', pady=10)
        
        # Loans treeview with scrollbar
        loans_tree_frame = tk.Frame(loans_container, bg='white')
        loans_tree_frame.pack(fill='both', expand=True, pady=10)
        
        self.loans_tree = ttk.Treeview(loans_tree_frame, 
                                      columns=('LoanID', 'Vehicle', 'LoanAmount', 'Balance', 'EMI', 'Status'),
                                      show='headings')
        
        for col in self.loans_tree['columns']:
            self.loans_tree.heading(col, text=col)
            self.loans_tree.column(col, width=120)
        
        loans_scrollbar = ttk.Scrollbar(loans_tree_frame, orient="vertical", command=self.loans_tree.yview)
        self.loans_tree.configure(yscrollcommand=loans_scrollbar.set)
        
        self.loans_tree.pack(side='left', fill='both', expand=True)
        loans_scrollbar.pack(side='right', fill='y')
        
        tk.Label(loans_container, text="Loan Installments", font=('Arial', 14, 'bold'), 
                bg='white').pack(anchor='w', pady=10)
        
        # Installments treeview with scrollbar
        installments_tree_frame = tk.Frame(loans_container, bg='white')
        installments_tree_frame.pack(fill='both', expand=True, pady=10)
        
        self.installments_tree = ttk.Treeview(installments_tree_frame,
                                             columns=('DueDate', 'Amount', 'Status', 'LateFee', 'PaidDate'),
                                             show='headings', height=8)
        
        for col in self.installments_tree['columns']:
            self.installments_tree.heading(col, text=col)
            self.installments_tree.column(col, width=120)
        
        installments_scrollbar = ttk.Scrollbar(installments_tree_frame, orient="vertical", command=self.installments_tree.yview)
        self.installments_tree.configure(yscrollcommand=installments_scrollbar.set)
        
        self.installments_tree.pack(side='left', fill='both', expand=True)
        installments_scrollbar.pack(side='right', fill='y')
        
        self.loans_tree.bind('<<TreeviewSelect>>', self.on_loan_select)
    
    def setup_history_tab(self):
        history_container = tk.Frame(self.history_frame, bg='white')
        history_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(history_container, text="Payment History", font=('Arial', 14, 'bold'), 
                bg='white').pack(anchor='w', pady=10)
        
        # History treeview with scrollbar
        history_tree_frame = tk.Frame(history_container, bg='white')
        history_tree_frame.pack(fill='both', expand=True, pady=10)
        
        self.history_tree = ttk.Treeview(history_tree_frame,
                                        columns=('Date', 'LoanID', 'Amount', 'Type', 'Remarks'),
                                        show='headings')
        
        for col in self.history_tree['columns']:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        history_scrollbar = ttk.Scrollbar(history_tree_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_tree.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')
    
    def load_customer_data(self):
        self.load_my_loans()
        self.load_payment_history()
    
    def load_my_loans(self):
        for item in self.loans_tree.get_children():
            self.loans_tree.delete(item)
        
        query = """
            SELECT l.LoanID, v.VehicleNo as Vehicle, l.LoanAmount, l.BalanceAmount, 
                   l.EMAmount as EMI, l.Status
            FROM Loan l
            JOIN Vehicle v ON l.VehicleID = v.VehicleID
            WHERE l.CustomerID = %s
            ORDER BY l.LoanID DESC
        """
        
        loans = self.db.execute_query(query, (self.customer_id,))
        if loans:
            for loan in loans:
                self.loans_tree.insert('', 'end', values=(
                    loan['LoanID'], loan['Vehicle'], loan['LoanAmount'],
                    loan['BalanceAmount'], loan['EMI'], loan['Status']
                ))
    
    def on_loan_select(self, event):
        selection = self.loans_tree.selection()
        if not selection:
            return
        
        item = self.loans_tree.item(selection[0])
        loan_id = item['values'][0]
        self.load_loan_installments(loan_id)
    
    def load_loan_installments(self, loan_id):
        for item in self.installments_tree.get_children():
            self.installments_tree.delete(item)
        
        query = """
            SELECT DueDate, TotalAmount as Amount, Status, LateFee, PaidDate
            FROM Installment
            WHERE LoanID = %s
            ORDER BY DueDate
        """
        
        installments = self.db.execute_query(query, (loan_id,))
        if installments:
            for installment in installments:
                paid_date = installment['PaidDate'] if installment['PaidDate'] else 'Not Paid'
                self.installments_tree.insert('', 'end', values=(
                    installment['DueDate'], installment['Amount'],
                    installment['Status'], installment['LateFee'], paid_date
                ))
    
    def load_payment_history(self):
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        query = """
            SELECT tl.TransactionDate as Date, tl.LoanID, tl.DebitAmount as Amount,
                   tl.TransactionType as Type, tl.Remarks
            FROM TransactionLogger tl
            JOIN Loan l ON tl.LoanID = l.LoanID
            WHERE l.CustomerID = %s AND tl.TransactionType = 'EMI Payment'
            ORDER BY tl.TransactionDate DESC
        """
        
        transactions = self.db.execute_query(query, (self.customer_id,))
        if transactions:
            for trans in transactions:
                self.history_tree.insert('', 'end', values=(
                    trans['Date'], trans['LoanID'], trans['Amount'],
                    trans['Type'], trans['Remarks']
                ))
    
    def export_my_loan_pdf(self):
        try:
            cur = self.loans_tree.selection()
            if cur:
                loan_id = self.loans_tree.item(cur[0])['values'][0]
            else:
                items = self.loans_tree.get_children()
                if not items:
                    messagebox.showinfo("No loans", "You have no loans")
                    return
                loan_id = self.loans_tree.item(items[0])['values'][0]
            generate_loan_pdf(self.db, loan_id, parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def logout(self):
        self.window.destroy()
        self.login_window.deiconify()
