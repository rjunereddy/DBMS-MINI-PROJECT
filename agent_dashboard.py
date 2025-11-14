import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils import LoanCalculator
import logging

# enhancements
from enhancements import show_emi_calculator, generate_loan_pdf, foreclose_loan, show_customer_profile, simulate_notification

class AgentDashboard:
    def __init__(self, login_window, user, db):
        self.login_window = login_window
        self.user = user
        self.db = db
        self.agent_id = user.get('AgentID')
        self.branch_id = user.get('BranchID')
        
        self.window = tk.Toplevel()
        self.window.title(f"Agent Dashboard - {user.get('AgentName','Agent')}")
        self.window.geometry("1200x700")
        self.window.configure(bg='#ecf0f1')
        
        self.window.protocol("WM_DELETE_WINDOW", self.logout)
        self.window.deiconify()
        
        self.setup_ui()
        self.load_agent_data()
    
    def setup_ui(self):
        header_frame = tk.Frame(self.window, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"Agent Dashboard - {self.user.get('AgentName','Agent')}", 
                font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=20)
        
        logout_btn = tk.Button(header_frame, text="Logout", command=self.logout,
                              bg='#e74c3c', fg='white', font=('Arial', 12))
        logout_btn.pack(side='right', padx=20, pady=20)

        # EMI calculator quick access
        emi_btn = tk.Button(header_frame, text="EMI Calculator", command=lambda: show_emi_calculator(self.window),
                            bg='#27ae60', fg='white', font=('Arial', 10))
        emi_btn.pack(side='right', padx=5, pady=20)
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        self.create_loan_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.create_loan_frame, text="Create New Loan")
        
        self.payment_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.payment_frame, text="Collect Payments")
        
        self.seizure_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.seizure_frame, text="Seize Vehicle")
        
        self.setup_dashboard_tab()
        self.setup_create_loan_tab()
        self.setup_payment_tab()
        self.setup_seizure_tab()
    
    def setup_dashboard_tab(self):
        stats_frame = tk.Frame(self.dashboard_frame, bg='white', relief='raised', bd=2)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        stats_data = [
            ("My Loans", "my_loans", "#3498db"),
            ("Active Loans", "active_loans", "#2ecc71"),
            ("Overdue Loans", "overdue_loans", "#e74c3c"),
            ("Total Collection", "total_collection", "#9b59b6")
        ]
        
        self.stats_labels = {}
        for i, (text, key, color) in enumerate(stats_data):
            frame = tk.Frame(stats_frame, bg=color, width=180, height=80)
            frame.grid(row=0, column=i, padx=5, pady=10)
            frame.pack_propagate(False)
            
            tk.Label(frame, text=text, fg='white', bg=color, font=('Arial', 10)).pack(pady=5)
            label = tk.Label(frame, text="0", fg='white', bg=color, font=('Arial', 16, 'bold'))
            label.pack()
            self.stats_labels[key] = label
        
        loans_frame = tk.Frame(self.dashboard_frame, bg='white', relief='raised', bd=2)
        loans_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(loans_frame, text="My Managed Loans", font=('Arial', 14, 'bold'), 
                bg='white').pack(anchor='w', padx=10, pady=10)
        
        # Treeview with scrollbar
        tree_frame = tk.Frame(loans_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.my_loans_tree = ttk.Treeview(tree_frame, 
                                         columns=('LoanID', 'Customer', 'LoanAmount', 'Balance', 'Status', 'EMI'),
                                         show='headings')
        
        for col in self.my_loans_tree['columns']:
            self.my_loans_tree.heading(col, text=col)
            self.my_loans_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.my_loans_tree.yview)
        self.my_loans_tree.configure(yscrollcommand=scrollbar.set)
        
        self.my_loans_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_create_loan_tab(self):
        form_frame = tk.Frame(self.create_loan_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        customer_frame = tk.LabelFrame(form_frame, text="Customer Search & Selection", bg='white')
        customer_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(customer_frame, text="Search Customer:", bg='white').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.customer_search = tk.Entry(customer_frame, width=30)
        self.customer_search.grid(row=0, column=1, pady=5, padx=5)
        self.customer_search.bind('<Return>', lambda e: self.search_customer())
        
        search_btn = tk.Button(customer_frame, text="Search", command=self.search_customer)
        search_btn.grid(row=0, column=2, pady=5, padx=5)
        
        # Customer treeview
        customer_tree_frame = tk.Frame(customer_frame, bg='white')
        customer_tree_frame.grid(row=1, column=0, columnspan=3, pady=5, padx=5, sticky='ew')
        
        self.customer_tree = ttk.Treeview(customer_tree_frame, columns=('CustomerID', 'Name', 'Phone', 'Email'), 
                                         show='headings', height=4)
        
        for col in self.customer_tree['columns']:
            self.customer_tree.heading(col, text=col)
        
        customer_scrollbar = ttk.Scrollbar(customer_tree_frame, orient="vertical", command=self.customer_tree.yview)
        self.customer_tree.configure(yscrollcommand=customer_scrollbar.set)
        
        self.customer_tree.pack(side='left', fill='both', expand=True)
        customer_scrollbar.pack(side='right', fill='y')
        
        self.customer_tree.bind('<<TreeviewSelect>>', self.on_customer_select)
        
        vehicle_frame = tk.LabelFrame(form_frame, text="Vehicle Details", bg='white')
        vehicle_frame.pack(fill='x', padx=10, pady=5)
        
        fields = [
            ('Vehicle Number:*', 'vehicle_no'),
            ('Make:*', 'vehicle_make'),
            ('Model:*', 'vehicle_model'),
            ('Year:*', 'vehicle_year'),
            ('Market Value:*', 'market_value'),
            ('Insurance Expiry (YYYY-MM-DD):*', 'insurance_expiry')
        ]
        
        self.vehicle_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(vehicle_frame, text=label, bg='white').grid(row=i, column=0, sticky='w', pady=2, padx=5)
            entry = tk.Entry(vehicle_frame, width=30)
            entry.grid(row=i, column=1, pady=2, padx=5)
            self.vehicle_entries[key] = entry
        
        loan_frame = tk.LabelFrame(form_frame, text="Loan Details", bg='white')
        loan_frame.pack(fill='x', padx=10, pady=5)
        
        loan_fields = [
            ('Loan Amount:*', 'loan_amount'),
            ('Interest Rate (%):*', 'interest_rate'),
            ('Tenure (Months):*', 'tenure')
        ]
        
        self.loan_entries = {}
        for i, (label, key) in enumerate(loan_fields):
            tk.Label(loan_frame, text=label, bg='white').grid(row=i, column=0, sticky='w', pady=2, padx=5)
            entry = tk.Entry(loan_frame, width=30)
            entry.grid(row=i, column=1, pady=2, padx=5)
            self.loan_entries[key] = entry
        
        calc_btn = tk.Button(loan_frame, text="Calculate EMI", command=self.calculate_emi)
        calc_btn.grid(row=3, column=0, pady=10, padx=5)
        
        tk.Label(loan_frame, text="Monthly EMI:", bg='white').grid(row=3, column=1, sticky='w', pady=10, padx=5)
        self.emi_label = tk.Label(loan_frame, text="₹0.00", bg='white', fg='green', font=('Arial', 10, 'bold'))
        self.emi_label.grid(row=3, column=2, sticky='w', pady=10, padx=5)
        
        create_btn = tk.Button(form_frame, text="Create Loan", command=self.create_loan,
                              bg='#27ae60', fg='white', font=('Arial', 12))
        create_btn.pack(pady=20)
        
        # Quick view customer profile button
        profile_btn = tk.Button(customer_frame, text="View Profile", command=lambda: self.open_selected_customer_profile(),
                                bg='#16a085', fg='white')
        profile_btn.grid(row=2, column=0, pady=6, padx=5, sticky='w')
    
    def setup_payment_tab(self):
        payment_frame = tk.Frame(self.payment_frame, bg='white')
        payment_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(payment_frame, text="Select Loan:", bg='white').pack(anchor='w', padx=10, pady=5)
        
        self.loan_var = tk.StringVar()
        self.loan_combo = ttk.Combobox(payment_frame, textvariable=self.loan_var, width=50, state='readonly')
        self.loan_combo.pack(fill='x', padx=10, pady=5)
        self.loan_combo.bind('<<ComboboxSelected>>', self.load_installments)
        
        load_btn = tk.Button(payment_frame, text="Load My Loans", command=self.load_agent_loans)
        load_btn.pack(anchor='w', padx=10, pady=5)
        
        # Installments treeview with scrollbar
        tree_frame = tk.Frame(payment_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.installments_tree = ttk.Treeview(tree_frame, 
                                             columns=('InstallmentID', 'DueDate', 'Amount', 'Status', 'LateFee'),
                                             show='headings', height=8)
        
        for col in self.installments_tree['columns']:
            self.installments_tree.heading(col, text=col)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.installments_tree.yview)
        self.installments_tree.configure(yscrollcommand=scrollbar.set)
        
        self.installments_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        details_frame = tk.Frame(payment_frame, bg='white')
        details_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(details_frame, text="Payment Mode:", bg='white').pack(side='left', padx=5)
        self.payment_mode = ttk.Combobox(details_frame, values=('Cash', 'Cheque', 'Online Transfer', 'UPI'), 
                                       width=20, state='readonly')
        self.payment_mode.pack(side='left', padx=5)
        
        collect_btn = tk.Button(details_frame, text="Collect Payment", command=self.collect_payment,
                               bg='#2980b9', fg='white', font=('Arial', 12))
        collect_btn.pack(side='left', padx=20)
        
        # Export PDF & Foreclose buttons
        pdf_btn = tk.Button(details_frame, text="Export Loan PDF", command=self.export_current_loan_pdf)
        pdf_btn.pack(side='left', padx=5)
        foreclose_btn = tk.Button(details_frame, text="Foreclose Loan", command=self.foreclose_selected_loan, bg='#e74c3c', fg='white')
        foreclose_btn.pack(side='left', padx=5)
    
    def setup_seizure_tab(self):
        seizure_frame = tk.Frame(self.seizure_frame, bg='white')
        seizure_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(seizure_frame, text="Select Defaulted Loan:", bg='white').pack(anchor='w', padx=10, pady=5)
        
        self.seizure_loan_var = tk.StringVar()
        self.seizure_loan_combo = ttk.Combobox(seizure_frame, textvariable=self.seizure_loan_var, width=50, state='readonly')
        self.seizure_loan_combo.pack(fill='x', padx=10, pady=5)
        
        load_btn = tk.Button(seizure_frame, text="Load Defaulted Loans", command=self.load_defaulted_loans)
        load_btn.pack(anchor='w', padx=10, pady=5)
        
        # Use details_frame as the parent for all grid-managed widgets
        details_frame = tk.LabelFrame(seizure_frame, text="Seizure Details", bg='white')
        details_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(details_frame, text="Reason:*", bg='white').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.seizure_reason = tk.Entry(details_frame, width=50)
        self.seizure_reason.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(details_frame, text="Vehicle Condition:*", bg='white').grid(row=1, column=0, sticky='w', pady=5, padx=5)
        # parent must be details_frame (not seizure_frame)
        self.vehicle_condition = ttk.Combobox(details_frame, 
                                             values=('Excellent', 'Good', 'Fair', 'Poor', 'Damaged'),
                                             state='readonly')
        self.vehicle_condition.grid(row=1, column=1, pady=5, padx=5)
        
        seize_btn = tk.Button(seizure_frame, text="Initiate Seizure", command=self.initiate_seizure,
                             bg='#e74c3c', fg='white', font=('Arial', 12))
        seize_btn.pack(pady=20)
    
    def load_agent_data(self):
        try:
            my_loans_query = "SELECT COUNT(*) as count FROM Loan WHERE AgentID = %s"
            result = self.db.execute_query(my_loans_query, (self.agent_id,))
            if result:
                self.stats_labels['my_loans'].config(text=result[0]['count'])
            
            active_loans_query = "SELECT COUNT(*) as count FROM Loan WHERE AgentID = %s AND Status = 'Active'"
            result = self.db.execute_query(active_loans_query, (self.agent_id,))
            if result:
                self.stats_labels['active_loans'].config(text=result[0]['count'])
            
            overdue_loans_query = """
                SELECT COUNT(DISTINCT l.LoanID) as count 
                FROM Loan l 
                JOIN Installment i ON l.LoanID = i.LoanID 
                WHERE l.AgentID = %s AND i.Status = 'Overdue'
            """
            result = self.db.execute_query(overdue_loans_query, (self.agent_id,))
            if result:
                self.stats_labels['overdue_loans'].config(text=result[0]['count'])
            
            collection_query = """
                SELECT SUM(tl.DebitAmount) as total 
                FROM TransactionLogger tl
                JOIN Loan l ON tl.LoanID = l.LoanID
                WHERE l.AgentID = %s AND tl.TransactionType = 'EMI Payment'
            """
            result = self.db.execute_query(collection_query, (self.agent_id,))
            if result and result[0]['total']:
                self.stats_labels['total_collection'].config(text=f"₹{result[0]['total']:,.2f}")
            else:
                self.stats_labels['total_collection'].config(text="₹0.00")
            
            self.load_my_loans()
            
        except Exception as e:
            logging.error(f"Error loading agent data: {e}")
            messagebox.showerror("Error", f"Failed to load agent data: {str(e)}")
    
    def load_my_loans(self):
        for item in self.my_loans_tree.get_children():
            self.my_loans_tree.delete(item)
        
        query = """
            SELECT l.LoanID, CONCAT(c.FirstName, ' ', c.LastName) as Customer,
                   l.LoanAmount, l.BalanceAmount, l.Status, l.EMAmount as EMI
            FROM Loan l
            JOIN Customer c ON l.CustomerID = c.CustomerID
            WHERE l.AgentID = %s
            ORDER BY l.LoanID DESC
        """
        
        loans = self.db.execute_query(query, (self.agent_id,))
        if loans:
            for loan in loans:
                self.my_loans_tree.insert('', 'end', values=(
                    loan['LoanID'], loan['Customer'], loan['LoanAmount'],
                    loan['BalanceAmount'], loan['Status'], loan['EMI']
                ))
    
    def search_customer(self):
        search_term = self.customer_search.get().strip()
        if not search_term:
            messagebox.showwarning("Warning", "Please enter search term")
            return
        
        query = """
            SELECT CustomerID, CONCAT(FirstName, ' ', LastName) as Name, Phone, Email
            FROM Customer
            WHERE FirstName LIKE %s OR LastName LIKE %s OR Phone LIKE %s OR Email LIKE %s
        """
        
        customers = self.db.execute_query(query, 
                                        (f"%{search_term}%", f"%{search_term}%", 
                                         f"%{search_term}%", f"%{search_term}%"))
        
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        
        if customers:
            for customer in customers:
                self.customer_tree.insert('', 'end', values=(
                    customer['CustomerID'], customer['Name'], 
                    customer['Phone'], customer['Email']
                ))
        else:
            messagebox.showinfo("No Results", "No customers found matching your search")
    
    def on_customer_select(self, event):
        selection = self.customer_tree.selection()
        if selection:
            item = self.customer_tree.item(selection[0])
            self.selected_customer_id = item['values'][0]
    
    def calculate_emi(self):
        try:
            loan_amount = float(self.loan_entries['loan_amount'].get())
            interest_rate = float(self.loan_entries['interest_rate'].get())
            tenure = int(self.loan_entries['tenure'].get())
            
            # Validate loan parameters
            market_value_text = self.vehicle_entries['market_value'].get()
            if market_value_text:
                market_value = float(market_value_text)
                validation_errors = LoanCalculator.validate_loan_parameters(loan_amount, market_value, interest_rate, tenure)
                if validation_errors:
                    messagebox.showerror("Validation Error", "\n".join(validation_errors))
                    return
            
            emi = LoanCalculator.calculate_emi(loan_amount, interest_rate, tenure)
            self.emi_label.config(text=f"₹{emi:,.2f}")
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid loan details (numbers only)")
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating EMI: {str(e)}")
    
    def create_loan(self):
        try:
            if not hasattr(self, 'selected_customer_id'):
                messagebox.showerror("Error", "Please select a customer")
                return
            
            # Validate required fields
            required_fields = {
                'vehicle_no': 'Vehicle Number',
                'vehicle_make': 'Vehicle Make', 
                'vehicle_model': 'Vehicle Model',
                'vehicle_year': 'Vehicle Year',
                'market_value': 'Market Value',
                'insurance_expiry': 'Insurance Expiry',
                'loan_amount': 'Loan Amount',
                'interest_rate': 'Interest Rate',
                'tenure': 'Tenure'
            }
            
            missing_fields = []
            for field_key, field_name in required_fields.items():
                if field_key in self.vehicle_entries:
                    value = self.vehicle_entries[field_key].get().strip()
                else:
                    value = self.loan_entries[field_key].get().strip()
                if not value:
                    missing_fields.append(field_name)
            
            if missing_fields:
                messagebox.showerror("Error", f"Please fill all required fields:\n" + "\n".join(missing_fields))
                return
            
            # Get and validate vehicle data
            vehicle_no = self.vehicle_entries['vehicle_no'].get().strip()
            make = self.vehicle_entries['vehicle_make'].get().strip()
            model = self.vehicle_entries['vehicle_model'].get().strip()
            year = int(self.vehicle_entries['vehicle_year'].get())
            market_value = float(self.vehicle_entries['market_value'].get())
            insurance_expiry = self.vehicle_entries['insurance_expiry'].get().strip()
            
            # Get and validate loan data
            loan_amount = float(self.loan_entries['loan_amount'].get())
            interest_rate = float(self.loan_entries['interest_rate'].get())
            tenure = int(self.loan_entries['tenure'].get())
            
            # Validate business rules
            validation_errors = LoanCalculator.validate_loan_parameters(loan_amount, market_value, interest_rate, tenure)
            if validation_errors:
                messagebox.showerror("Validation Error", "\n".join(validation_errors))
                return
            
            # Calculate financials
            emi = LoanCalculator.calculate_emi(loan_amount, interest_rate, tenure)
            total_payable = LoanCalculator.calculate_total_payable(emi, tenure)
            
            # Create loan using transaction
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            try:
                # Create vehicle
                vehicle_query = """
                    INSERT INTO Vehicle (CustomerID, VehicleNo, Make, Model, `Year`, 
                                       MarketValue, InsuranceExpiry, `Condition`)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Good')
                """
                cursor.execute(vehicle_query, (self.selected_customer_id, vehicle_no, make, 
                                             model, year, market_value, insurance_expiry))
                vehicle_id = cursor.lastrowid
                
                # Create loan
                loan_query = """
                    INSERT INTO Loan (CustomerID, VehicleID, LoanAmount, SanctionDate, 
                                    TenureMonths, InterestRate, EMAmount, TotalPayable, 
                                    BalanceAmount, Status, BranchID, AgentID)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'Active', %s, %s)
                """
                cursor.execute(loan_query, (self.selected_customer_id, vehicle_id, loan_amount,
                                          datetime.now().date(), tenure, interest_rate, emi,
                                          total_payable, loan_amount, self.branch_id, self.agent_id))
                loan_id = cursor.lastrowid
                
                # Create installments using procedure
                cursor.callproc('CreateLoanInstallments', 
                               (loan_id, loan_amount, interest_rate, tenure, datetime.now().date()))
                
                # Log transaction
                transaction_query = """
                    INSERT INTO TransactionLogger (LoanID, CreditAmount, BalanceAfterTransaction, 
                                                Remarks, TransactionType)
                    VALUES (%s, %s, %s, 'Loan Disbursement', 'Loan Disbursement')
                """
                cursor.execute(transaction_query, (loan_id, loan_amount, loan_amount))
                
                conn.commit()
                messagebox.showinfo("Success", "Loan created successfully!")
                
                self.clear_loan_form()
                self.load_agent_data()
                
            except Exception as e:
                conn.rollback()
                logging.error(f"Loan creation error: {e}")
                messagebox.showerror("Error", f"Failed to create loan: {str(e)}")
            finally:
                cursor.close()
                conn.close()
                
        except ValueError as e:
            messagebox.showerror("Error", "Please check all fields have valid values")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
    
    def clear_loan_form(self):
        for entry in self.vehicle_entries.values():
            entry.delete(0, tk.END)
        for entry in self.loan_entries.values():
            entry.delete(0, tk.END)
        self.emi_label.config(text="₹0.00")
        for item in self.customer_tree.get_children():
            self.customer_tree.delete(item)
        if hasattr(self, 'selected_customer_id'):
            del self.selected_customer_id
        self.customer_search.delete(0, tk.END)
    
    def load_agent_loans(self):
        query = """
            SELECT l.LoanID, CONCAT(c.FirstName, ' ', c.LastName, ' - Loan ₹', l.LoanAmount) as Display
            FROM Loan l
            JOIN Customer c ON l.CustomerID = c.CustomerID
            WHERE l.AgentID = %s AND l.Status = 'Active'
        """
        
        loans = self.db.execute_query(query, (self.agent_id,))
        
        self.loan_combo['values'] = []
        if loans:
            loan_values = [f"{loan['LoanID']} - {loan['Display']}" for loan in loans]
            self.loan_combo['values'] = loan_values
        else:
            messagebox.showinfo("No Loans", "No active loans found for your account")
    
    def load_installments(self, event=None):
        if not self.loan_var.get():
            return
        
        loan_id = self.loan_var.get().split(' - ')[0]
        
        query = """
            SELECT InstallmentID, DueDate, TotalAmount, Status, LateFee
            FROM Installment
            WHERE LoanID = %s
            ORDER BY DueDate
        """
        
        installments = self.db.execute_query(query, (loan_id,))
        
        for item in self.installments_tree.get_children():
            self.installments_tree.delete(item)
        
        if installments:
            for installment in installments:
                self.installments_tree.insert('', 'end', values=(
                    installment['InstallmentID'], installment['DueDate'],
                    installment['TotalAmount'], installment['Status'],
                    installment['LateFee']
                ))
    
    def collect_payment(self):
        selection = self.installments_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an installment")
            return
        
        if not self.payment_mode.get():
            messagebox.showwarning("Warning", "Please select payment mode")
            return
        
        item = self.installments_tree.item(selection[0])
        installment_id = item['values'][0]
        payment_mode = self.payment_mode.get()
        
        try:
            result = self.db.call_procedure('ProcessEMIPayment', (installment_id, payment_mode, datetime.now().date()))
            
            if result is not None:
                messagebox.showinfo("Success", "Payment collected successfully!")
                self.load_installments()
                self.load_agent_data()
            else:
                messagebox.showerror("Error", "Failed to process payment")
        except Exception as e:
            messagebox.showerror("Error", f"Payment processing failed: {str(e)}")
    
    def open_selected_customer_profile(self):
        try:
            if not hasattr(self, 'selected_customer_id'):
                messagebox.showwarning("Select Customer", "Please select a customer first")
                return
            show_customer_profile(self.db, self.selected_customer_id, parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open profile: {e}")
    
    def export_current_loan_pdf(self):
        try:
            if not self.loan_var.get():
                messagebox.showwarning("Select Loan", "Please select a loan first")
                return
            loan_id = int(self.loan_var.get().split(' - ')[0])
            generate_loan_pdf(self.db, loan_id, parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")

    def foreclose_selected_loan(self):
        try:
            if not self.loan_var.get():
                messagebox.showwarning("Select Loan", "Please select a loan first")
                return
            loan_id = int(self.loan_var.get().split(' - ')[0])
            ok = messagebox.askyesno("Confirm", f"Foreclose loan {loan_id}? This will mark remaining balance as paid.")
            if not ok:
                return
            success = foreclose_loan(self.db, loan_id, agent_id=self.agent_id, parent=self.window)
            if success:
                simulate_notification(self.window, "Loan Foreclosed", f"Loan {loan_id} foreclosed by {self.user.get('AgentName','Agent')}")
                self.load_agent_data()
                self.load_installments()
        except Exception as e:
            messagebox.showerror("Error", f"Foreclosure failed: {e}")
    
    def load_defaulted_loans(self):
        query = """
            SELECT DISTINCT l.LoanID, CONCAT(c.FirstName, ' ', c.LastName, ' - Loan ₹', l.LoanAmount) as Display
            FROM Loan l
            JOIN Customer c ON l.CustomerID = c.CustomerID
            JOIN Installment i ON l.LoanID = i.LoanID
            WHERE l.AgentID = %s AND i.Status = 'Overdue'
            AND i.DueDate < DATE_SUB(CURDATE(), INTERVAL 90 DAY)
        """
        
        loans = self.db.execute_query(query, (self.agent_id,))
        
        self.seizure_loan_combo['values'] = []
        if loans:
            loan_values = [f"{loan['LoanID']} - {loan['Display']}" for loan in loans]
            self.seizure_loan_combo['values'] = loan_values
        else:
            messagebox.showinfo("No Defaults", "No loans eligible for seizure found")
    
    def initiate_seizure(self):
        if not self.seizure_loan_var.get():
            messagebox.showwarning("Warning", "Please select a loan")
            return
        
        if not self.seizure_reason.get().strip():
            messagebox.showwarning("Warning", "Please enter seizure reason")
            return
        
        if not self.vehicle_condition.get():
            messagebox.showwarning("Warning", "Please select vehicle condition")
            return
        
        loan_id = self.seizure_loan_var.get().split(' - ')[0]
        reason = self.seizure_reason.get().strip()
        condition = self.vehicle_condition.get()
        
        query = """
            INSERT INTO Seizure (LoanID, AgentID, SeizureDate, Reason, 
                               VehicleConditionAtSeizure, SeizureStatus)
            VALUES (%s, %s, %s, %s, %s, 'Initiated')
        """
        
        try:
            result = self.db.execute_query(query, (loan_id, self.agent_id, datetime.now().date(), reason, condition), False)
            
            if result:
                # Update loan status to defaulted
                update_query = "UPDATE Loan SET Status = 'Defaulted' WHERE LoanID = %s"
                self.db.execute_query(update_query, (loan_id,), False)
                
                messagebox.showinfo("Success", "Seizure initiated successfully!")
                self.seizure_reason.delete(0, tk.END)
                self.vehicle_condition.set('')
                self.seizure_loan_var.set('')
                self.load_defaulted_loans()
            else:
                messagebox.showerror("Error", "Failed to initiate seizure")
        except Exception as e:
            messagebox.showerror("Error", f"Seizure initiation failed: {str(e)}")
    
    def logout(self):
        self.window.destroy()
        self.login_window.deiconify()
