import streamlit as st
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from datetime import date

# ---------------- SUPABASE SETUP ----------------
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="🎟️ Event Management Website",
    page_icon="🎉",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
/* Background gradient */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #e0f7fa, #e1bee7);
    font-family: 'Segoe UI', sans-serif;
}

/* Tabs customization */
.css-1kyxreq.edgvbvh3 {  /* Streamlit tab container */
    background-color: #6a1b9a !important;
    color: white !important;
}
.css-1kyxreq.edgvbvh3 button {
    background-color: #6a1b9a;
    color: #fff;
    font-weight: bold;
    border-radius: 8px;
    margin: 3px;
    padding: 8px 15px;
    transition: 0.3s;
}
.css-1kyxreq.edgvbvh3 button:hover {
    background-color: #7b1fa2;
    color: #ffeb3b;
}

/* Titles */
h1 {
    color: #4a148c;
    text-align: center;
    font-weight: bold;
}
h2 {
    color: #6a1b9a;
    font-weight: bold;
}

/* Buttons */
.stButton>button {
    background-color: #ff4081;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    padding: 8px 20px;
    margin: 5px 0;
    transition: 0.3s;
}
.stButton>button:hover {
    background-color: #f50057;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- PAGE TITLE ----------------
st.title("🎉 Event Management Website")

# ---------------- TABS (TOP HORIZONTAL MENU) ----------------
tabs = ["Add Customer", "View Customers", "Add Event", "View Events", "Delete Event",
        "Book Event", "View Bookings", "Cancel Booking", "Payments"]

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs(tabs)

# ---------------- ADD CUSTOMER ----------------
with tab1:
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

# ---------------- VIEW CUSTOMERS ----------------
with tab2:
    st.subheader("All Customers")
    try:
        customers = supabase.table("customers").select("*").execute()
        st.dataframe(customers.data)
    except Exception as e:
        st.error(f"Error fetching customers: {e}")

# ---------------- ADD EVENT ----------------
with tab3:
    st.subheader("Add Event")
    title = st.text_input("Event Title", key="event_title")
    date_input = st.date_input("Event Date", min_value=date.today(), key="event_date")
    location = st.text_input("Location", key="event_location")
    capacity = st.number_input("Capacity", min_value=1, step=1, key="event_capacity")
    price = st.number_input("Price (₹)", min_value=0.0, step=0.01, format="%.2f", key="event_price")
    if st.button("Save Event"):
        try:
            supabase.table("events").insert({
                "title": title,
                "date": str(date_input),
                "location": location,
                "capacity": int(capacity),
                "price": float(price)
            }).execute()
            st.success(f"✅ Event '{title}' added successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- VIEW EVENTS ----------------
with tab4:
    st.subheader("All Events")
    try:
        events = supabase.table("events").select("*").execute()
        st.dataframe(events.data)
    except Exception as e:
        st.error(f"Error fetching events: {e}")

# ---------------- DELETE EVENT ----------------
with tab5:
    st.subheader("Delete Event")
    try:
        events = supabase.table("events").select("*").execute()
        if events.data:
            event_list = {e["event_id"]: e["title"] for e in events.data}
            event_id = st.selectbox("Select Event", list(event_list.keys()), format_func=lambda x: event_list[x])
            if st.button("Delete Event"):
                bookings = supabase.table("bookings").select("*").eq("event_id", event_id).execute()
                if bookings.data:
                    for b in bookings.data:
                        payments = supabase.table("payments").select("*").eq("booking_id", b["booking_id"]).execute()
                        if payments.data:
                            for p in payments.data:
                                if p["status"] == "PAID":
                                    supabase.table("payments").update({"status": "REFUNDED"}).eq("payment_id", p["payment_id"]).execute()
                                supabase.table("payments").delete().eq("payment_id", p["payment_id"]).execute()
                    supabase.table("bookings").delete().eq("event_id", event_id).execute()
                supabase.table("events").delete().eq("event_id", event_id).execute()
                st.warning(f"🗑️ Event '{event_list[event_id]}' deleted. Bookings cancelled & payments refunded/deleted.")
        else:
            st.info("No events available.")
    except Exception as e:
        st.error(f"Error deleting event: {e}")

# ---------------- BOOK EVENT ----------------
with tab6:
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

# ---------------- VIEW BOOKINGS ----------------
with tab7:
    st.subheader("All Bookings")
    try:
        bookings = supabase.table("bookings").select("*").execute()
        st.dataframe(bookings.data)
    except Exception as e:
        st.error(f"Error fetching bookings: {e}")

# ---------------- CANCEL BOOKING ----------------
with tab8:
    st.subheader("Cancel Booking")
    try:
        bookings = supabase.table("bookings").select("*").eq("status", "BOOKED").execute()
        if bookings.data:
            booking_list = {b["booking_id"]: f"Cust {b['cust_id']} - Event {b['event_id']} ({b['seats']} seats)" for b in bookings.data}
            booking_id = st.selectbox("Select Booking to Cancel", list(booking_list.keys()), format_func=lambda x: booking_list[x])
            if st.button("Cancel Booking"):
                payments = supabase.table("payments").select("*").eq("booking_id", booking_id).execute()
                if payments.data:
                    for p in payments.data:
                        if p["status"] == "PAID":
                            supabase.table("payments").update({"status": "REFUNDED"}).eq("payment_id", p["payment_id"]).execute()
                        supabase.table("payments").delete().eq("payment_id", p["payment_id"]).execute()
                supabase.table("bookings").update({"status": "CANCELLED"}).eq("booking_id", booking_id).execute()
                st.warning("Booking cancelled & payment refunded if paid.")
        else:
            st.info("No active bookings to cancel.")
    except Exception as e:
        st.error(f"Error cancelling booking: {e}")

# ---------------- PAYMENTS ----------------
with tab9:
    st.subheader("Payments")
    try:
        payments = supabase.table("payments").select("*").execute()
        st.dataframe(payments.data)
    except Exception as e:
        st.error(f"Error fetching payments: {e}")
