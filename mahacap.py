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
    "City Name", "District", "Population", "ULB Category",
    "CAP Status", "GHG Emissions", "Environment Department Exist",
    "Department Name", "Head Name", "Department Email"
]
cap_cols = []

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# Remove Raigad Council (case-insensitive)
st.session_state.data = st.session_state.data[~st.session_state.data["City Name"].str.contains("Raigad Council", case=False, na=False)]

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

if st.session_state.authenticated and st.sidebar.button("CAP Preparation"):
    st.session_state.menu = "CAP Preparation"

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
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

    # --- Reported GHG ---
    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig_reported = px.bar(
            df.sort_values("GHG Emissions", ascending=False),
            x="City Name",
            y="GHG Emissions",
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
            x="City Name",
            y="Estimated GHG Emissions",
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
                    st.download_button("Download PDF", buffer,
                                       file_name=f"{city}_GHG_Report.pdf",
                                       mime="application/pdf")
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
elif menu == "CAP Preparation":
    st.header("CAP : Data Collection")

    if not st.session_state.authenticated:
        admin_login()
    else:
        st.markdown("""
        Collect detailed city-level activity data for generating a comprehensive GHG inventory as per
        GPC/C40/ICLEI guidelines.
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

                st.success(f"Raw data for {city} submitted successfully!")

                # Instead of experimental_rerun, just set menu to GHG Inventory
                st.session_state.menu = "GHG Inventory"

# ---------------------------
# GHG Inventory Page
# ---------------------------
if menu == "GHG Inventory":  # Make sure it's exactly this
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

            # --- Calculate Sector Emissions ---
            # ... your existing emissions calculations ...

            # Display charts
            st.subheader(f"{city} — Sector-wise GHG Emissions (tCO2e)")
            # ... your existing charts and table ...

            # ---------------------------
            # Suggested Actions Section (STRICTLY HERE)
            # ---------------------------
            if st.button("Show Suggested Actions to Achieve Net Zero by 2050"):
                st.subheader("Suggested Actions per Sector (Short, Mid, Long-term Goals)")

                # Example goals dictionary
                goals = {
                    "Residential Energy": {
                        "Short-term (2030)": [
                            "1. Implement energy-efficient lighting (Priority 1)",
                            "2. Promote rooftop solar adoption (Priority 2)"
                        ],
                        "Mid-term (2040)": [
                            "1. Incentivize heat pump systems (Priority 1)"
                        ],
                        "Long-term (2050)": [
                            "1. Achieve 100% renewable electricity in households (Priority 1)"
                        ]
                    }
                    # Add other sectors here...
                }

                # Build table
                table_data = []
                for sector, s_goals in goals.items():
                    max_len = max(len(s_goals.get("Short-term (2030)", [])),
                                  len(s_goals.get("Mid-term (2040)", [])),
                                  len(s_goals.get("Long-term (2050)", [])))
                    for i in range(max_len):
                        row = {
                            "Sector": sector if i == 0 else "",
                            "Short-term (2030)": s_goals.get("Short-term (2030)", [])[i] if i < len(s_goals.get("Short-term (2030)", [])) else "",
                            "Mid-term (2040)": s_goals.get("Mid-term (2040)", [])[i] if i < len(s_goals.get("Mid-term (2040)", [])) else "",
                            "Long-term (2050)": s_goals.get("Long-term (2050)", [])[i] if i < len(s_goals.get("Long-term (2050)", [])) else ""
                        }
                        table_data.append(row)
                
                st.table(pd.DataFrame(table_data))
                
# ---------------------------
# Suggested Actions Button
# ---------------------------
if st.button("View Suggested Actions to Achieve Net Zero by 2050"):
    st.header("Suggested Actions to Achieve Net Zero by 2050")
    st.markdown("""
    The following sector-wise actions are recommended based on the GHG inventory of the selected city.  
    Actions are categorized into **Short-term (by 2030)**, **Mid-term (by 2040)**, and **Long-term (by 2050)** goals.
    """)

    # ---------------------------
    # Define Sector-wise Actions
    # ---------------------------
    actions_data = {
        "Residential Energy": {
            "Short-term (2030)": [
                "1. Promote rooftop solar adoption", "2. Implement energy-efficient appliances program",
                "3. Launch LED replacement scheme", "4. Conduct residential energy audits",
                "5. Implement smart metering", "6. Subsidize home insulation", "7. Promote rooftop rainwater harvesting",
                "8. Public awareness campaigns on energy saving", "9. Encourage behavioural change programs", "10. Set local EE building codes"
            ],
            "Mid-term (2040)": [
                "1. Net-zero-ready residential buildings", "2. 50% homes on renewable energy",
                "3. Advanced energy storage adoption", "4. Incentivize electric heating", "5. Retrofit existing buildings",
                "6. Demand-response energy programs", "7. Local microgrid development", "8. Smart home automation for efficiency",
                "9. Integrate EV charging infrastructure in homes", "10. Phase out fossil-fuel heating systems"
            ],
            "Long-term (2050)": [
                "1. 100% residential renewable energy", "2. Fully decarbonized buildings", "3. Zero-carbon appliance standards",
                "4. Smart energy-positive homes", "5. Advanced energy storage integration", "6. Building-integrated PV widespread",
                "7. Circular economy in building materials", "8. Smart urban energy networks", "9. Complete phase-out of fossil fuels in homes",
                "10. Fully automated residential energy management"
            ]
        },
        "Commercial Energy": {
            "Short-term (2030)": [
                "1. Conduct commercial energy audits", "2. Retrofit lighting to LEDs", "3. Implement smart thermostats",
                "4. Incentivize rooftop solar on commercial buildings", "5. Promote energy-efficient HVAC systems",
                "6. Implement green lease agreements", "7. Awareness campaigns for businesses", "8. Encourage energy reporting",
                "9. Subsidize building envelope improvements", "10. Introduce energy efficiency labeling"
            ],
            "Mid-term (2040)": [
                "1. Net-zero-ready commercial buildings", "2. 50% energy from renewables", "3. Smart energy management systems",
                "4. Advanced HVAC retrofits", "5. Integration with district energy networks", "6. Energy performance benchmarking",
                "7. EV charging for commercial fleets", "8. Incentivize building retrofits", "9. Automated energy analytics", "10. Waste heat recovery systems"
            ],
            "Long-term (2050)": [
                "1. Fully decarbonized commercial sector", "2. 100% renewable energy consumption", "3. Energy-positive buildings",
                "4. Zero-carbon HVAC and lighting", "5. Full integration with smart grid", "6. Circular energy use practices",
                "7. AI-driven energy optimization", "8. Complete electrification of commercial processes", "9. Sustainable materials adoption", "10. Continuous monitoring & optimization"
            ]
        },
        "Industrial Energy": {
            "Short-term (2030)": [
                "1. Conduct industrial energy audits", "2. Upgrade to high-efficiency motors", "3. Implement process optimization",
                "4. Waste heat recovery", "5. Switch to cleaner fuels", "6. Introduce energy management systems", "7. Employee training on energy efficiency",
                "8. Monitor & report energy use", "9. Install sub-metering", "10. Promote circular economy practices"
            ],
            "Mid-term (2040)": [
                "1. Electrify industrial processes", "2. Deploy large-scale onsite renewables", "3. Carbon capture pilot projects",
                "4. Industrial microgrids", "5. Smart automation for energy efficiency", "6. Sustainable material sourcing",
                "7. Advanced process optimization", "8. Digital twins for energy monitoring", "9. Integrate with district energy networks", "10. Minimize industrial waste generation"
            ],
            "Long-term (2050)": [
                "1. Fully decarbonized industry", "2. 100% renewable energy use", "3. Advanced carbon capture and utilization",
                "4. Zero-waste manufacturing", "5. Circular production models", "6. AI-driven process optimization",
                "7. Energy-positive industrial complexes", "8. Electrification of all processes", "9. Industry-wide net-zero compliance", "10. Continuous emissions monitoring"
            ]
        },
        "Transport": {
            "Short-term (2030)": [
                "1. Promote public transport", "2. Implement EV incentives", "3. Introduce low-emission zones", "4. Fuel efficiency standards for vehicles",
                "5. Bicycle infrastructure development", "6. Awareness campaigns on modal shift", "7. Promote carpooling", "8. EV charging infrastructure expansion",
                "9. Efficient logistics planning", "10. Promote hybrid vehicles"
            ],
            "Mid-term (2040)": [
                "1. 50% EV adoption in urban fleet", "2. Advanced public transport electrification", "3. Hydrogen fuel pilot projects",
                "4. Smart traffic management systems", "5. Freight electrification", "6. Integration with MaaS (Mobility as a Service)",
                "7. Promote EV buses", "8. Phase-out of diesel taxis", "9. Implement low-carbon transport corridors", "10. Urban logistics optimization"
            ],
            "Long-term (2050)": [
                "1. Fully electrified transport sector", "2. Zero-emission public transport", "3. Hydrogen for heavy transport", "4. Smart integrated mobility networks",
                "5. Autonomous EV deployment", "6. Phase-out of fossil fuel vehicles", "7. Net-zero freight systems", "8. Mobility hubs with renewables",
                "9. Advanced battery and hydrogen infrastructure", "10. Smart demand-responsive transport"
            ]
        },
        "Waste": {
            "Short-term (2030)": [
                "1. Segregate waste at source", "2. Promote composting", "3. Reduce landfill dependency", "4. Awareness campaigns on recycling",
                "5. Introduce waste collection efficiency improvements", "6. Industrial waste audits", "7. Promote waste-to-energy pilots",
                "8. Encourage circular economy", "9. Implement recycling incentives", "10. Monitor methane emissions"
            ],
            "Mid-term (2040)": [
                "1. 50% reduction in landfill waste", "2. Expand composting programs", "3. Optimize waste-to-energy plants",
                "4. Industrial waste minimization", "5. Smart waste collection", "6. Advanced recycling technology adoption",
                "7. Implement circular material loops", "8. Continuous methane monitoring", "9. Promote biogas utilization", "10. Phase-out of non-recyclables"
            ],
            "Long-term (2050)": [
                "1. Zero waste to landfill", "2. Full circular economy integration", "3. Net-zero emissions from waste sector",
                "4. Advanced material recovery", "5. Complete biogas adoption", "6. Methane capture optimization",
                "7. Smart waste management systems", "8. Decentralized composting and recycling", "9. Waste sector electrification", "10. Continuous monitoring & optimization"
            ]
        },
        "Water & Sewage": {
            "Short-term (2030)": [
                "1. Optimize water pumping energy", "2. Improve wastewater treatment efficiency", "3. Promote water conservation", "4. Leak detection and repair",
                "5. Awareness campaigns on water saving", "6. Incentivize rainwater harvesting", "7. Install energy-efficient pumps", "8. Use renewable energy in water treatment",
                "9. Reduce sewer losses", "10. Monitor energy consumption"
            ],
            "Mid-term (2040)": [
                "1. Electrify water treatment plants", "2. Implement smart water networks", "3. Increase reuse of treated wastewater",
                "4. Solar-powered pumping stations", "5. Advanced monitoring & automation", "6. Optimize chemical usage",
                "7. Reduce non-revenue water", "8. Integrate water-energy nexus programs", "9. Smart metering for consumers", "10. Promote decentralized water systems"
            ],
            "Long-term (2050)": [
                "1. Net-zero energy water & sewage systems", "2. 100% renewable energy powered plants", "3. Circular water use",
                "4. Smart water-energy integration", "5. Zero-discharge systems", "6. AI-driven optimization", "7. Decentralized treatment adoption",
                "8. Full electrification of processes", "9. Energy-positive wastewater treatment", "10. Continuous monitoring & optimization"
            ]
        }
    }

    # ---------------------------
    # Convert to DataFrame for Display
    # ---------------------------
    for sector, goals in actions_data.items():
        st.subheader(sector)
        df_actions = pd.DataFrame({
            "Short-term (2030)": goals["Short-term (2030)"],
            "Mid-term (2040)": goals["Mid-term (2040)"],
            "Long-term (2050)": goals["Long-term (2050)"]
        })
        st.table(df_actions)

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------
# Create CAP PDF
# ---------------------------
if st.button("Create CAP PDF Report"):
    if not PDF_AVAILABLE:
        st.warning("PDF generation not available. Install reportlab library.")
    else:
        st.success("Generating CAP PDF...")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        style_title = styles['Title']
        style_heading = styles['Heading2']
        style_normal = styles['Normal']

        # --- Title ---
        elements.append(Paragraph("City Climate Action Plan (CAP) Report", style_title))
        elements.append(Spacer(1, 12))

        # --- GHG Inventory Table ---
        elements.append(Paragraph("GHG Inventory", style_heading))
        ghg_data = [["Sector", "Emissions (tCO2e)"]] + list(emissions_df.itertuples(index=False, name=None))
        t_ghg = Table(ghg_data, hAlign="LEFT")
        t_ghg.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3E6BE6")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black)
        ]))
        elements.append(t_ghg)
        elements.append(Spacer(1, 24))

        # --- Suggested Actions ---
        elements.append(Paragraph("Suggested Actions to Achieve Net Zero by 2050", style_heading))
        for sector, goals in actions_data.items():
            elements.append(Paragraph(f"{sector}", styles['Heading3']))
            
            # Prepare data for table: Action #, Short, Mid, Long
            max_actions = max(len(goals['Short-term (2030)']),
                              len(goals['Mid-term (2040)']),
                              len(goals['Long-term (2050)']))
            
            table_data = [["#", "Short-term (2030)", "Mid-term (2040)", "Long-term (2050)"]]
            for i in range(max_actions):
                table_data.append([
                    i+1,
                    goals['Short-term (2030)'][i] if i < len(goals['Short-term (2030)']) else "",
                    goals['Mid-term (2040)'][i] if i < len(goals['Mid-term (2040)']) else "",
                    goals['Long-term (2050)'][i] if i < len(goals['Long-term (2050)']) else ""
                ])
            
            t_actions = Table(table_data, hAlign="LEFT")
            t_actions.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E67E22")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('VALIGN', (0,0), (-1,-1), 'TOP')
            ]))
            elements.append(t_actions)
            elements.append(Spacer(1, 12))
            elements.append(PageBreak())

        # --- Build PDF ---
        doc.build(elements)
        buffer.seek(0)

        st.download_button(
            label="Download CAP Report (PDF)",
            data=buffer,
            file_name="CAP_Report.pdf",
            mime="application/pdf"
        )
