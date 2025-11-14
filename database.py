import mysql.connector
from mysql.connector import Error, pooling
import hashlib
import os
import logging
from datetime import datetime

class Database:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '1234')
        self.database = os.getenv('DB_NAME', 'VehicleLoanDB')
        self.connection_pool = None
        self.init_pool()
    
    def init_pool(self):
        try:
            self.connection_pool = pooling.MySQLConnectionPool(
                pool_name="loan_pool",
                pool_size=5,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False
            )
            logging.info("Database connection pool created successfully")
        except Error as e:
            logging.error(f"Error creating connection pool: {e}")
            raise
    
    def get_connection(self):
        try:
            if self.connection_pool:
                return self.connection_pool.get_connection()
            else:
                return mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=False
                )
        except Error as e:
            logging.error(f"Error getting connection: {e}")
            raise
    
    def hash_password(self, password):
        """Secure password hashing with salt"""
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + key.hex()
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        try:
            salt = bytes.fromhex(hashed[:64])
            key = bytes.fromhex(hashed[64:])
            new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
            return new_key == key
        except:
            return False
    
    def authenticate_user(self, username, password, role):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT u.*, 
                       c.CustomerID, c.FirstName, c.LastName,
                       a.AgentID, a.Name as AgentName, a.BranchID
                FROM Users u
                LEFT JOIN Customer c ON u.CustomerID = c.CustomerID
                LEFT JOIN Agent a ON u.AgentID = a.AgentID
                WHERE u.Username = %s AND u.Role = %s AND u.IsActive = 1
            """
            
            cursor.execute(query, (username, role))
            user = cursor.fetchone()
            
            if user and self.verify_password(password, user['Password']):
                cursor.close()
                conn.close()
                return user
            else:
                cursor.close()
                conn.close()
                return None
            
        except Error as e:
            logging.error(f"Authentication error: {e}")
            if 'conn' in locals():
                conn.close()
            return None
    
    def execute_query(self, query, params=None, fetch=True):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch and query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid if not fetch else None
            
            cursor.close()
            return result
        except Error as e:
            logging.error(f"Query error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    def call_procedure(self, procedure_name, params=None):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.callproc(procedure_name, params or ())
            
            results = []
            for result in cursor.stored_results():
                results.extend(result.fetchall())
            
            conn.commit()
            cursor.close()
            return results
        except Error as e:
            logging.error(f"Procedure error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    def get_all_branches(self):
        return self.execute_query("SELECT BranchID, BranchName FROM Branch WHERE BranchID IS NOT NULL")
    
    def create_agent(self, branch_id, name, role, phone, email, salary, hire_date, username, password):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if username already exists
            check_query = "SELECT UserID FROM Users WHERE Username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                raise ValueError("Username already exists")
            
            agent_query = """
                INSERT INTO Agent (BranchID, Name, Role, Phone, Email, Salary, HireDate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(agent_query, (branch_id, name, role, phone, email, salary, hire_date))
            agent_id = cursor.lastrowid
            
            user_query = """
                INSERT INTO Users (AgentID, Username, Password, Role, IsActive)
                VALUES (%s, %s, %s, 'agent', 1)
            """
            hashed_password = self.hash_password(password)
            cursor.execute(user_query, (agent_id, username, hashed_password))
            
            conn.commit()
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Create agent error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def create_customer(self, first_name, last_name, phone, email, address, city, pincode, dob, aadhar, pan, username, password):
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if username already exists
            check_query = "SELECT UserID FROM Users WHERE Username = %s"
            cursor.execute(check_query, (username,))
            if cursor.fetchone():
                raise ValueError("Username already exists")
            
            customer_query = """
                INSERT INTO Customer (FirstName, LastName, Phone, Email, Address, City, Pincode, DateOfBirth, AadharNumber, PANNumber)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(customer_query, (first_name, last_name, phone, email, address, city, pincode, dob, aadhar, pan))
            customer_id = cursor.lastrowid
            
            user_query = """
                INSERT INTO Users (CustomerID, Username, Password, Role, IsActive)
                VALUES (%s, %s, %s, 'customer', 1)
            """
            hashed_password = self.hash_password(password)
            cursor.execute(user_query, (customer_id, username, hashed_password))
            
            conn.commit()
            return True
            
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Create customer error: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_all_users(self):
        query = """
            SELECT u.UserID, u.Username, u.Role, u.IsActive,
                   COALESCE(c.FirstName, a.Name) as Name,
                   COALESCE(c.CustomerID, a.AgentID) as EntityID
            FROM Users u
            LEFT JOIN Customer c ON u.CustomerID = c.CustomerID
            LEFT JOIN Agent a ON u.AgentID = a.AgentID
            WHERE u.UserID IS NOT NULL
            ORDER BY u.UserID
        """
        return self.execute_query(query)
    
    def execute_complex_query(self, query_type):
        queries = {
            'nested_query': """
                SELECT CustomerID, CONCAT(FirstName, ' ', LastName) as CustomerName,
                       (SELECT COUNT(*) FROM Loan l WHERE l.CustomerID = c.CustomerID) as LoanCount,
                       (SELECT SUM(LoanAmount) FROM Loan l WHERE l.CustomerID = c.CustomerID) as TotalBorrowed
                FROM Customer c
                WHERE (SELECT SUM(LoanAmount) FROM Loan l WHERE l.CustomerID = c.CustomerID) > 
                      (SELECT AVG(LoanAmount) FROM Loan)
                ORDER BY TotalBorrowed DESC
            """,
            'aggregate_join': """
                SELECT b.BranchName, 
                       COUNT(l.LoanID) as TotalLoans,
                       SUM(l.LoanAmount) as TotalAmount,
                       AVG(l.InterestRate) as AvgInterestRate,
                       MAX(l.LoanAmount) as MaxLoan,
                       MIN(l.InterestRate) as MinInterestRate,
                       SUM(CASE WHEN l.Status = 'Active' THEN 1 ELSE 0 END) as ActiveLoans
                FROM Branch b
                LEFT JOIN Loan l ON b.BranchID = l.BranchID
                GROUP BY b.BranchID, b.BranchName
                HAVING TotalLoans > 0
                ORDER BY TotalAmount DESC
            """,
            'complex_join': """
                SELECT l.LoanID, 
                       CONCAT(c.FirstName, ' ', c.LastName) as CustomerName,
                       v.VehicleNo, v.Make, v.Model,
                       a.Name as AgentName,
                       b.BranchName,
                       COUNT(i.InstallmentID) as TotalInstallments,
                       SUM(CASE WHEN i.Status = 'Paid' THEN 1 ELSE 0 END) as PaidInstallments,
                       l.BalanceAmount,
                       (l.TotalPayable - l.BalanceAmount) as AmountPaid
                FROM Loan l
                JOIN Customer c ON l.CustomerID = c.CustomerID
                JOIN Vehicle v ON l.VehicleID = v.VehicleID
                JOIN Agent a ON l.AgentID = a.AgentID
                JOIN Branch b ON l.BranchID = b.BranchID
                LEFT JOIN Installment i ON l.LoanID = i.LoanID
                GROUP BY l.LoanID, CustomerName, v.VehicleNo, v.Make, v.Model, 
                         a.Name, b.BranchName, l.BalanceAmount, l.TotalPayable
                ORDER BY l.LoanID
            """,
            'view_demo': """
                SELECT * FROM CustomerLoanSummary 
                WHERE TotalLoans > 0 
                ORDER BY CreditScore DESC
                LIMIT 10
            """,
            'trigger_demo': """
                SELECT i.InstallmentID, l.LoanID, c.FirstName, c.LastName,
                       i.DueDate, i.TotalAmount, i.LateFee, i.Status,
                       DATEDIFF(CURDATE(), i.DueDate) as DaysOverdue
                FROM Installment i
                JOIN Loan l ON i.LoanID = l.LoanID
                JOIN Customer c ON l.CustomerID = c.CustomerID
                WHERE i.Status = 'Overdue'
                ORDER BY DaysOverdue DESC
            """,
            'function_demo': """
                SELECT CustomerID, CONCAT(FirstName, ' ', LastName) as CustomerName,
                       CalculateCreditScore(CustomerID) as CreditScore,
                       CASE 
                           WHEN CalculateCreditScore(CustomerID) >= 750 THEN 'Excellent'
                           WHEN CalculateCreditScore(CustomerID) >= 650 THEN 'Good'
                           WHEN CalculateCreditScore(CustomerID) >= 550 THEN 'Fair'
                           ELSE 'Poor'
                       END as CreditRating
                FROM Customer
                WHERE CustomerID IN (SELECT DISTINCT CustomerID FROM Loan)
                ORDER BY CreditScore DESC
            """,
            'procedure_demo': """
                SELECT LoanID, CustomerID, LoanAmount, InterestRate, TenureMonths, SanctionDate
                FROM Loan 
                WHERE Status = 'Active'
                LIMIT 5
            """
        }
        
        if query_type in queries:
            return self.execute_query(queries[query_type])
        return None
    
    def close(self):
        """Close all connections in pool"""
        if self.connection_pool:
            self.connection_pool._remove_connections()