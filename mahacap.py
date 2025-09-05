# mahacap.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin Password
# ---------------------------
ADMIN_PASSWORD = "eintrust2025"

# ---------------------------
# Data Files
# ---------------------------
DATA_FILE = "cities_data.csv"
CAP_DATA_FILE = "cap_raw_data.csv"

# ---------------------------
# Cities & Districts
# ---------------------------
cities_districts = {
    "Mumbai": "Mumbai", "Kalyan-Dombivli": "Thane", "Mira-Bhayandar": "Thane",
    "Navi Mumbai": "Thane", "Bhiwandi": "Thane", "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane", "Vasai-Virar": "Thane", "Thane": "Thane",
    "Badlapur Council": "Thane", "Pune": "Pune", "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad", "Raigad Council": "Raigad", "Malegaon": "Nashik",
    "Nashik": "Nashik", "Nandurbar Council": "Nandurbar", "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon", "Dhule": "Dhule", "Ahmednagar": "Ahmednagar",
    "Aurangabad": "Aurangabad", "Jalna": "Jalna", "Beed Council": "Beed",
    "Satara Council": "Satara", "Sangli-Miraj-Kupwad": "Sangli", "Kolhapur": "Kolhapur",
    "Ichalkaranji": "Kolhapur", "Solapur": "Solapur", "Barshi Council": "Solapur",
    "Nanded-Waghala": "Nanded", "Yawatmal Council": "Yawatmal", "Osmanabad Council": "Osmanabad",
    "Latur": "Latur", "Udgir Council": "Latur", "Akola": "Akola",
    "Parbhani Council": "Parbhani", "Amravati": "Amravati", "Achalpur Council": "Amravati",
    "Wardha Council": "Wardha", "Hinganghat Council": "Wardha", "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur", "Gondia Council": "Gondia"
}

# ---------------------------
# Session State
# ---------------------------
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "menu" not in st.session_state: st.session_state.menu = "Home"
if "admin_click" not in st.session_state: st.session_state.admin_click = False

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
# Dark Theme CSS
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color: #121212; color: #E0E0E0;}
[data-testid="stSidebar"] {background-color: #1C1C1C; color: #E0E0E0;}
.css-1d391kg button, .stButton>button {background-color: #228B22 !important; color: #FFFFFF !important; width: 100% !important; margin-bottom: 5px !important; height: 40px !important; font-size: 16px !important; border-radius: 5px !important;}
.css-1d391kg button:hover, .stButton>button:hover {background-color: #196619 !important;}
[data-testid="stMetricValue"] {color: #4169E1 !important; font-weight: bold;}
.stExpander>div>div>div>div {background-color: #1E1E1E !important; color: #E0E0E0 !important;}
h1,h2,h3,h4,h5,h6 {color: #7CFC00 !important;}
.css-1hwfws3, .css-1r6slb0, .stTextInput>div>input, .stNumberInput>div>input {background-color: #1C1C1C !important; color: #E0E0E0 !important; border-color: #228B22 !important;}
.stFileUploader>div>div {background-color:#1C1C1C !important; color:#E0E0E0 !important;}
</style>
""", unsafe_allow_html=True)

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
                st.session_state.menu = "Admin Panel"
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

if st.sidebar.button("Home"): st.session_state.menu = "Home"
if st.sidebar.button("City Dashboard"): st.session_state.menu = "City Dashboard"
if st.session_state.authenticated:
    if st.sidebar.button("CAP Preparation"): st.session_state.menu = "CAP Preparation"
st.sidebar.markdown("EinTrust | © 2025")

# ---------------------------
# Logo Click opens Admin Login
# ---------------------------
if not st.session_state.authenticated and st.sidebar.button("Admin Login"):
    admin_login()

# ---------------------------
# Menu Pages
# ---------------------------
menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra Climate Action Plan Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")
    df = st.session_state.data

    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        if "GHG Emissions" in df.columns:
            df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors='coerce').fillna(0)

        st.metric("Total Cities", df.shape[0])
        st.metric("Cities with CAP Completed", df[df["CAP Status"]=="Completed"].shape[0])

        if "GHG Emissions" in df.columns:
            fig = px.bar(df, x="City Name", y="GHG Emissions", text="GHG Emissions",
                         title="GHG Emissions by City",
                         color="GHG Emissions", color_continuous_scale=px.colors.sequential.Viridis)
            fig.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="#E0E0E0")
            st.plotly_chart(fig, use_container_width=True)

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

        if os.path.exists(DATA_FILE):
            last_updated = pd.to_datetime(os.path.getmtime(DATA_FILE), unit='s')
            st.markdown(f"*Last Updated: {last_updated.strftime('%B %Y')}*")

# ---------------------------
# Admin Panel & CAP Preparation
# ---------------------------
elif menu in ["Admin Panel", "CAP Preparation"]:
    if not st.session_state.authenticated:
        admin_login()
    else:
        # Here include full Admin Panel & CAP Preparation code exactly as in previous version
        st.header("CAP Preparation - Detailed Raw Data Input")
        st.markdown("Enter all city-level raw data to generate GHG Inventory and CAP.")
        df_cap = st.session_state.cap_data

        with st.form("cap_form"):
            city_name = st.selectbox("Select City", st.session_state.data["City Name"].dropna().unique(), key="cap_city_select")
            
            st.subheader("Energy Sector")
            energy_elec = st.number_input("Annual Electricity Consumption (kWh)", min_value=0, key="energy_elec")
            energy_fuel = st.number_input("Annual Fossil Fuel Consumption (liters)", min_value=0, key="energy_fuel")
            energy_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="energy_file")
            
            st.subheader("Transport Sector")
            vehicles_total = st.number_input("Total Vehicles in City", min_value=0, key="vehicles_total")
            fuel_consumption = st.number_input("Annual Fuel Consumption by Vehicles (liters)", min_value=0, key="fuel_consumption")
            transport_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="transport_file")
            
            st.subheader("Buildings Sector")
            buildings_count = st.number_input("Total Buildings", min_value=0, key="buildings_count")
            buildings_area = st.number_input("Total Built-up Area (sq.m)", min_value=0, key="buildings_area")
            buildings_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="buildings_file")
            
            st.subheader("Water Sector")
            water_consumption = st.number_input("Total Water Consumption (ML/year)", min_value=0, key="water_consumption")
            water_waste = st.number_input("Wastewater Generated (ML/year)", min_value=0, key="water_waste")
            water_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="water_file")
            
            st.subheader("Waste Sector")
            waste_generated = st.number_input("Total Waste Generated (tonnes/year)", min_value=0, key="waste_generated")
            waste_recycled = st.number_input("Waste Recycled (tonnes/year)", min_value=0, key="waste_recycled")
            waste_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="waste_file")
            
            st.subheader("Industry Sector")
            industry_count = st.number_input("Number of Industrial Units", min_value=0, key="industry_count")
            industry_energy = st.number_input("Industrial Energy Consumption (kWh/year)", min_value=0, key="industry_energy")
            industry_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="industry_file")
            
            st.subheader("Urban Forestry & Land Use")
            green_cover = st.number_input("Urban Green Cover (ha)", min_value=0, key="green_cover")
            forestry_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="forestry_file")
            
            st.subheader("Other Emissions")
            other_emissions = st.number_input("Other City Emissions (MTCO2e)", min_value=0, key="other_emissions")
            other_upload = st.file_uploader("Upload supporting file (optional)", type=["xlsx","csv","pdf"], key="other_file")
            
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
                    "Water Consumption (ML)": water_consumption,
                    "Wastewater Generated (ML)": water_waste,
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
