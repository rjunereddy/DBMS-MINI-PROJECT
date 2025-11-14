import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from admin_dashboard import AdminDashboard
from agent_dashboard import AgentDashboard
from customer_dashboard import CustomerDashboard
import logging

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Vehicle Loan System - Login")
        self.root.geometry("400x400")
        self.root.configure(bg='#2c3e50')
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        
        try:
            self.db = Database()
            self.setup_ui()
        except Exception as e:
            messagebox.showerror("Database Error", f"Cannot connect to database: {str(e)}")
            self.root.destroy()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#2c3e50', padx=20, pady=20)
        main_frame.pack(expand=True, fill='both')
        
        title_label = tk.Label(main_frame, text="Vehicle Loan System", 
                              font=('Arial', 20, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(pady=20)
        
        form_frame = tk.Frame(main_frame, bg='#34495e', padx=20, pady=20, relief='raised', bd=2)
        form_frame.pack(pady=10, fill='x')
        
        tk.Label(form_frame, text="Username:", fg='white', bg='#34495e').grid(row=0, column=0, sticky='w', pady=5)
        self.username_entry = tk.Entry(form_frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=10)
        self.username_entry.focus()
        
        tk.Label(form_frame, text="Password:", fg='white', bg='#34495e').grid(row=1, column=0, sticky='w', pady=5)
        self.password_entry = tk.Entry(form_frame, width=25, show='*')
        self.password_entry.grid(row=1, column=1, pady=5, padx=10)
        
        tk.Label(form_frame, text="Role:", fg='white', bg='#34495e').grid(row=2, column=0, sticky='w', pady=5)
        self.role_var = tk.StringVar()
        role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, width=23, state='readonly')
        role_combo['values'] = ('admin', 'agent', 'customer')
        role_combo.grid(row=2, column=1, pady=5, padx=10)
        
        login_btn = tk.Button(form_frame, text="Login", command=self.login, 
                             bg='#3498db', fg='white', font=('Arial', 12), width=15)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)
        
        info_frame = tk.Frame(form_frame, bg='#34495e')
        info_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        tk.Label(info_frame, text="Test Credentials:", fg='yellow', bg='#34495e', font=('Arial', 9, 'bold')).pack()
        tk.Label(info_frame, text="Admin: admin/admin123", fg='white', bg='#34495e', font=('Arial', 8)).pack()
        tk.Label(info_frame, text="Agent: ramesh_k/admin123", fg='white', bg='#34495e', font=('Arial', 8)).pack()
        tk.Label(info_frame, text="Customer: aarav_sharma/admin123", fg='white', bg='#34495e', font=('Arial', 8)).pack()
        
        self.root.bind('<Return>', lambda event: self.login())
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        role = self.role_var.get()
        
        if not username or not password or not role:
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        try:
            user = self.db.authenticate_user(username, password, role)
            
            if user:
                logging.info(f"User {username} logged in as {role}")
                self.root.withdraw()
                self.open_dashboard(user, role)
            else:
                messagebox.showerror("Error", "Invalid credentials or role")
                
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {str(e)}")
    
    def open_dashboard(self, user, role):
        try:
            if role == 'admin':
                AdminDashboard(self.root, user, self.db)
            elif role == 'agent':
                AgentDashboard(self.root, user, self.db)
            elif role == 'customer':
                CustomerDashboard(self.root, user, self.db)
            else:
                messagebox.showerror("Error", "Invalid user role")
                self.root.deiconify()
        except Exception as e:
            import traceback
            error_msg = traceback.format_exc()
            logging.error(f"Dashboard error: {error_msg}")
            messagebox.showerror("Dashboard Error", f"Cannot open dashboard:\n\n{str(e)}\n\nCheck terminal for details")
            self.root.deiconify()  # Show login window again

    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            if hasattr(self, 'db'):
                self.db.close()