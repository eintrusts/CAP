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
    st.header("CAP : Raw Data Collection for Comprehensive GHG Inventory")

    if not st.session_state.authenticated:
        admin_login()
    else:
        st.markdown("""
        Collect detailed city-level activity data to generate a comprehensive GHG inventory.
        Data is collected as per GPC/C40/ICLEI guidelines. Emissions are calculated automatically.
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
            residential_electricity_mwh = st.number_input("Residential Electricity (MWh/year)", min_value=0, value=0, step=100)
            commercial_electricity_mwh = st.number_input("Commercial Electricity (MWh/year)", min_value=0, value=0, step=100)
            industrial_electricity_mwh = st.number_input("Industrial Electricity (MWh/year)", min_value=0, value=0, step=100)
            streetlights_energy_mwh = st.number_input("Streetlights Energy (MWh/year)", min_value=0, value=0, step=100)
            public_buildings_energy_mwh = st.number_input("Public Buildings Energy (MWh/year)", min_value=0, value=0, step=100)
            renewable_energy_mwh = st.number_input("Renewable Energy Produced in City (MWh/year)", min_value=0, value=0, step=10)

            # --- Transport Table ---
            st.subheader("Transport Fleet Data")
            transport_data = st.experimental_data_editor(
                pd.DataFrame({
                    "Vehicle Type": ["Two-Wheeler", "Car/Taxi", "Bus", "Truck", "Auto-rickshaw", "Metro/Rail (if any)"],
                    "Diesel Vehicles": [0]*6,
                    "Petrol Vehicles": [0]*6,
                    "CNG Vehicles": [0]*6,
                    "LPG Vehicles": [0]*6,
                    "Electric Vehicles": [0]*6,
                    "Average km/year": [0]*6
                }),
                num_rows="fixed",
            )

            # --- Municipal Fleet Table ---
            st.subheader("Municipal / Government Fleet")
            municipal_data = st.experimental_data_editor(
                pd.DataFrame({
                    "Vehicle Type": ["Truck", "Bus", "Service Vehicles"],
                    "Diesel Vehicles": [0]*3,
                    "Petrol Vehicles": [0]*3,
                    "CNG Vehicles": [0]*3,
                    "Electric Vehicles": [0]*3,
                    "Average km/year": [0]*3
                }),
                num_rows="fixed",
            )

            # --- Industries Table ---
            st.subheader("Industrial & Commercial Fuel/Energy Use")
            industry_data = st.experimental_data_editor(
                pd.DataFrame({
                    "Industry Name": ["Industry 1", "Industry 2", "Industry 3"],
                    "Diesel (tons/year)": [0]*3,
                    "Petrol (tons/year)": [0]*3,
                    "CNG (tons/year)": [0]*3,
                    "LPG (tons/year)": [0]*3,
                    "Electricity (MWh/year)": [0]*3
                }),
                num_rows="fixed",
            )

            # --- Waste ---
            st.subheader("Waste Management")
            municipal_solid_waste_tons = st.number_input("Municipal Solid Waste Generated (tons/year)", min_value=0, value=0, step=10)
            fraction_landfilled = st.number_input("Fraction Landfilled (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            fraction_composted = st.number_input("Fraction Composted (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            wastewater_volume_m3 = st.number_input("Wastewater Treated (m3/year)", min_value=0, value=0, step=1000)

            # --- Water & Sewage ---
            st.subheader("Water & Sewage")
            water_supply_m3 = st.number_input("Total Water Supplied (m3/year)", min_value=0, value=0, step=1000)
            energy_for_water_mwh = st.number_input("Energy for Water Supply & Treatment (MWh/year)", min_value=0, value=0, step=10)

            # --- Urban Green / Other ---
            st.subheader("Urban Green / Offsets")
            urban_green_area_ha = st.number_input("Urban Green Area (hectares)", min_value=0, value=0, step=1)

            # --- Supporting Documents ---
            file_upload = st.file_uploader("Attach supporting documents (optional)", type=["pdf", "xlsx", "csv"])

            submit_cap = st.form_submit_button("Submit Raw Data and Generate GHG Inventory")

            if submit_cap:
                # Save raw data
                raw_row = {
                    "City Name": city,
                    "Population": population,
                    "Households": households,
                    "Urbanization Rate (%)": urbanization_rate,
                    "Residential Electricity (MWh)": residential_electricity_mwh,
                    "Commercial Electricity (MWh)": commercial_electricity_mwh,
                    "Industrial Electricity (MWh)": industrial_electricity_mwh,
                    "Streetlights Energy (MWh)": streetlights_energy_mwh,
                    "Public Buildings Energy (MWh)": public_buildings_energy_mwh,
                    "Renewable Energy (MWh)": renewable_energy_mwh,
                    "Transport Data": transport_data.to_dict(orient="records"),
                    "Municipal Fleet Data": municipal_data.to_dict(orient="records"),
                    "Industry Data": industry_data.to_dict(orient="records"),
                    "Municipal Solid Waste (tons)": municipal_solid_waste_tons,
                    "Waste Landfilled (%)": fraction_landfilled,
                    "Waste Composted (%)": fraction_composted,
                    "Wastewater Treated (m3)": wastewater_volume_m3,
                    "Water Supplied (m3)": water_supply_m3,
                    "Energy for Water (MWh)": energy_for_water_mwh,
                    "Urban Green Area (ha)": urban_green_area_ha,
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
                st.session_state.menu = "GHG Inventory"
                st.experimental_rerun()

st.session_state.menu = "GHG Inventory"
st.experimental_rerun()

df_cap.to_csv(CAP_DATA_FILE, index=False)
st.session_state.last_updated = datetime.now()

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu == "GHG Inventory":
    st.header("City GHG Inventory Dashboard")

    if not st.session_state.authenticated:
        admin_login()
    else:
        df_cap = st.session_state.cap_data.copy()
        if df_cap.empty:
            st.warning("No CAP data available. Please submit raw data first.")
        else:
            city = st.selectbox("Select City to View GHG Inventory", list(df_cap["City Name"].unique()))
            city_row = df_cap[df_cap["City Name"] == city].iloc[0]

            # --- Emission Factors ---
            EF = {
                "Electricity": 0.82,  # tCO2e/MWh
                "Diesel_vehicle": 2.68/1000,  # tCO2e/km
                "Petrol_vehicle": 2.31/1000,
                "CNG_vehicle": 2.74/1000,
                "LPG_vehicle": 1.51/1000,
                "Electric_vehicle": 0,
                "Diesel_fuel": 2.68, "Petrol_fuel": 2.31, "CNG_fuel": 2.74, "LPG_fuel": 1.51,
                "Waste_Landfill": 1/10, "Waste_Compost": 0.1/10, "Wastewater": 0.25/1000,
                "Water_Energy": 0.82
            }

            emissions = {}

            # --- Energy ---
            emissions["Residential Energy"] = city_row.get("Residential Electricity (MWh)",0)*EF["Electricity"]
            emissions["Commercial Energy"] = city_row.get("Commercial Electricity (MWh)",0)*EF["Electricity"]
            emissions["Industrial Energy"] = city_row.get("Industrial Electricity (MWh)",0)*EF["Electricity"]
            emissions["Streetlights & Public Buildings"] = city_row.get("Streetlights Energy (MWh)",0)*EF["Electricity"] + city_row.get("Public Buildings Energy (MWh)",0)*EF["Electricity"]

            # --- Transport ---
            for row in city_row.get("Transport Data", []):
                for fuel in ["Diesel","Petrol","CNG","LPG","Electric"]:
                    key = f"Transport {row['Vehicle Type']} {fuel}"
                    emissions[key] = row.get(f"{fuel} Vehicles",0)*row.get("Average km/year",0)*EF[f"{fuel}_vehicle"]

            # --- Municipal Fleet ---
            for row in city_row.get("Municipal Fleet Data", []):
                for fuel in ["Diesel","Petrol","CNG","Electric"]:
                    key = f"Municipal {row['Vehicle Type']} {fuel}"
                    emissions[key] = row.get(f"{fuel} Vehicles",0)*row.get("Average km/year",0)*EF[f"{fuel}_vehicle"]

            # --- Industry ---
            for row in city_row.get("Industry Data", []):
                emissions[f"Industry {row['Industry Name']} Diesel"] = row.get("Diesel (tons/year)",0)*EF["Diesel_fuel"]
                emissions[f"Industry {row['Industry Name']} Petrol"] = row.get("Petrol (tons/year)",0)*EF["Petrol_fuel"]
                emissions[f"Industry {row['Industry Name']} CNG"] = row.get("CNG (tons/year)",0)*EF["CNG_fuel"]
                emissions[f"Industry {row['Industry Name']} LPG"] = row.get("LPG (tons/year)",0)*EF["LPG_fuel"]
                emissions[f"Industry {row['Industry Name']} Electricity"] = row.get("Electricity (MWh/year)",0)*EF["Electricity"]

            # --- Waste ---
            waste_total = city_row.get("Municipal Solid Waste (tons)",0)
            emissions["Waste Landfilled"] = waste_total*(city_row.get("Waste Landfilled (%)",0)/100)*EF["Waste_Landfill"]
            emissions["Waste Composted"] = waste_total*(city_row.get("Waste Composted (%)",0)/100)*EF["Waste_Compost"]
            emissions["Wastewater"] = city_row.get("Wastewater Treated (m3)",0)*EF["Wastewater"]

            # --- Water ---
            emissions["Water Energy"] = city_row.get("Energy for Water (MWh)",0)*EF["Water_Energy"]

            # --- Urban Green / Renewable ---
            emissions["Urban Green / Offsets"] = -1*city_row.get("Renewable Energy (MWh)",0)*EF["Electricity"]

            # --- Display ---
            st.subheader(f"{city} — Sector-wise GHG Emissions (tCO2e)")

            emissions_df = pd.DataFrame({
                "Sector": list(emissions.keys()),
                "Emissions (tCO2e)": list(emissions.values())
            })

            total_emissions = sum(emissions.values())
            st.metric("Total City GHG Emissions (tCO2e)", format(total_emissions,",.0f"))

            # Bar Chart
            fig_bar = px.bar(
                emissions_df.sort_values("Emissions (tCO2e)", ascending=False),
                x="Sector", y="Emissions (tCO2e)",
                text=emissions_df["Emissions (tCO2e)"].apply(lambda x: format(int(x), ",")),
                color_discrete_sequence=["#3E6BE6"]
            )
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie Chart
            fig_pie = px.pie(emissions_df, names="Sector", values="Emissions (tCO2e)", title="Sector-wise GHG Contribution")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Detailed Table
            st.write("### Detailed Emissions Table")
            st.table(emissions_df.assign(**{
                "Emissions (tCO2e)": lambda d: d["Emissions (tCO2e)"].map(lambda x: format(int(x), ","))
            }))

            # --- Action Button ---
            if st.button("View Sector-wise Net Zero Actions"):
                if "selected_city" not in st.session_state:
                    st.session_state.selected_city = city
                st.session_state.menu = "Actions"
                st.experimental_rerun()

                if st.button("View Sector-wise Net Zero Actions"):
            if "selected_city" not in st.session_state:
            st.session_state.selected_city = city
        st.session_state.menu = "Actions"
        st.experimental_rerun()

# ---------------------------
# Actions Page
# ---------------------------
elif menu == "Actions":
    selected_city = st.session_state.get("selected_city", None)
    if not selected_city:
        st.warning("Please select a city from GHG Inventory page first.")
    else:
        st.header(f"Actions & Roadmap for {selected_city} to Achieve Net Zero by 2050")

        # ---------------------------
        # Sector-wise actions aligned with NAPCCC (Indian city-specific)
        # ---------------------------
        sectors_actions = {
            "Energy": {
                "Short-term": [
                    "Replace streetlights with LED bulbs",
                    "Energy audits for public buildings",
                    "Promote rooftop solar for households",
                    "Implement smart meters in commercial buildings",
                    "Encourage energy-efficient appliances",
                    "Retrofitting old buildings with insulation",
                    "Install solar-powered water pumps",
                    "Promote energy conservation campaigns",
                    "Grid optimization for peak load reduction",
                    "Transition municipal buildings to renewable energy"
                ],
                "Mid-term": [
                    "Expand city-level solar parks",
                    "Promote decentralized renewable energy projects",
                    "Smart grid integration for distributed energy",
                    "Electrify public transport fleet",
                    "Phase out fossil fuel boilers in industries",
                    "Encourage green building certification",
                    "Battery storage implementation for renewables",
                    "Energy efficiency retrofit for industries",
                    "District cooling projects in commercial zones",
                    "Incentivize private sector renewable adoption"
                ],
                "Long-term": [
                    "100% renewable electricity for city",
                    "Smart city energy management system",
                    "Zero-emission industrial zones",
                    "City-wide energy storage infrastructure",
                    "Net-zero municipal operations",
                    "Phase out coal-based power entirely",
                    "Urban microgrid networks",
                    "Net-zero residential and commercial sectors",
                    "Carbon-neutral public transport network",
                    "Integration of green hydrogen for industries"
                ]
            },
            "Transport": {
                "Short-term": [
                    "Promote public transport usage",
                    "Introduce electric buses on high-density routes",
                    "Create bicycle lanes",
                    "Implement vehicle emission inspections",
                    "Carpooling awareness campaigns",
                    "Optimize traffic signals to reduce idle emissions",
                    "Encourage e-rickshaws in last-mile transport",
                    "Parking restrictions for high-emission vehicles",
                    "Electric vehicle subsidies for citizens",
                    "Promote low-emission logistics for goods transport"
                ],
                "Mid-term": [
                    "Expand metro and urban rail network",
                    "City-wide EV charging infrastructure",
                    "Bus rapid transit (BRT) corridors",
                    "Fleet electrification for municipal services",
                    "Adopt EV taxis and commercial vehicles",
                    "Low-emission zones for congested areas",
                    "Public bike-sharing systems",
                    "Smart traffic management for emission reduction",
                    "Integration of hydrogen fuel buses",
                    "Promote EV adoption incentives for private vehicles"
                ],
                "Long-term": [
                    "100% electric public transport",
                    "Autonomous electric vehicle network",
                    "Net-zero freight transport system",
                    "City-wide modal shift to non-motorized transport",
                    "Integrated transport-energy planning",
                    "Zero-emission logistic hubs",
                    "Phasing out fossil fuel vehicles",
                    "Carbon-neutral metro and rail",
                    "Urban mobility-as-a-service platform",
                    "City-wide low-carbon transport policy"
                ]
            },
            "Industry": {
                "Short-term": [
                    "Energy audits for industries",
                    "Fuel switching to cleaner fuels",
                    "Promote energy efficiency in industrial processes",
                    "Waste heat recovery in industries",
                    "Substitute high-emission raw materials",
                    "Install pollution monitoring systems",
                    "Promote ISO 50001 energy management",
                    "Optimize production schedules for efficiency",
                    "Awareness workshops on carbon reduction",
                    "Encourage green logistics"
                ],
                "Mid-term": [
                    "Electrification of industrial processes",
                    "Install onsite renewable energy systems",
                    "Carbon capture pilot projects",
                    "Green certification for industrial units",
                    "Adopt circular economy practices",
                    "Optimize supply chain for lower emissions",
                    "Industrial symbiosis networks",
                    "Energy-efficient machinery replacement",
                    "Industry-wide renewable PPA contracts",
                    "Benchmarking and performance tracking"
                ],
                "Long-term": [
                    "Net-zero industrial zones",
                    "Complete process electrification",
                    "Large-scale carbon capture and storage",
                    "Green hydrogen integration",
                    "Industrial circular economy adoption",
                    "Zero-emission logistics within industrial parks",
                    "Net-zero industrial buildings",
                    "Full adoption of renewable energy",
                    "City-wide industrial energy optimization platform",
                    "Advanced automation to minimize emissions"
                ]
            },
            "Waste": {
                "Short-term": [
                    "Segregate waste at source",
                    "Promote composting at household level",
                    "Awareness campaigns for waste reduction",
                    "Optimize waste collection routes",
                    "Pilot anaerobic digestion for organic waste",
                    "Install methane capture in landfills",
                    "Promote recycling centers",
                    "Reduce single-use plastics",
                    "Encourage EPR (Extended Producer Responsibility)",
                    "Municipal solid waste monitoring"
                ],
                "Mid-term": [
                    "City-wide composting facilities",
                    "Waste-to-energy pilot projects",
                    "Expanded recycling programs",
                    "Organic waste management in commercial areas",
                    "Methane capture & flaring systems",
                    "Industrial waste reduction programs",
                    "Integration with circular economy",
                    "Upgrade landfill management technology",
                    "Promote zero-waste commercial zones",
                    "Smart waste monitoring & reporting"
                ],
                "Long-term": [
                    "100% organic waste recycling",
                    "City-wide waste-to-energy plants",
                    "Net-zero landfill emissions",
                    "Complete industrial waste circularity",
                    "Zero-waste policies for commercial zones",
                    "Advanced anaerobic digestion",
                    "Full-scale methane capture from waste",
                    "Integrated smart waste management",
                    "Community-led zero-waste initiatives",
                    "Net-zero municipal waste sector"
                ]
            },
            "Water": {
                "Short-term": [
                    "Reduce water losses in pipelines",
                    "Energy audits of pumping stations",
                    "Promote water-efficient appliances",
                    "Rainwater harvesting promotion",
                    "Awareness campaigns for water conservation",
                    "Optimize wastewater treatment energy",
                    "Pilot solar pumping projects",
                    "Leakage detection programs",
                    "Encourage greywater reuse",
                    "Install flow meters in water distribution"
                ],
                "Mid-term": [
                    "Upgrade water treatment plants to efficient tech",
                    "Decentralized wastewater reuse systems",
                    "Solar-powered pumping stations",
                    "Smart metering for city-wide water network",
                    "Energy recovery in water pipelines",
                    "Integrated urban water management",
                    "Wastewater energy recovery",
                    "Incentivize industries for water efficiency",
                    "Water recycling in commercial buildings",
                    "Stormwater management & recharge projects"
                ],
                "Long-term": [
                    "Net-zero water sector energy use",
                    "City-wide wastewater reuse networks",
                    "100% efficient water distribution",
                    "Fully solar-powered water infrastructure",
                    "Smart city water-energy integration",
                    "Closed-loop water management",
                    "Net-zero municipal pumping stations",
                    "Advanced leakage-free distribution network",
                    "Net-zero industrial water use",
                    "Urban resilience to water scarcity"
                ]
            },
            "Urban Green / Renewable": {
                "Short-term": [
                    "Plant trees in vacant land",
                    "Promote rooftop gardens",
                    "Protect existing green spaces",
                    "Urban park awareness campaigns",
                    "Promote community gardens",
                    "Plant along streets and roads",
                    "Encourage school greening programs",
                    "Restore degraded urban areas",
                    "Install green roofs on public buildings",
                    "Integrate green belts in urban planning"
                ],
                "Mid-term": [
                    "Develop city-wide green corridors",
                    "Expand urban parks and forests",
                    "Promote urban agriculture",
                    "Increase green cover in industrial areas",
                    "Urban wetlands restoration",
                    "Eco-sensitive landscaping in public areas",
                    "Green infrastructure for climate resilience",
                    "Biodiversity enhancement programs",
                    "Promote rooftop solar with greenery",
                    "Carbon sequestration monitoring"
                ],
                "Long-term": [
                    "Net-zero urban green and offset strategy",
                    "Carbon sink programs integrated with city planning",
                    "City-wide ecosystem restoration",
                    "Urban forest expansion",
                    "Full integration of green and blue infrastructure",
                    "Net-zero emissions from urban land use",
                    "Green building mandates city-wide",
                    "City-wide renewable energy + green synergy",
                    "Biodiverse urban ecosystems",
                    "Community-led climate resilience forests"
                ]
            }
        }

        # ---------------------------
        # Display sector actions in tables
        # ---------------------------
        for sector, goals in sectors_actions.items():
            st.subheader(sector)

            max_len = max(len(goals["Short-term"]), len(goals["Mid-term"]), len(goals["Long-term"]))
            table_data = []
            for i in range(max_len):
                table_data.append({
                    "Short-term (by 2030)": goals["Short-term"][i] if i < len(goals["Short-term"]) else "",
                    "Mid-term (by 2040)": goals["Mid-term"][i] if i < len(goals["Mid-term"]) else "",
                    "Long-term (by 2050)": goals["Long-term"][i] if i < len(goals["Long-term"]) else ""
                })

            st.dataframe(pd.DataFrame(table_data), use_container_width=True)
# ---------------------------
    # Create CAP PDF Button
    # ---------------------------
    if st.button("Create CAP Report (PDF)"):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
        from reportlab.lib import colors
        import matplotlib.pyplot as plt
        import tempfile

        # --- Recalculate GHG inventory ---
        EF = {
            "Electricity": 0.82, "Diesel_vehicle": 2.68/1000, "Petrol_vehicle": 2.31/1000,
            "CNG_vehicle": 2.74/1000, "LPG_vehicle": 1.51/1000, "Electric_vehicle": 0,
            "Diesel_fuel": 2.68, "Petrol_fuel": 2.31, "CNG_fuel": 2.74, "LPG_fuel": 1.51,
            "Waste_Landfill": 1/10, "Waste_Compost": 0.1/10, "Wastewater": 0.25/1000,
            "Water_Energy": 0.82
        }
        emissions = {}
        emissions["Residential Energy"] = city_row.get("Residential Electricity (MWh)",0)*EF["Electricity"]
        emissions["Commercial Energy"] = city_row.get("Commercial Electricity (MWh)",0)*EF["Electricity"]
        emissions["Industrial Energy"] = city_row.get("Industrial Electricity (MWh)",0)*EF["Electricity"]
        emissions["Streetlights & Public Buildings"] = city_row.get("Streetlights Energy (MWh)",0)*EF["Electricity"] + city_row.get("Public Buildings Energy (MWh)",0)*EF["Electricity"]
        waste_total = city_row.get("Municipal Solid Waste (tons)",0)
        emissions["Waste Landfilled"] = waste_total*(city_row.get("Waste Landfilled (%)",0)/100)*EF["Waste_Landfill"]
        emissions["Waste Composted"] = waste_total*(city_row.get("Waste Composted (%)",0)/100)*EF["Waste_Compost"]
        emissions["Wastewater"] = city_row.get("Wastewater Treated (m3)",0)*EF["Wastewater"]
        emissions["Water Energy"] = city_row.get("Energy for Water (MWh)",0)*EF["Water_Energy"]
        emissions["Urban Green / Offsets"] = -1*city_row.get("Renewable Energy (MWh)",0)*EF["Electricity"]
        total_emissions = sum(emissions.values())
        emissions_df = pd.DataFrame({"Sector": list(emissions.keys()), "Emissions (tCO2e)": list(emissions.values())})

        # --- Create chart ---
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            plt.figure(figsize=(6,4))
            plt.bar(emissions_df["Sector"], emissions_df["Emissions (tCO2e)"], color="#3E6BE6")
            plt.xticks(rotation=45, ha="right")
            plt.ylabel("tCO2e")
            plt.title(f"{selected_city} GHG Emissions")
            plt.tight_layout()
            plt.savefig(tmpfile.name)
            chart_path = tmpfile.name
            plt.close()

        # --- Generate PDF ---
        pdf_buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(pdf_buffer.name, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        elements.append(Paragraph(f"Climate Action Plan (CAP) Report — {selected_city}", styles['Title']))
        elements.append(Spacer(1, 12))

        # City Metadata
        elements.append(Paragraph(f"Population: {city_row.get('Population',0)}", styles['Normal']))
        elements.append(Paragraph(f"Households: {city_row.get('Households',0)}", styles['Normal']))
        elements.append(Paragraph(f"Urbanization Rate: {city_row.get('Urbanization Rate (%)',0)}%", styles['Normal']))
        elements.append(Spacer(1, 12))

        # GHG Inventory Table
        elements.append(Paragraph("Sector-wise GHG Inventory (tCO2e)", styles['Heading2']))
        table_data = [list(emissions_df.columns)] + emissions_df.values.tolist()
        t = Table(table_data, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3E6BE6")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN',(1,1),(-1,-1),'RIGHT')
        ]))
        elements.append(t)
        elements.append(Spacer(1,12))

        # GHG Chart
        elements.append(Image(chart_path, width=400, height=250))
        elements.append(Spacer(1,12))

        # Actions Tables
        elements.append(Paragraph("Sector-wise Net Zero Actions", styles['Heading2']))
        for sector, df_actions in sector_dfs.items():
            elements.append(Paragraph(sector, styles['Heading3']))
            actions_table = [list(df_actions.columns)] + df_actions.values.tolist()
            t_sector = Table(actions_table, hAlign='LEFT')
            t_sector.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3E6BE6")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ]))
            elements.append(t_sector)
            elements.append(Spacer(1,12))

        # Build PDF
        doc.build(elements)

        st.success("CAP PDF report generated successfully!")
        st.download_button(
            label="Download CAP PDF",
            data=open(pdf_buffer.name, "rb").read(),
            file_name=f"{selected_city}_CAP_Report.pdf",
            mime="application/pdf"
        )
