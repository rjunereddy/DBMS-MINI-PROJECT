-- =============================================
-- Vehicle Loan Management System Database
-- PES1UG23CS374 & PES1UG23CS927
-- =============================================

-- Create Database
CREATE DATABASE IF NOT EXISTS VehicleLoanDB;
USE VehicleLoanDB;

-- =============================================
-- Table Definitions with Constraints
-- =============================================

-- Branch Table
CREATE TABLE Branch (
    BranchID INT PRIMARY KEY AUTO_INCREMENT,
    BranchName VARCHAR(100) NOT NULL UNIQUE,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(50) NOT NULL,
    Phone VARCHAR(15) NOT NULL UNIQUE,
    ManagerName VARCHAR(100) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Customer Table
CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Phone VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100) UNIQUE,
    Address VARCHAR(255) NOT NULL,
    City VARCHAR(50) NOT NULL,
    Pincode VARCHAR(10) NOT NULL,
    CustomerStatus ENUM('Active', 'Inactive', 'Suspended') DEFAULT 'Active',
    DateOfBirth DATE,
    AadharNumber VARCHAR(12) UNIQUE,
    PANNumber VARCHAR(10) UNIQUE,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (CHAR_LENGTH(Phone) >= 10)
);

-- Agent Table
CREATE TABLE Agent (
    AgentID INT PRIMARY KEY AUTO_INCREMENT,
    BranchID INT NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Role ENUM('Loan Officer', 'Manager', 'Field Agent', 'Supervisor') NOT NULL,
    Phone VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Salary DECIMAL(10,2) DEFAULT 0,
    HireDate DATE NOT NULL,
    AgentStatus ENUM('Active', 'Inactive', 'On Leave') DEFAULT 'Active',
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE RESTRICT,
    CHECK (Salary >= 0)
);

-- Vehicle Table (Corrected - using backticks for reserved keywords)
CREATE TABLE Vehicle (
    VehicleID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    VehicleNo VARCHAR(20) NOT NULL UNIQUE,
    Make VARCHAR(50) NOT NULL,
    Model VARCHAR(50) NOT NULL,
    `Year` INT NOT NULL,
    `Condition` ENUM('Excellent', 'Good', 'Fair', 'Poor') DEFAULT 'Good',
    InsuranceExpiry DATE NOT NULL,
    ROStatus ENUM('Active', 'Expired', 'Under Process') DEFAULT 'Active',
    ChassisNumber VARCHAR(50) UNIQUE,
    MarketValue DECIMAL(10,2) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    CHECK (`Year` BETWEEN 1900 AND 2100),
    CHECK (MarketValue > 0)
);

-- Loan Table
CREATE TABLE Loan (
    LoanID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NOT NULL,
    VehicleID INT NOT NULL,
    LoanAmount DECIMAL(12,2) NOT NULL,
    SanctionDate DATE NOT NULL,
    TenureMonths INT NOT NULL,
    InterestRate DECIMAL(5,2) NOT NULL,
    EMAmount DECIMAL(10,2) NOT NULL,
    TotalPayable DECIMAL(12,2) NOT NULL,
    BalanceAmount DECIMAL(12,2) NOT NULL,
    Status ENUM('Active', 'Closed', 'Defaulted', 'Written Off', 'Under Process') DEFAULT 'Under Process',
    BranchID INT NOT NULL,
    AgentID INT NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID) ON DELETE CASCADE,
    FOREIGN KEY (BranchID) REFERENCES Branch(BranchID) ON DELETE RESTRICT,
    FOREIGN KEY (AgentID) REFERENCES Agent(AgentID) ON DELETE RESTRICT,
    CHECK (LoanAmount > 0),
    CHECK (TenureMonths BETWEEN 6 AND 84), -- 6 months to 7 years
    CHECK (InterestRate BETWEEN 5 AND 25),
    CHECK (EMAmount > 0),
    CHECK (TotalPayable >= LoanAmount),
    CHECK (BalanceAmount >= 0)
);

-- Installment Table
CREATE TABLE Installment (
    InstallmentID INT PRIMARY KEY AUTO_INCREMENT,
    LoanID INT NOT NULL,
    DueDate DATE NOT NULL,
    PaidDate DATE NULL,
    PrincipalAmount DECIMAL(10,2) NOT NULL,
    InterestAmount DECIMAL(10,2) NOT NULL,
    TotalAmount DECIMAL(10,2) NOT NULL,
    PaymentMode ENUM('Cash', 'Cheque', 'Online Transfer', 'UPI', 'DD') DEFAULT 'Online Transfer',
    Status ENUM('Pending', 'Paid', 'Overdue', 'Partial') DEFAULT 'Pending',
    LateFee DECIMAL(8,2) DEFAULT 0,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (LoanID) REFERENCES Loan(LoanID) ON DELETE CASCADE,
    CHECK (PrincipalAmount > 0),
    CHECK (InterestAmount >= 0),
    CHECK (TotalAmount = PrincipalAmount + InterestAmount),
    CHECK (LateFee >= 0)
);

-- TransactionLogger Table
CREATE TABLE TransactionLogger (
    TransactionID INT PRIMARY KEY AUTO_INCREMENT,
    LoanID INT NOT NULL,
    TransactionDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    DebitAmount DECIMAL(10,2) DEFAULT 0,
    CreditAmount DECIMAL(10,2) DEFAULT 0,
    BalanceAfterTransaction DECIMAL(12,2) NOT NULL,
    Remarks VARCHAR(255),
    TransactionType ENUM('EMI Payment', 'Late Fee', 'Prepayment', 'Loan Disbursement') NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (LoanID) REFERENCES Loan(LoanID) ON DELETE CASCADE,
    CHECK (DebitAmount >= 0),
    CHECK (CreditAmount >= 0),
    CHECK (BalanceAfterTransaction >= 0)
);

-- Seizure Table
CREATE TABLE Seizure (
    SeizureID INT PRIMARY KEY AUTO_INCREMENT,
    LoanID INT NOT NULL,
    AgentID INT NOT NULL,
    SeizureDate DATE NOT NULL,
    Reason VARCHAR(255) NOT NULL,
    VehicleConditionAtSeizure ENUM('Excellent', 'Good', 'Fair', 'Poor', 'Damaged') NOT NULL,
    SeizureStatus ENUM('Initiated', 'Completed', 'Cancelled') DEFAULT 'Initiated',
    RecoveryAmount DECIMAL(10,2) DEFAULT 0,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (LoanID) REFERENCES Loan(LoanID) ON DELETE CASCADE,
    FOREIGN KEY (AgentID) REFERENCES Agent(AgentID) ON DELETE RESTRICT,
    CHECK (RecoveryAmount >= 0)
);

-- Users Table for Authentication
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    CustomerID INT NULL,
    AgentID INT NULL,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Role ENUM('admin', 'agent', 'customer') NOT NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    LastLogin TIMESTAMP NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON DELETE CASCADE,
    FOREIGN KEY (AgentID) REFERENCES Agent(AgentID) ON DELETE CASCADE
);

-- =============================================
-- Insert Sample Data (15+ records per table)
-- =============================================

-- Insert Branches
INSERT INTO Branch (BranchName, Address, City, Phone, ManagerName) VALUES
('Main Branch', '123 MG Road', 'Bangalore', '080-1234567', 'Rajesh Kumar'),
('Electronic City Branch', '456 IT Park', 'Bangalore', '080-1234568', 'Priya Sharma'),
('Whitefield Branch', '789 Whitefield Road', 'Bangalore', '080-1234569', 'Arun Patel'),
('HSR Layout Branch', '321 HSR Layout', 'Bangalore', '080-1234570', 'Sneha Reddy'),
('Koramangala Branch', '654 Koramangala', 'Bangalore', '080-1234571', 'Vikram Singh'),
('Jayanagar Branch', '987 Jayanagar', 'Bangalore', '080-1234572', 'Anita Desai'),
('Indiranagar Branch', '147 Indiranagar', 'Bangalore', '080-1234573', 'Rahul Mehta'),
('BTM Layout Branch', '258 BTM Layout', 'Bangalore', '080-1234574', 'Pooja Verma'),
('Malleshwaram Branch', '369 Malleshwaram', 'Bangalore', '080-1234575', 'Sanjay Joshi'),
('Rajajinagar Branch', '741 Rajajinagar', 'Bangalore', '080-1234576', 'Neha Gupta'),
('Basavanagudi Branch', '852 Basavanagudi', 'Bangalore', '080-1234577', 'Kiran Rao'),
('Yeshwanthpur Branch', '963 Yeshwanthpur', 'Bangalore', '080-1234578', 'Manoj Bhat'),
('Hebbal Branch', '159 Hebbal', 'Bangalore', '080-1234579', 'Swati Choudhary'),
('Banashankari Branch', '357 Banashankari', 'Bangalore', '080-1234580', 'Alok Mishra'),
('Marathahalli Branch', '486 Marathahalli', 'Bangalore', '080-1234581', 'Deepa Nair');

-- Insert Customers
INSERT INTO Customer (FirstName, LastName, Phone, Email, Address, City, Pincode, DateOfBirth, AadharNumber, PANNumber) VALUES
('Aarav', 'Sharma', '9876543210', 'aarav.sharma@email.com', '101 MG Road', 'Bangalore', '560001', '1985-03-15', '123456789012', 'ABCDE1234F'),
('Priya', 'Patel', '9876543211', 'priya.patel@email.com', '202 Koramangala', 'Bangalore', '560034', '1990-07-22', '123456789013', 'BCDEF1234G'),
('Rahul', 'Kumar', '9876543212', 'rahul.kumar@email.com', '303 Indiranagar', 'Bangalore', '560038', '1988-11-30', '123456789014', 'CDEFG1234H'),
('Anjali', 'Singh', '9876543213', 'anjali.singh@email.com', '404 HSR Layout', 'Bangalore', '560102', '1992-05-18', '123456789015', 'DEFGH1234I'),
('Vikram', 'Reddy', '9876543214', 'vikram.reddy@email.com', '505 Whitefield', 'Bangalore', '560066', '1987-09-12', '123456789016', 'EFGHI1234J'),
('Sneha', 'Joshi', '9876543215', 'sneha.joshi@email.com', '606 Jayanagar', 'Bangalore', '560041', '1991-12-25', '123456789017', 'FGHIJ1234K'),
('Raj', 'Verma', '9876543216', 'raj.verma@email.com', '707 BTM Layout', 'Bangalore', '560076', '1986-08-08', '123456789018', 'GHIJK1234L'),
('Pooja', 'Mehta', '9876543217', 'pooja.mehta@email.com', '808 Malleshwaram', 'Bangalore', '560055', '1993-02-14', '123456789019', 'HIJKL1234M'),
('Sanjay', 'Gupta', '9876543218', 'sanjay.gupta@email.com', '909 Rajajinagar', 'Bangalore', '560010', '1984-06-30', '123456789020', 'IJKLM1234N'),
('Neha', 'Shah', '9876543219', 'neha.shah@email.com', '111 Basavanagudi', 'Bangalore', '560004', '1989-04-05', '123456789021', 'JKLMN1234O'),
('Alok', 'Das', '9876543220', 'alok.das@email.com', '222 Yeshwanthpur', 'Bangalore', '560022', '1994-10-20', '123456789022', 'KLMNO1234P'),
('Manoj', 'Bose', '9876543221', 'manoj.bose@email.com', '333 Hebbal', 'Bangalore', '560024', '1983-01-15', '123456789023', 'LMNOP1234Q'),
('Kiran', 'Nair', '9876543222', 'kiran.nair@email.com', '444 Banashankari', 'Bangalore', '560050', '1990-07-07', '123456789024', 'MNOPQ1234R'),
('Divya', 'Rao', '9876543223', 'divya.rao@email.com', '555 Marathahalli', 'Bangalore', '560037', '1988-03-28', '123456789025', 'NOPQR1234S'),
('Arun', 'Mishra', '9876543224', 'arun.mishra@email.com', '666 Electronic City', 'Bangalore', '560100', '1985-11-11', '123456789026', 'OPQRS1234T');

-- Insert Agents
INSERT INTO Agent (BranchID, Name, Role, Phone, Email, Salary, HireDate) VALUES
(1, 'Ramesh Kumar', 'Loan Officer', '9880012345', 'ramesh.kumar@loanco.com', 50000, '2020-01-15'),
(1, 'Sita Menon', 'Manager', '9880012346', 'sita.menon@loanco.com', 75000, '2019-03-20'),
(2, 'Anil Kapoor', 'Loan Officer', '9880012347', 'anil.kapoor@loanco.com', 48000, '2021-06-10'),
(2, 'Meera Desai', 'Field Agent', '9880012348', 'meera.desai@loanco.com', 42000, '2022-02-14'),
(3, 'Karthik Raj', 'Supervisor', '9880012349', 'karthik.raj@loanco.com', 60000, '2020-11-05'),
(3, 'Lakshmi Iyer', 'Loan Officer', '9880012350', 'lakshmi.iyer@loanco.com', 52000, '2021-08-22'),
(4, 'Vijay Malhotra', 'Field Agent', '9880012351', 'vijay.malhotra@loanco.com', 45000, '2022-04-18'),
(4, 'Sunita Reddy', 'Manager', '9880012352', 'sunita.reddy@loanco.com', 78000, '2018-12-01'),
(5, 'Prakash Jain', 'Loan Officer', '9880012353', 'prakash.jain@loanco.com', 49000, '2021-09-30'),
(5, 'Anita Choudhary', 'Field Agent', '9880012354', 'anita.choudhary@loanco.com', 43000, '2022-07-15'),
(6, 'Rohit Sharma', 'Supervisor', '9880012355', 'rohit.sharma@loanco.com', 62000, '2020-05-20'),
(6, 'Nandini Patel', 'Loan Officer', '9880012356', 'nandini.patel@loanco.com', 51000, '2021-11-08'),
(7, 'Deepak Singh', 'Field Agent', '9880012357', 'deepak.singh@loanco.com', 44000, '2022-03-25'),
(7, 'Shweta Nair', 'Manager', '9880012358', 'shweta.nair@loanco.com', 76000, '2019-07-12'),
(8, 'Amit Verma', 'Loan Officer', '9880012359', 'amit.verma@loanco.com', 47000, '2022-01-05');

-- Insert Vehicles (Note: Using backticks for Year and Condition)
INSERT INTO Vehicle (CustomerID, VehicleNo, Make, Model, `Year`, `Condition`, InsuranceExpiry, MarketValue) VALUES
(1, 'KA01AB1234', 'Hyundai', 'Creta', 2022, 'Excellent', '2024-12-31', 1500000),
(2, 'KA02CD5678', 'Maruti', 'Swift', 2021, 'Good', '2024-10-15', 800000),
(3, 'KA03EF9012', 'Honda', 'City', 2023, 'Excellent', '2025-03-20', 1200000),
(4, 'KA04GH3456', 'Toyota', 'Innova', 2020, 'Good', '2024-08-10', 1800000),
(5, 'KA05IJ7890', 'Hyundai', 'i20', 2022, 'Excellent', '2024-11-30', 900000),
(6, 'KA06KL1234', 'Tata', 'Nexon', 2021, 'Fair', '2024-09-25', 1100000),
(7, 'KA07MN5678', 'Mahindra', 'XUV700', 2023, 'Excellent', '2025-05-15', 2000000),
(8, 'KA08OP9012', 'Kia', 'Seltos', 2022, 'Good', '2024-12-20', 1300000),
(9, 'KA09QR3456', 'Maruti', 'Baleno', 2021, 'Fair', '2024-07-18', 750000),
(10, 'KA10ST7890', 'Hyundai', 'Verna', 2023, 'Excellent', '2025-02-28', 1400000),
(11, 'KA11UV1234', 'Toyota', 'Fortuner', 2022, 'Excellent', '2024-11-10', 3500000),
(12, 'KA12WX5678', 'MG', 'Hector', 2021, 'Good', '2024-08-05', 1700000),
(13, 'KA13YZ9012', 'Skoda', 'Slavia', 2023, 'Excellent', '2025-04-12', 1600000),
(14, 'KA14AB3456', 'Volkswagen', 'Taigun', 2022, 'Good', '2024-10-22', 1450000),
(15, 'KA15CD7890', 'Renault', 'Kiger', 2021, 'Fair', '2024-06-30', 850000);

-- Insert Loans
INSERT INTO Loan (CustomerID, VehicleID, LoanAmount, SanctionDate, TenureMonths, InterestRate, EMAmount, TotalPayable, BalanceAmount, Status, BranchID, AgentID) VALUES
(1, 1, 1200000, '2023-01-15', 60, 8.5, 24627, 1477620, 1200000, 'Active', 1, 1),
(2, 2, 600000, '2023-02-20', 36, 9.0, 19086, 687096, 450000, 'Active', 2, 3),
(3, 3, 900000, '2023-03-10', 48, 8.75, 22267, 1068816, 700000, 'Active', 1, 2),
(4, 4, 1400000, '2023-04-05', 72, 8.25, 24627, 1773144, 1300000, 'Active', 3, 5),
(5, 5, 700000, '2023-05-12', 36, 9.5, 22442, 807912, 550000, 'Active', 2, 4),
(6, 6, 800000, '2023-06-18', 48, 9.25, 20015, 960720, 650000, 'Active', 4, 7),
(7, 7, 1600000, '2023-07-22', 60, 8.0, 32435, 1946100, 1550000, 'Active', 3, 6),
(8, 8, 1000000, '2023-08-30', 48, 8.5, 24627, 1182096, 900000, 'Active', 5, 9),
(9, 9, 500000, '2023-09-14', 24, 10.0, 23072, 553728, 300000, 'Active', 6, 11),
(10, 10, 1100000, '2023-10-08', 60, 8.75, 22715, 1362900, 1050000, 'Active', 4, 8),
(11, 11, 2800000, '2023-11-25', 84, 7.5, 42586, 3577224, 2750000, 'Active', 7, 13),
(12, 12, 1300000, '2023-12-12', 60, 8.25, 26487, 1589220, 1250000, 'Active', 5, 10),
(13, 13, 1200000, '2024-01-20', 48, 8.0, 29315, 1407120, 1150000, 'Active', 8, 14),
(14, 14, 1100000, '2024-02-15', 36, 9.0, 34986, 1259496, 950000, 'Active', 7, 12),
(15, 15, 600000, '2024-03-08', 24, 9.5, 27529, 660696, 500000, 'Active', 6, 15);

-- Insert Installments
INSERT INTO Installment (LoanID, DueDate, PrincipalAmount, InterestAmount, TotalAmount, Status) VALUES
-- Loan 1 Installments
(1, '2023-02-15', 20000, 8500, 28500, 'Paid'),
(1, '2023-03-15', 20200, 8480, 28680, 'Paid'),
(1, '2023-04-15', 20400, 8460, 28860, 'Paid'),
(1, '2023-05-15', 20600, 8440, 29040, 'Paid'),
(1, '2023-06-15', 20800, 8420, 29220, 'Pending'),

-- Loan 2 Installments
(2, '2023-03-20', 16667, 4500, 21167, 'Paid'),
(2, '2023-04-20', 16867, 4480, 21347, 'Paid'),
(2, '2023-05-20', 17067, 4460, 21527, 'Overdue'),

-- Loan 3 Installments
(3, '2023-04-10', 18750, 6563, 25313, 'Paid'),
(3, '2023-05-10', 18950, 6543, 25493, 'Paid'),

-- Add more installments for other loans...
(4, '2023-05-05', 19444, 11528, 30972, 'Paid'),
(5, '2023-06-12', 19444, 5542, 24986, 'Paid'),
(6, '2023-07-18', 16667, 6167, 22834, 'Paid'),
(7, '2023-08-22', 26667, 10667, 37334, 'Paid'),
(8, '2023-09-30', 20833, 7083, 27916, 'Paid'),
(9, '2023-10-14', 20833, 4167, 25000, 'Paid'),
(10, '2023-11-08', 18333, 8021, 26354, 'Paid');

-- Insert Transactions
INSERT INTO TransactionLogger (LoanID, DebitAmount, CreditAmount, BalanceAfterTransaction, Remarks, TransactionType) VALUES
(1, 0, 1200000, 1200000, 'Loan Disbursement', 'Loan Disbursement'),
(1, 28500, 0, 1171500, 'EMI Payment for Feb 2023', 'EMI Payment'),
(1, 28680, 0, 1142820, 'EMI Payment for Mar 2023', 'EMI Payment'),
(2, 0, 600000, 600000, 'Loan Disbursement', 'Loan Disbursement'),
(2, 21167, 0, 578833, 'EMI Payment for Mar 2023', 'EMI Payment'),
(3, 0, 900000, 900000, 'Loan Disbursement', 'Loan Disbursement'),
(3, 25313, 0, 874687, 'EMI Payment for Apr 2023', 'EMI Payment');

-- Insert Seizures
INSERT INTO Seizure (LoanID, AgentID, SeizureDate, Reason, VehicleConditionAtSeizure, SeizureStatus) VALUES
(2, 4, '2023-06-01', 'Multiple EMI defaults - 3 consecutive months', 'Good', 'Completed'),
(6, 7, '2023-08-15', 'Non-payment for 4 months', 'Fair', 'Initiated');

-- Insert Users (with hashed passwords for 'admin123')
INSERT INTO Users (CustomerID, AgentID, Username, Password, Role) VALUES
-- Admin user (password: admin123)
(NULL, NULL, 'admin', '98a08a01449065a6d1170fd0ed0fbb8bf92d6011989a544cdee95efcfaa95e8f84c12bf876cba5c1d6f0c149c919a7a2882741397e1abc73c984020a17c7ac29', 'admin'),
-- Agent users (password: admin123) 
(NULL, 1, 'ramesh_k', '98a08a01449065a6d1170fd0ed0fbb8bf92d6011989a544cdee95efcfaa95e8f84c12bf876cba5c1d6f0c149c919a7a2882741397e1abc73c984020a17c7ac29', 'agent'),
(NULL, 2, 'sita_m', '98a08a01449065a6d1170fd0ed0fbb8bf92d6011989a544cdee95efcfaa95e8f84c12bf876cba5c1d6f0c149c919a7a2882741397e1abc73c984020a17c7ac29', 'agent'),
-- Customer users (password: admin123)
(1, NULL, 'aarav_sharma', '98a08a01449065a6d1170fd0ed0fbb8bf92d6011989a544cdee95efcfaa95e8f84c12bf876cba5c1d6f0c149c919a7a2882741397e1abc73c984020a17c7ac29', 'customer'),
(2, NULL, 'priya_patel', '98a08a01449065a6d1170fd0ed0fbb8bf92d6011989a544cdee95efcfaa95e8f84c12bf876cba5c1d6f0c149c919a7a2882741397e1abc73c984020a17c7ac29', 'customer');


-- =============================================
-- Stored Procedures
-- =============================================

DELIMITER //

-- Procedure to calculate and create installments for a loan
CREATE PROCEDURE CreateLoanInstallments(
    IN p_LoanID INT,
    IN p_LoanAmount DECIMAL(12,2),
    IN p_InterestRate DECIMAL(5,2),
    IN p_TenureMonths INT,
    IN p_StartDate DATE
)
BEGIN
    DECLARE v_counter INT DEFAULT 1;
    DECLARE v_due_date DATE;
    DECLARE v_monthly_interest DECIMAL(10,2);
    DECLARE v_monthly_principal DECIMAL(10,2);
    DECLARE v_remaining_balance DECIMAL(12,2) DEFAULT p_LoanAmount;
    
    SET v_monthly_interest = (p_LoanAmount * (p_InterestRate/100)) / 12;
    SET v_monthly_principal = p_LoanAmount / p_TenureMonths;
    
    WHILE v_counter <= p_TenureMonths DO
        SET v_due_date = DATE_ADD(p_StartDate, INTERVAL v_counter MONTH);
        
        INSERT INTO Installment (LoanID, DueDate, PrincipalAmount, InterestAmount, TotalAmount, Status)
        VALUES (p_LoanID, v_due_date, v_monthly_principal, v_monthly_interest, 
                v_monthly_principal + v_monthly_interest, 'Pending');
        
        SET v_counter = v_counter + 1;
    END WHILE;
END//

-- Procedure to process EMI payment
CREATE PROCEDURE ProcessEMIPayment(
    IN p_InstallmentID INT,
    IN p_PaymentMode VARCHAR(20),
    IN p_PaymentDate DATE
)
BEGIN
    DECLARE v_loan_id INT;
    DECLARE v_amount DECIMAL(10,2);
    DECLARE v_old_balance DECIMAL(12,2);
    DECLARE v_new_balance DECIMAL(12,2);
    
    -- Get loan details
    SELECT i.LoanID, i.TotalAmount, l.BalanceAmount 
    INTO v_loan_id, v_amount, v_old_balance
    FROM Installment i
    JOIN Loan l ON i.LoanID = l.LoanID
    WHERE i.InstallmentID = p_InstallmentID;
    
    SET v_new_balance = v_old_balance - v_amount;
    
    -- Update installment
    UPDATE Installment 
    SET Status = 'Paid', 
        PaidDate = p_PaymentDate,
        PaymentMode = p_PaymentMode
    WHERE InstallmentID = p_InstallmentID;
    
    -- Update loan balance
    UPDATE Loan 
    SET BalanceAmount = v_new_balance
    WHERE LoanID = v_loan_id;
    
    -- Log transaction
    INSERT INTO TransactionLogger (LoanID, DebitAmount, CreditAmount, BalanceAfterTransaction, Remarks, TransactionType)
    VALUES (v_loan_id, v_amount, 0, v_new_balance, 
            CONCAT('EMI Payment - Installment ID: ', p_InstallmentID), 'EMI Payment');
    
    -- Check if loan is fully paid
    IF v_new_balance <= 0 THEN
        UPDATE Loan SET Status = 'Closed' WHERE LoanID = v_loan_id;
    END IF;
END//

-- Function to calculate credit score
CREATE FUNCTION CalculateCreditScore(p_CustomerID INT) 
RETURNS INT
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_score INT DEFAULT 850;
    DECLARE v_default_count INT;
    DECLARE v_active_loans INT;
    DECLARE v_total_loans INT;
    
    -- Check for defaults
    SELECT COUNT(*) INTO v_default_count
    FROM Loan 
    WHERE CustomerID = p_CustomerID AND Status = 'Defaulted';
    
    -- Count active loans
    SELECT COUNT(*) INTO v_active_loans
    FROM Loan 
    WHERE CustomerID = p_CustomerID AND Status = 'Active';
    
    -- Count total loans
    SELECT COUNT(*) INTO v_total_loans
    FROM Loan 
    WHERE CustomerID = p_CustomerID;
    
    -- Deduct for defaults
    SET v_score = v_score - (v_default_count * 100);
    
    -- Adjust for loan burden
    IF v_active_loans > 2 THEN
        SET v_score = v_score - 50;
    END IF;
    
    -- Ensure score doesn't go below 300
    IF v_score < 300 THEN
        SET v_score = 300;
    END IF;
    
    RETURN v_score;
END//

DELIMITER ;

-- =============================================
-- Triggers
-- =============================================

DELIMITER //

-- Trigger to update installment status when due date passes
CREATE TRIGGER UpdateInstallmentStatus
BEFORE UPDATE ON Installment
FOR EACH ROW
BEGIN
    IF NEW.DueDate < CURDATE() AND NEW.Status = 'Pending' THEN
        SET NEW.Status = 'Overdue';
        SET NEW.LateFee = NEW.TotalAmount * 0.02; -- 2% late fee
    END IF;
END//

-- Trigger to log loan status changes
CREATE TRIGGER LogLoanStatusChange
AFTER UPDATE ON Loan
FOR EACH ROW
BEGIN
    IF OLD.Status != NEW.Status THEN
        INSERT INTO TransactionLogger (LoanID, DebitAmount, CreditAmount, BalanceAfterTransaction, Remarks, TransactionType)
        VALUES (NEW.LoanID, 0, 0, NEW.BalanceAmount, 
                CONCAT('Loan status changed from ', OLD.Status, ' to ', NEW.Status), 'EMI Payment');
    END IF;
END//

DELIMITER ;

-- =============================================
-- Views
-- =============================================

-- View for customer loan summary
CREATE VIEW CustomerLoanSummary AS
SELECT 
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    c.Phone,
    c.Email,
    COUNT(l.LoanID) AS TotalLoans,
    SUM(CASE WHEN l.Status = 'Active' THEN 1 ELSE 0 END) AS ActiveLoans,
    SUM(CASE WHEN l.Status = 'Defaulted' THEN 1 ELSE 0 END) AS DefaultedLoans,
    SUM(l.LoanAmount) AS TotalLoanAmount,
    SUM(l.BalanceAmount) AS TotalBalance,
    CalculateCreditScore(c.CustomerID) AS CreditScore
FROM Customer c
LEFT JOIN Loan l ON c.CustomerID = l.CustomerID
GROUP BY c.CustomerID, c.FirstName, c.LastName, c.Phone, c.Email;

-- View for agent performance
CREATE VIEW AgentPerformance AS
SELECT 
    a.AgentID,
    a.Name AS AgentName,
    b.BranchName,
    a.Role,
    COUNT(l.LoanID) AS TotalLoansManaged,
    SUM(l.LoanAmount) AS TotalLoanVolume,
    AVG(l.InterestRate) AS AvgInterestRate,
    SUM(CASE WHEN l.Status = 'Active' THEN 1 ELSE 0 END) AS ActiveLoans,
    SUM(CASE WHEN l.Status = 'Defaulted' THEN 1 ELSE 0 END) AS DefaultedLoans,
    (COUNT(l.LoanID) - SUM(CASE WHEN l.Status = 'Defaulted' THEN 1 ELSE 0 END)) / COUNT(l.LoanID) * 100 AS SuccessRate
FROM Agent a
LEFT JOIN Loan l ON a.AgentID = l.AgentID
LEFT JOIN Branch b ON a.BranchID = b.BranchID
GROUP BY a.AgentID, a.Name, b.BranchName, a.Role;

-- View for overdue installments
CREATE VIEW OverdueInstallments AS
SELECT 
    i.InstallmentID,
    l.LoanID,
    c.CustomerID,
    CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
    i.DueDate,
    i.TotalAmount,
    i.LateFee,
    DATEDIFF(CURDATE(), i.DueDate) AS DaysOverdue,
    a.Name AS AgentName,
    a.Phone AS AgentPhone
FROM Installment i
JOIN Loan l ON i.LoanID = l.LoanID
JOIN Customer c ON l.CustomerID = c.CustomerID
JOIN Agent a ON l.AgentID = a.AgentID
WHERE i.Status = 'Overdue'
AND i.DueDate < CURDATE();

-- =============================================
-- Complex Queries Examples
-- =============================================

-- Query 1: Find customers with highest loan amounts and their credit scores
SELECT 
    cls.CustomerName,
    cls.TotalLoanAmount,
    cls.CreditScore,
    CASE 
        WHEN cls.CreditScore >= 750 THEN 'Excellent'
        WHEN cls.CreditScore >= 650 THEN 'Good'
        WHEN cls.CreditScore >= 550 THEN 'Fair'
        ELSE 'Poor'
    END AS CreditRating
FROM CustomerLoanSummary cls
ORDER BY cls.TotalLoanAmount DESC
LIMIT 10;

-- Query 2: Monthly collection report by branch
SELECT 
    b.BranchName,
    YEAR(t.TransactionDate) AS Year,
    MONTH(t.TransactionDate) AS Month,
    COUNT(t.TransactionID) AS TotalTransactions,
    SUM(t.DebitAmount) AS TotalCollection,
    AVG(t.DebitAmount) AS AverageTransaction
FROM TransactionLogger t
JOIN Loan l ON t.LoanID = l.LoanID
JOIN Branch b ON l.BranchID = b.BranchID
WHERE t.TransactionType = 'EMI Payment'
GROUP BY b.BranchName, YEAR(t.TransactionDate), MONTH(t.TransactionDate)
ORDER BY Year DESC, Month DESC, TotalCollection DESC;

-- Query 3: Nested Query - Find agents with no defaulted loans
SELECT 
    a.AgentID,
    a.Name,
    b.BranchName,
    COUNT(l.LoanID) AS ManagedLoans
FROM Agent a
JOIN Branch b ON a.BranchID = b.BranchID
LEFT JOIN Loan l ON a.AgentID = l.AgentID
WHERE a.AgentID NOT IN (
    SELECT DISTINCT AgentID 
    FROM Loan 
    WHERE Status = 'Defaulted'
)
GROUP BY a.AgentID, a.Name, b.BranchName
HAVING ManagedLoans > 0;

-- Query 4: Join with Aggregate - Branch-wise performance
SELECT 
    b.BranchID,
    b.BranchName,
    b.ManagerName,
    COUNT(l.LoanID) AS TotalLoans,
    SUM(l.LoanAmount) AS TotalSanctioned,
    SUM(l.BalanceAmount) AS OutstandingBalance,
    SUM(CASE WHEN l.Status = 'Active' THEN 1 ELSE 0 END) AS ActiveLoans,
    SUM(CASE WHEN i.Status = 'Overdue' THEN 1 ELSE 0 END) AS OverdueInstallments,
    (SUM(l.LoanAmount) - SUM(l.BalanceAmount)) AS TotalRecovered
FROM Branch b
LEFT JOIN Loan l ON b.BranchID = l.BranchID
LEFT JOIN Installment i ON l.LoanID = i.LoanID AND i.Status = 'Overdue'
GROUP BY b.BranchID, b.BranchName, b.ManagerName
ORDER BY TotalSanctioned DESC;

-- Query 5: Vehicle details with loan information
SELECT 
    v.VehicleID,
    v.VehicleNo,
    v.Make,
    v.Model,
    v.`Year`,
    v.MarketValue,
    l.LoanID,
    l.LoanAmount,
    l.BalanceAmount,
    l.Status AS LoanStatus,
    c.FirstName,
    c.LastName,
    DATEDIFF(v.InsuranceExpiry, CURDATE()) AS DaysUntilInsuranceExpiry
FROM Vehicle v
JOIN Loan l ON v.VehicleID = l.VehicleID
JOIN Customer c ON v.CustomerID = c.CustomerID
WHERE l.Status = 'Active'
ORDER BY DaysUntilInsuranceExpiry ASC;

-- =============================================
-- Indexes for Performance
-- =============================================

CREATE INDEX idx_loan_customer ON Loan(CustomerID);
CREATE INDEX idx_loan_agent ON Loan(AgentID);
CREATE INDEX idx_loan_branch ON Loan(BranchID);
CREATE INDEX idx_loan_status ON Loan(Status);
CREATE INDEX idx_installment_loan ON Installment(LoanID);
CREATE INDEX idx_installment_due_date ON Installment(DueDate);
CREATE INDEX idx_installment_status ON Installment(Status);
CREATE INDEX idx_transaction_loan ON TransactionLogger(LoanID);
CREATE INDEX idx_transaction_date ON TransactionLogger(TransactionDate);
CREATE INDEX idx_vehicle_customer ON Vehicle(CustomerID);
CREATE INDEX idx_agent_branch ON Agent(BranchID);

-- =============================================
-- Sample CRUD Operations
-- =============================================

-- CREATE: Add a new customer
INSERT INTO Customer (FirstName, LastName, Phone, Email, Address, City, Pincode, DateOfBirth, AadharNumber, PANNumber)
VALUES ('New', 'Customer', '9876543225', 'new.customer@email.com', '777 New Address', 'Bangalore', '560068', '1990-01-01', '123456789027', 'PQRST1234U');

-- READ: Get customer details with their loans
SELECT c.*, l.LoanID, l.LoanAmount, l.Status 
FROM Customer c 
LEFT JOIN Loan l ON c.CustomerID = l.CustomerID 
WHERE c.CustomerID = 1;

-- UPDATE: Update customer information
UPDATE Customer 
SET Phone = '9876543999', Email = 'updated.email@email.com'
WHERE CustomerID = 1;

-- DELETE: Delete a customer (will cascade to related tables due to CASCADE constraint)
DELETE FROM Customer WHERE CustomerID = 16;

-- =============================================
-- Database Users and Permissions
-- =============================================

CREATE USER 'loan_admin'@'localhost' IDENTIFIED BY 'admin123';
GRANT ALL PRIVILEGES ON VehicleLoanDB.* TO 'loan_admin'@'localhost';

CREATE USER 'loan_agent'@'localhost' IDENTIFIED BY 'agent123';
GRANT SELECT, INSERT, UPDATE ON VehicleLoanDB.* TO 'loan_agent'@'localhost';

CREATE USER 'loan_customer'@'localhost' IDENTIFIED BY 'customer123';
GRANT SELECT ON VehicleLoanDB.Customer TO 'loan_customer'@'localhost';
GRANT SELECT ON VehicleLoanDB.Loan TO 'loan_customer'@'localhost';
GRANT SELECT ON VehicleLoanDB.Installment TO 'loan_customer'@'localhost';

FLUSH PRIVILEGES;

-- =============================================
-- End of Database Setup
-- =============================================