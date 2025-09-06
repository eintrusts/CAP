# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

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
[data-testid="stAppViewContainer"] {background-color: #1e1e1e; color: #f0f2f0; font-family: 'Inter', sans-serif;}
[data-testid="stSidebar"] {background-color: #060c06; color: #f0f2f0; font-family: 'Inter', sans-serif;}
.stButton>button {background-color:#54c750; color:#f0f2f0; border-radius:8px; height:40px;}
.stButton>button:hover {background-color:#3e3f3e;}
[data-testid="stMetricValue"] {color:#54c750; font-weight:700; font-size:26px;}
.stExpander>div>div>div>div {background-color:#060c06; color:#f0f2f0;}
input, textarea, select {background-color:#060c06; color:#f0f2f0; border-color:#54c750;}
table th {background-color:#54c750; color:white;}
.stCard {background-color:#060c06; padding:15px; border-radius:10px; box-shadow: 0px 0px 15px rgba(0,0,0,0.5);}
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
    not_started = df[df["CAP Status"].str.lower() == "not started"].shape[0]
    in_progress = df[df["CAP Status"].str.lower() == "in progress"].shape[0]
    completed = df[df["CAP Status"].str.lower() == "completed"].shape[0]
    total_status = not_started + in_progress + completed

    st.markdown("### CAP Status Overview")

    # Define columns
    c1, c2, c3, c4 = st.columns(4)

    # Card styling
    block_style = """
        background-color:#1E1E2F;
        padding:20px;
        border-radius:12px;
        text-align:center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    """
    title_style = "color:#E6E6E6; margin:0; font-size:16px;"
    value_style = "font-size:28px; font-weight:bold; color:#54c750; margin:5px 0 0 0;"

    # Metrics dictionary
    metrics = {
        "Not Started": not_started,
        "In Progress": in_progress,
        "Completed": completed,
        "Total": total_status
    }

    # Render cards
    for col, (title, val) in zip([c1, c2, c3, c4], metrics.items()):
        col.markdown(
            f"<div style='{block_style}'><h3 style='{title_style}'>{title}</h3><p style='{value_style}'>{format_indian_number(val)}</p></div>",
            unsafe_allow_html=True
        )
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

    st.subheader(f"{city} — Overview")
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row, 'District')}")
        st.write(f"**Population (as per census 2011):** {format_population(safe_get(meta_row, 'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row, 'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row, 'CAP Status')}")
    else:
        st.write(f"**District:** {cities_districts.get(city, '—')}")

    if not df_cap.empty and city in df_cap["City Name"].values:
        cap_row = df_cap[df_cap["City Name"] == city].iloc[0]
        sector_cols = [c for c in cap_row.index if c.endswith(" Emissions (tCO2e)")]
        sectors = {c.replace(" Emissions (tCO2e)", ""): max(float(cap_row[c]), 0) for c in sector_cols}

        if sectors:
            chart_df = pd.DataFrame({"Sector": list(sectors.keys()), "Emissions": list(sectors.values())})

            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text=chart_df["Emissions"].apply(lambda x: format_indian_number(round(x))),
                             title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v: format_indian_number(round(v)))))

        last_mod = st.session_state.last_updated or datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
        st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")

        # PDF Download
        if PDF_AVAILABLE:
            st.subheader("Download GHG Inventory Report")
            with st.form("pdf_form"):
                user_name = st.text_input("Your Full Name")
                user_email = st.text_input("Your Work Email")
                user_contact = st.text_input("Contact Number")
                submit_pdf = st.form_submit_button("Generate PDF")
                if submit_pdf:
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4)
                    elements = []
                    styles = getSampleStyleSheet()
                    elements.append(Paragraph(f"{city} — GHG Inventory Report", styles["Title"]))
                    elements.append(Spacer(1, 12))
                    data = [["Sector", "Emissions (tCO2e)"]] + [[s, format_indian_number(round(v))] for s, v in sectors.items()]
                    t = Table(data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3E6BE6")),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.white)
                    ]))
                    elements.append(t)
                    doc.build(elements)
                    buffer.seek(0)
                    st.download_button("Download PDF", buffer, file_name=f"{city}_GHG_Report.pdf", mime="application/pdf")
        else:
            st.warning("PDF generation not available. Install reportlab library.")

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

            # --- Fuel Consumption (Transport + Industry) ---
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

            # --- Buildings & Commercial Activity ---
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

            # --- Water Supply & Sewage ---
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
