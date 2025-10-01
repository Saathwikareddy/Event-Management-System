from typing import Optional, Dict, List
from src.config import get_supabase

class PaymentDAO:
    def __init__(self):
        self._sb = get_supabase()

    def create_payment(self, booking_id: int, amount: float, method: str | None = None) -> Optional[Dict]:
        payload = {
            "booking_id": booking_id,
            "amount": amount,
            "method": method,
            "status": "PENDING"
        }
        self._sb.table("payments").insert(payload).execute()
        resp = self._sb.table("payments").select("*").eq("booking_id", booking_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def mark_paid(self, booking_id: int, method: str) -> Optional[Dict]:
        self._sb.table("payments").update({"status": "PAID", "method": method}).eq("booking_id", booking_id).execute()
        resp = self._sb.table("payments").select("*").eq("booking_id", booking_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def refund_payment(self, booking_id: int) -> Optional[Dict]:
        self._sb.table("payments").update({"status": "REFUNDED"}).eq("booking_id", booking_id).execute()
        resp = self._sb.table("payments").select("*").eq("booking_id", booking_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_payment_by_booking(self, booking_id: int) -> Optional[Dict]:
        resp = self._sb.table("payments").select("*").eq("booking_id", booking_id).limit(1).execute()
        return resp.data[0] if resp.data else None
