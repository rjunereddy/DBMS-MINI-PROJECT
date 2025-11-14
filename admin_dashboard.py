import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from user_management import UserManagement
from demo_queries import DemoQueries
import logging

# Enhancements
from enhancements import generate_loan_pdf, show_admin_graphs, run_overdue_scan, simulate_notification

class AdminDashboard:
    def __init__(self, login_window, user, db):
        self.login_window = login_window
        self.user = user
        self.db = db
        
        self.window = tk.Toplevel()
        self.window.title(f"Admin Dashboard - {user['Username']}")
        self.window.geometry("1200x700")
        self.window.configure(bg='#ecf0f1')
        
        self.window.protocol("WM_DELETE_WINDOW", self.logout)
        self.window.deiconify()
        
        self.setup_ui()
        self.load_dashboard_data()
    
    def setup_ui(self):
        header_frame = tk.Frame(self.window, bg='#2c3e50', height=80)
        header_frame.pack(fill='x', padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="Admin Dashboard", font=('Arial', 20, 'bold'), 
                fg='white', bg='#2c3e50').pack(side='left', padx=20, pady=20)
        
        button_frame = tk.Frame(header_frame, bg='#2c3e50')
        button_frame.pack(side='right', padx=20, pady=20)
        
        user_btn = tk.Button(button_frame, text="User Management", command=self.open_user_management,
                            bg='#3498db', fg='white', font=('Arial', 10))
        user_btn.pack(side='left', padx=5)
        
        demo_btn = tk.Button(button_frame, text="DB Features Demo", command=self.open_demo_queries,
                            bg='#9b59b6', fg='white', font=('Arial', 10))
        demo_btn.pack(side='left', padx=5)
        
        # New enhancement buttons
        pdf_btn = tk.Button(button_frame, text="Export Loan PDF", command=lambda: self.export_selected_loan_pdf(),
                            bg='#16a085', fg='white', font=('Arial', 10))
        pdf_btn.pack(side='left', padx=5)

        graphs_btn = tk.Button(button_frame, text="Analytics", command=lambda: show_admin_graphs(self.db, self.window),
                               bg='#8e44ad', fg='white', font=('Arial', 10))
        graphs_btn.pack(side='left', padx=5)

        overdue_btn = tk.Button(button_frame, text="Run Overdue Scan", command=lambda: run_overdue_scan(self.db, self.window),
                                bg='#f39c12', fg='white', font=('Arial', 10))
        overdue_btn.pack(side='left', padx=5)
        
        logout_btn = tk.Button(button_frame, text="Logout", command=self.logout,
                              bg='#e74c3c', fg='white', font=('Arial', 10))
        logout_btn.pack(side='left', padx=5)
        
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="Reports & Statistics")
        
        self.loans_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.loans_frame, text="All Loans")
        
        self.seizures_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.seizures_frame, text="Seized Vehicles")
        
        self.setup_dashboard_tab()
        self.setup_reports_tab()
        self.setup_loans_tab()
        self.setup_seizures_tab()
    
    def setup_dashboard_tab(self):
        stats_frame = tk.Frame(self.dashboard_frame, bg='white', relief='raised', bd=2)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        stats_data = [
            ("Total Loans", "total_loans", "#3498db"),
            ("Active Loans", "active_loans", "#2ecc71"),
            ("Defaulted Loans", "defaulted_loans", "#e74c3c"),
            ("Total Customers", "total_customers", "#9b59b6"),
            ("Overdue Installments", "overdue_installments", "#f39c12"),
            ("Seized Vehicles", "seized_vehicles", "#34495e")
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
        
        activities_frame = tk.Frame(self.dashboard_frame, bg='white', relief='raised', bd=2)
        activities_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(activities_frame, text="Recent Transactions", font=('Arial', 14, 'bold'), 
                bg='white').pack(anchor='w', padx=10, pady=10)
        
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(activities_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.activities_tree = ttk.Treeview(tree_frame, 
                                          columns=('Date', 'LoanID', 'Type', 'Amount', 'Balance', 'Remarks'), 
                                          show='headings', height=8)
        
        for col in self.activities_tree['columns']:
            self.activities_tree.heading(col, text=col)
            self.activities_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.activities_tree.yview)
        self.activities_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activities_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_reports_tab(self):
        report_frame = tk.Frame(self.reports_frame, bg='white')
        report_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(report_frame, text="Select Report:", bg='white').pack(side='left', padx=5)
        
        self.report_var = tk.StringVar()
        report_combo = ttk.Combobox(report_frame, textvariable=self.report_var, width=20, state='readonly')
        report_combo['values'] = ('Monthly Collection', 'Agent Performance', 'Branch Performance', 'Loan Status Summary')
        report_combo.pack(side='left', padx=5)
        report_combo.bind('<<ComboboxSelected>>', self.generate_report)
        
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(self.reports_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.report_tree = ttk.Treeview(tree_frame, show='headings')
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        
        self.report_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_loans_tab(self):
        search_frame = tk.Frame(self.loans_frame, bg='white')
        search_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(search_frame, text="Search:", bg='white').pack(side='left', padx=5)
        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', lambda e: self.search_loans())
        
        search_btn = tk.Button(search_frame, text="Search", command=self.search_loans)
        search_btn.pack(side='left', padx=5)
        
        refresh_btn = tk.Button(search_frame, text="Refresh", command=self.load_loans)
        refresh_btn.pack(side='left', padx=5)
        
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(self.loans_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.loans_tree = ttk.Treeview(tree_frame, 
                                      columns=('LoanID', 'Customer', 'LoanAmount', 'Balance', 'Status', 'Agent', 'Branch'),
                                      show='headings')
        
        for col in self.loans_tree['columns']:
            self.loans_tree.heading(col, text=col)
            self.loans_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.loans_tree.yview)
        self.loans_tree.configure(yscrollcommand=scrollbar.set)
        
        self.loans_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def setup_seizures_tab(self):
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(self.seizures_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.seizures_tree = ttk.Treeview(tree_frame,
                                         columns=('SeizureID', 'LoanID', 'Customer', 'Vehicle', 'SeizureDate', 'Status', 'Reason'),
                                         show='headings')
        
        for col in self.seizures_tree['columns']:
            self.seizures_tree.heading(col, text=col)
            self.seizures_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.seizures_tree.yview)
        self.seizures_tree.configure(yscrollcommand=scrollbar.set)
        
        self.seizures_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def load_dashboard_data(self):
        try:
            stats_queries = {
                'total_loans': "SELECT COUNT(*) as count FROM Loan",
                'active_loans': "SELECT COUNT(*) as count FROM Loan WHERE Status = 'Active'",
                'defaulted_loans': "SELECT COUNT(*) as count FROM Loan WHERE Status = 'Defaulted'",
                'total_customers': "SELECT COUNT(*) as count FROM Customer",
                'overdue_installments': "SELECT COUNT(*) as count FROM Installment WHERE Status = 'Overdue'",
                'seized_vehicles': "SELECT COUNT(*) as count FROM Seizure WHERE SeizureStatus = 'Completed'"
            }
            
            for key, query in stats_queries.items():
                result = self.db.execute_query(query)
                if result:
                    self.stats_labels[key].config(text=result[0]['count'])
                else:
                    self.stats_labels[key].config(text="0")
            
            transactions_query = """
                SELECT tl.TransactionDate as Date, tl.LoanID, tl.TransactionType as Type,
                       tl.DebitAmount as Amount, tl.BalanceAfterTransaction as Balance,
                       tl.Remarks
                FROM TransactionLogger tl
                ORDER BY tl.TransactionDate DESC 
                LIMIT 20
            """
            transactions = self.db.execute_query(transactions_query)
            if transactions:
                for trans in transactions:
                    self.activities_tree.insert('', 'end', values=(
                        trans['Date'], trans['LoanID'], trans['Type'],
                        trans['Amount'], trans['Balance'], trans['Remarks']
                    ))
            
            self.load_loans()
            self.load_seizures()
            
        except Exception as e:
            logging.error(f"Error loading dashboard data: {e}")
            messagebox.showerror("Error", f"Failed to load dashboard data: {str(e)}")
    
    def load_loans(self):
        for item in self.loans_tree.get_children():
            self.loans_tree.delete(item)
        
        query = """
            SELECT l.LoanID, CONCAT(c.FirstName, ' ', c.LastName) as Customer,
                   l.LoanAmount, l.BalanceAmount, l.Status, a.Name as Agent, b.BranchName as Branch
            FROM Loan l
            JOIN Customer c ON l.CustomerID = c.CustomerID
            JOIN Agent a ON l.AgentID = a.AgentID
            JOIN Branch b ON l.BranchID = b.BranchID
            ORDER BY l.LoanID DESC
        """
        
        loans = self.db.execute_query(query)
        if loans:
            for loan in loans:
                self.loans_tree.insert('', 'end', values=(
                    loan['LoanID'], loan['Customer'], loan['LoanAmount'],
                    loan['BalanceAmount'], loan['Status'], loan['Agent'], loan['Branch']
                ))
    
    def load_seizures(self):
        for item in self.seizures_tree.get_children():
            self.seizures_tree.delete(item)
        
        query = """
            SELECT s.SeizureID, s.LoanID, CONCAT(c.FirstName, ' ', c.LastName) as Customer,
                   v.VehicleNo, s.SeizureDate, s.SeizureStatus, s.Reason
            FROM Seizure s
            JOIN Loan l ON s.LoanID = l.LoanID
            JOIN Customer c ON l.CustomerID = c.CustomerID
            JOIN Vehicle v ON l.VehicleID = v.VehicleID
            ORDER BY s.SeizureDate DESC
        """
        
        seizures = self.db.execute_query(query)
        if seizures:
            for seizure in seizures:
                self.seizures_tree.insert('', 'end', values=(
                    seizure['SeizureID'], seizure['LoanID'], seizure['Customer'],
                    seizure['VehicleNo'], seizure['SeizureDate'], 
                    seizure['SeizureStatus'], seizure['Reason']
                ))
    
    def search_loans(self):
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_loans()
            return
        
        query = """
            SELECT l.LoanID, CONCAT(c.FirstName, ' ', c.LastName) as Customer,
                   l.LoanAmount, l.BalanceAmount, l.Status, a.Name as Agent, b.BranchName as Branch
            FROM Loan l
            JOIN Customer c ON l.CustomerID = c.CustomerID
            JOIN Agent a ON l.AgentID = a.AgentID
            JOIN Branch b ON l.BranchID = b.BranchID
            WHERE c.FirstName LIKE %s OR c.LastName LIKE %s OR l.LoanID = %s OR a.Name LIKE %s
            OR b.BranchName LIKE %s
        """
        
        try:
            search_param = f"%{search_term}%"
            loans = self.db.execute_query(query, (search_param, search_param, search_term, search_param, search_param))
            
            for item in self.loans_tree.get_children():
                self.loans_tree.delete(item)
            
            if loans:
                for loan in loans:
                    self.loans_tree.insert('', 'end', values=(
                        loan['LoanID'], loan['Customer'], loan['LoanAmount'],
                        loan['BalanceAmount'], loan['Status'], loan['Agent'], loan['Branch']
                    ))
            else:
                messagebox.showinfo("No Results", "No loans found matching your search criteria")
        except Exception as e:
            messagebox.showerror("Search Error", f"Failed to search loans: {str(e)}")
    
    def generate_report(self, event=None):
        report_type = self.report_var.get()
        if not report_type:
            return
        
        # Clear previous results
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # Clear previous columns
        self.report_tree['columns'] = ()
        
        if report_type == 'Monthly Collection':
            query = """
                SELECT DATE_FORMAT(TransactionDate, '%Y-%m') as Month,
                       SUM(DebitAmount) as TotalCollection,
                       COUNT(*) as TotalTransactions
                FROM TransactionLogger
                WHERE TransactionType = 'EMI Payment'
                GROUP BY DATE_FORMAT(TransactionDate, '%Y-%m')
                ORDER BY Month DESC
            """
            columns = ('Month', 'Total Collection', 'Transactions')
        
        elif report_type == 'Agent Performance':
            query = """
                SELECT a.Name as Agent, b.BranchName,
                       COUNT(l.LoanID) as TotalLoans,
                       SUM(l.LoanAmount) as TotalVolume,
                       AVG(l.InterestRate) as AvgInterestRate
                FROM Agent a
                JOIN Branch b ON a.BranchID = b.BranchID
                LEFT JOIN Loan l ON a.AgentID = l.AgentID
                GROUP BY a.AgentID, a.Name, b.BranchName
            """
            columns = ('Agent', 'Branch', 'Total Loans', 'Loan Volume', 'Avg Interest Rate')
        
        elif report_type == 'Branch Performance':
            query = """
                SELECT b.BranchName, b.ManagerName,
                       COUNT(l.LoanID) as TotalLoans,
                       SUM(l.LoanAmount) as TotalSanctioned,
                       SUM(l.BalanceAmount) as Outstanding
                FROM Branch b
                LEFT JOIN Loan l ON b.BranchID = l.BranchID
                GROUP BY b.BranchID, b.BranchName, b.ManagerName
            """
            columns = ('Branch', 'Manager', 'Total Loans', 'Sanctioned Amount', 'Outstanding')
        
        elif report_type == 'Loan Status Summary':
            query = """
                SELECT Status, COUNT(*) as Count, 
                       SUM(LoanAmount) as TotalAmount,
                       AVG(InterestRate) as AvgInterestRate
                FROM Loan
                GROUP BY Status
            """
            columns = ('Status', 'Count', 'Total Amount', 'Avg Interest Rate')
        else:
            return
        
        try:
            self.report_tree['columns'] = columns
            
            for col in columns:
                self.report_tree.heading(col, text=col)
                col_width = max(100, len(col) * 8)
                self.report_tree.column(col, width=col_width)
            
            results = self.db.execute_query(query)
            if results:
                for row in results:
                    self.report_tree.insert('', 'end', values=tuple(row.values()))
        except Exception as e:
            messagebox.showerror("Report Error", f"Failed to generate report: {str(e)}")
    
    def open_user_management(self):
        try:
            UserManagement(self.window, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open user management: {str(e)}")
    
    def open_demo_queries(self):
        try:
            DemoQueries(self.window, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open demo queries: {str(e)}")
    
    def export_selected_loan_pdf(self):
        try:
            sel = self.loans_tree.selection()
            if sel:
                item = self.loans_tree.item(sel[0])
                loan_id = item['values'][0]
            else:
                loan_id = simpledialog.askinteger("Loan ID", "Enter Loan ID to export")
            if not loan_id:
                return
            generate_loan_pdf(self.db, loan_id, parent=self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {e}")
    
    def logout(self):
        self.window.destroy()
        self.login_window.deiconify()
