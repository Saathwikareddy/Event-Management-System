import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Streamlit UI
st.set_page_config(page_title="Event Management System", page_icon="🎉", layout="wide")
st.title("🎉 Event Management System")

menu = ["Customers", "Events", "Bookings", "Payments"]
choice = st.sidebar.selectbox("Menu", menu)

# -------------------- CUSTOMERS --------------------
if choice == "Customers":
    st.header("👥 Manage Customers")
    sub_menu = st.radio("Select Action", ["Add Customer", "View Customers"])

    if sub_menu == "Add Customer":
        name = st.text_input("Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        city = st.text_input("City")

        if st.button("Save Customer"):
            if name and email:
                try:
                    supabase.table("customers").insert({
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "city": city
                    }).execute()
                    st.success(f"✅ Customer '{name}' added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("⚠️ Name and Email are required!")

    elif sub_menu == "View Customers":
        try:
            customers = supabase.table("customers").select("*").execute()
            st.dataframe(customers.data)
        except Exception as e:
            st.error(f"Error fetching customers: {e}")

# -------------------- EVENTS --------------------
elif choice == "Events":
    st.header("📅 Manage Events")
    sub_menu = st.radio("Select Action", ["Add Event", "View Events", "Update Event", "Delete Event"])

    if sub_menu == "Add Event":
        title = st.text_input("Event Title")
        date = st.date_input("Event Date")
        location = st.text_input("Location")
        capacity = st.number_input("Capacity", min_value=1, step=1)
        price = st.number_input("Price (₹)", min_value=0.0, step=0.01, format="%.2f")

        if st.button("Save Event"):
            if title and date and capacity and price is not None:
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
            else:
                st.error("⚠️ Title, Date, Capacity, and Price required!")

    elif sub_menu == "View Events":
        try:
            events = supabase.table("events").select("*").execute()
            st.dataframe(events.data)
        except Exception as e:
            st.error(f"Error fetching events: {e}")

    elif sub_menu == "Update Event":
        events = supabase.table("events").select("*").execute()
        if events.data:
            event_list = {e["event_id"]: e["title"] for e in events.data}
            event_id = st.selectbox("Select Event", list(event_list.keys()), format_func=lambda x: event_list[x])
            selected_event = next((e for e in events.data if e["event_id"] == event_id), None)

            if selected_event:
                title = st.text_input("Event Title", selected_event["title"])
                date = st.date_input("Event Date")
                location = st.text_input("Location", selected_event["location"])
                capacity = st.number_input("Capacity", min_value=1, step=1, value=selected_event["capacity"])
                price = st.number_input("Price (₹)", min_value=0.0, step=0.01, format="%.2f", value=float(selected_event["price"]))

                if st.button("Update Event"):
                    try:
                        supabase.table("events").update({
                            "title": title,
                            "date": str(date),
                            "location": location,
                            "capacity": int(capacity),
                            "price": float(price)
                        }).eq("event_id", event_id).execute()
                        st.success("✅ Event updated successfully!")
                    except Exception as e:
                        st.error(f"Error updating event: {e}")

    elif sub_menu == "Delete Event":
        events = supabase.table("events").select("*").execute()
        if events.data:
            event_list = {e["event_id"]: e["title"] for e in events.data}
            event_id = st.selectbox("Select Event", list(event_list.keys()), format_func=lambda x: event_list[x])
            if st.button("Delete Event"):
                try:
                    supabase.table("events").delete().eq("event_id", event_id).execute()
                    st.warning("🗑️ Event deleted successfully!")
                except Exception as e:
                    st.error(f"Error deleting event: {e}")

# -------------------- BOOKINGS --------------------
elif choice == "Bookings":
    st.header("🎟️ Manage Bookings")
    sub_menu = st.radio("Select Action", ["Add Booking", "View Bookings"])

    if sub_menu == "Add Booking":
        customers = supabase.table("customers").select("*").execute()
        events = supabase.table("events").select("*").execute()

        if customers.data and events.data:
            cust_dict = {c["cust_id"]: c["name"] for c in customers.data}
            event_dict = {e["event_id"]: e["title"] for e in events.data}

            cust_id = st.selectbox("Select Customer", list(cust_dict.keys()), format_func=lambda x: cust_dict[x])
            event_id = st.selectbox("Select Event", list(event_dict.keys()), format_func=lambda x: event_dict[x])
            seats = st.number_input("Seats", min_value=1, step=1)

            if st.button("Book Seats"):
                try:
                    supabase.table("bookings").insert({
                        "cust_id": cust_id,
                        "event_id": event_id,
                        "seats": seats,
                        "status": "BOOKED"
                    }).execute()
                    st.success("✅ Booking created successfully!")
                except Exception as e:
                    st.error(f"Error booking: {e}")

    elif sub_menu == "View Bookings":
        try:
            bookings = supabase.table("bookings").select("*").execute()
            st.dataframe(bookings.data)
        except Exception as e:
            st.error(f"Error fetching bookings: {e}")

# -------------------- PAYMENTS --------------------
elif choice == "Payments":
    st.header("💳 Manage Payments")
    sub_menu = st.radio("Select Action", ["Add Payment", "View Payments"])

    if sub_menu == "Add Payment":
        bookings = supabase.table("bookings").select("*").execute()
        if bookings.data:
            booking_dict = {b["booking_id"]: f"Booking {b['booking_id']} (Cust {b['cust_id']}, Event {b['event_id']})"
                            for b in bookings.data}

            booking_id = st.selectbox("Select Booking", list(booking_dict.keys()), format_func=lambda x: booking_dict[x])
            amount = st.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
            method = st.selectbox("Payment Method", ["Cash", "Card", "UPI"])
            status = st.selectbox("Status", ["PENDING", "PAID"])

            if st.button("Save Payment"):
                try:
                    supabase.table("payments").insert({
                        "booking_id": booking_id,
                        "amount": float(amount),
                        "method": method,
                        "status": status
                    }).execute()
                    st.success("✅ Payment recorded successfully!")
                except Exception as e:
                    st.error(f"Error saving payment: {e}")

    elif sub_menu == "View Payments":
        try:
            payments = supabase.table("payments").select("*").execute()
            st.dataframe(payments.data)
        except Exception as e:
            st.error(f"Error fetching payments: {e}")

