# src/dao/bookings_dao.py
from typing import Optional, List, Dict
from src.config import get_supabase

class BookingDAO:
    def __init__(self):
        self._sb = get_supabase()

    def create_booking(self, cust_id: int, event_id: int, seats: int) -> Optional[Dict]:
        payload = {
            "cust_id": cust_id,
            "event_id": event_id,
            "seats": seats,
            "status": "BOOKED"
        }
        self._sb.table("bookings").insert(payload).execute()
        resp = self._sb.table("bookings").select("*")\
                   .eq("cust_id", cust_id).eq("event_id", event_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_booking_by_id(self, booking_id: int) -> Optional[Dict]:
        resp = self._sb.table("bookings").select("*").eq("booking_id", booking_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def list_bookings(self, limit: int = 100) -> List[Dict]:
        resp = self._sb.table("bookings").select("*").order("booking_id").limit(limit).execute()
        return resp.data or []

    def update_booking(self, booking_id: int, fields: Dict) -> Optional[Dict]:
        self._sb.table("bookings").update(fields).eq("booking_id", booking_id).execute()
        resp = self._sb.table("bookings").select("*").eq("booking_id", booking_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def delete_booking(self, booking_id: int) -> Optional[Dict]:
        resp_before = self._sb.table("bookings").select("*").eq("booking_id", booking_id).limit(1).execute()
        row = resp_before.data[0] if resp_before.data else None
        self._sb.table("bookings").delete().eq("booking_id", booking_id).execute()
        return row
