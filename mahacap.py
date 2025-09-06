# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

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
    "Bhiwandi-Nizampur": "Thane",
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
def reset_all_data():
    # Clear session state
    st.session_state.clear()
    
    # Optionally, reset CSV files
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    if os.path.exists(CAP_DATA_FILE):
        os.remove(CAP_DATA_FILE)
    
    st.success("All data has been reset successfully!")
    st.experimental_rerun()  # Refresh the app

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
/* Main container */
[data-testid="stAppViewContainer"] {
    background-color: #1E1E2F; 
    color: #E6E6E6;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #2B2B3B; 
    color: #E6E6E6;
}

/* Buttons */
.stButton>button {
    background-color:#54c750; 
    color:#FFFFFF; 
    border-radius:8px; 
    height:40px;
}
.stButton>button:hover {
    background-color:#3a8b34;
}

/* Metrics */
[data-testid="stMetricValue"] {
    color:#54c750; 
    font-weight:700;
}

/* Expander */
.stExpander>div>div>div>div {
    background-color:#2B2B3B; 
    color:#E6E6E6;
}

/* Inputs */
input, textarea, select {
    background-color:#2B2B3B; 
    color:#E6E6E6; 
    border-color:#54c750;
}

/* Tables */
.stDataFrame, .stTable {
    color:#E6E6E6;
    background-color:#1E1E2F;
}

/* Links */
a {
    color:#54c750;
}

/* Custom cards */
.stCard {
    background-color:#2B2B3B;
    padding:20px;
    border-radius:12px;
    text-align:center;
    margin-bottom:10px;
}
.stCard h4 {
    margin:0;
    font-weight:500;
    color:#E6E6E6;
}
.stCard h2 {
    margin:5px 0 0 0;
    font-weight:700;
    color:#54c750;
    font-size:28px;
}
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
st.sidebar.image("https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png", use_container_width=True)


for btn, name in [("Home", "Home"), ("City Information", "City Information"), ("Admin", "Admin")]:
    if st.sidebar.button(btn):
        st.session_state.menu = name

if st.session_state.authenticated and st.sidebar.button("CAP Generation"):
    st.session_state.menu = "CAP Generation"

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
        c1, c2, c3, c4 = st.columns(4)
        not_started = df[df["CAP Status"].str.lower() == "not started"].shape[0]
        in_progress = df[df["CAP Status"].str.lower() == "in progress"].shape[0]
        completed = df[df["CAP Status"].str.lower() == "completed"].shape[0]

        cards = [
            ("Total Cities", len(df)),
            ("Not Started", not_started),
            ("In Progress", in_progress),
            ("Completed", completed)
        ]
        for col, (title, val) in zip([c1, c2, c3, c4], cards):
            col.markdown(f"<div class='stCard'><h4>{title}</h4><h2>{format_indian_number(val)}</h2></div>", unsafe_allow_html=True)

    # --- Reported GHG ---
    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig_reported = px.bar(
            df.sort_values("GHG Emissions", ascending=False),
            x="City Name", y="GHG Emissions",
            title="City-level Reported GHG Emissions (tCO2e)",
            text=df["GHG Emissions"].apply(format_indian_number),
            color_discrete_sequence=["#3E6BE6"]
        )
        fig_reported.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig_reported, use_container_width=True)

    # --- Estimated GHG ---
    if not df.empty and "Population" in df.columns:
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce").fillna(0)
        EMISSION_FACTOR = 2.5
        df["Estimated GHG Emissions"] = df["Population"] * EMISSION_FACTOR
        fig_estimated = px.bar(
            df.sort_values("Estimated GHG Emissions", ascending=False),
            x="City Name", y="Estimated GHG Emissions",
            title=f"Estimated GHG Emissions (tCO2e) — based on {EMISSION_FACTOR} tCO2e/person",
            text=df["Estimated GHG Emissions"].apply(lambda x: format_indian_number(round(x))),
            color_discrete_sequence=["#E67E22"]
        )
        fig_estimated.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig_estimated, use_container_width=True)

    # --- Vulnerability Scores ---
    if not df.empty:
        # Environmental Vulnerability Score (EVS)
        df["EVS"] = 0
        env_factors = ["GHG Emissions", "Urban Green Area (ha)", "Renewable Energy (MWh)",
                       "Municipal Solid Waste (tons)", "Wastewater Treated (m3)"]
        for f in env_factors:
            if f in df.columns:
                df[f] = pd.to_numeric(df[f], errors="coerce").fillna(0)

        # Simple scoring logic (example: normalize 0-100 scale)
        max_ghg = df["GHG Emissions"].max() or 1
        max_waste = df["Municipal Solid Waste (tons)"].max() or 1
        max_ww = df["Wastewater Treated (m3)"].max() or 1
        max_green = df["Urban Green Area (ha)"].max() or 1
        max_re = df["Renewable Energy (MWh)"].max() or 1

        df["EVS"] = (
            (df["GHG Emissions"]/max_ghg)*0.4 + 
            (1 - df["Urban Green Area (ha)"]/max_green)*0.2 + 
            (1 - df["Renewable Energy (MWh)"]/max_re)*0.1 + 
            (df["Municipal Solid Waste (tons)"]/max_waste)*0.2 + 
            (1 - df["Wastewater Treated (m3)"]/max_ww)*0.1
        ) * 100  # Scale 0-100

        # Social Vulnerability Score (SVS)
        df["SVS"] = 0
        social_factors = ["Literacy Rate", "Children (%)", "Elderly (%)", "Poverty (%)", "Slum (%)", "Water/Sanitation (%)"]
        for f in social_factors:
            if f in df.columns:
                df[f] = pd.to_numeric(df[f], errors="coerce").fillna(0)

        df["SVS"] = (
            (100 - df["Literacy Rate"])*0.2 +
            df["Children (%)"]*0.1 +
            df["Elderly (%)"]*0.1 +
            df["Poverty (%)"]*0.3 +
            df["Slum (%)"]*0.2 +
            (100 - df["Water/Sanitation (%)"])*0.1
        )  # Scale 0-100

        # --- Vulnerability Chart ---
        vuln_df = df[["City Name", "EVS", "SVS"]].melt(id_vars="City Name", var_name="Score Type", value_name="Score")
        fig_vuln = px.bar(
            vuln_df,
            x="City Name",
            y="Score",
            color="Score Type",
            barmode="group",
            title="City-wise Vulnerability Scores (0-100)"
        )
        fig_vuln.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig_vuln, use_container_width=True)

# ---------------------------
# City Information
# ---------------------------
elif menu == "City Information":
    st.header("City Information")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()

    cities_for_select = list(cities_districts.keys())
    city = st.selectbox("Select City", cities_for_select)

    meta_row = df_meta[df_meta["City Name"] == city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None
    cap_row = df_cap[df_cap["City Name"] == city].iloc[0] if (not df_cap.empty and city in df_cap["City Name"].values) else None

    # --- Basic Information ---
    st.subheader("Basic Information")
    st.write(f"**City:** {city}")
    st.write(f"**District:** {safe_get(meta_row, 'District')}")
    st.write(f"**ULB Category:** {safe_get(meta_row, 'ULB Category')}")
    st.write(f"**CAP Status:** {safe_get(meta_row, 'CAP Status')}")

    # --- Environmental Information ---
    st.subheader("Environmental Information")
    if cap_row is not None:
        population = cap_row.get("Population", 0)
        total_ghg = cap_row.get("GHG Emissions", 0)
        per_capita_ghg = total_ghg / population if population > 0 else 0
        st.write(f"**Total GHG Emissions (tCO2e):** {format_indian_number(round(total_ghg))}")
        st.write(f"**Per Capita GHG Emissions (tCO2e/person):** {round(per_capita_ghg, 2)}")
        st.write(f"**Urban Green Area (ha):** {cap_row.get('Urban Green Area (ha)', '—')}")
        st.write(f"**Renewable Energy (MWh):** {cap_row.get('Renewable Energy (MWh)', '—')}")
        st.write(f"**Municipal Solid Waste (tons/year):** {cap_row.get('Municipal Solid Waste (tons)', '—')}")
        st.write(f"**Wastewater Treated (m3/year):** {cap_row.get('Wastewater Treated (m3)', '—')}")

        # Environmental Vulnerability Score (normalized)
        ev_factors = ["Per Capita GHG Emissions (tCO2e/person)", "Wastewater Treated (m3/year)", "Urban Green Area (ha)"]
        ev_score = 0
        try:
            # Simple example: higher green area → lower vulnerability, higher per capita GHG → higher vulnerability
            ev_score = round((per_capita_ghg * 0.5 + max(0, 1000 - cap_row.get("Urban Green Area (ha)",0))*0.3 + 0)/100,2)
        except:
            ev_score = None
        st.write(f"**Environmental Vulnerability Score (EVS):** {ev_score if ev_score is not None else '—'}")

    # --- Social Information ---
    st.subheader("Social Information")
    if meta_row is not None:
        st.write(f"**Population:** {format_population(safe_get(meta_row, 'Population'))}")
        st.write(f"**Literacy Rate (%):** {safe_get(meta_row, 'Literacy Rate', '—')}")
        st.write(f"**Children (%)**: {safe_get(meta_row, 'Children (%)', '—')}")
        st.write(f"**Elderly (%)**: {safe_get(meta_row, 'Elderly (%)', '—')}")
        st.write(f"**Poverty Rate (%)**: {safe_get(meta_row, 'Poverty (%)', '—')}")
        st.write(f"**Slum Population (%)**: {safe_get(meta_row, 'Slum (%)', '—')}")
        st.write(f"**Access to Water/Sanitation (%)**: {safe_get(meta_row, 'Water/Sanitation (%)', '—')}")

        # Social Vulnerability Score (normalized)
        sv_score = 0
        try:
            sv_score = round(
                (safe_get(meta_row,"Poverty (%)",0)*0.4 + safe_get(meta_row,"Slum (%)",0)*0.3 + (100 - safe_get(meta_row,"Literacy Rate",100))*0.3)/100,2
            )
        except:
            sv_score = None
        st.write(f"**Social Vulnerability Score (SVS):** {sv_score if sv_score is not None else '—'}")

    # --- Contact Information ---
    st.subheader("Contact Information")
    if meta_row is not None:
        st.write(f"**City Official Name:** {safe_get(meta_row,'Department Head Name')}")
        st.write(f"**Email ID:** {safe_get(meta_row,'Department Email')}")
        st.write(f"**Website:** {safe_get(meta_row,'Department Website','—')}")

    last_mod = st.session_state.last_updated or datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
    st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")


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
            
            # --- Basic Info ---
            population = st.number_input("Population", min_value=0, value=0, step=1000)
            ulb_category = st.text_input("ULB Category")
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            
            # --- Environmental Info ---
            ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)
            urban_green_area = st.number_input("Urban Green Area (ha)", min_value=0.0, value=0.0, step=1.0)
            renewable_energy = st.number_input("Renewable Energy (MWh/year)", min_value=0.0, value=0.0, step=1.0)
            municipal_solid_waste = st.number_input("Municipal Solid Waste (tons/year)", min_value=0.0, value=0.0, step=10.0)
            wastewater_volume = st.number_input("Wastewater Treated (m3/year)", min_value=0.0, value=0.0, step=100.0)

            # --- Social Info ---
            literacy_rate = st.number_input("Literacy Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            children_pct = st.number_input("Children (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            elderly_pct = st.number_input("Elderly (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            poverty_pct = st.number_input("Poverty Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            slum_pct = st.number_input("Slum Population (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            water_sanitation_access = st.number_input("Access to Water/Sanitation (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

            # --- Contact Info ---
            dept_name = st.text_input("Department Name")
            head_name = st.text_input("City Official Name")
            dept_email = st.text_input("Department Email")
            dept_website = st.text_input("Department Website")

            submit_admin = st.form_submit_button("Add/Update City Data")

            if submit_admin:
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "—"),
                    "Population": population,
                    "ULB Category": ulb_category,
                    "CAP Status": cap_status,
                    "GHG Emissions": ghg_val,
                    "Urban Green Area (ha)": urban_green_area,
                    "Renewable Energy (MWh)": renewable_energy,
                    "Municipal Solid Waste (tons)": municipal_solid_waste,
                    "Wastewater Treated (m3)": wastewater_volume,
                    "Literacy Rate": literacy_rate,
                    "Children (%)": children_pct,
                    "Elderly (%)": elderly_pct,
                    "Poverty (%)": poverty_pct,
                    "Slum (%)": slum_pct,
                    "Water/Sanitation (%)": water_sanitation_access,
                    "Department Name": dept_name,
                    "Department Head Name": head_name,
                    "Department Email": dept_email,
                    "Department Website": dept_website
                }

                df_meta = st.session_state.data.copy()
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"] == city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)

                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE, index=False)
                st.success(f"{city} data updated successfully!")

        # --- All Cities Data Table ---
        st.write("### All Cities Data")
        st.table(st.session_state.data.assign(
            Population=lambda d: d["Population"].map(format_indian_number),
            GHG_Emissions=lambda d: d["GHG Emissions"].map(format_indian_number)
        ))

        # --- Reset Button ---
        if st.button("Reset All Data", key="reset_admin"):
            reset_all_data()
# ---------------------------
# CAP Preparation Page
# ---------------------------
elif menu == "CAP Generation":
    st.header("CAP : Data Collection")

    if not st.session_state.authenticated:
        admin_login()
    else:
        st.markdown("""
        Collect detailed city-level activity data for generating a comprehensive GHG inventory
        """)

        with st.form("cap_raw_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))

            # --- Demographics ---
            st.subheader("Population & Demographics")
            population = st.number_input("Total Population", min_value=0, value=0, step=1000)
            households = st.number_input("Number of Households", min_value=0, value=0, step=100)
            urbanization_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

            # --- Electricity & Energy ---
            st.subheader("Electricity & Energy Use")
            residential_electricity_mwh = st.number_input("Residential Electricity Consumption (MWh/year)", min_value=0, value=0, step=100)
            commercial_electricity_mwh = st.number_input("Commercial Electricity Consumption (MWh/year)", min_value=0, value=0, step=100)
            industrial_electricity_mwh = st.number_input("Industrial Electricity Consumption (MWh/year)", min_value=0, value=0, step=100)
            streetlights_energy_mwh = st.number_input("Streetlights & Public Buildings Energy (MWh/year)", min_value=0, value=0, step=100)

            # --- Transport & Industry Fuel ---
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

            # --- Buildings ---
            st.subheader("Buildings & Commercial")
            residential_energy_mwh = st.number_input("Residential Energy Consumption (MWh/year)", min_value=0, value=0, step=100)
            commercial_energy_mwh = st.number_input("Commercial Energy Consumption (MWh/year)", min_value=0, value=0, step=100)
            public_buildings_energy_mwh = st.number_input("Public Buildings Energy (MWh/year)", min_value=0, value=0, step=100)

            # --- Waste ---
            st.subheader("Waste Management")
            municipal_solid_waste_tons = st.number_input("Municipal Solid Waste Generated (tons/year)", min_value=0, value=0, step=10)
            fraction_landfilled = st.number_input("Fraction Landfilled (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            fraction_composted = st.number_input("Fraction Composted (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            wastewater_volume_m3 = st.number_input("Wastewater Treated (m3/year)", min_value=0, value=0, step=1000)

            # --- Water & Sewage ---
            st.subheader("Water & Sewage")
            water_supply_m3 = st.number_input("Total Water Supplied (m3/year)", min_value=0, value=0, step=1000)
            energy_for_water_mwh = st.number_input("Energy Used for Water Supply & Treatment (MWh/year)", min_value=0, value=0, step=10)

            # --- Urban Green / Other ---
            st.subheader("Urban Green / Other")
            urban_green_area_ha = st.number_input("Urban Green Area (hectares)", min_value=0, value=0, step=1)
            renewable_energy_mwh = st.number_input("Renewable Energy Generated in City (MWh/year)", min_value=0, value=0, step=10)

            # --- Optional Files / Verification ---
            file_upload = st.file_uploader("Attach supporting documents (optional)", type=["pdf", "xlsx", "csv"])

            submit_cap = st.form_submit_button("Generate GHG Inventory")

            if submit_cap:
                # Save raw data into CAP dataframe
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
                    "Industrial Diesel (tons)": industrial_fuel_diesel_tons,
                    "Industrial Petrol (tons)": industrial_fuel_petrol_tons,
                    "Industrial CNG (tons)": industrial_fuel_cng_tons,
                    "Industrial LPG (tons)": industrial_fuel_lpg_tons,
                    "Industrial Energy (MWh)": industrial_energy_mwh,
                    "Residential Energy (MWh)": residential_energy_mwh,
                    "Commercial Energy (MWh)": commercial_energy_mwh,
                    "Public Buildings Energy (MWh)": public_buildings_energy_mwh,
                    "Municipal Solid Waste (tons)": municipal_solid_waste_tons,
                    "Waste Landfilled (%)": fraction_landfilled,
                    "Waste Composted (%)": fraction_composted,
                    "Wastewater Treated (m3)": wastewater_volume_m3,
                    "Water Supplied (m3)": water_supply_m3,
                    "Energy for Water (MWh)": energy_for_water_mwh,
                    "Urban Green Area (ha)": urban_green_area_ha,
                    "Renewable Energy (MWh)": renewable_energy_mwh,
                    "Submission Date": datetime.now()
                }

                df_cap = st.session_state.cap_data.copy()
                if not df_cap.empty and city in df_cap["City Name"].values:
                    for k, v in raw_row.items():
                        df_cap.loc[df_cap["City Name"] == city, k] = v
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([raw_row])], ignore_index=True)

                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE, index=False)
                st.session_state.last_updated = datetime.now()

                st.success(f"Raw data for {city} submitted successfully! Redirecting to GHG Inventory dashboard...")
                st.session_state.menu = "GHG Inventory"  # Redirect to GHG Inventory page
                st.experimental_rerun()

        # --- Reset Button ---
        if st.button("Reset All Data", key="reset_cap_data"):
            reset_all_data()

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu == "GHG Inventory":
    st.header("GHG Inventory")

    if not st.session_state.authenticated:
        admin_login()
    else:
        df_cap = st.session_state.cap_data.copy()
        if df_cap.empty:
            st.warning("No CAP data available. Please submit raw data first.")
        else:
            city = st.selectbox("Select City to View GHG Inventory", list(df_cap["City Name"].unique()))
            city_row = df_cap[df_cap["City Name"] == city].iloc[0]

            # --- Emission Factors (EF) ---
            EF_electricity = 0.82  # tCO2e/MWh
            EF_diesel_vehicle = 2.68 / 1000
            EF_petrol_vehicle = 2.31 / 1000
            EF_cng_vehicle = 2.74 / 1000
            EF_lpg_vehicle = 1.51 / 1000
            EF_electric_vehicle = 0
            EF_industrial_fuel = {"Diesel": 2.68, "Petrol": 2.31, "CNG": 2.74, "LPG": 1.51}
            EF_waste_landfill = 1.0 / 10
            EF_waste_compost = 0.1 / 10
            EF_wastewater = 0.25 / 1000
            EF_water_energy = 0.82

            # --- Calculate Sector Emissions ---
            emissions = {}
            emissions["Residential Energy"] = city_row.get("Residential Energy (MWh)",0) * EF_electricity
            emissions["Commercial Energy"] = city_row.get("Commercial Energy (MWh)",0) * EF_electricity
            emissions["Industrial Energy"] = city_row.get("Industrial Energy (MWh)",0) * EF_electricity
            emissions["Streetlights & Public Buildings"] = (
                city_row.get("Streetlights Energy (MWh)",0) + city_row.get("Public Buildings Energy (MWh)",0)
            ) * EF_electricity

            emissions["Transport Diesel"] = city_row.get("Diesel Vehicles",0) * city_row.get("Avg km/Vehicle",0) * EF_diesel_vehicle
            emissions["Transport Petrol"] = city_row.get("Petrol Vehicles",0) * city_row.get("Avg km/Vehicle",0) * EF_petrol_vehicle
            emissions["Transport CNG"] = city_row.get("CNG Vehicles",0) * city_row.get("Avg km/Vehicle",0) * EF_cng_vehicle
            emissions["Transport LPG"] = city_row.get("LPG Vehicles",0) * city_row.get("Avg km/Vehicle",0) * EF_lpg_vehicle
            emissions["Transport Electric"] = city_row.get("Electric Vehicles",0) * city_row.get("Avg km/Vehicle",0) * EF_electric_vehicle

            emissions["Industrial Diesel"] = city_row.get("Industrial Diesel (tons)",0) * EF_industrial_fuel["Diesel"]
            emissions["Industrial Petrol"] = city_row.get("Industrial Petrol (tons)",0) * EF_industrial_fuel["Petrol"]
            emissions["Industrial CNG"] = city_row.get("Industrial CNG (tons)",0) * EF_industrial_fuel["CNG"]
            emissions["Industrial LPG"] = city_row.get("Industrial LPG (tons)",0) * EF_industrial_fuel["LPG"]

            waste_total = city_row.get("Municipal Solid Waste (tons)",0)
            emissions["Waste Landfilled"] = waste_total * (city_row.get("Waste Landfilled (%)",0)/100) * EF_waste_landfill
            emissions["Waste Composted"] = waste_total * (city_row.get("Waste Composted (%)",0)/100) * EF_waste_compost
            emissions["Wastewater"] = city_row.get("Wastewater Treated (m3)",0) * EF_wastewater

            emissions["Water Energy"] = city_row.get("Energy for Water (MWh)",0) * EF_water_energy
            emissions["Urban Green / Offsets"] = -1 * city_row.get("Renewable Energy (MWh)",0) * EF_electricity

            # --- Display Metrics ---
            st.subheader(f"{city} — Sector-wise GHG Emissions (tCO2e)")
            emissions_df = pd.DataFrame({
                "Sector": list(emissions.keys()),
                "Emissions (tCO2e)": list(emissions.values())
            })

            # Total Emissions
            total_emissions = sum(emissions.values())
            st.metric("Total City GHG Emissions (tCO2e)", format(total_emissions, ","))

            # Bar Chart
            fig_bar = px.bar(
                emissions_df.sort_values("Emissions (tCO2e)", ascending=False),
                x="Sector",
                y="Emissions (tCO2e)",
                text=emissions_df["Emissions (tCO2e)"].apply(lambda x: format(int(x), ",")),
                color_discrete_sequence=["#3E6BE6"]
            )
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie Chart
            fig_pie = px.pie(
                emissions_df,
                names="Sector",
                values="Emissions (tCO2e)",
                title="Sector-wise GHG Contribution",
            )
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Detailed Table
            st.write("### Detailed Emissions Table")
            st.table(emissions_df.assign(**{
                "Emissions (tCO2e)": lambda d: d["Emissions (tCO2e)"].map(lambda x: format(int(x), ","))
            }))
