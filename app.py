import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load Supabase credentials
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="🎟️ Event Management System", page_icon="🎉", layout="centered")
st.title("🎉 Event Management System")

menu = ["Add Customer", "View Customers",
        "Add Event", "View Events", "Delete Event",
        "Book Event", "View Bookings", "Cancel Booking",
        "Payments"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------- CUSTOMERS ----------------
if choice == "Add Customer":
    st.subheader("Add Customer")
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    city = st.text_input("City")

    if st.button("Save Customer"):
        try:
            supabase.table("customers").insert({
                "name": name,
                "email": email,
                "phone": phone,
                "city": city
            }).execute()
            st.success(f"✅ Customer {name} added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

elif choice == "View Customers":
    st.subheader("All Customers")
    try:
        customers = supabase.table("customers").select("*").execute()
        st.dataframe(customers.data)
    except Exception as e:
        st.error(f"Error fetching customers: {e}")

# ---------------- EVENTS ----------------
elif choice == "Add Event":
    st.subheader("Add Event")
    title = st.text_input("Event Title")
    date = st.date_input("Event Date")
    location = st.text_input("Location")
    capacity = st.number_input("Capacity", min_value=1, step=1)
    price = st.number_input("Price (₹)", min_value=0.0, step=0.01, format="%.2f")

    if st.button("Save Event"):
        try:
            supabase.table("events").insert({
                "title": title,
                "date": str(date),
                "location": location,
                "capacity": int(capacity),
                "price": float(price)
            }).execute()
            st.success(f"✅ Event '{title}' added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

elif choice == "View Events":
    st.subheader("All Events")
    try:
        events = supabase.table("events").select("*").execute()
        st.dataframe(events.data)
    except Exception as e:
        st.error(f"Error fetching events: {e}")

elif choice == "Delete Event":
    st.subheader("Delete Event")
    try:
        events = supabase.table("events").select("*").execute()
        if events.data:
            event_list = {e["event_id"]: e["title"] for e in events.data}
            event_id = st.selectbox("Select Event", list(event_list.keys()), format_func=lambda x: event_list[x])

            if st.button("Delete Event"):
                # check bookings before deleting
                bookings = supabase.table("bookings").select("booking_id").eq("event_id", event_id).execute()
                if bookings.data:
                    st.error("⚠️ Cannot delete event. Bookings exist.")
                else:
                    supabase.table("events").delete().eq("event_id", event_id).execute()
                    st.warning("🗑️ Event deleted successfully!")
        else:
            st.info("No events available.")
    except Exception as e:
        st.error(f"Error deleting event: {e}")

# ---------------- BOOKINGS ----------------
elif choice == "Book Event":
    st.subheader("Book Event")
    try:
        customers = supabase.table("customers").select("*").execute()
        events = supabase.table("events").select("*").execute()

        if customers.data and events.data:
            cust_list = {c["cust_id"]: c["name"] for c in customers.data}
            event_list = {e["event_id"]: e["title"] for e in events.data}

            cust_id = st.selectbox("Select Customer", list(cust_list.keys()), format_func=lambda x: cust_list[x])
            event_id = st.selectbox("Select Event", list(event_list.keys()), format_func=lambda x: event_list[x])
            seats = st.number_input("Number of Seats", min_value=1, step=1)

            if st.button("Book Tickets"):
                selected_event = next((e for e in events.data if e["event_id"] == event_id), None)

                if selected_event:
                    booked = supabase.table("bookings").select("seats").eq("event_id", event_id).execute()
                    total_booked = sum([b["seats"] for b in booked.data]) if booked.data else 0
                    available = selected_event["capacity"] - total_booked

                    if seats <= available:
                        booking_resp = supabase.table("bookings").insert({
                            "cust_id": cust_id,
                            "event_id": event_id,
                            "seats": seats,
                            "status": "BOOKED"
                        }).execute()

                        booking_id = booking_resp.data[0]["booking_id"]
                        amount = float(selected_event["price"]) * seats

                        # Auto create payment entry
                        supabase.table("payments").insert({
                            "booking_id": booking_id,
                            "amount": amount,
                            "method": "PENDING",
                            "status": "PENDING"
                        }).execute()

                        st.success(f"✅ {seats} seats booked for {selected_event['title']}. Payment pending: ₹{amount}")
                    else:
                        st.error(f"⚠️ Only {available} seats left. Cannot book {seats} seats.")
        else:
            st.warning("Please add customers and events first.")
    except Exception as e:
        st.error(f"Error booking event: {e}")

elif choice == "View Bookings":
    st.subheader("All Bookings")
    try:
        bookings = supabase.table("bookings").select("*").execute()
        st.dataframe(bookings.data)
    except Exception as e:
        st.error(f"Error fetching bookings: {e}")

elif choice == "Cancel Booking":
    st.subheader("Cancel Booking")
    try:
        bookings = supabase.table("bookings").select("*").eq("status", "BOOKED").execute()
        if bookings.data:
            booking_list = {b["booking_id"]: f"Cust {b['cust_id']} - Event {b['event_id']} ({b['seats']} seats)" for b in bookings.data}
            booking_id = st.selectbox("Select Booking", list(booking_list.keys()), format_func=lambda x: booking_list[x])

            if st.button("Cancel Booking"):
                supabase.table("bookings").update({
                    "status": "CANCELLED"
                }).eq("booking_id", booking_id).execute()

                supabase.table("payments").update({
                    "status": "REFUNDED"
                }).eq("booking_id", booking_id).execute()

                st.warning("🚫 Booking cancelled and payment marked REFUNDED.")
        else:
            st.info("No active bookings to cancel.")
    except Exception as e:
        st.error(f"Error cancelling booking: {e}")

# ---------------- PAYMENTS ----------------
elif choice == "Payments":
    st.subheader("Payments")
    try:
        payments = supabase.table("payments").select("*").execute()
        if payments.data:
            st.dataframe(payments.data)

            payment_ids = {p["payment_id"]: f"Booking {p['booking_id']} - ₹{p['amount']} ({p['status']})"
                           for p in payments.data}
            payment_id = st.selectbox("Select Payment", list(payment_ids.keys()), format_func=lambda x: payment_ids[x])
            method = st.selectbox("Payment Method", ["Cash", "Card", "UPI"])
            if st.button("Mark as Paid"):
                supabase.table("payments").update({
                    "method": method,
                    "status": "PAID"
                }).eq("payment_id", payment_id).execute()
                st.success("✅ Payment updated successfully!")
        else:
            st.info("No payments found.")
    except Exception as e:
        st.error(f"Error fetching payments: {e}")

