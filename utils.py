from datetime import datetime, timedelta
import math
import hashlib
from typing import Union

class LoanCalculator:
    @staticmethod
    def calculate_emi(principal, annual_rate, tenure_months):
        """Calculate EMI using standard formula"""
        if principal <= 0 or annual_rate <= 0 or tenure_months <= 0:
            raise ValueError("Principal, rate, and tenure must be positive")
        
        monthly_rate = annual_rate / (12 * 100)
        if monthly_rate == 0:  # Handle zero interest case
            return round(principal / tenure_months, 2)
        
        emi = (principal * monthly_rate * math.pow(1 + monthly_rate, tenure_months)) / \
              (math.pow(1 + monthly_rate, tenure_months) - 1)
        return round(emi, 2)
    
    @staticmethod
    def calculate_total_payable(emi, tenure_months):
        """Calculate total payable amount"""
        if emi <= 0 or tenure_months <= 0:
            raise ValueError("EMI and tenure must be positive")
        return round(emi * tenure_months, 2)
    
    @staticmethod
    def calculate_installments(loan_amount, interest_rate, tenure_months, start_date):
        """Calculate installment schedule"""
        if loan_amount <= 0 or interest_rate < 0 or tenure_months <= 0:
            raise ValueError("Invalid loan parameters")
        
        monthly_interest = interest_rate / (12 * 100)
        monthly_principal = loan_amount / tenure_months
        installments = []
        
        remaining_balance = loan_amount
        
        for month in range(1, tenure_months + 1):
            due_date = start_date + timedelta(days=30 * month)
            interest_amount = remaining_balance * monthly_interest
            total_amount = monthly_principal + interest_amount
            remaining_balance -= monthly_principal
            
            installments.append({
                'due_date': due_date,
                'principal_amount': round(monthly_principal, 2),
                'interest_amount': round(interest_amount, 2),
                'total_amount': round(total_amount, 2),
                'remaining_balance': round(remaining_balance, 2)
            })
        
        return installments
    
    @staticmethod
    def validate_loan_parameters(loan_amount, market_value, interest_rate, tenure):
        """Validate loan parameters against business rules"""
        errors = []
        
        # Loan-to-value ratio (should not exceed 80%)
        ltv_ratio = (loan_amount / market_value) * 100
        if ltv_ratio > 80:
            errors.append(f"Loan amount exceeds 80% of vehicle value (LTV: {ltv_ratio:.1f}%)")
        
        # Interest rate bounds
        if interest_rate < 5 or interest_rate > 25:
            errors.append("Interest rate must be between 5% and 25%")
        
        # Tenure bounds
        if tenure < 6 or tenure > 84:
            errors.append("Loan tenure must be between 6 and 84 months")
        
        return errors

class DateUtils:
    @staticmethod
    def is_overdue(due_date):
        return due_date < datetime.now().date()
    
    @staticmethod
    def calculate_late_fee(due_date, total_amount):
        if not DateUtils.is_overdue(due_date):
            return 0
        
        days_overdue = (datetime.now().date() - due_date).days
        if days_overdue <= 0:
            return 0
        
        # 2% per month or part thereof, capped at 20%
        months_overdue = max(1, (days_overdue + 14) // 30)  # Give 15-day grace period
        late_fee_percentage = min(0.02 * months_overdue, 0.20)  # Cap at 20%
        return round(total_amount * late_fee_percentage, 2)
    
    @staticmethod
    def validate_date(date_string, date_format='%Y-%m-%d'):
        """Validate date string format"""
        try:
            datetime.strptime(date_string, date_format)
            return True
        except ValueError:
            return False

# -------------------------
# Portable MD5 helper below
# -------------------------
def md5_hex(data: Union[bytes, str]) -> str:
    """
    Return hex MD5 digest for given data (bytes or str).
    Robust across different Python/OpenSSL builds that may or may not accept
    the 'usedforsecurity' keyword or expose openssl_md5.
    """
    if isinstance(data, str):
        data = data.encode('utf-8')

    # Try hashlib.openssl_md5 if present and callable
    try:
        func = getattr(hashlib, "openssl_md5", None)
        if callable(func):
            try:
                # some builds accept no args, then update
                h = func()
                h.update(data)
                return h.hexdigest()
            except TypeError:
                # some builds accept initial data
                h = func(data)
                if hasattr(h, "hexdigest"):
                    return h.hexdigest()
    except Exception:
        pass

    # Standard md5 fallback
    try:
        h = hashlib.md5()
        h.update(data)
        return h.hexdigest()
    except Exception:
        # As a last resort, use hashlib.new without risky kwargs
        h = hashlib.new('md5')
        h.update(data)
        return h.hexdigest()
