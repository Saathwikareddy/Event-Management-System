# src/dao/event_dao.py
from typing import Optional, List, Dict
from src.config import get_supabase

class EventDAO:
    def __init__(self):
        self._sb = get_supabase()

    def create_event(self, title: str, date: str, location: str, capacity: int, price: float) -> Optional[Dict]:
        payload = {
            "title": title,
            "date": date,
            "location": location,
            "capacity": capacity,
            "price": price
        }
        self._sb.table("events").insert(payload).execute()
        resp = self._sb.table("events").select("*").eq("title", title).limit(1).execute()
        return resp.data[0] if resp.data else None

    def get_event_by_id(self, event_id: int) -> Optional[Dict]:
        resp = self._sb.table("events").select("*").eq("event_id", event_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def list_events(self, limit: int = 100) -> List[Dict]:
        resp = self._sb.table("events").select("*").order("event_id").limit(limit).execute()
        return resp.data or []

    def update_event(self, event_id: int, fields: Dict) -> Optional[Dict]:
        self._sb.table("events").update(fields).eq("event_id", event_id).execute()
        resp = self._sb.table("events").select("*").eq("event_id", event_id).limit(1).execute()
        return resp.data[0] if resp.data else None

    def delete_event(self, event_id: int) -> Optional[Dict]:
        resp_before = self._sb.table("events").select("*").eq("event_id", event_id).limit(1).execute()
        row = resp_before.data[0] if resp_before.data else None
        self._sb.table("events").delete().eq("event_id", event_id).execute()
        return row

