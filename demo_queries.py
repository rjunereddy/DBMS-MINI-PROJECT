import tkinter as tk
from tkinter import ttk

class DemoQueries:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("Database Features Demo")
        self.window.geometry("1000x700")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.window, bg='#ecf0f1')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        title_label = tk.Label(main_frame, text="Database Features Demonstration", 
                              font=('Arial', 16, 'bold'), bg='#ecf0f1')
        title_label.pack(pady=10)
        
        query_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        query_frame.pack(fill='x', pady=10)
        
        tk.Label(query_frame, text="Select Query Type:", bg='white', font=('Arial', 10, 'bold')).pack(pady=5)
        
        buttons_frame = tk.Frame(query_frame, bg='white')
        buttons_frame.pack(pady=10)
        
        queries = [
            ('Nested Query', 'nested_query'),
            ('Aggregate with Join', 'aggregate_join'),
            ('Complex Join', 'complex_join'),
            ('View Demo', 'view_demo'),
            ('Trigger Demo', 'trigger_demo'),
            ('Function Demo', 'function_demo'),
            ('Procedure Demo', 'procedure_demo')
        ]
        
        for i, (text, query_type) in enumerate(queries):
            btn = tk.Button(buttons_frame, text=text, width=15, height=2,
                           command=lambda qt=query_type: self.execute_demo_query(qt))
            btn.grid(row=i//4, column=i%4, padx=5, pady=5)
        
        results_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        results_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(results_frame, text="Query Results:", bg='white', font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(results_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.results_tree = ttk.Treeview(tree_frame, show='headings')
        self.results_tree.pack(side='left', fill='both', expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        self.desc_label = tk.Label(results_frame, text="Select a query to see results", 
                                  bg='white', font=('Arial', 10), wraplength=800)
        self.desc_label.pack(pady=5)
    
    def execute_demo_query(self, query_type):
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Clear previous columns
        self.results_tree['columns'] = ()
        
        descriptions = {
            'nested_query': "NESTED QUERY: Customers with above average loan amounts using subqueries. Demonstrates correlated subqueries and nested SELECT statements.",
            'aggregate_join': "AGGREGATE WITH JOIN: Branch performance summary with GROUP BY, HAVING, and multiple aggregate functions (COUNT, SUM, AVG, MAX, MIN).",
            'complex_join': "COMPLEX JOIN: Loan details with multiple table joins (5 tables) and aggregate calculations. Shows relational database power.",
            'view_demo': "VIEW DEMO: Using CustomerLoanSummary view that combines data from multiple tables with calculated credit scores.",
            'trigger_demo': "TRIGGER DEMO: Showing overdue installments with auto-calculated late fees (trigger automatically updates status and fees).",
            'function_demo': "FUNCTION DEMO: Using CalculateCreditScore function to compute customer ratings. Shows user-defined functions in action.",
            'procedure_demo': "PROCEDURE DEMO: Loans ready for CreateLoanInstallments procedure. Stored procedures automate complex operations."
        }
        
        self.desc_label.config(text=descriptions.get(query_type, ""))
        
        results = self.db.execute_complex_query(query_type)
        
        if results and len(results) > 0:
            columns = list(results[0].keys())
            self.results_tree['columns'] = columns
            
            for col in columns:
                self.results_tree.heading(col, text=col)
                # Auto-adjust column width based on content
                col_width = max(80, len(col) * 8)
                self.results_tree.column(col, width=col_width, minwidth=80)
            
            for row in results:
                values = [row.get(col, '') for col in columns]
                self.results_tree.insert('', 'end', values=values)
        else:
            self.desc_label.config(text="No results returned or error in query execution")