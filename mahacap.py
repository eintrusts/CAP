# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import requests

# PDF support
try:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Maharashtra CAP Dashboard",
    page_icon="🌍",
    layout="wide"
)

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
    "Mumbai": "Mumbai",
    "Kalyan-Dombivli": "Thane",
    "Mira-Bhayandar": "Thane",
    "Navi Mumbai": "Thane",
    "Bhiwandi-Nozampur": "Thane",
    "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane",
    "Vasai-Virar": "Palghar",
    "Thane": "Thane",
    "Badlapur Council": "Thane",
    "Pune": "Pune",
    "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad",
    "Malegaon": "Nashik",
    "Nashik": "Nashik",
    "Nandurbar Council": "Nandurbar",
    "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon",
    "Dhule": "Dhule",
    "Ahilyanagar": "Ahilyanagar",
    "Chh. Sambhajinagar": "Chh. Sambhajianagar",
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
    "Dharashiv Council": "Dharashiv",
    "Latur": "Latur",
    "Udgir Council": "Latur",
    "Akola": "Akola",
    "Parbhani Council": "Parbhani",
    "Amravati": "Amravati",
    "Achalpur Council": "Amravati",
    "Wardha Council": "Wardha",
    "Hinganghat Council": "Wardha",
    "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None
if "show_inventory" not in st.session_state:
    st.session_state.show_inventory = False
if "selected_city" not in st.session_state:
    st.session_state.selected_city = None

# ---------------------------
# Load Data
# ---------------------------
def load_csv(file_path, default_cols):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except:
            return pd.DataFrame(columns=default_cols)
    else:
        return pd.DataFrame(columns=default_cols)

meta_cols = [
    "City Name", "District", "Population", "ULB Category", "CAP Status",
    "GHG Emissions", "Environment Department Exist", "Department Name",
    "Head Name", "Department Email"
]
cap_cols = []

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# Remove Raigad Council (case-insensitive)
st.session_state.data = st.session_state.data[
    ~st.session_state.data["City Name"].str.contains("Raigad Council", case=False, na=False)
]

# ---------------------------
# Helper Functions
# ---------------------------
def format_indian_number(num):
    try:
        num = int(num)
        s = str(num)[::-1]
        lst = []
        lst.append(s[:3])
        s = s[3:]
        while s:
            lst.append(s[:2])
            s = s[2:]
        return ','.join(lst)[::-1]
    except:
        return str(num)

def format_population(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        return format_indian_number(num)
    except:
        return str(num)

def safe_get(row, col, default="—"):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else val
    except:
        return default

# ---------------------------
# Dark / Professional CSS
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color: #0f0f10; color: #E6E6E6;}
[data-testid="stSidebar"] {background-color: #141518; color: #E6E6E6;}
.stButton>button {background-color:#3E6BE6; color:#FFFFFF; border-radius:8px; height:40px;}
.stButton>button:hover {background-color:#2e50b0;}
[data-testid="stMetricValue"] {color:#3E6BE6; font-weight:700;}
.stExpander>div>div>div>div {background-color:#141518; color:#E6E6E6;}
input, textarea, select {background-color:#141518; color:#E6E6E6; border-color:#3E6BE6;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Admin Login
# ---------------------------
def admin_login():
    with st.form("login_form", clear_on_submit=False):
        pw = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Admin login successful")
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image(
    "https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

for btn, name in [("Home", "Home"), ("City Information", "City Information"), ("Admin", "Admin")]:
    if st.sidebar.button(btn):
        st.session_state.menu = name
        st.session_state.show_inventory = False

if st.session_state.authenticated and st.sidebar.button("CAP Generation"):
    st.session_state.menu = "CAP Generation"
    st.session_state.show_inventory = True

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra's Net Zero Journey")
    st.markdown("Climate Action Plan Dashboard")
    df = st.session_state.data.copy()

    # --- CAP Status Summary ---
    if not df.empty and "CAP Status" in df.columns:
        not_started = df[df["CAP Status"].str.lower() == "not started"].shape[0]
        in_progress = df[df["CAP Status"].str.lower() == "in progress"].shape[0]
        completed = df[df["CAP Status"].str.lower() == "completed"].shape[0]
        total_status = not_started + in_progress + completed

        st.markdown("### CAP Status Overview")
        c1, c2, c3, c4 = st.columns(4)

        block_style = """
            background-color:#141518;
            padding:20px;
            border-radius:12px;
            text-align:center;
        """
        title_style = "color:#E6E6E6; margin:0;"
        value_style = "font-size:28px; font-weight:bold; color:#3E6BE6;"

        c1.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Not Started</h3><p style='{value_style}'>{format_indian_number(not_started)}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>In Progress</h3><p style='{value_style}'>{format_indian_number(in_progress)}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Completed</h3><p style='{value_style}'>{format_indian_number(completed)}</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Total</h3><p style='{value_style}'>{format_indian_number(total_status)}</p></div>", unsafe_allow_html=True)

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin":
    st.header("Admin Board")
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.subheader("Add/Update City Data")
        with st.form("admin_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            population = st.number_input("Population (as per census 2011)", min_value=0, value=0, step=1000)
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)
            dept_exist = st.selectbox("Environment Department Exist?", ["Yes", "No"])
            dept_name = st.text_input("Department Name")
            head_name = st.text_input("Department Head Name")
            dept_email = st.text_input("Department Email")
            submit_admin = st.form_submit_button("Add/Update City Data")

            if submit_admin:
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "—"),
                    "Population": population,
                    "CAP Status": cap_status,
                    "GHG Emissions": ghg_val,
                    "Environment Department Exist": dept_exist,
                    "Department Name": dept_name,
                    "Head Name": head_name,
                    "Department Email": dept_email
                }
                df_meta = st.session_state.data.copy()
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"] == city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE, index=False)
                st.success(f"{city} data updated successfully!")

        st.write("### All Cities Data")
        st.table(st.session_state.data.assign(
            Population=lambda d: d["Population"].map(format_indian_number),
            GHG_Emissions=lambda d: d["GHG Emissions"].map(format_indian_number)
        ))

# ---------------------------
# CAP Generation Page
# ---------------------------
if st.session_state.menu == "CAP Generation":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("CAP : Data Collection")

        # --- City Selection ---
        cities_for_select = ["Sangli", "Miraj", "Kupwad"]
        city = st.selectbox("Select City", cities_for_select, index=0)
        st.session_state.selected_city = city

        # --- CAP Raw Data Form ---
        with st.form("cap_raw_form", clear_on_submit=False):
            st.subheader("Population & Demographics")
            population = st.number_input("Total Population", min_value=0, value=0, step=1000)
            households = st.number_input("Number of Households", min_value=0, value=0, step=100)
            urbanization_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

            st.subheader("Electricity & Energy Use")
            residential_electricity_mwh = st.number_input("Residential Electricity Consumption (MWh/year)", min_value=0, value=0, step=100)
            commercial_electricity_mwh = st.number_input("Commercial Electricity Consumption (MWh/year)", min_value=0, value=0, step=100)
            industrial_electricity_mwh = st.number_input("Industrial Electricity Consumption (MWh/year)", min_value=0, value=0, step=100)
            streetlights_energy_mwh = st.number_input("Streetlights & Public Buildings Energy (MWh/year)", min_value=0, value=0, step=100)

            st.subheader("Transport Activity")
            vehicles_diesel = st.number_input("Number of Diesel Vehicles", min_value=0, value=0, step=10)
            vehicles_petrol = st.number_input("Number of Petrol Vehicles", min_value=0, value=0, step=10)
            vehicles_cng = st.number_input("Number of CNG Vehicles", min_value=0, value=0, step=10)
            vehicles_lpg = st.number_input("Number of LPG Vehicles", min_value=0, value=0, step=10)
            vehicles_electric = st.number_input("Number of Electric Vehicles", min_value=0, value=0, step=10)
            avg_km_per_vehicle_year = st.number_input("Average km per Vehicle per Year", min_value=0, value=0, step=100)

            st.subheader("Industry & Commercial Fuel Use")
            industrial_fuel_diesel_tons = st.number_input("Industrial Diesel Fuel (tons/year)", min_value=0, value=0, step=10)
            industrial_fuel_petrol_tons = st.number_input("Industrial Petrol Fuel (tons/year)", min_value=0, value=0, step=10)
            industrial_fuel_cng_tons = st.number_input("Industrial CNG Fuel (tons/year)", min_value=0, value=0, step=10)
            industrial_fuel_lpg_tons = st.number_input("Industrial LPG Fuel (tons/year)", min_value=0, value=0, step=10)
            industrial_energy_mwh = st.number_input("Industrial Energy Consumption (MWh/year)", min_value=0, value=0, step=100)

            st.subheader("Buildings & Commercial")
            residential_energy_mwh = st.number_input("Residential Energy Consumption (MWh/year)", min_value=0, value=0, step=100)
            commercial_energy_mwh = st.number_input("Commercial Energy Consumption (MWh/year)", min_value=0, value=0, step=100)
            public_buildings_energy_mwh = st.number_input("Public Buildings Energy (MWh/year)", min_value=0, value=0, step=100)

            st.subheader("Waste Management")
            municipal_solid_waste_tons = st.number_input("Municipal Solid Waste Generated (tons/year)", min_value=0, value=0, step=10)
            fraction_landfilled = st.number_input("Fraction Landfilled (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            fraction_composted = st.number_input("Fraction Composted (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            wastewater_volume_m3 = st.number_input("Wastewater Treated (m3/year)", min_value=0, value=0, step=1000)

            st.subheader("Water & Sewage")
            water_supply_m3 = st.number_input("Total Water Supplied (m3/year)", min_value=0, value=0, step=1000)
            energy_for_water_mwh = st.number_input("Energy Used for Water Supply & Treatment (MWh/year)", min_value=0, value=0, step=10)

            st.subheader("Urban Green / Other")
            urban_green_area_ha = st.number_input("Urban Green Area (hectares)", min_value=0, value=0, step=1)
            renewable_energy_mwh = st.number_input("Renewable Energy Generated in City (MWh/year)", min_value=0, value=0, step=10)

            submit_cap = st.form_submit_button("Save & View GHG Inventory")

            if submit_cap:
                raw_row = {
                    "City Name": city,
                    "Population": population,
                    "Households": households,
                    "Urbanization Rate (%)": urbanization_rate,
                    "Residential Electricity (MWh)": residential_electricity_mwh,
                    "Commercial Electricity (MWh)": commercial_electricity_mwh,
                    "Industrial Electricity (MWh)": industrial_electricity_mwh,
                    "Streetlights Energy (MWh)": streetlights_energy_mwh,
                    "Diesel Vehicles": vehicles_diesel,
                    "Petrol Vehicles": vehicles_petrol,
                    "CNG Vehicles": vehicles_cng,
                    "LPG Vehicles": vehicles_lpg,
                    "Electric Vehicles": vehicles_electric,
                    "Avg km/Vehicle": avg_km_per_vehicle_year,
                    "Industrial Diesel (t)": industrial_fuel_diesel_tons,
                    "Industrial Petrol (t)": industrial_fuel_petrol_tons,
                    "Industrial CNG (t)": industrial_fuel_cng_tons,
                    "Industrial LPG (t)": industrial_fuel_lpg_tons,
                    "Industrial Energy (MWh)": industrial_energy_mwh,
                    "Residential Energy (MWh)": residential_energy_mwh,
                    "Commercial Energy (MWh)": commercial_energy_mwh,
                    "Public Buildings Energy (MWh)": public_buildings_energy_mwh,
                    "Municipal Solid Waste (t)": municipal_solid_waste_tons,
                    "Fraction Landfilled (%)": fraction_landfilled,
                    "Fraction Composted (%)": fraction_composted,
                    "Wastewater Treated (m3)": wastewater_volume_m3,
                    "Water Supply (m3)": water_supply_m3,
                    "Energy for Water (MWh)": energy_for_water_mwh,
                    "Urban Green Area (ha)": urban_green_area_ha,
                    "Renewable Energy (MWh)": renewable_energy_mwh
                }

                df_cap = st.session_state.cap_data.copy()
                if city in df_cap["City Name"].values:
                    df_cap.loc[df_cap["City Name"] == city, list(raw_row.keys())[1:]] = list(raw_row.values())[1:]
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([raw_row])], ignore_index=True)

                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE, index=False)
                st.success(f"CAP raw data for {city} saved successfully!")
                st.session_state.show_inventory = True

        # --- Generate GHG Inventory Button ---
        if st.session_state.show_inventory:
            if st.button("Generate GHG Inventory"):
                st.session_state.menu = "GHG Inventory"
                st.experimental_rerun()

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif st.session_state.menu == "GHG Inventory":
    city = st.session_state.selected_city
    if city not in st.session_state.cap_data["City Name"].values:
        st.warning("Please generate CAP first.")
    else:
        st.header(f"GHG Inventory - {city}")

        df_city = st.session_state.cap_data.loc[st.session_state.cap_data["City Name"] == city].iloc[0]

        # --- Emission Factors ---
        EF_electricity = 0.82
        EF_diesel_vehicle = 0.00268
        EF_petrol_vehicle = 0.00231
        EF_cng_vehicle = 0.0016
        EF_lpg_vehicle = 0.00151
        EF_electric_vehicle = 0
        EF_diesel_industry = 2.68
        EF_petrol_industry = 2.31
        EF_cng_industry = 1.6
        EF_lpg_industry = 1.51
        EF_msw_landfill = 0.25
        EF_msw_compost = 0.05
        EF_wastewater = 0.5

        elec_emissions = (
            df_city["Residential Electricity (MWh)"] +
            df_city["Commercial Electricity (MWh)"] +
            df_city["Industrial Electricity (MWh)"] +
            df_city["Streetlights Energy (MWh)"]
        ) * EF_electricity

        transport_emissions = (
            df_city["Diesel Vehicles"] * df_city["Avg km/Vehicle"] * EF_diesel_vehicle +
            df_city["Petrol Vehicles"] * df_city["Avg km/Vehicle"] * EF_petrol_vehicle +
            df_city["CNG Vehicles"] * df_city["Avg km/Vehicle"] * EF_cng_vehicle +
            df_city["LPG Vehicles"] * df_city["Avg km/Vehicle"] * EF_lpg_vehicle +
            df_city["Electric Vehicles"] * df_city["Avg km/Vehicle"] * EF_electric_vehicle
        )

        industry_emissions = (
            df_city["Industrial Diesel (t)"] * EF_diesel_industry +
            df_city["Industrial Petrol (t)"] * EF_petrol_industry +
            df_city["Industrial CNG (t)"] * EF_cng_industry +
            df_city["Industrial LPG (t)"] * EF_lpg_industry +
            df_city["Industrial Energy (MWh)"] * EF_electricity
        )

        waste_emissions = (
            df_city["Municipal Solid Waste (t)"] * (df_city["Fraction Landfilled (%)"]/100) * EF_msw_landfill +
            df_city["Municipal Solid Waste (t)"] * (df_city["Fraction Composted (%)"]/100) * EF_msw_compost +
            df_city["Wastewater Treated (m3)"] * EF_wastewater
        )

        water_emissions = df_city["Energy for Water (MWh)"] * EF_electricity

        total_ghg = elec_emissions + transport_emissions + industry_emissions + waste_emissions + water_emissions
        per_capita = total_ghg / max(df_city["Population"], 1)

        st.metric("Total Annual GHG Emissions (tCO2e)", format_indian_number(round(total_ghg)))
        st.metric("Per Capita GHG Emissions (tCO2e)", round(per_capita, 2))

        ghg_breakdown = pd.DataFrame({
            "Sector": ["Electricity", "Transport", "Industry", "Waste", "Water & Other"],
            "Emissions (tCO2e)": [elec_emissions, transport_emissions, industry_emissions, waste_emissions, water_emissions]
        })

        fig_bar = px.bar(
            ghg_breakdown, x="Sector", y="Emissions (tCO2e)",
            text="Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"]
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_pie = px.pie(
            ghg_breakdown, names="Sector", values="Emissions (tCO2e)",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        if st.button("Actions"):
            st.session_state.menu = "Actions"
            st.experimental_rerun()

# ---------------------------
# Actions Page
# ---------------------------
elif st.session_state.menu == "Actions":
    st.header(f"Suggested Actions - {st.session_state.selected_city}")

    sectors = ["Electricity", "Transport", "Industry", "Waste", "Water & Other"]

    actions_data = {
        "Short Term": [
            "LED streetlight replacement", "Solar rooftop pilot", "Energy audit", "Public EV charging", 
            "Waste segregation awareness", "Water leak detection", "Urban tree planting", "Efficient public pumps",
            "Industrial energy check", "Smart traffic signals"
        ],
        "Mid Term": [
            "City-wide rooftop solar", "Electric bus deployment", "Industrial cogeneration", "Organic waste composting",
            "Wastewater recycling plants", "Solar water heating in buildings", "Green corridors", "EV incentives",
            "Public transport expansion", "Smart grid implementation"
        ],
        "Long Term": [
            "Net-zero city plan", "Mass transit network expansion", "Renewable energy parks", "Circular waste economy",
            "Decentralized water management", "Urban forest expansion", "100% EV adoption", "Zero energy buildings",
            "Advanced industrial emission control", "Carbon credit monetization"
        ]
    }

    for sector in sectors:
        st.subheader(sector)
        df_actions = pd.DataFrame(actions_data)
        st.table(df_actions)

    if st.button("Generate CAP"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        # Logo
        logo_url = "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true"
        logo_image = ImageReader(requests.get(logo_url, stream=True).raw)
        c.drawImage(logo_image, 30, height-80, width=100, height=50)

        c.setFont("Helvetica-Bold", 16)
        c.drawString(150, height-50, f"Climate Action Plan - {st.session_state.selected_city}")

        # GHG Inventory
        c.setFont("Helvetica", 12)
        c.drawString(30, height-120, f"Total GHG Emissions (tCO2e): {round(total_ghg,2)}")
        c.drawString(30, height-140, f"Per Capita GHG Emissions (tCO2e): {round(per_capita,2)}")

        # Actions
        y = height-180
        for sector in sectors:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, y, sector)
            y -= 20
            c.setFont("Helvetica", 10)
            for term in ["Short Term","Mid Term","Long Term"]:
                c.drawString(40, y, f"{term}: {', '.join(actions_data[term])}")
                y -= 15
            y -= 10

        c.save()
        buffer.seek(0)
        st.download_button("Download CAP PDF", data=buffer, file_name=f"CAP_{st.session_state.selected_city}.pdf", mime="application/pdf")
