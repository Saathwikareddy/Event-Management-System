# src/services/booking_service.py
from typing import Dict
from src.dao.booking_dao import BookingDAO
from src.dao.event_dao import EventDAO
from src.dao.customer_dao import CustomerDAO
from src.services.payment_service import PaymentService, PaymentError

class BookingError(Exception):
    """Custom exception for booking-related errors."""
    pass

class BookingService:
    def __init__(self, 
                 booking_dao: BookingDAO = None, 
                 event_dao: EventDAO = None, 
                 customer_dao: CustomerDAO = None, 
                 payment_service: PaymentService = None):
        # Dependency injection
        self.booking_dao = booking_dao or BookingDAO()
        self.event_dao = event_dao or EventDAO()
        self.customer_dao = customer_dao or CustomerDAO()
        self.payment_service = payment_service or PaymentService()

    def book_event(self, cust_id: int, event_id: int, seats: int) -> Dict:
        # Validate customer
        customer = self.customer_dao.get_customer_by_id(cust_id)
        if not customer:
            raise BookingError(f"Customer not found: {cust_id}")

        # Validate event and capacity
        event = self.event_dao.get_event_by_id(event_id)
        if not event:
            raise BookingError(f"Event not found: {event_id}")
        if seats > event.get("capacity", 0):
            raise BookingError("Not enough seats available")

        # Reduce event capacity
        new_capacity = event["capacity"] - seats
        self.event_dao.update_event(event_id, {"capacity": new_capacity})

        # Create booking
        booking = self.booking_dao.create_booking(cust_id, event_id, seats)

        # Create pending payment
        amount = seats * event["price"]
        self.payment_service.create_pending_payment(booking["booking_id"], amount)

        return booking

    def get_booking(self, booking_id: int) -> Dict:
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if not booking:
            raise BookingError("Booking not found")
        return booking

    def cancel_booking(self, booking_id: int) -> Dict:
        booking = self.booking_dao.get_booking_by_id(booking_id)
        if not booking:
            raise BookingError("Booking not found")

        # Update booking status
        self.booking_dao.update_booking(booking_id, {"status": "CANCELLED"})

        # Refund payment
        try:
            self.payment_service.refund_payment(booking_id)
        except PaymentError as e:
            print("Payment refund warning:", e)

        # Restore event capacity
        event = self.event_dao.get_event_by_id(booking["event_id"])
        self.event_dao.update_event(event["event_id"], {"capacity": event["capacity"] + booking["seats"]})

        return self.booking_dao.get_booking_by_id(booking_id)

