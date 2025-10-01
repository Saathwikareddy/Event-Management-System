# src/services/payment_service.py
from typing import Dict
from src.dao.payment_dao import PaymentDAO

class PaymentError(Exception):
    """Custom exception for payment-related errors."""
    pass

class PaymentService:
    def __init__(self, dao: PaymentDAO = None):
        # Allow dependency injection, default to PaymentDAO
        self.dao = dao or PaymentDAO()

    def create_pending_payment(self, booking_id: int, amount: float) -> Dict:
        """
        Create a pending payment record for a booking.
        """
        return self.dao.create_payment(booking_id, amount)

    def process_payment(self, booking_id: int, method: str) -> Dict:
        """
        Mark a payment as PAID with a given method (Cash/Card/UPI).
        """
        payment = self.dao.get_payment_by_booking(booking_id)
        if not payment:
            raise PaymentError(f"No payment found for booking {booking_id}")
        if payment["status"] == "PAID":
            raise PaymentError("Payment is already completed")
        return self.dao.mark_paid(booking_id, method)

    def refund_payment(self, booking_id: int) -> Dict:
        """
        Mark a payment as REFUNDED for a cancelled booking.
        """
        payment = self.dao.get_payment_by_booking(booking_id)
        if not payment:
            raise PaymentError(f"No payment found for booking {booking_id}")
        if payment["status"] == "REFUNDED":
            raise PaymentError("Payment is already refunded")
        return self.dao.refund_payment(booking_id)
