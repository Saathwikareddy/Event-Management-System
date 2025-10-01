# src/services/customer_service.py
from typing import Dict, List
from src.dao.customer_dao import CustomerDAO

class CustomerError(Exception):
    """Custom exception for customer-related errors."""
    pass

class CustomerService:
    def __init__(self, dao: CustomerDAO):
        self.dao = dao

    def add_customer(self, name: str, email: str, phone: str, city: str | None = None) -> Dict:
        # Validate email uniqueness
        existing = self.dao.get_customer_by_email(email)
        if existing:
            raise CustomerError(f"Customer with email '{email}' already exists.")
        return self.dao.create_customer(name, email, phone, city)

    def get_customer(self, cust_id: int) -> Dict:
        customer = self.dao.get_customer_by_id(cust_id)
        if not customer:
            raise CustomerError(f"Customer not found with id: {cust_id}")
        return customer

    def update_customer(self, cust_id: int, fields: Dict) -> Dict:
        # Optional: validate fields (like email uniqueness)
        if 'email' in fields:
            existing = self.dao.get_customer_by_email(fields['email'])
            if existing and existing['cust_id'] != cust_id:
                raise CustomerError(f"Email '{fields['email']}' already used by another customer.")
        updated = self.dao.update_customer(cust_id, fields)
        if not updated:
            raise CustomerError(f"Failed to update customer with id: {cust_id}")
        return updated

    def delete_customer(self, cust_id: int) -> Dict:
        deleted = self.dao.delete_customer(cust_id)
        if not deleted:
            raise CustomerError(f"Customer not found with id: {cust_id}")
        return deleted

    def list_customers(self, limit: int = 100) -> List[Dict]:
        return self.dao.list_customers(limit)

    def search_customers(self, email: str | None = None, city: str | None = None) -> List[Dict]:
        return self.dao.search_customers(email=email, city=city)
