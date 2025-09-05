# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO

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
# Cities & Districts (43 cities list)
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
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# ---------------------------
# Load / initialize data
# ---------------------------
if os.path.exists(DATA_FILE):
    st.session_state.data = pd.read_csv(DATA_FILE)
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Department Email"
    ])

if os.path.exists(CAP_DATA_FILE):
    st.session_state.cap_data = pd.read_csv(CAP_DATA_FILE)
else:
    # will store raw input + computed sector emissions + total
    st.session_state.cap_data = pd.DataFrame()

# ---------------------------
# Emission factors (default IPCC/CPCB-ish for India)
# Values in kg CO2 per unit (or tCO2e per tonne where noted).
# Convert to tonnes where appropriate.
# ---------------------------
EMISSION_FACTORS = {
    "electricity_kg_per_kwh": 0.82,        # kg CO2 / kWh -> 0.00082 tCO2 / kWh
    "petrol_kg_per_l": 2.31,              # kg CO2 / L -> 0.00231 tCO2 / L
    "diesel_kg_per_l": 2.68,              # kg CO2 / L
    "lpg_kg_per_l": 1.51,                 # kg CO2 / L
    "naturalgas_kg_per_m3": 2.0,          # kg CO2 / m3
    "waste_tco2_per_tonne": 1.0,          # tCO2e / tonne to landfill
    "water_supply_tco2_per_ml": 0.5,      # tCO2e per ML (pumping/treatment)
    "wastewater_tco2_per_ml": 0.3,        # tCO2e per ML
    "forest_sequestration_t_per_ha": 3.0, # tCO2e sequestration per ha per year (negative emissions)
    # fallback transport factor (kg CO2 per L)
    "transport_default_kg_per_l": 2.5
}

# ---------------------------
# Helper functions
# ---------------------------
def format_population(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        return "{:,}".format(int(num))
    except Exception:
        return "—"

def safe_num(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def compute_sector_emissions(raw):
    """Given a dict of raw inputs (numbers), return sector emissions dictionary in tonnes CO2e."""
    out = {}
    # Energy (electricity + fuels). electricity in kWh, fuel_l in liters
    elec_t = safe_num(raw.get("energy_electricity_kwh", 0)) * (EMISSION_FACTORS["electricity_kg_per_kwh"] / 1000.0)
    fuel_l = safe_num(raw.get("energy_fuel_l", 0))
    # assume admin may split petrol/diesel fields; else use overall fuel field
    petrol_l = safe_num(raw.get("petrol_l", 0))
    diesel_l = safe_num(raw.get("diesel_l", 0))
    lpg_l = safe_num(raw.get("lpg_l", 0))
    # if petrol/diesel explicitly provided, use them; else if fuel_l provided, use default factor
    fuel_t = 0.0
    if petrol_l or diesel_l or lpg_l:
        fuel_t += petrol_l * (EMISSION_FACTORS["petrol_kg_per_l"] / 1000.0)
        fuel_t += diesel_l * (EMISSION_FACTORS["diesel_kg_per_l"] / 1000.0)
        fuel_t += lpg_l * (EMISSION_FACTORS["lpg_kg_per_l"] / 1000.0)
    elif fuel_l:
        fuel_t += fuel_l * (EMISSION_FACTORS["transport_default_kg_per_l"] / 1000.0)
    out["Energy (Stationary) (tCO2e)"] = elec_t + fuel_t

    # Transport (if transport fuel provided)
    transport_fuel_l = safe_num(raw.get("transport_fuel_l", 0))
    transport_petrol_l = safe_num(raw.get("transport_petrol_l", 0))
    transport_diesel_l = safe_num(raw.get("transport_diesel_l", 0))
    transport_t = 0.0
    if transport_petrol_l or transport_diesel_l:
        transport_t += transport_petrol_l * (EMISSION_FACTORS["petrol_kg_per_l"] / 1000.0)
        transport_t += transport_diesel_l * (EMISSION_FACTORS["diesel_kg_per_l"] / 1000.0)
    elif transport_fuel_l:
        transport_t += transport_fuel_l * (EMISSION_FACTORS["transport_default_kg_per_l"] / 1000.0)
    out["Transport (tCO2e)"] = transport_t

    # Buildings (if you gave electricity/fuel for public/residential/etc. we currently include in energy)
    # Industry (industrial energy specified in kWh)
    industry_elec_t = safe_num(raw.get("industry_energy_kwh", 0)) * (EMISSION_FACTORS["electricity_kg_per_kwh"] / 1000.0)
    out["Industry (tCO2e)"] = industry_elec_t

    # Waste: assume waste_to_landfill fraction; waste in tonnes
    waste_tonnes = safe_num(raw.get("waste_generated_t", 0))
    landfill_share = safe_num(raw.get("waste_landfill_pct", 0)) / 100.0
    waste_em = waste_tonnes * landfill_share * EMISSION_FACTORS["waste_tco2_per_tonne"]
    out["Waste (tCO2e)"] = waste_em

    # Water: water consumption ML * factor; wastewater ML * factor
    water_ml = safe_num(raw.get("water_consumption_ml", 0))
    wastewater_ml = safe_num(raw.get("wastewater_generated_ml", 0))
    water_em = water_ml * EMISSION_FACTORS["water_supply_tco2_per_ml"]
    wastewater_em = wastewater_ml * EMISSION_FACTORS["wastewater_tco2_per_ml"]
    out["Water & Wastewater (tCO2e)"] = water_em + wastewater_em

    # UGB (urban green): sequestration (negative)
    green_ha = safe_num(raw.get("urban_green_ha", 0))
    sequestration = green_ha * EMISSION_FACTORS["forest_sequestration_t_per_ha"]
    # treat as negative emission (removal)
    out["Urban Green (sequestration) (tCO2e)"] = -sequestration

    # Other emissions (straight MTCO2e input)
    other_mt = safe_num(raw.get("other_emissions_mtco2e", 0))
    out["Other (tCO2e)"] = other_mt

    # Sum positive sectors (tCO2e) + negative sequestration
    total = 0.0
    for k, v in out.items():
        total += v
    out["Total (tCO2e)"] = total
    return out

# ---------------------------
# Styling / theme (dark, forest green & royal blue accents)
# ---------------------------
st.markdown(
    """
    <style>
    /* App & Sidebar background */
    [data-testid="stAppViewContainer"] {background-color: #0f0f0f;}
    [data-testid="stSidebar"] {background-color: #121212;}
    /* Buttons */
    .stButton>button { background-color: #1f7a1f !important; color: white !important; }
    .stButton>button:hover { background-color: #165b16 !important; }
    /* Metrics color */
    [data-testid="stMetricValue"] { color: #4f7ae6 !important; font-weight:700; }
    /* Headers */
    h1, h2, h3, h4 { color: #9bdc9b !important; }
    /* Inputs dark */
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div, .css-1hwfws3 {
        background-color:#1a1a1a !important; color:#eaeaea !important; border-color:#1f7a1f !important;
    }
    .stFileUploader>div { background-color: #1a1a1a !important; color: #eaeaea !important; }
    .stExpander { background-color:#141414 !important; color:#eaeaea !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Helper: write dataframes to excel bytes for downloads
# ---------------------------
def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    return output.getvalue()

# ---------------------------
# Top area: logo + hidden admin trigger
# ---------------------------
col1, col2 = st.columns([1, 8])
with col1:
    # logo; make clickable text below for admin (image-click programmatic detection is limited in Streamlit)
    st.image("https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true", use_column_width=True)
    # small admin hint: clicking the "Open Admin" button below opens admin form
    if st.button("🔒 Open Admin (click to login)"):
        st.session_state.menu = "Admin Panel"
with col2:
    st.title("Maharashtra Climate Action Plan (CAP) Dashboard")
    st.markdown("Unified CAP input → automatic GHG inventory → sectoral charts")

# ---------------------------
# Sidebar: navigation
# ---------------------------
with st.sidebar:
    st.markdown("## Navigate")
    if st.button("Home"):
        st.session_state.menu = "Home"
    if st.button("City Dashboard"):
        st.session_state.menu = "City Dashboard"
    if st.button("CAP Preparation (admin)"):
        st.session_state.menu = "CAP Preparation"
    st.markdown("---")
    st.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# HOME
# ---------------------------
if menu == "Home":
    st.header("State overview — Maharashtra (selected 43 cities)")
    df = st.session_state.data.copy()
    if df.empty:
        st.info("No city metadata available. Admin: use Open Admin -> Admin Panel to add city entries.")
    else:
        # ensure GHG Emissions numeric and fill 0
        if "GHG Emissions" in df.columns:
            df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        total_cities = df.shape[0]
        completed = df[df["CAP Status"] == "Completed"].shape[0] if "CAP Status" in df.columns else 0
        col1, col2, col3 = st.columns(3)
        col1.metric("Total cities loaded", total_cities)
        col2.metric("CAPs completed", completed)
        # District-wise summary (count of completed CAPs)
        if "District" in df.columns and "CAP Status" in df.columns:
            district_summary = df.groupby("District").apply(lambda x: (x["CAP Status"]=="Completed").sum()).reset_index()
            district_summary.columns = ["District", "CAPs Done"]
            fig = px.bar(district_summary, x="District", y="CAPs Done", title="District-wise CAPs Completed",
                         color_discrete_sequence=["#4f7ae6"])
            fig.update_layout(plot_bgcolor="#0f0f0f", paper_bgcolor="#0f0f0f", font_color="#eaeaea")
            st.plotly_chart(fig, use_container_width=True)
        # GHG by city
        if "GHG Emissions" in df.columns:
            fig2 = px.bar(df.sort_values("GHG Emissions", ascending=False), x="City Name", y="GHG Emissions",
                          title="GHG Emissions by City (tCO2e)", text="GHG Emissions",
                          color_discrete_sequence=["#9bdc9b"])
            fig2.update_layout(plot_bgcolor="#0f0f0f", paper_bgcolor="#0f0f0f", font_color="#eaeaea")
            st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# CITY DASHBOARD
# ---------------------------
elif menu == "City Dashboard":
    st.header("City Dashboard")
    df_meta = st.session_state.data
    if df_meta.empty:
        st.info("No cities found. Admin: add cities in Admin Panel.")
    else:
        city = st.selectbox("Select City", df_meta["City Name"].dropna().unique())
        row = df_meta[df_meta["City Name"] == city].iloc[0]

        st.subheader(f"{city} — summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("District", row.get("District", "—"))
        col2.metric("Population (2011)", format_population(row.get("Population", None)))
        col3.metric("CAP status", row.get("CAP Status", "—"))

        # pull computed CAP raw data for this city if exists
        cap_df = st.session_state.cap_data
        if not cap_df.empty and "City Name" in cap_df.columns and city in cap_df["City Name"].values:
            cap_row = cap_df[cap_df["City Name"] == city].iloc[0].to_dict()
            # compute sector emissions from stored raw (raw columns named consistently)
            # reconstruct minimal raw dict from cap_row
            raw = {
                "energy_electricity_kwh": cap_row.get("Energy Electricity (kWh)", 0),
                "energy_fuel_l": cap_row.get("Energy Fuel (L)", 0),
                "petrol_l": cap_row.get("Petrol (L)", 0) if "Petrol (L)" in cap_row else 0,
                "diesel_l": cap_row.get("Diesel (L)", 0) if "Diesel (L)" in cap_row else 0,
                "transport_fuel_l": cap_row.get("Transport Fuel (L)", 0),
                "industry_energy_kwh": cap_row.get("Industry Energy (kWh)", 0),
                "waste_generated_t": cap_row.get("Waste Generated (t)", 0),
                "waste_landfill_pct": cap_row.get("Waste to Landfill (%)", 100),
                "water_consumption_ml": cap_row.get("Water Consumption (ML)", 0),
                "wastewater_generated_ml": cap_row.get("Wastewater Generated (ML)", 0),
                "urban_green_ha": cap_row.get("Urban Green Cover (ha)", 0),
                "other_emissions_mtco2e": cap_row.get("Other Emissions (MTCO2e)", 0)
            }
            emissions = compute_sector_emissions(raw)
            # show totals
            total = emissions.get("Total (tCO2e)", 0.0)
            st.metric("Total GHG (tCO₂e / year)", f"{total:,.1f}")

            # Sector bar chart (exclude negative sequestration from bar chart positive axis but show in pie)
            sector_items = {k: v for k, v in emissions.items() if k not in ["Total (tCO2e)"]}
            sectors = list(sector_items.keys())
            values = [max(0, sector_items[s]) for s in sectors]  # make bars >=0
            fig = px.bar(x=sectors, y=values, title="Sector-wise emissions (tCO₂e)", labels={"x":"Sector","y":"tCO₂e"}, color_discrete_sequence=["#9bdc9b"])
            fig.update_layout(plot_bgcolor="#0f0f0f", paper_bgcolor="#0f0f0f", font_color="#eaeaea", xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

            # Pie chart that shows contribution (including negative if present)
            pie_vals = [v for v in sector_items.values()]
            # If all zero, handle gracefully
            if sum(abs(v) for v in pie_vals) == 0:
                st.info("All sector emissions are zero for this city (raw data entries are zero).")
            else:
                pie = px.pie(names=sectors, values=[abs(v) for v in pie_vals], title="Sector share (absolute tCO₂e)")
                pie.update_traces(textposition='inside', textinfo='percent+label')
                pie.update_layout(plot_bgcolor="#0f0f0f", paper_bgcolor="#0f0f0f", font_color="#eaeaea")
                st.plotly_chart(pie, use_container_width=True)

            # Show computed sector table
            em_df = pd.DataFrame(list(sector_items.items()), columns=["Sector","tCO2e"])
            st.dataframe(em_df.style.format({"tCO2e":"{:.2f}"}), height=300)

            # Download inventory as Excel (button outside any form)
            excel_bytes = df_to_excel_bytes(em_df.assign(City=city)[["City","Sector","tCO2e"]])
            st.download_button("📥 Download city GHG inventory (Excel)", data=excel_bytes, file_name=f"{city}_GHG_inventory.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        else:
            st.info("No CAP raw data entered yet for this city. Admin: go to CAP Preparation to enter raw data.")

        # last updated month/year
        if os.path.exists(DATA_FILE):
            last_updated = pd.to_datetime(os.path.getmtime(DATA_FILE), unit='s')
            st.markdown(f"*Last Updated: {last_updated.strftime('%B %Y')}*")

# ---------------------------
# ADMIN PANEL (city metadata entry)
# ---------------------------
elif menu == "Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("Admin Panel — Add / Update city metadata")
        df = st.session_state.data
        cities_list = list(cities_districts.keys())

        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list)
            district = st.text_input("District", value=cities_districts[city_name], disabled=True)
            # try to read existing population if present
            population_val = int(df[df["City Name"]==city_name]["Population"].values[0]) if (city_name in df.get("City Name", []) and not pd.isna(df[df["City Name"]==city_name]["Population"].values[0])) else 0
            population = st.number_input("Population (as per 2011 census)", min_value=0, value=population_val, step=1000, format="%d")
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            ghg = st.text_input("GHG Emissions (total tCO2e) - optional (if you have official number)", value=(str(df[df["City Name"]==city_name]["GHG Emissions"].values[0]) if city_name in df.get("City Name", []) and not pd.isna(df[df["City Name"]==city_name]["GHG Emissions"].values[0]) else ""))
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"], index=0)
            dept_name = st.text_input("Department Name", value=(df[df["City Name"]==city_name]["Department Name"].values[0] if city_name in df.get("City Name", []) else ""))
            head_name = st.text_input("Head Name", value=(df[df["City Name"]==city_name]["Head Name"].values[0] if city_name in df.get("City Name", []) else ""))
            dept_email = st.text_input("Department Email", value=(df[df["City Name"]==city_name]["Department Email"].values[0] if city_name in df.get("City Name", []) else ""))
            submitted = st.form_submit_button("Add / Update City")
            if submitted:
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
                    idx = df[df["City Name"]==city_name].index[0]
                    df.loc[idx] = new_row
                    st.success(f"{city_name} updated.")
                else:
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"{city_name} added.")
                st.session_state.data = df
                df.to_csv(DATA_FILE, index=False)
                st.session_state.last_updated = pd.Timestamp.now()

# ---------------------------
# CAP PREPARATION (Unified raw data form + compute & save)
# ---------------------------
elif menu == "CAP Preparation":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("CAP Preparation — Unified raw data input (all sectors)")
        st.markdown("Enter raw activity data for the city. Upload supporting files optionally for verification. After saving, emissions are computed automatically with default IPCC/CPCB factors.")
        df_cap = st.session_state.cap_data

        # build form
        with st.form("cap_form"):
            city_sel = st.selectbox("Select City", st.session_state.data["City Name"].dropna().unique(), key="cap_city_sel")
            st.subheader("ENERGY (stationary)")
            energy_electricity_kwh = st.number_input("Electricity consumption - total (kWh/year)", min_value=0, value=0, step=1000, key="energy_electricity_kwh")
            energy_fuel_l = st.number_input("Other fossil fuels - total (liters/year) [if mixed fuels use total liters]", min_value=0, value=0, step=1000, key="energy_fuel_l")
            petrol_l = st.number_input("Petrol (L/year) - optional", min_value=0, value=0, key="petrol_l")
            diesel_l = st.number_input("Diesel (L/year) - optional", min_value=0, value=0, key="diesel_l")
            lpg_l = st.number_input("LPG (L/year) - optional", min_value=0, value=0, key="lpg_l")
            st.file_uploader("Upload energy supporting file (optional)", type=["xlsx","csv","pdf"], key="energy_upload")

            st.subheader("TRANSPORT")
            transport_fuel_l = st.number_input("Transport fuel - total (L/year) [if mixed fuels use total liters]", min_value=0, value=0, key="transport_fuel_l")
            transport_petrol_l = st.number_input("Transport petrol (L/year) - optional", min_value=0, value=0, key="transport_petrol_l")
            transport_diesel_l = st.number_input("Transport diesel (L/year) - optional", min_value=0, value=0, key="transport_diesel_l")
            total_vehicles = st.number_input("Total registered vehicles in city", min_value=0, value=0, key="total_vehicles")
            public_transport_ridership = st.number_input("Annual public transport ridership (passenger trips)", min_value=0, value=0, key="public_transport_ridership")
            st.file_uploader("Upload transport supporting file (optional)", type=["xlsx","csv","pdf"], key="transport_upload")

            st.subheader("BUILDINGS")
            buildings_count = st.number_input("Number of buildings (approx)", min_value=0, value=0, key="buildings_count")
            buildings_builtup_sqm = st.number_input("Built-up area total (sq.m)", min_value=0, value=0, key="buildings_area")
            st.file_uploader("Upload buildings supporting file (optional)", type=["xlsx","csv","pdf"], key="buildings_upload")

            st.subheader("WATER & WASTEWATER")
            water_consumption_ml = st.number_input("Water supplied (ML / year)", min_value=0, value=0, key="water_consumption_ml")
            wastewater_generated_ml = st.number_input("Wastewater treated/generated (ML / year)", min_value=0, value=0, key="wastewater_generated_ml")
            st.file_uploader("Upload water supporting file (optional)", type=["xlsx","csv","pdf"], key="water_upload")

            st.subheader("WASTE")
            waste_generated_t = st.number_input("MSW (municipal solid waste) generated (tonnes/year)", min_value=0, value=0, key="waste_generated_t")
            waste_recycled_t = st.number_input("MSW recycled/composted (tonnes/year)", min_value=0, value=0, key="waste_recycled_t")
            waste_landfill_pct = st.number_input("Share sent to landfill (%)", min_value=0, max_value=100, value=100, key="waste_landfill_pct")
            st.file_uploader("Upload waste supporting file (optional)", type=["xlsx","csv","pdf"], key="waste_upload")

            st.subheader("INDUSTRY")
            industry_units = st.number_input("Number of industrial units (approx)", min_value=0, value=0, key="industry_units")
            industry_energy_kwh = st.number_input("Industry electricity consumption (kWh/year)", min_value=0, value=0, key="industry_energy_kwh")
            st.file_uploader("Upload industry supporting file (optional)", type=["xlsx","csv","pdf"], key="industry_upload")

            st.subheader("URBAN GREEN & LAND USE")
            urban_green_ha = st.number_input("Urban green cover / trees area (ha)", min_value=0, value=0, key="urban_green_ha")
            st.file_uploader("Upload urban green supporting file (optional)", type=["xlsx","csv","pdf"], key="urban_green_upload")

            st.subheader("OTHER")
            other_emissions_mtco2e = st.number_input("Other emissions / methane / fugitive (tCO2e/year) - if any", min_value=0.0, value=0.0, key="other_emissions_mtco2e")
            other_upload = st.file_uploader("Upload other supporting file (optional)", type=["xlsx","csv","pdf"], key="other_upload")

            save = st.form_submit_button("Save CAP raw data (compute emissions)")

        # form end
        if save:
            raw_row = {
                "City Name": city_sel,
                "Energy Electricity (kWh)": energy_electricity_kwh,
                "Energy Fuel (L)": energy_fuel_l,
                "Petrol (L)": petrol_l,
                "Diesel (L)": diesel_l,
                "LPG (L)": lpg_l,
                "Transport Fuel (L)": transport_fuel_l,
                "Transport Petrol (L)": transport_petrol_l,
                "Transport Diesel (L)": transport_diesel_l,
                "Total Vehicles": total_vehicles,
                "Public Transport Ridership": public_transport_ridership,
                "Buildings Count": buildings_count,
                "Buildings Area (sq.m)": buildings_builtup_sqm,
                "Water Consumption (ML)": water_consumption_ml,
                "Wastewater Generated (ML)": wastewater_generated_ml,
                "Waste Generated (t)": waste_generated_t,
                "Waste Recycled (t)": waste_recycled_t,
                "Waste to Landfill (%)": waste_landfill_pct,
                "Industry Units": industry_units,
                "Industry Energy (kWh)": industry_energy_kwh,
                "Urban Green Cover (ha)": urban_green_ha,
                "Other Emissions (MTCO2e)": other_emissions_mtco2e
            }

            # compute emissions from raw inputs
            raw_for_calc = {
                "energy_electricity_kwh": energy_electricity_kwh,
                "energy_fuel_l": energy_fuel_l,
                "petrol_l": petrol_l,
                "diesel_l": diesel_l,
                "transport_fuel_l": transport_fuel_l,
                "transport_petrol_l": transport_petrol_l,
                "transport_diesel_l": transport_diesel_l,
                "industry_energy_kwh": industry_energy_kwh,
                "waste_generated_t": waste_generated_t,
                "waste_landfill_pct": waste_landfill_pct,
                "water_consumption_ml": water_consumption_ml,
                "wastewater_generated_ml": wastewater_generated_ml,
                "urban_green_ha": urban_green_ha,
                "other_emissions_mtco2e": other_emissions_mtco2e
            }
            computed = compute_sector_emissions(raw_for_calc)

            # merge computed into row (store numbers)
            for k, v in computed.items():
                raw_row[k] = v

            # insert/update into cap_data
            cap_df = st.session_state.cap_data.copy()
            if "City Name" in cap_df.columns and city_sel in cap_df["City Name"].values:
                idx = cap_df[cap_df["City Name"] == city_sel].index[0]
                cap_df.loc[idx] = raw_row
            else:
                cap_df = pd.concat([cap_df, pd.DataFrame([raw_row])], ignore_index=True)
            st.session_state.cap_data = cap_df
            cap_df.to_csv(CAP_DATA_FILE, index=False)
            # update meta GHG Emissions in cities table too (total)
            # find total from computed
            total_t = computed.get("Total (tCO2e)", 0.0)
            # update metadata table
            meta = st.session_state.data.copy()
            if city_sel in meta.get("City Name", []):
                meta_idx = meta[meta["City Name"] == city_sel].index[0]
                meta.at[meta_idx, "GHG Emissions"] = total_t
                st.session_state.data = meta
                meta.to_csv(DATA_FILE, index=False)
            # success and allow download outside form
            st.success(f"CAP raw data saved for {city_sel} — total emissions {total_t:,.2f} tCO2e/year")

            # Prepare downloadable CSV for this city's raw+computed row (single)
            city_row = st.session_state.cap_data[st.session_state.cap_data["City Name"] == city_sel]
            csv_bytes = city_row.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="📥 Download this city's CAP raw data + computed emissions (CSV)",
                data=csv_bytes,
                file_name=f"{city_sel}_CAP_raw_and_emissions.csv",
                mime="text/csv"
            )

# ---------------------------
# End of file
# ---------------------------
