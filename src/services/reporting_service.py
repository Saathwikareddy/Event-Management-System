# src/services/reporting_service.py
from typing import List, Dict
from src.dao.booking_dao import BookingDAO
from src.dao.event_dao import EventDAO
from src.dao.customer_dao import CustomerDAO
from datetime import datetime, timedelta

# Custom exception
class ReportingError(Exception):
    pass

class ReportingService:
    def __init__(self, booking_dao: BookingDAO, event_dao: EventDAO, customer_dao: CustomerDAO):
        self.booking_dao = booking_dao
        self.event_dao = event_dao
        self.customer_dao = customer_dao

    def top_selling_events(self, limit: int = 5) -> List[Dict]:
        try:
            bookings = self.booking_dao.list_bookings()
            event_count = {}
            for b in bookings:
                eid = b["event_id"]
                event_count[eid] = event_count.get(eid, 0) + b["seats"]

            top_eids = sorted(event_count, key=event_count.get, reverse=True)[:limit]
            top_events = []
            for eid in top_eids:
                event = self.event_dao.get_event_by_id(eid)
                top_events.append({"event": event["title"], "seats_sold": event_count[eid]})
            return top_events
        except Exception as e:
            raise ReportingError(str(e))

    def total_revenue_last_month(self) -> float:
        try:
            bookings = self.booking_dao.list_bookings()
            last_month = datetime.now() - timedelta(days=30)
            revenue = 0.0
            for b in bookings:
                if datetime.strptime(b["created_at"], "%Y-%m-%d") >= last_month:
                    event = self.event_dao.get_event_by_id(b["event_id"])
                    revenue += b["seats"] * event["price"]
            return revenue
        except Exception as e:
            raise ReportingError(str(e))

    def total_bookings_per_customer(self) -> List[Dict]:
        try:
            bookings = self.booking_dao.list_bookings()
            customer_count = {}
            for b in bookings:
                cid = b["cust_id"]
                customer_count[cid] = customer_count.get(cid, 0) + 1
            result = []
            for cid, count in customer_count.items():
                customer = self.customer_dao.get_customer_by_id(cid)
                result.append({"customer": customer["name"], "total_bookings": count})
            return result
        except Exception as e:
            raise ReportingError(str(e))

    def customers_with_multiple_bookings(self, min_bookings: int = 2) -> List[Dict]:
        try:
            bookings = self.booking_dao.list_bookings()
            customer_count = {}
            for b in bookings:
                cid = b["cust_id"]
                customer_count[cid] = customer_count.get(cid, 0) + 1
            result = []
            for cid, count in customer_count.items():
                if count > min_bookings:
                    customer = self.customer_dao.get_customer_by_id(cid)
                    result.append({"customer": customer["name"], "bookings": count})
            return result
        except Exception as e:
            raise ReportingError(str(e))
