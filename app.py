import streamlit as st
from datetime import datetime
from src.config import get_supabase

# Initialize Supabase client
supabase = get_supabase()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Event Management Website",
    page_icon="🎫",  # Decent ticket icon
    layout="wide"
)

# ---------------- CSS STYLES ----------------
st.markdown("""
<style>
/* Top horizontal menu styling */
div[data-baseweb="tab-list"] button {
    background-color: #4CAF50 !important;
    color: white !important;
    font-weight: bold;
}
div[data-baseweb="tab-list"] button:hover {
    background-color: #45a049 !important;
}
/* Colored horizontal line under header */
hr.stHorizontal {
    border: 2px solid #4CAF50;
}
/* Success & error message styling */
div.stAlert {
    border-radius: 10px;
    padding: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.title("🎫 Event Management System")
st.markdown("---", unsafe_allow_html=True)

# ---------------- TOP HORIZONTAL TABS ----------------
tabs = st.tabs(["Customers", "Events", "Book Event", "Bookings", "Payments", "Reports"])

# ---------------- CUSTOMERS ----------------
with tabs[0]:
    st.subheader("Customers")
    try:
        cust_resp = supabase.table("customers").select("*").execute()
        customers = cust_resp.data if cust_resp.data else []
        # Add Customer
        with st.form("add_customer"):
            st.write("Add New Customer")
            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            city = st.text_input("City")
            submitted = st.form_submit_button("Add Customer")
            if submitted:
                # Check email uniqueness
                existing = supabase.table("customers").select("*").eq("email", email).execute()
                if existing.data:
                    st.error("Email already exists!")
                else:
                    supabase.table("customers").insert({
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "city": city
                    }).execute()
                    st.success(f"Customer {name} added successfully!")

        # List Customers
        st.write("Customer List")
        for c in customers:
            st.write(f"{c['cust_id']}: {c['name']} - {c['email']} - {c['city']}")

    except Exception as e:
        st.error(f"Error loading customers: {e}")

# ---------------- EVENTS ----------------
with tabs[1]:
    st.subheader("Events")
    try:
        event_resp = supabase.table("events").select("*").execute()
        events = event_resp.data if event_resp.data else []

        # Add Event
        with st.form("add_event"):
            st.write("Add New Event")
            title = st.text_input("Title")
            date = st.date_input("Date")
            location = st.text_input("Location")
            capacity = st.number_input("Capacity", min_value=1, step=1)
            price = st.number_input("Price", min_value=0.0, step=0.01)
            submitted = st.form_submit_button("Add Event")
            if submitted:
                supabase.table("events").insert({
                    "title": title,
                    "date": date.strftime("%Y-%m-%d"),
                    "location": location,
                    "capacity": capacity,
                    "price": price
                }).execute()
                st.success(f"Event '{title}' added successfully!")

        # List & Delete Event
        st.write("Event List")
        for e in events:
            col1, col2 = st.columns([4,1])
            col1.write(f"{e['event_id']}: {e['title']} - {e['date']} - Seats: {e['capacity']} - Price: ₹{e['price']}")
            if col2.button(f"Delete {e['title']}", key=f"del_{e['event_id']}"):
                try:
                    # Get bookings for event
                    bookings_resp = supabase.table("bookings").select("*").eq("event_id", e['event_id']).execute()
                    bookings = bookings_resp.data if bookings_resp.data else []
                    # Refund payments
                    for b in bookings:
                        payment_resp = supabase.table("payments").select("*").eq("booking_id", b['booking_id']).execute()
                        payments = payment_resp.data if payment_resp.data else []
                        for p in payments:
                            if p["status"] != "REFUNDED":
                                supabase.table("payments").update({"status": "REFUNDED"}).eq("payment_id", p["payment_id"]).execute()
                    # Delete bookings
                    for b in bookings:
                        supabase.table("bookings").delete().eq("booking_id", b['booking_id']).execute()
                    # Delete event
                    supabase.table("events").delete().eq("event_id", e['event_id']).execute()
                    st.success(f"Event '{e['title']}' deleted and payments refunded if applicable.")
                except Exception as err:
                    st.error(f"Error deleting event: {err}")

    except Exception as e:
        st.error(f"Error loading events: {e}")

# ---------------- BOOK EVENT ----------------
with tabs[2]:
    st.subheader("Book Event")
    try:
        # Fetch customers and events
        customers_resp = supabase.table("customers").select("*").execute()
        events_resp = supabase.table("events").select("*").execute()

        if customers_resp.data and events_resp.data:
            cust_list = {c["cust_id"]: c["name"] for c in customers_resp.data}
            event_list = {e["event_id"]: e["title"] for e in events_resp.data}

            cust_id = st.selectbox("Select Customer", list(cust_list.keys()), format_func=lambda x: cust_list[x])
            event_id = st.selectbox("Select Event", list(event_list.keys()), format_func=lambda x: event_list[x])
            seats = st.number_input("Number of Seats", min_value=1, step=1)

            if st.button("Book Tickets"):
                # Get selected event details
                selected_event = next((e for e in events_resp.data if e["event_id"] == event_id), None)
                if selected_event:
                    # Calculate total seats already booked
                    booked_resp = supabase.table("bookings").select("seats").eq("event_id", event_id).execute()
                    total_booked = sum([b["seats"] for b in booked_resp.data]) if booked_resp.data else 0

                    available = selected_event["capacity"] - total_booked

                    if seats <= available:
                        # Insert booking
                        booking_resp = supabase.table("bookings").insert({
                            "cust_id": cust_id,
                            "event_id": event_id,
                            "seats": seats,
                            "status": "BOOKED"
                        }).execute()
                        booking_id = booking_resp.data[0]["booking_id"]

                        # Create pending payment
                        amount = float(selected_event["price"]) * seats
                        supabase.table("payments").insert({
                            "booking_id": booking_id,
                            "amount": amount,
                            "method": "PENDING",
                            "status": "PENDING"
                        }).execute()

                        st.success(f"✅ {seats} seats booked for '{selected_event['title']}'! Payment pending: ₹{amount}")
                    else:
                        st.error(f"⚠️ Only {available} seats left. Cannot book {seats} seats.")
        else:
            st.warning("Please add customers and events first.")

    except Exception as e:
        st.error(f"Error booking event: {e}")

# ---------------- BOOKINGS ----------------
with tabs[3]:
    st.subheader("Bookings")
    try:
        bookings_resp = supabase.table("bookings").select("*").execute()
        bookings = bookings_resp.data if bookings_resp.data else []
        for b in bookings:
            col1, col2 = st.columns([5,1])
            customer = supabase.table("customers").select("*").eq("cust_id", b['cust_id']).execute().data[0]
            event = supabase.table("events").select("*").eq("event_id", b['event_id']).execute().data[0]
            col1.write(f"Booking {b['booking_id']}: {customer['name']} -> {event['title']} ({b['seats']} seats) - Status: {b['status']}")
            if col2.button(f"Cancel {b['booking_id']}", key=f"cancel_{b['booking_id']}"):
                try:
                    supabase.table("bookings").update({"status": "CANCELLED"}).eq("booking_id", b['booking_id']).execute()
                    # Refund payment
                    supabase.table("payments").update({"status": "REFUNDED"}).eq("booking_id", b['booking_id']).execute()
                    st.success(f"Booking {b['booking_id']} cancelled and payment refunded.")
                except Exception as err:
                    st.error(f"Error cancelling booking: {err}")
    except Exception as e:
        st.error(f"Error loading bookings: {e}")

# ---------------- PAYMENTS ----------------
with tabs[4]:
    st.subheader("Payments")
    try:
        payments_resp = supabase.table("payments").select("*").execute()
        payments = payments_resp.data if payments_resp.data else []
        for p in payments:
            booking = supabase.table("bookings").select("*").eq("booking_id", p['booking_id']).execute().data[0]
            event = supabase.table("events").select("*").eq("event_id", booking['event_id']).execute().data[0]
            customer = supabase.table("customers").select("*").eq("cust_id", booking['cust_id']).execute().data[0]
            st.write(f"Payment {p['payment_id']}: {customer['name']} -> {event['title']} - ₹{p['amount']} - Status: {p['status']}")
    except Exception as e:
        st.error(f"Error loading payments: {e}")

# ---------------- REPORTS ----------------
with tabs[5]:
    st.subheader("Reports")
    try:
        # Top selling events
        bookings_resp = supabase.table("bookings").select("*").execute()
        bookings = bookings_resp.data if bookings_resp.data else []
        event_count = {}
        for b in bookings:
            event_count[b['event_id']] = event_count.get(b['event_id'], 0) + b['seats']
        top_events = sorted(event_count.items(), key=lambda x: x[1], reverse=True)[:5]
        st.write("Top Selling Events:")
        for eid, seats_sold in top_events:
            event = supabase.table("events").select("*").eq("event_id", eid).execute().data[0]
            st.write(f"{event['title']} - Seats Sold: {seats_sold}")

        # Total revenue last month
        revenue = 0.0
        last_month = datetime.now().replace(day=1)
        for b in bookings:
            event = supabase.table("events").select("*").eq("event_id", b['event_id']).execute().data[0]
            revenue += b['seats'] * float(event['price'])
        st.write(f"Total Revenue (approx): ₹{revenue}")

    except Exception as e:
        st.error(f"Error generating reports: {e}")
