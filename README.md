# DBMS-MINI-PROJECT

# 🚗 Vehicle Loan Management System  
A Full-Stack Loan Processing, EMI Management & Analytics Desktop Application

This project is a complete **Vehicle Loan Management System** built using **Python (Tkinter GUI)** and **MySQL**, featuring role-based dashboards, automated installment generation, EMI payments, overdue detection, PDF export (FPDF), notifications, analytics and much more.

---

## 📌 Table of Contents
- Project Overview
- Features
- Tech Stack
- Screens
- Database Structure
- Stored Procedures / Functions / Triggers / Views
- Installation
- How to Run
- Project Structure
- Enhancements Added
- Demo Flow (Presentation Guide)

---

# 📘 Project Overview
The **Vehicle Loan Management System** is a robust desktop-based system designed for:
- Customer loan creation  
- EMI calculation & complete installment management  
- Automated overdue detection  
- EMI payment processing  
- Agent & admin dashboards  
- Vehicle seizure workflow  
- Customer dashboard view  
- Reporting using PDF  
- Analytics using Matplotlib  

It includes **Admin**, **Agent**, and **Customer** role-based dashboards.

---

# 🚀 Features

## 🔐 Authentication
- Secure login  
- Role-based dashboards:  
  - **Admin**  
  - **Agent**  
  - **Customer**  

---

## 🧑‍💼 ADMIN FEATURES
✔ Create Agents and Customers  
✔ View all users  
✔ Run demo SQL queries (nested, join, aggregate, view, trigger, function)  
✔ Run Overdue Scan (apply late fees)  
✔ View analytics (pie charts + bar charts)  
✔ Export loan PDF  
✔ View branch-wise loan information  
✔ Access Customer Loan Summary (View + Function)  

---

## 🧑‍💼 AGENT FEATURES
✔ Customer search  
✔ Vehicle entry  
✔ Loan creation (with business validations)  
✔ Automatic installment generation (Stored Procedure)  
✔ EMI calculator with full amortization  
✔ Collect EMI payments (Stored Procedure)  
✔ Loan foreclosure (close loan early)  
✔ Vehicle seizure workflow  
✔ Manage loans  
✔ View overdue customers  
✔ Notifications  
✔ PDF export of loan details  
✔ Graphs & performance metrics  

---

## 👤 CUSTOMER FEATURES
✔ View active loans  
✔ View EMI schedule  
✔ View payment transaction history  
✔ Export loan PDF  
✔ Vehicle insurance alerts  
✔ Seizure status history  
✔ Edit profile  
✔ Notifications  

---

# 📊 Analytics
- Loan Status Pie Chart  
- Monthly EMI Collection Bar Chart  
- Branch-wise performance  
- Agent statistics  
- Customer credit scoring  

---

# 🧾 Reporting
- PDF Loan Summary Export (Using FPDF2)  
- Includes Customer, Vehicle, Loan & Installments  

---

# 🧰 Tech Stack
| Component | Technology |
|----------|------------|
| Frontend | Python Tkinter |
| Backend | Python |
| Database | MySQL |
| Reporting | FPDF2 |
| Graphs | Matplotlib |
| OS | Windows/Linux |

---

# 🗄 Database Structure

### Main Tables
| Table | Description |
|-------|-------------|
| **Users** | Login for admin, agents, customers |
| **Customer** | Customer personal details |
| **Agent** | Agents and their branch details |
| **Branch** | Branch list |
| **Vehicle** | Customer vehicles |
| **Loan** | Loan details & balance |
| **Installment** | EMI schedule |
| **TransactionLogger** | EMI transactions |
| **Seizure** | Vehicle seizure logs |

---

# ⚙️ Stored Procedures / Functions / Triggers / Views

## 🔷 Stored Procedure: `CreateLoanInstallments`
Auto-generates EMI installments when a loan is created.  
Logic:
- Calculates monthly EMI  
- Creates installment rows  
- Sets DueDate, TotalAmount, Status  

---

## 🔷 Stored Procedure: `ProcessEMIPayment`
Handles EMI payment workflow:  
- Marks installment “Paid”  
- Updates loan balance  
- Logs transaction  
- Closes loan if balance = 0  

---

## 🟩 SQL Function: `CalculateCreditScore(CustomerID)`
Calculates credit score based on:  
- Payment history  
- Defaults  
- Number of loans  
- Customer behavior  

Used in **CustomerLoanSummary** view.

---

## 🟧 Trigger 1: `BeforeUpdateInstallment`
Automatically marks overdue installments.  
If:  
New.DueDate < CURDATE() AND Status = 'Pending'

makefile
Copy code
Then:  
Status = 'Overdue' AND LateFee updated

yaml
Copy code

---

## 🟧 Trigger 2: `AfterUpdateLoanStatus`
Logs all loan status changes into `TransactionLogger`.

---

## 🟪 Views
### ✔ `CustomerLoanSummary`
Shows:  
- Customer details  
- Total loans  
- Active loans  
- Total borrowed amount  
- Credit score  

### ✔ `OverdueInstallmentsView`
Displays all overdue installments.

### ✔ `AgentPerformance`
Shows EMI collections, active loans, pending customers.

---

# 🛠 Installation

## Install Python Libraries
pip install mysql-connector-python
pip install matplotlib
pip install fpdf2

markdown
Copy code

## Setup MySQL Database
1. Create database:
CREATE DATABASE VehicleLoanDB;

markdown
Copy code
2. Import the SQL file:
database.sql

yaml
Copy code
3. Configure your MySQL details in `database.py`.

---

# ▶️ How to Run
From your project folder:

python main.py

yaml
Copy code

---

# 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Agent | ramesh_k | admin123 |
| Customer | aarav_sharma | admin123 |

---

# 📁 Project Structure
├── admin_dashboard.py
├── agent_dashboard.py
├── customer_dashboard.py
├── auth.py
├── main.py
├── enhancements.py
├── utils.py
├── database.py
├── fix_test_users.py
├── demo_queries.py
├── database.sql
└── README.md

yaml
Copy code

---

# ✨ Enhancements Added
| Enhancement | Description |
|-------------|-------------|
| EMI Calculator | Full amortization schedule |
| PDF Export | Loan summary PDF using FPDF |
| Graph Analytics | Pie & bar charts |
| Notifications | Alerts for overdue, expiry |
| Foreclosure | Close loan early |
| Vehicle History | Insurance, seizure logs |
| Overdue Scan | Auto late fee calculation |
| Profile Editor | Update phone/email/address |
| Loan Search | Customer, vehicle, ID search |

---

# 🎤 Demo Flow (Presentation Guide)

## ⭐ Admin Demo
1. Login → Dashboard  
2. Create Agent/Customer  
3. View users  
4. Run advanced SQL demo queries  
5. View loan analytics charts  
6. Run overdue scan  
7. Open CustomerLoanSummary view  
8. Export loan PDF  

---

## ⭐ Agent Demo
1. Search customer  
2. Enter vehicle details  
3. Create loan (auto EMI generation)  
4. Use EMI calculator  
5. Collect EMI (stored procedure)  
6. Foreclose a loan  
7. Seize vehicle  
8. Generate loan PDF  
9. View analytics  

---

## ⭐ Customer Demo
1. View active loans  
2. View EMI schedule  
3. View payment history  
4. View vehicle insurance alerts  
5. Download PDF  
6. Edit profile  

---

# 🏁 Conclusion
This system is a **complete enterprise-level vehicle loan automation solution**, demonstrating:

- Advanced SQL: Procedures, triggers, views, functions  
- Full Tkinter GUI  
- Database-driven architecture  
- Real-world workflow automation  
- Analytics & visualization  
- Professional PDF reports  



---
