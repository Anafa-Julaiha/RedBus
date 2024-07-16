
import psycopg2
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

DATABASE_URL = "postgresql://postgres:1234@localhost/redbus"

# Create an engine for SQLAlchemy
engine = create_engine(DATABASE_URL)

# Step 2: Fetch data from the database
def fetch_data():
    query = "SELECT * FROM bus_details"  # Adjust the query as needed
    return pd.read_sql(query, engine)

# Load the data
data = fetch_data()

# Ensure departing_time is properly recognized as datetime
data['departing_time'] = pd.to_datetime(data['departing_time'], format='%H:%M:%S').dt.time

data.drop('bus_route_link', axis=1, inplace=True)
routes = data['bus_route_name'].unique()
bus = data['bus_type'].unique()
depart = data['departing_time'].unique()

# Function to create time ranges
def create_time_ranges(data):
    time_ranges = []
    for hour in range(24):
        time_ranges.append(f"{hour:02}:00 - {hour:02}:59")
    return time_ranges

time_ranges = create_time_ranges(data)

# Define each page as a function
def home_page():
    st.title("Home")
    st.write("Welcome to the Home Page")

def bus_page():
    st.markdown(
        """
        <h1 style='text-align: center;'>Bus Details</h1>
        """,
        unsafe_allow_html=True
    )
    st.subheader("Welcome to the Bus Details")
    col1, col_space, col2 = st.columns([1, 0.2, 1])
    with col1:
        bus_route = st.selectbox('Select Route', options=['All'] + list(routes))
        star = st.select_slider(
            "Select the Star Rating:",
            options=[5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1, 0.5, 0, 'All'],
            value='All')
        time = st.selectbox("Select the Departing Time", options=['All'] + time_ranges)
        
    with col2:
        bus_type = st.selectbox("Select the A/C Type:",
                     options=['All', 'A/C', 'Non A/C'])
        seat_type = st.selectbox("Select the Seat Type:",
                                 options=['All', 'Seater', 'Sleeper'])

        apply = st.button("**Apply**")
        reset = st.button("**Reset**")
    
    if apply:
        filtering = data.copy()
        if bus_route != 'All':
            filtering = filtering[filtering['bus_route_name'] == bus_route]
        if star != 'All':
            filtering = filtering[filtering['star_rating'] == float(star)]
        if bus_type != 'All':
            filtering = filtering[filtering['bus_type'].str.contains(bus_type, case=False)]
        if seat_type != 'All':
            filtering = filtering[filtering['bus_type'].str.contains(seat_type, case=False)]
        if time != 'All':
            start_hour = int(time[:2])
            end_hour = start_hour + 1
            filtering = filtering[(filtering['departing_time'] >= pd.to_datetime(f'{start_hour:02}:00:00', format='%H:%M:%S').time()) &
                                  (filtering['departing_time'] <= pd.to_datetime(f'{end_hour:02}:59:59', format='%H:%M:%S').time())]
        
        st.dataframe(filtering)
    else:
        st.dataframe(data)

    if reset:
        bus_route = 'All'
        star = 'All'
        bus_type = 'All'
        seat_type = 'All'
        time = 'All'
    
with st.sidebar: 
    selected = option_menu(
        menu_title="Main Menu", 
        options=["Home", "Bus Details"]
    )

# Display the selected page
if selected == "Bus Details":
    bus_page()
elif selected == "Home":
    home_page()
