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
# Home Page: Vulnerability Scores
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

    # --- Environmental Vulnerability Score (EVS) ---
    evs_cols = ["GHG Emissions", "Municipal Solid Waste (tons)", "Wastewater Treated (m3)"]
    for col in evs_cols:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    max_vals_env = {col: df[col].max() or 1 for col in evs_cols}
    df["EVS"] = (
        df["GHG Emissions"]/max_vals_env["GHG Emissions"]*0.5 +
        df["Municipal Solid Waste (tons)"]/max_vals_env["Municipal Solid Waste (tons)"]*0.25 +
        df["Wastewater Treated (m3)"]/max_vals_env["Wastewater Treated (m3)"]*0.25
    ) * 100

    # --- Social Vulnerability Score (SVS) ---
    social_factors = {
        "Population": 0.3,
        "Households": 0.2,
        "Urbanization Rate (%)": 0.2,
        "Literacy Rate (%)": 0.15,
        "Poverty Rate (%)": 0.15
    }

    for col in social_factors:
        if col not in df.columns:
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    max_vals_social = {col: df[col].max() or 1 for col in social_factors}

    df["SVS"] = (
        (df["Population"]/max_vals_social["Population"])*0.3 +
        (df["Households"]/max_vals_social["Households"])*0.2 +
        (df["Urbanization Rate (%)"]/max_vals_social["Urbanization Rate (%)"])*0.2 +
        (1 - df["Literacy Rate (%)"]/max_vals_social["Literacy Rate (%)"])*0.15 +
        (df["Poverty Rate (%)"]/max_vals_social["Poverty Rate (%)"])*0.15
    ) * 100

    # --- Vulnerability Chart ---
    import plotly.express as px
    vuln_df = df[["City Name", "EVS", "SVS"]].melt(id_vars="City Name", var_name="Score Type", value_name="Score")

    fig_vuln = px.bar(
        vuln_df,
        x="City Name",
        y="Score",
        color="Score Type",
        barmode="group",
        text=vuln_df["Score"].apply(lambda x: f"{round(x,1)}"),
        title="City Vulnerability Scores (Environmental vs Social)"
    )
    fig_vuln.update_layout(
        plot_bgcolor="#0f0f10",
        paper_bgcolor="#0f0f10",
        font_color="#E6E6E6",
        xaxis_title=None,
        yaxis_title="Vulnerability Score (0-100)"
    )
    st.plotly_chart(fig_vuln, use_container_width=True)

# ---------------------------
# City Information Page
# ---------------------------
elif menu == "City Information":
    st.header("City Information")
    df_meta = st.session_state.data.copy()
    city = st.selectbox("Select City", list(cities_districts.keys()))

    if not df_meta.empty and city in df_meta["City Name"].values:
        row = df_meta[df_meta["City Name"] == city].iloc[0]

        # -------- BASIC INFO --------
        st.subheader("Basic Information")
        st.table(pd.DataFrame({
            "Attribute": [
                "District", "ULB Category", "Population", "Area (sq.km)",
                "Density (per sq.km)", "Est. Year", "CAP Status"
            ],
            "Value": [
                row.get("District", "—"),
                row.get("ULB Category", "—"),
                format_indian_number(row.get("Population", 0)),
                row.get("Area (sq.km)", "—"),
                round(row.get("Population", 0)/row.get("Area (sq.km)", 1), 2) if row.get("Area (sq.km)", 0) else "—",
                row.get("Est. Year", "—"),
                row.get("CAP Status", "—"),
            ]
        }))

        # -------- ENVIRONMENTAL INFO --------
        st.subheader("Environmental Information")
        st.table(pd.DataFrame({
            "Indicator": [
                "Total GHG Emissions (tCO2e)",
                "Per Capita Emissions (tCO2e)",
                "Renewable Energy (MWh/year)",
                "Urban Green Area (ha)",
                "Municipal Solid Waste (tons/year)",
                "Waste Landfilled (%)",
                "Waste Composted (%)",
                "Wastewater Treated (m³/year)",
            ],
            "Value": [
                format_indian_number(row.get("GHG Emissions", 0)),
                round(row.get("GHG Emissions", 0)/row.get("Population", 1), 2) if row.get("Population", 0) else "—",
                format_indian_number(row.get("Renewable Energy (MWh)", 0)),
                format_indian_number(row.get("Urban Green Area (ha)", 0)),
                format_indian_number(row.get("Municipal Solid Waste (tons)", 0)),
                f"{row.get('Waste Landfilled (%)', 0)}%",
                f"{row.get('Waste Composted (%)', 0)}%",
                format_indian_number(row.get("Wastewater Treated (m3)", 0)),
            ]
        }))

        # -------- SOCIAL INFO --------
        st.subheader("Social Information")
        st.table(pd.DataFrame({
            "Indicator": [
                "Male Population", "Female Population", "Children (0–6 Male)", "Children (0–6 Female)",
                "Overall Literacy (%)", "Male Literacy (%)", "Female Literacy (%)", "Migrant (%)", "Slum (%)"
            ],
            "Value": [
                format_indian_number(row.get("Males", 0)),
                format_indian_number(row.get("Females", 0)),
                format_indian_number(row.get("Children Male", 0)),
                format_indian_number(row.get("Children Female", 0)),
                f"{row.get('Literacy (%)', 0)}%",
                f"{row.get('Male Literacy (%)', 0)}%",
                f"{row.get('Female Literacy (%)', 0)}%",
                f"{row.get('Migrant (%)', 0)}%",
                f"{row.get('Slum (%)', 0)}%"
            ]
        }))

        # -------- CONTACT INFO --------
        st.subheader("Contact Information")
        st.table(pd.DataFrame({
            "Field": ["Department Exist", "Department Name", "Email", "Contact Number", "Website"],
            "Details": [
                row.get("Department Exist", "—"),
                row.get("Department Name", "—"),
                row.get("Email", "—"),
                row.get("Contact Number", "—"),
                row.get("Website", "—"),
            ]
        }))


# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin":
    st.header("Admin Board")
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.subheader("Add / Update City Data")

        with st.form("admin_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))

            # ---------------- BASIC INFO ----------------
            st.markdown("### Basic Information")
            population = st.number_input("Population (2011 Census)", min_value=0, step=1000)
            area = st.number_input("Geographical Area (sq. km)", min_value=0.0, step=0.1)
            ulb_category = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council", "Nagar Panchayat"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            est_year = st.number_input("Year of Establishment of ULB", min_value=1800, max_value=2100, step=1)

            # ---------------- ENVIRONMENTAL INFO ----------------
            st.markdown("### Environmental Information")
            ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, step=100.0)
            renewable_energy = st.number_input("Renewable Energy Generated (MWh/year)", min_value=0, step=10)
            green_area = st.number_input("Urban Green Area (hectares)", min_value=0, step=1)
            solid_waste = st.number_input("Municipal Solid Waste (tons/year)", min_value=0, step=10)
            waste_landfilled = st.number_input("Waste Landfilled (%)", min_value=0.0, max_value=100.0, step=0.1)
            waste_composted = st.number_input("Waste Composted (%)", min_value=0.0, max_value=100.0, step=0.1)
            wastewater = st.number_input("Wastewater Treated (m³/year)", min_value=0, step=1000)

            # ---------------- SOCIAL INFO ----------------
            st.markdown("### Social Information")
            males = st.number_input("Male Population", min_value=0, step=100)
            females = st.number_input("Female Population", min_value=0, step=100)
            children_m = st.number_input("Children (0–6) Male", min_value=0, step=10)
            children_f = st.number_input("Children (0–6) Female", min_value=0, step=10)
            literacy = st.number_input("Overall Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
            literacy_m = st.number_input("Male Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
            literacy_f = st.number_input("Female Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
            bpl = st.number_input("BPL Households (%)", min_value=0.0, max_value=100.0, step=0.1)
            migrant = st.number_input("Migrant Population (%)", min_value=0.0, max_value=100.0, step=0.1)
            slum = st.number_input("Slum Population (%)", min_value=0.0, max_value=100.0, step=0.1)

            # ---------------- CONTACT INFO ----------------
            st.markdown("### Contact Information")
            dept_exist = st.selectbox("Environment Department Exist?", ["Yes", "No"])
            dept_name = st.text_input("Department Name")
            dept_email = st.text_input("Department Email")
            contact_number = st.text_input("Contact Number")
            official_website = st.text_input("Official Website")

            submit_admin = st.form_submit_button("Save / Update")

            if submit_admin:
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "—"),
                    "Population": population or 0,
                    "Area (sq.km)": area or 0,
                    "ULB Category": ulb_category or "—",
                    "CAP Status": cap_status or "—",
                    "Est. Year": est_year or "—",
                    "GHG Emissions": ghg_val or 0,
                    "Renewable Energy (MWh)": renewable_energy or 0,
                    "Urban Green Area (ha)": green_area or 0,
                    "Municipal Solid Waste (tons)": solid_waste or 0,
                    "Waste Landfilled (%)": waste_landfilled or 0,
                    "Waste Composted (%)": waste_composted or 0,
                    "Wastewater Treated (m3)": wastewater or 0,
                    "Males": males or 0,
                    "Females": females or 0,
                    "Children Male": children_m or 0,
                    "Children Female": children_f or 0,
                    "Literacy (%)": literacy or 0,
                    "Male Literacy (%)": literacy_m or 0,
                    "Female Literacy (%)": literacy_f or 0,
                    "Migrant (%)": migrant or 0,
                    "Slum (%)": slum or 0,
                    "Department Exist": dept_exist or "—",
                    "Department Name": dept_name or "—",
                    "Email": dept_email or "—",
                    "Contact Number": contact_number or "—",
                    "Website": official_website or "—",
                }
                df_meta = st.session_state.data.copy()
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"] == city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE, index=False)
                st.success(f"{city} data updated successfully!")
                
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
