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
st.set_page_config(page_title="Event Management System", page_icon="🎉", layout="centered")

st.title("🎉 Event Management System")
menu = ["Add Event", "View Events", "Update Event", "Delete Event"]
choice = st.sidebar.selectbox("Menu", menu)

# --- Add Event ---
if choice == "Add Event":
    st.subheader("Add New Event")
    name = st.text_input("Event Name")
    date = st.date_input("Event Date")
    location = st.text_input("Location")
    description = st.text_area("Description")

    if st.button("Save Event"):
        if name and location:
            data = {
                "name": name,
                "date": str(date),
                "location": location,
                "description": description
            }
            supabase.table("events").insert(data).execute()
            st.success(f"✅ Event '{name}' added successfully!")
        else:
            st.error("⚠️ Event Name and Location are required!")

# --- View Events ---
elif choice == "View Events":
    st.subheader("All Events")
    events = supabase.table("events").select("*").execute()
    if events.data:
        st.table(events.data)
    else:
        st.info("No events found.")

# --- Update Event ---
elif choice == "Update Event":
    st.subheader("Update Event")
    events = supabase.table("events").select("*").execute()
    if events.data:
        event_list = {e["id"]: e["name"] for e in events.data}
        event_id = st.selectbox("Select Event to Update", list(event_list.keys()), format_func=lambda x: event_list[x])

        selected_event = next((e for e in events.data if e["id"] == event_id), None)
        if selected_event:
            name = st.text_input("Event Name", selected_event["name"])
            date = st.date_input("Event Date")
            location = st.text_input("Location", selected_event["location"])
            description = st.text_area("Description", selected_event.get("description", ""))

            if st.button("Update Event"):
                supabase.table("events").update({
                    "name": name,
                    "date": str(date),
                    "location": location,
                    "description": description
                }).eq("id", event_id).execute()
                st.success("✅ Event updated successfully!")
    else:
        st.info("No events available for update.")

# --- Delete Event ---
elif choice == "Delete Event":
    st.subheader("Delete Event")
    events = supabase.table("events").select("*").execute()
    if events.data:
        event_list = {e["id"]: e["name"] for e in events.data}
        event_id = st.selectbox("Select Event to Delete", list(event_list.keys()), format_func=lambda x: event_list[x])

        if st.button("Delete Event"):
            supabase.table("events").delete().eq("id", event_id).execute()
            st.warning("🗑️ Event deleted successfully!")
    else:
        st.info("No events available for deletion.")

