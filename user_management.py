import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import re

class UserManagement:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        
        self.window = tk.Toplevel(parent)
        self.window.title("User Management")
        self.window.geometry("800x600")
        self.window.configure(bg='#ecf0f1')
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_existing_users()
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.agent_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.agent_frame, text="Create Agent")
        
        self.customer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customer_frame, text="Create Customer")
        
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="View All Users")
        
        self.setup_agent_tab()
        self.setup_customer_tab()
        self.setup_view_tab()
    
    def setup_agent_tab(self):
        form_frame = tk.Frame(self.agent_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        personal_frame = tk.LabelFrame(form_frame, text="Personal Details", bg='white')
        personal_frame.pack(fill='x', padx=10, pady=5)
        
        fields = [
            ('Name:*', 'name', 'text'),
            ('Role:*', 'role', 'combo'),
            ('Phone:*', 'phone', 'text'),
            ('Email:', 'email', 'text'),
            ('Salary:*', 'salary', 'text'),
            ('Hire Date (YYYY-MM-DD):*', 'hire_date', 'text')
        ]
        
        self.agent_entries = {}
        for i, (label, key, field_type) in enumerate(fields):
            tk.Label(personal_frame, text=label, bg='white').grid(row=i, column=0, sticky='w', pady=5, padx=5)
            if field_type == 'combo':
                entry = ttk.Combobox(personal_frame, values=['Loan Officer', 'Field Agent', 'Supervisor', 'Manager'], 
                                   width=30, state='readonly')
            else:
                entry = tk.Entry(personal_frame, width=30)
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.agent_entries[key] = entry
        
        tk.Label(personal_frame, text="Branch:*", bg='white').grid(row=6, column=0, sticky='w', pady=5, padx=5)
        self.branch_var = tk.StringVar()
        branch_combo = ttk.Combobox(personal_frame, textvariable=self.branch_var, width=30, state='readonly')
        branch_combo.grid(row=6, column=1, pady=5, padx=5)
        
        branches = self.db.get_all_branches()
        if branches:
            branch_combo['values'] = [f"{b['BranchID']} - {b['BranchName']}" for b in branches]
        
        login_frame = tk.LabelFrame(form_frame, text="Login Credentials", bg='white')
        login_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(login_frame, text="Username:*", bg='white').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.agent_username = tk.Entry(login_frame, width=30)
        self.agent_username.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(login_frame, text="Password:*", bg='white').grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.agent_password = tk.Entry(login_frame, width=30, show='*')
        self.agent_password.grid(row=1, column=1, pady=5, padx=5)
        
        create_btn = tk.Button(form_frame, text="Create Agent", command=self.create_agent,
                              bg='#27ae60', fg='white', font=('Arial', 12))
        create_btn.pack(pady=20)
    
    def setup_customer_tab(self):
        form_frame = tk.Frame(self.customer_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        personal_frame = tk.LabelFrame(form_frame, text="Personal Details", bg='white')
        personal_frame.pack(fill='x', padx=10, pady=5)
        
        fields = [
            ('First Name:*', 'first_name', 'text'),
            ('Last Name:*', 'last_name', 'text'),
            ('Phone:*', 'phone', 'text'),
            ('Email:', 'email', 'text'),
            ('Address:', 'address', 'text'),
            ('City:', 'city', 'text'),
            ('Pincode:', 'pincode', 'text'),
            ('Date of Birth (YYYY-MM-DD):', 'dob', 'text'),
            ('Aadhar Number:', 'aadhar', 'text'),
            ('PAN Number:', 'pan', 'text')
        ]
        
        self.customer_entries = {}
        for i, (label, key, field_type) in enumerate(fields):
            tk.Label(personal_frame, text=label, bg='white').grid(row=i, column=0, sticky='w', pady=2, padx=5)
            entry = tk.Entry(personal_frame, width=30)
            entry.grid(row=i, column=1, pady=2, padx=5)
            self.customer_entries[key] = entry
        
        login_frame = tk.LabelFrame(form_frame, text="Login Credentials", bg='white')
        login_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(login_frame, text="Username:*", bg='white').grid(row=0, column=0, sticky='w', pady=5, padx=5)
        self.customer_username = tk.Entry(login_frame, width=30)
        self.customer_username.grid(row=0, column=1, pady=5, padx=5)
        
        tk.Label(login_frame, text="Password:*", bg='white').grid(row=1, column=0, sticky='w', pady=5, padx=5)
        self.customer_password = tk.Entry(login_frame, width=30, show='*')
        self.customer_password.grid(row=1, column=1, pady=5, padx=5)
        
        create_btn = tk.Button(form_frame, text="Create Customer", command=self.create_customer,
                              bg='#2980b9', fg='white', font=('Arial', 12))
        create_btn.pack(pady=20)
    
    def setup_view_tab(self):
        view_frame = tk.Frame(self.view_frame, bg='white')
        view_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create frame for treeview and scrollbar
        tree_frame = tk.Frame(view_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, pady=10)
        
        self.users_tree = ttk.Treeview(tree_frame, 
                                      columns=('UserID', 'Username', 'Role', 'Name', 'Status'),
                                      show='headings')
        
        for col in self.users_tree['columns']:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        refresh_btn = tk.Button(view_frame, text="Refresh", command=self.load_existing_users)
        refresh_btn.pack(pady=5)
    
    def validate_agent_data(self, data):
        errors = []
        
        if not data['name'].strip():
            errors.append("Name is required")
        
        if not data['role']:
            errors.append("Role is required")
        
        if not self.validate_phone(data['phone']):
            errors.append("Invalid phone number (10 digits starting with 6-9)")
        
        if data['email'] and not self.validate_email(data['email']):
            errors.append("Invalid email format")
        
        try:
            salary = float(data['salary'])
            if salary < 0:
                errors.append("Salary cannot be negative")
            if salary < 15000:
                errors.append("Salary should be at least ₹15,000")
        except ValueError:
            errors.append("Invalid salary amount")
        
        if not self.validate_date(data['hire_date']):
            errors.append("Invalid hire date format (YYYY-MM-DD)")
        
        if not data['username'].strip():
            errors.append("Username is required")
        elif len(data['username']) < 3:
            errors.append("Username must be at least 3 characters")
        
        if len(data['password']) < 6:
            errors.append("Password must be at least 6 characters")
        
        return errors
    
    def validate_customer_data(self, data):
        errors = []
        
        if not data['first_name'].strip():
            errors.append("First name is required")
        elif len(data['first_name']) < 2:
            errors.append("First name must be at least 2 characters")
        
        if not data['last_name'].strip():
            errors.append("Last name is required")
        elif len(data['last_name']) < 2:
            errors.append("Last name must be at least 2 characters")
        
        if not self.validate_phone(data['phone']):
            errors.append("Invalid phone number (10 digits starting with 6-9)")
        
        if data['email'] and not self.validate_email(data['email']):
            errors.append("Invalid email format")
        
        if data['aadhar'] and not self.validate_aadhar(data['aadhar']):
            errors.append("Invalid Aadhar number (12 digits required)")
        
        if data['pan'] and not self.validate_pan(data['pan']):
            errors.append("Invalid PAN number format (e.g., ABCDE1234F)")
        
        if data['dob'] and not self.validate_date(data['dob']):
            errors.append("Invalid date of birth format (YYYY-MM-DD)")
        elif data['dob']:
            # Check if customer is at least 18 years old
            dob = datetime.strptime(data['dob'], '%Y-%m-%d')
            age = (datetime.now() - dob).days // 365
            if age < 18:
                errors.append("Customer must be at least 18 years old")
        
        if not data['username'].strip():
            errors.append("Username is required")
        elif len(data['username']) < 3:
            errors.append("Username must be at least 3 characters")
        
        if len(data['password']) < 6:
            errors.append("Password must be at least 6 characters")
        
        return errors
    
    def validate_phone(self, phone):
        return bool(re.match(r'^[6-9]\d{9}$', phone.strip()))
    
    def validate_email(self, email):
        if not email.strip():
            return True  # Email is optional
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.strip()))
    
    def validate_aadhar(self, aadhar):
        if not aadhar.strip():
            return True  # Aadhar is optional
        return bool(re.match(r'^\d{12}$', aadhar.strip()))
    
    def validate_pan(self, pan):
        if not pan.strip():
            return True  # PAN is optional
        return bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan.strip().upper()))
    
    def validate_date(self, date_string):
        if not date_string.strip():
            return False
        try:
            datetime.strptime(date_string.strip(), '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    def create_agent(self):
        try:
            branch_text = self.branch_var.get()
            if not branch_text:
                messagebox.showerror("Error", "Please select a branch")
                return
            
            branch_id = int(branch_text.split(' - ')[0])
            
            data = {
                'name': self.agent_entries['name'].get(),
                'role': self.agent_entries['role'].get(),
                'phone': self.agent_entries['phone'].get(),
                'email': self.agent_entries['email'].get(),
                'salary': self.agent_entries['salary'].get(),
                'hire_date': self.agent_entries['hire_date'].get(),
                'username': self.agent_username.get(),
                'password': self.agent_password.get()
            }
            
            validation_errors = self.validate_agent_data(data)
            if validation_errors:
                messagebox.showerror("Validation Error", "\n".join(validation_errors))
                return
            
            # Confirm creation
            confirm_msg = f"Create agent with following details?\n\nName: {data['name']}\nRole: {data['role']}\nPhone: {data['phone']}\nBranch: {branch_text}"
            if not messagebox.askyesno("Confirm", confirm_msg):
                return
            
            success = self.db.create_agent(
                branch_id, data['name'], data['role'], data['phone'], 
                data['email'], float(data['salary']), data['hire_date'],
                data['username'], data['password']
            )
            
            if success:
                messagebox.showinfo("Success", "Agent created successfully!")
                self.clear_agent_form()
                self.load_existing_users()
            else:
                messagebox.showerror("Error", "Failed to create agent - username may already exist")
                
        except ValueError as e:
            messagebox.showerror("Error", "Please check all fields have valid values")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating agent: {str(e)}")
    
    def create_customer(self):
        try:
            data = {
                'first_name': self.customer_entries['first_name'].get(),
                'last_name': self.customer_entries['last_name'].get(),
                'phone': self.customer_entries['phone'].get(),
                'email': self.customer_entries['email'].get(),
                'address': self.customer_entries['address'].get(),
                'city': self.customer_entries['city'].get(),
                'pincode': self.customer_entries['pincode'].get(),
                'dob': self.customer_entries['dob'].get(),
                'aadhar': self.customer_entries['aadhar'].get(),
                'pan': self.customer_entries['pan'].get(),
                'username': self.customer_username.get(),
                'password': self.customer_password.get()
            }
            
            validation_errors = self.validate_customer_data(data)
            if validation_errors:
                messagebox.showerror("Validation Error", "\n".join(validation_errors))
                return
            
            # Confirm creation
            confirm_msg = f"Create customer with following details?\n\nName: {data['first_name']} {data['last_name']}\nPhone: {data['phone']}\nEmail: {data['email'] or 'Not provided'}"
            if not messagebox.askyesno("Confirm", confirm_msg):
                return
            
            success = self.db.create_customer(
                data['first_name'], data['last_name'], data['phone'], 
                data['email'], data['address'], data['city'], data['pincode'],
                data['dob'] or None, data['aadhar'] or None, data['pan'] or None,
                data['username'], data['password']
            )
            
            if success:
                messagebox.showinfo("Success", "Customer created successfully!")
                self.clear_customer_form()
                self.load_existing_users()
            else:
                messagebox.showerror("Error", "Failed to create customer - username may already exist")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error creating customer: {str(e)}")
    
    def clear_agent_form(self):
        for entry in self.agent_entries.values():
            if isinstance(entry, tk.Entry):
                entry.delete(0, tk.END)
            elif isinstance(entry, ttk.Combobox):
                entry.set('')
        self.agent_username.delete(0, tk.END)
        self.agent_password.delete(0, tk.END)
        self.branch_var.set('')
    
    def clear_customer_form(self):
        for entry in self.customer_entries.values():
            entry.delete(0, tk.END)
        self.customer_username.delete(0, tk.END)
        self.customer_password.delete(0, tk.END)
    
    def load_existing_users(self):
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        users = self.db.get_all_users()
        if users:
            for user in users:
                status = "Active" if user['IsActive'] else "Inactive"
                name = user['Name'] if user['Name'] else "N/A"
                self.users_tree.insert('', 'end', values=(
                    user['UserID'], user['Username'], user['Role'], name, status
                ))
        else:
            # Insert a message if no users found
            self.users_tree.insert('', 'end', values=("No users found", "", "", "", ""))