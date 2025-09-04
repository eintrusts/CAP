# mahacap.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin Password
# ---------------------------
ADMIN_PASSWORD = "eintrust2025"

# ---------------------------
# Data Files for Persistence
# ---------------------------
DATA_FILE = "cities_data.csv"
CAP_DATA_FILE = "cap_raw_data.csv"

# ---------------------------
# Cities and Districts
# ---------------------------
cities_districts = {
    "Mumbai": "Mumbai",
    "Kalyan-Dombivli": "Thane",
    "Mira-Bhayandar": "Thane",
    "Navi Mumbai": "Thane",
    "Bhiwandi": "Thane",
    "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane",
    "Vasai-Virar": "Thane",
    "Thane": "Thane",
    "Badlapur Council": "Thane",
    "Pune": "Pune",
    "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad",
    "Raigad Council": "Raigad",
    "Malegaon": "Nashik",
    "Nashik": "Nashik",
    "Nandurbar Council": "Nandurbar",
    "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon",
    "Dhule": "Dhule",
    "Ahmednagar": "Ahmednagar",
    "Aurangabad": "Aurangabad",
    "Jalna": "Jalna",
    "Beed Council": "Beed",
    "Satara Council": "Satara",
    "Sangli-Miraj-Kupwad": "Sangli",
    "Kolhapur": "Kolhapur",
    "Ichalkaranji": "Kolhapur",
    "Solapur": "Solapur",
    "Barshi Council": "Solapur",
    "Nanded-Waghala": "Nanded",
    "Yawatmal Council": "Yawatmal",
    "Osmanabad Council": "Osmanabad",
    "Latur": "Latur",
    "Udgir Coucil": "Latur",
    "Akola": "Akola",
    "Parbhani Council": "Parbhani",
    "Amravati": "Amravati",
    "Achalpur Council": "Amravati",
    "Wardha Coumcil": "Wardha",
    "Hinganghat Ciuncil": "Wardha",
    "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State Initialization
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"

# Load city data
if os.path.exists(DATA_FILE):
    st.session_state.data = pd.read_csv(DATA_FILE)
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Department Email"
    ])

# Load CAP raw data
if os.path.exists(CAP_DATA_FILE):
    st.session_state.cap_data = pd.read_csv(CAP_DATA_FILE)
else:
    st.session_state.cap_data = pd.DataFrame()

# ---------------------------
# Helper Functions
# ---------------------------
def get_val(row: pd.Series, target: str, default="—"):
    return row[target] if target in row and pd.notna(row[target]) else default

def format_population(num):
    if pd.isna(num) or num == "":
        return "—"
    return "{:,}".format(int(num))

# ---------------------------
# Admin Login
# ---------------------------
def admin_login():
    with st.form("login_form"):
        password = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Admin login successful")
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

st.sidebar.markdown(
    """
    <style>
    .css-1d391kg button { 
        background-color: #228B22 !important; 
        color: white !important; 
        width: 100%;
        margin-bottom: 5px;
        height: 40px;
        font-size: 16px;
        border-radius: 5px;
    }
    .css-1d391kg button:hover { 
        background-color: #196619 !important; 
        color: white !important; 
    }
    </style>
    """, unsafe_allow_html=True
)

if st.sidebar.button("Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("City Dashboard"):
    st.session_state.menu = "City Dashboard"
if st.sidebar.button("Admin Panel"):
    st.session_state.menu = "Admin Panel"
if st.session_state.authenticated:
    if st.sidebar.button("CAP Preparation"):
        st.session_state.menu = "CAP Preparation"

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra CAP Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")

    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        total_cities = df.shape[0]
        cities_done = df[df["CAP Status"] == "Completed"].shape[0]
        st.metric("Total Cities", total_cities)
        st.metric("Cities with CAP Completed", cities_done)

        if "GHG Emissions" in df.columns:
            fig2 = px.bar(df, x="City Name", y="GHG Emissions", title="GHG Emissions by City", text="GHG Emissions")
            st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        st.header("City Dashboard")
        st.markdown("View detailed information for each city.")

        city = st.selectbox("Select City", df["City Name"].dropna().unique())
        city_row = df[df["City Name"] == city].iloc[0]

        with st.expander("Basic Info", expanded=True):
            st.write(f"**District:** {get_val(city_row, 'District')}")
            st.write(f"**Population:** {format_population(get_val(city_row, 'Population'))}")
            st.write(f"**ULB Category:** {get_val(city_row, 'ULB Category')}")
            st.write(f"**CAP Status:** {get_val(city_row, 'CAP Status')}")

        with st.expander("Environment Department"):
            st.write(f"**Exists:** {get_val(city_row, 'Environment Department Exist')}")
            st.write(f"**Dept Name:** {get_val(city_row, 'Department Name')}")
            st.write(f"**Head Name:** {get_val(city_row, 'Head Name')}")
            st.write(f"**Email:** {get_val(city_row, 'Department Email')}")

        # Last updated month/year
        if os.path.exists(DATA_FILE):
            last_updated = pd.to_datetime(os.path.getmtime(DATA_FILE), unit='s')
            st.markdown(f"*Last Updated: {last_updated.strftime('%B %Y')}*")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("Admin Panel")
        st.write("Add or update city data below.")

        df = st.session_state.data
        cities_list = list(cities_districts.keys())

        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list)
            district = st.text_input("District", value=cities_districts[city_name], disabled=True)

            population_val = df[df["City Name"]==city_name]["Population"].values[0] if city_name in df.get("City Name", []) else 0
            population = st.number_input("Population(as per 2011 census)", min_value=0, value=int(population_val), step=1000, format="%d")
            
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            
            ghg = st.text_input("GHG Emissions (MTCO2e)", df[df["City Name"]==city_name]["GHG Emissions"].values[0] if city_name in df.get("City Name", []) else "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"], index=0)
            dept_name = st.text_input("Department Name", df[df["City Name"]==city_name]["Department Name"].values[0] if city_name in df.get("City Name", []) else "")
            head_name = st.text_input("Head Name", df[df["City Name"]==city_name]["Head Name"].values[0] if city_name in df.get("City Name", []) else "")
            dept_email = st.text_input("Department Email", df[df["City Name"]==city_name]["Department Email"].values[0] if city_name in df.get("City Name", []) else "")

            submit = st.form_submit_button("Add/Update City")
            if submit:
                new_row = {
                    "City Name": city_name,
                    "District": district,
                    "Population": population,
                    "ULB Category": ulb_cat,
                    "CAP Status": cap_status,
                    "GHG Emissions": ghg,
                    "Environment Department Exist": env_exist,
                    "Department Name": dept_name,
                    "Head Name": head_name,
                    "Department Email": dept_email
                }

                if city_name in df.get("City Name", []):
                    idx = df[df["City Name"] == city_name].index[0]
                    df.loc[idx] = new_row
                    st.success(f"{city_name} updated successfully.")
                else:
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"{city_name} added successfully.")
                
                # Save data
                st.session_state.data = df
                df.to_csv(DATA_FILE, index=False)
                st.session_state.last_updated = pd.Timestamp.now()

# ---------------------------
# CAP Preparation
# ---------------------------
elif menu == "CAP Preparation":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("CAP Preparation - Raw Data Input")
        st.markdown("Enter detailed raw data to generate GHG Inventory and CAP.")

        df_cap = st.session_state.cap_data

        with st.form("cap_form"):
            city_name = st.selectbox("Select City", st.session_state.data["City Name"].dropna().unique())
            
            st.subheader("Energy Sector")
            energy_elec = st.number_input("Annual Electricity Consumption (kWh)", min_value=0)
            energy_fuel = st.number_input("Annual Fossil Fuel Consumption (liters)", min_value=0)
            energy_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"])
            
            st.subheader("Transport Sector")
            vehicles_total = st.number_input("Total Vehicles in City", min_value=0)
            fuel_consumption = st.number_input("Annual Fuel Consumption by Vehicles (liters)", min_value=0)
            transport_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"])
            
            st.subheader("Buildings Sector")
            buildings_count = st.number_input("Total Buildings", min_value=0)
            buildings_area = st.number_input("Total Built-up Area (sq.m)", min_value=0)
            buildings_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"])
            
            st.subheader("Waste Sector")
            waste_generated = st.number_input("Total Waste Generated (tonnes/year)", min_value=0)
            waste_recycled = st.number_input("Waste Recycled (tonnes/year)", min_value=0)
            waste_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"])
            
            st.subheader("Industry Sector")
            industry_count = st.number_input("Number of Industrial Units", min_value=0)
            industry_energy = st.number_input("Industrial Energy Consumption (kWh/year)", min_value=0)
            industry_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"])
            
            st.subheader("Urban Forestry & Land Use")
            green_cover = st.number_input("Urban Green Cover (ha)", min_value=0)
            forestry_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"])
            
            st.subheader("Other Emissions")
            other_emissions = st.number_input("Other City Emissions (MTCO2e)", min_value=0)
            other_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"])
            
            submit = st.form_submit_button("Save CAP Raw Data & Download CSV")
            if submit:
                new_data = {
                    "City Name": city_name,
                    "Energy Electricity (kWh)": energy_elec,
                    "Energy Fuel (L)": energy_fuel,
                    "Transport Vehicles": vehicles_total,
                    "Transport Fuel (L)": fuel_consumption,
                    "Buildings Count": buildings_count,
                    "Buildings Area (sq.m)": buildings_area,
                    "Waste Generated (t)": waste_generated,
                    "Waste Recycled (t)": waste_recycled,
                    "Industry Units": industry_count,
                    "Industry Energy (kWh)": industry_energy,
                    "Urban Green Cover (ha)": green_cover,
                    "Other Emissions (MTCO2e)": other_emissions
                }

                if city_name in df_cap.get("City Name", []):
                    idx = df_cap[df_cap["City Name"] == city_name].index[0]
                    df_cap.loc[idx] = new_data
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([new_data])], ignore_index=True)

                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE, index=False)
                st.success(f"CAP Raw Data for {city_name} saved successfully!")

                st.download_button(
                    label="Download CAP Raw Data CSV",
                    data=df_cap.to_csv(index=False).encode('utf-8'),
                    file_name=f"{city_name}_CAP_Data.csv",
                    mime="text/csv"
                )
