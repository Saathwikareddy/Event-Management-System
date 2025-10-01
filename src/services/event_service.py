# src/services/event_service.py
from typing import Dict, List
from src.dao.event_dao import EventDAO

class EventError(Exception):
    """Custom exception for event-related errors."""
    pass

class EventService:
    def __init__(self, dao: EventDAO):
        self.dao = dao

    def add_event(self, title: str, date: str, location: str, capacity: int, price: float) -> Dict:
        # Basic validation
        if capacity <= 0:
            raise EventError("Event capacity must be greater than 0")
        if price < 0:
            raise EventError("Event price cannot be negative")
        return self.dao.create_event(title, date, location, capacity, price)

    def get_event(self, event_id: int) -> Dict:
        event = self.dao.get_event_by_id(event_id)
        if not event:
            raise EventError(f"Event not found with id: {event_id}")
        return event

    def update_event(self, event_id: int, fields: Dict) -> Dict:
        updated = self.dao.update_event(event_id, fields)
        if not updated:
            raise EventError(f"Failed to update event with id: {event_id}")
        return updated

    def delete_event(self, event_id: int) -> Dict:
        deleted = self.dao.delete_event(event_id)
        if not deleted:
            raise EventError(f"Event not found with id: {event_id}")
        return deleted

    def list_events(self, limit: int = 100) -> List[Dict]:
        return self.dao.list_events(limit)
    
    def search_events(self, title: str | None = None, date: str | None = None, location: str | None = None) -> List[Dict]:
        return self.dao.search_events(title=title, date=date, location=location)
