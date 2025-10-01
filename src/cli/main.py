# src/cli/main.py
from src.dao.customer_dao import CustomerDAO
from src.dao.event_dao import EventDAO
from src.dao.booking_dao import BookingDAO
from src.services.customer_service import CustomerService
from src.services.event_service import EventService
from src.services.booking_service import BookingService
from src.services.payment_service import PaymentService
from src.services.reporting_service import ReportingService, ReportingError

from datetime import datetime

class EventManagementCLI:
    def __init__(self):
        # DAOs
        self.customer_dao = CustomerDAO()
        self.event_dao = EventDAO()
        self.booking_dao = BookingDAO()
        
        # Services
        self.customer_service = CustomerService(self.customer_dao)
        self.event_service = EventService(self.event_dao)
        self.payment_service = PaymentService()
        self.booking_service = BookingService(
            booking_dao=self.booking_dao,
            event_dao=self.event_dao,
            customer_dao=self.customer_dao,
            payment_service=self.payment_service
        )
        self.reporting_service = ReportingService(
            booking_dao=self.booking_dao,
            event_dao=self.event_dao,
            customer_dao=self.customer_dao
        )

    def run(self):
        while True:
            print("\n--- Event Management System ---")
            print("1. Customer Management")
            print("2. Event Management")
            print("3. Book Event")
            print("4. Payment Processing")
            print("5. Reports")
            print("0. Exit")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                self.customer_menu()
            elif choice == "2":
                self.event_menu()
            elif choice == "3":
                self.book_event_menu()
            elif choice == "4":
                self.payment_menu()
            elif choice == "5":
                self.reporting_menu()
            elif choice == "0":
                break
            else:
                print("Invalid choice")

    # ---------------- CUSTOMER ----------------
    def customer_menu(self):
        while True:
            print("\n--- Customer Menu ---")
            print("1. Add Customer")
            print("2. List Customers")
            print("3. Get Customer by ID")
            print("4. Update Customer")
            print("5. Delete Customer")
            print("0. Back")
            choice = input("Choice: ").strip()
            if choice == "1":
                name = input("Name: ")
                email = input("Email: ")
                phone = input("Phone: ")
                city = input("City (optional): ").strip() or None
                customer = self.customer_service.create_customer(name, email, phone, city)
                print("Customer added:", customer)
            elif choice == "2":
                customers = self.customer_service.list_customers()
                for c in customers:
                    print(c)
            elif choice == "3":
                cust_id = int(input("Customer ID: "))
                c = self.customer_service.get_customer(cust_id)
                print(c if c else "Customer not found")
            elif choice == "4":
                cust_id = int(input("Customer ID to update: "))
                fields = {}
                name = input("New Name (blank to skip): ").strip()
                email = input("New Email (blank to skip): ").strip()
                phone = input("New Phone (blank to skip): ").strip()
                city = input("New City (blank to skip): ").strip()
                if name: fields["name"] = name
                if email: fields["email"] = email
                if phone: fields["phone"] = phone
                if city: fields["city"] = city
                updated = self.customer_service.update_customer(cust_id, fields)
                print("Updated:", updated if updated else "Update failed")
            elif choice == "5":
                cust_id = int(input("Customer ID to delete: "))
                deleted = self.customer_service.delete_customer(cust_id)
                print("Deleted:", deleted if deleted else "Customer not found")
            elif choice == "0":
                break
            else:
                print("Invalid choice")

    # ---------------- EVENT ----------------
    def event_menu(self):
        while True:
            print("\n--- Event Menu ---")
            print("1. Add Event")
            print("2. List Events")
            print("3. Get Event by ID")
            print("4. Update Event")
            print("5. Delete Event")
            print("0. Back")
            choice = input("Choice: ").strip()
            if choice == "1":
                title = input("Title: ")
                date = input("Date (YYYY-MM-DD): ")
                location = input("Location: ")
                capacity = int(input("Capacity: "))
                price = float(input("Price: "))
                event = self.event_service.add_event(title, date, location, capacity, price)
                print("Event added:", event)
            elif choice == "2":
                events = self.event_service.list_events()
                for e in events:
                    print(e)
            elif choice == "3":
                eid = int(input("Event ID: "))
                e = self.event_service.get_event(eid)
                print(e)
            elif choice == "4":
                eid = int(input("Event ID to update: "))
                fields = {}
                title = input("New Title (blank to skip): ").strip()
                date = input("New Date (YYYY-MM-DD, blank to skip): ").strip()
                location = input("New Location (blank to skip): ").strip()
                capacity = input("New Capacity (blank to skip): ").strip()
                price = input("New Price (blank to skip): ").strip()
                if title: fields["title"] = title
                if date: fields["date"] = date
                if location: fields["location"] = location
                if capacity: fields["capacity"] = int(capacity)
                if price: fields["price"] = float(price)
                updated = self.event_service.update_event(eid, fields)
                print("Updated:", updated)
            elif choice == "5":
                eid = int(input("Event ID to delete: "))
                deleted = self.event_service.delete_event(eid)
                print("Deleted:", deleted)
            elif choice == "0":
                break
            else:
                print("Invalid choice")

    # ---------------- BOOKINGS ----------------
    def book_event_menu(self):
        while True:
            print("\n--- Booking Menu ---")
            print("1. Book Event")
            print("2. View Booking by ID")
            print("3. Cancel Booking")
            print("0. Back")
            choice = input("Choice: ").strip()
            if choice == "1":
                cust_id = int(input("Customer ID: "))
                event_id = int(input("Event ID: "))
                seats = int(input("Number of Seats: "))
                try:
                    booking = self.booking_service.book_event(cust_id, event_id, seats)
                    print("Booking successful:", booking)
                except Exception as e:
                    print("Error:", e)
            elif choice == "2":
                bid = int(input("Booking ID: "))
                try:
                    booking = self.booking_service.get_booking(bid)
                    print(booking)
                except Exception as e:
                    print("Error:", e)
            elif choice == "3":
                bid = int(input("Booking ID to cancel: "))
                try:
                    cancelled = self.booking_service.cancel_booking(bid)
                    print("Booking cancelled:", cancelled)
                except Exception as e:
                    print("Error:", e)
            elif choice == "0":
                break
            else:
                print("Invalid choice")

    # ---------------- PAYMENTS ----------------
    def payment_menu(self):
        while True:
            print("\n--- Payment Menu ---")
            print("1. Process Payment")
            print("2. Back")
            choice = input("Choice: ").strip()
            if choice == "1":
                booking_id = int(input("Booking ID: "))
                method = input("Payment Method (Cash/Card/UPI): ").strip()
                try:
                    payment = self.payment_service.process_payment(booking_id, method)
                    print("Payment successful:", payment)
                except Exception as e:
                    print("Error:", e)
            elif choice == "2":
                break
            else:
                print("Invalid choice")

    # ---------------- REPORTING ----------------
    def reporting_menu(self):
        while True:
            print("\n--- Reporting Menu ---")
            print("1. Top 5 Selling Events")
            print("2. Total Revenue Last Month")
            print("3. Total Bookings per Customer")
            print("4. Customers with >2 Bookings")
            print("0. Back")
            choice = input("Choice: ").strip()
            try:
                if choice == "1":
                    top_events = self.reporting_service.top_selling_events()
                    for e in top_events:
                        print(e)
                elif choice == "2":
                    revenue = self.reporting_service.total_revenue_last_month()
                    print("Total revenue last month:", revenue)
                elif choice == "3":
                    counts = self.reporting_service.total_bookings_per_customer()
                    for c in counts:
                        print(c)
                elif choice == "4":
                    customers = self.reporting_service.customers_with_multiple_bookings()
                    for c in customers:
                        print(c)
                elif choice == "0":
                    break
                else:
                    print("Invalid choice")
            except ReportingError as e:
                print("Reporting error:", e)


if __name__ == "__main__":
    cli = EventManagementCLI()
    cli.run()
