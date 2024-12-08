import streamlit as st
import pandas as pd
from db import SessionLocal
import crud
from datetime import datetime
from streamlit_navigation_bar import st_navbar

db = SessionLocal()

navbar = ["Home", "Manage Events", "View Events", "Buy Tickets"]

styles = {
    "active": {"color": "#FF4B4B", "border-bottom": "2px solid #FF4B4B"}
}

selected_option = st_navbar(navbar, styles=styles)


if selected_option == "Home":
    st.title("Welcome to Nihar's event planner!")
    st.header("You can create events, see future events, and buy tickets!")

if selected_option == "Manage Events":

    # RESET DATA
    if st.button("Reset All Data"):
        crud.reset_database()
        st.success("All data has been reset!")

    # CREATE EVENTS
    st.header("Create Events")
    event_name = st.text_input("Event Name")
    event_date = st.date_input("Event Date")
    event_time = st.time_input("Event Time")
    venue_name = st.text_input("Venue Name")
    event_tickets = st.number_input("Total Tickets", min_value=1)
    event_price = st.number_input("Ticket Price", min_value=1.0, format="%.2f", step=1.00)
    event_type = st.selectbox("Event Type", ["Concert", "Fundraiser", "Social Event", "Other"])

    if st.button("Create Event"):

        event = crud.create_event(db,
                                  name=event_name,
                                  date=event_date,
                                  time=str(event_time),
                                  venue_name=venue_name,
                                  total_tickets=int(event_tickets),
                                  price=float(event_price),
                                  event_type=event_type)
        st.success(f"Event {event.name} created!")

    # UPDATE EVENTS
    st.header("Update Events")
    events = crud.get_all_events(db)

    if events:
        event_options = {event.name: event for event in events}
        selected_event_name = st.selectbox("Select Event to Update",
                                            options=list(event_options.keys()),
                                            key="update_select")

        selected_event = event_options[selected_event_name]

        event_name = st.text_input("Event Name",
                                    value=selected_event.name,
                                    key="update_name")
        event_date = st.date_input("Event Date",
                                    value=selected_event.date.date(),
                                    key="update_date")
        event_time = st.time_input("Event Time",
                                       value=datetime.strptime(selected_event.time, '%H:%M:%S').time(),
                                       key="update_time")
        venue_name = st.text_input("Venue Name",
                                       value=selected_event.venue_name,
                                       key="update_venue")
        event_tickets = st.number_input("Total Tickets",
                                            min_value=0,
                                            value=selected_event.total_tickets,
                                            key="update_tickets")
        event_price = st.number_input("Ticket Price",
                                          min_value=1.0,
                                          value=float(selected_event.price),
                                          format="%.2f",
                                          step=1.00,
                                          key="update_price")
        event_type = st.selectbox("Event Type",
                                      ["Concert", "Fundraiser", "Social Event", "Other"],
                                      index=["Concert", "Fundraiser", "Social Event", "Other"].index(
                                          selected_event.event_type),
                                      key="update_type")

        if st.button("Update Event"):
            updated_event = crud.update_event(
                    db,
                    event_id=selected_event.id,
                    name=event_name,
                    date=event_date,
                    time=str(event_time),
                    venue_name=venue_name,
                    total_tickets=int(event_tickets),
                    price=float(event_price),
                    event_type=event_type
                )
            if updated_event:
                    st.success(f"Event {updated_event.name} updated successfully!")
            else:
                    st.error("Failed to update event!")
    else:
        st.write("No events available to update.")

    # DELETE EVENT
    st.header("Delete Events")
    events = crud.get_all_events(db)
    if events:
        event_options = {event.name: event.id for event in events}
        selected_event_name = st.selectbox("Select Event to Delete", options=list(event_options.keys()))

        if st.button("Delete Event"):
            event_id_to_delete = event_options[selected_event_name]
            crud.delete_event(db, event_id=event_id_to_delete)
            st.rerun()
    else:
        st.write("No events available to delete.")

elif selected_option == "View Events":
    st.header("View Events")
    events = crud.get_all_events(db)

    view_option = st.radio("Select View Option", options=["View All Events", "Filter Events"])

    if view_option == "Filter Events":
        search_date = st.date_input("Event Date", value=pd.to_datetime('today'))

        max_price = st.number_input("Max Ticket Price", min_value=0.0, step=1.00, format="%.2f")

        event_types = ["Concert", "Fundraiser", "Social Event", "Other"]
        selected_event_types = st.multiselect("Event Type", event_types, default=[])

        filtered_events = [
            event for event in events
            if event.date.date() == search_date
               and event.price <= max_price
               and event.event_type in selected_event_types
        ]

        if filtered_events:
            average_price = sum(event.price for event in filtered_events) / len(filtered_events)

            event_data = [{
                "Name": event.name,
                "Date": event.date.strftime('%Y-%m-%d'),
                "Time": event.time,
                "Venue": event.venue_name,
                "Price": f"${event.price:.2f}",
                "Type": event.event_type,
                "Sold Out": "Yes" if event.total_tickets == 0 else "No"
            } for event in filtered_events]

            event_df = pd.DataFrame(event_data)
            st.dataframe(event_df, use_container_width=True, hide_index=True)
            st.write(f"Average ticket price for filtered events: ${average_price:.2f}")
        else:
            st.write("No filtered events found.")

    else:
        if events:
            average_price = sum(event.price for event in events) / len(events)
            event_data = [{
                    "Name": event.name,
                    "Date": event.date.strftime('%Y-%m-%d'),
                    "Time": event.time,
                    "Venue": event.venue_name,
                    "Price": f"${event.price:.2f}",
                    "Type": event.event_type,
                    "Sold Out": "Yes" if event.total_tickets == 0 else "No"}
                for event in events]

            event_df = pd.DataFrame(event_data)
            st.dataframe(event_df, use_container_width=True, hide_index=True)
            st.write(f"Average ticket price for all events: ${average_price:.2f}")
        else:
            st.write("No events found.")

elif selected_option == "Buy Tickets":
    st.title("Buy Tickets")

    events = crud.get_available_events(db)

    if events:
        event_options = {f"{event.name}": event.id for event in events}
        selected_event_text = st.selectbox("Select Event", options=list(event_options.keys()))
        selected_event_id = event_options[selected_event_text]

        num_tickets = st.number_input("Number of Tickets", min_value=1, value=1)

        selected_event = next(event for event in events if event.id == selected_event_id)
        total_cost = selected_event.price * num_tickets

        ticket_info = pd.DataFrame({
            'Remaining Tickets': [selected_event.total_tickets],
            'Total Cost': [f'${total_cost:.2f}']
        })

        st.dataframe(ticket_info, hide_index=True)

        if st.button("Buy Tickets"):
            available_tickets = selected_event.total_tickets

            if num_tickets <= available_tickets:
                ticket = crud.buy_ticket(db, event_id=selected_event_id, num_tickets=num_tickets)
                st._set_query_params(updated="true")
                st.success(f"{num_tickets} ticket(s) successfully purchased for {selected_event.name}!")
            else:
                st.error("Not enough tickets available for this event.")
    else:
        st.write("No available events to display.")


db.close()
