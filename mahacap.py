# mahacap.py
# Maharashtra CAP Dashboard - single-file Streamlit app
# - Dark professional theme
# - Admin login (click admin button under logo)
# - City dashboard (43 cities pre-listed)
# - Persistent CSV storage (cities_data.csv, cap_raw_data.csv)
# - Comprehensive CAP raw-data input & GHG inventory calculation (per GPC/C40/ICLEI alignment)
# - Download CAP raw-data CSV (download button outside form)
# Notes: default emission factors are editable via UI.

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard",
                   page_icon="🌍",
                   layout="wide",
                   initial_sidebar_state="expanded")

# ---------------------------
# Admin Password (change in production)
# ---------------------------
ADMIN_PASSWORD = "eintrust2025"

# ---------------------------
# Data files for persistence
# ---------------------------
DATA_FILE = "cities_data.csv"
CAP_DATA_FILE = "cap_raw_data.csv"

# ---------------------------
# City list (43 selected cities & district mapping)
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
# Session state defaults
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"

# Load stored city table or create skeleton
if os.path.exists(DATA_FILE):
    try:
        st.session_state.data = pd.read_csv(DATA_FILE)
    except Exception:
        st.session_state.data = pd.DataFrame(columns=[
            "City Name", "District", "Population", "ULB Category", "CAP Status",
            "GHG Emissions", "Environment Department Exist", "Department Name",
            "Head Name", "Department Email"
        ])
else:
    # start with empty table (admin will add)
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Department Email"
    ])

# Load CAP raw-data store (detailed sectoral raw inputs)
if os.path.exists(CAP_DATA_FILE):
    try:
        st.session_state.cap_data = pd.read_csv(CAP_DATA_FILE)
    except Exception:
        st.session_state.cap_data = pd.DataFrame()
else:
    st.session_state.cap_data = pd.DataFrame()

# ---------------------------
# Helper functions
# ---------------------------
def fmt_pop(x):
    """Format population in Indian style (commas)."""
    try:
        if pd.isna(x) or x == "":
            return "—"
        return "{:,}".format(int(x))
    except Exception:
        return str(x)

def get_val(row, col, default="—"):
    if col in row and pd.notna(row[col]):
        return row[col]
    return default

def save_city_table(df):
    st.session_state.data = df
    df.to_csv(DATA_FILE, index=False)
    st.session_state.last_updated = pd.Timestamp.now()

def save_cap_table(df):
    st.session_state.cap_data = df
    df.to_csv(CAP_DATA_FILE, index=False)
    st.session_state.last_updated = pd.Timestamp.now()

# ---------------------------
# Default emission factors (editable in UI)
# These are defaults used if user doesn't provide EFs per city.
# Electricity EF (India grid default) ~0.82 kgCO2e/kWh (common baseline from CEA & compilations).
# Diesel ~2.68 kgCO2/l, Petrol ~2.31 kgCO2/l (IPCC/standard).
# ---------------------------
DEFAULT_EF = {
    "electricity_kg_per_kwh": 0.82,   # kgCO2e per kWh (India default; editable)
    "diesel_kg_per_l": 2.68,
    "petrol_kg_per_l": 2.31,
    # Add more if desired (CNG, LPG, coal per tonne etc.)
}

# ---------------------------
# Dark professional CSS (black/grey background, forest green & royal blue accents)
# ---------------------------
st.markdown(
    """
    <style>
    /* App background */
    [data-testid="stAppViewContainer"] { background-color:#0d0d0d; color:#e6eef8; }
    [data-testid="stSidebar"] { background-color:#111111; color:#e6eef8; }
    /* Buttons (forest green) */
    .stButton>button, .css-1d391kg button { background-color: #196619 !important; color: #ffffff !important; border-radius:8px; }
    .stButton>button:hover, .css-1d391kg button:hover { background-color:#0f4d0f !important; color:#ffffff !important; }
    /* Metric color (royal blue) */
    [data-testid="stMetricValue"] { color: #5b8cff !important; font-weight:700; }
    /* Headers in forest green */
    h1, h2, h3, h4 { color: #7CFC00 !important; }
    /* Inputs */
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div, .stMultiSelect>div>div {
        background-color:#1b1b1b !important; color:#e6eef8 !important; border:1px solid #2f8f2f !important;
    }
    .stFileUploader>div { background-color:#1b1b1b !important; color:#e6eef8 !important; }
    /* Expander */
    .stExpander { background-color:#141414 !important; color:#e6eef8 !important; border-radius:6px; padding:6px; }
    </style>
    """, unsafe_allow_html=True
)

# ---------------------------
# Sidebar - logo + navigation
# (Admin access via 'Admin (click here)' button below logo)
# ---------------------------
with st.sidebar:
    st.image("https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png", use_column_width=True)
    st.markdown("## Maharashtra CAP Dashboard")
    st.markdown("**Engage • Enlighten • Empower**")
    st.markdown("---")
    if st.button("Home"):
        st.session_state.menu = "Home"
    if st.button("City Dashboard"):
        st.session_state.menu = "City Dashboard"
    if st.button("CAP Preparation (admin only)"):
        # only allowed if logged in - will prompt login if not
        if not st.session_state.authenticated:
            st.session_state.menu = "Admin Panel"
        else:
            st.session_state.menu = "CAP Preparation"
    st.markdown("---")
    # Admin trigger under the logo (click to open admin login)
    if st.button("🔒 Admin (login)"):
        st.session_state.menu = "Admin Panel"
    st.markdown("---")
    st.markdown("EinTrust | © {}".format(datetime.now().year))

menu = st.session_state.menu

# ---------------------------
# Admin login form
# ---------------------------
def admin_login_block():
    st.subheader("Admin login")
    with st.form("admin_login_form"):
        pwd = st.text_input("Enter Admin Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if pwd == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Admin authenticated — you can access CAP Preparation and Admin Panel.")
                st.session_state.menu = "Home"
            else:
                st.error("Incorrect password")

# ---------------------------
# Home page
# ---------------------------
if menu == "Home":
    st.title("Maharashtra Climate Action Plan Dashboard")
    st.markdown("State-level overview of CAP status and city inventories.")

    df = st.session_state.data.copy()
    if df.empty:
        st.info("No city data yet. Admin should add city records in Admin Panel.")
    else:
        # ensure GHG Emissions numeric and fill missing with 0
        if "GHG Emissions" in df.columns:
            df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Cities tracked", f"{df.shape[0]}/43")
        with col2:
            avg_pct = "—"
            if "Environment Budget" in df.columns:
                try:
                    avg_pct = f"{pd.to_numeric(df['Environment Budget'], errors='coerce').mean():.1f}"
                except Exception:
                    avg_pct = "—"
            st.metric("Avg Env Budget (if available)", avg_pct)
        with col3:
            done = df[df.get("CAP Status", "") == "Completed"].shape[0] if "CAP Status" in df.columns else 0
            st.metric("CAPs Completed", done)

        st.markdown("### District-wise CAP completion")
        if "District" in df.columns:
            district_summary = (df.groupby("District")["CAP Status"]
                                .apply(lambda x: (x == "Completed").sum())
                                .reset_index().rename(columns={"CAP Status": "CAPs Done"}))
            fig = px.bar(district_summary, x="District", y="CAPs Done", title="CAPs done by district",
                         color_discrete_sequence=["#7CFC00"])
            fig.update_layout(plot_bgcolor="#0d0d0d", paper_bgcolor="#0d0d0d", font_color="#e6eef8")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("District data not available in city table.")

        st.markdown("### City GHG emissions (most recent entries, missing = 0 shown)")
        if "GHG Emissions" in df.columns:
            fig2 = px.bar(df.sort_values("GHG Emissions", ascending=False),
                          x="City Name", y="GHG Emissions", title="GHG Emissions by City (MTCO2e)",
                          color_discrete_sequence=["#5b8cff"])
            fig2.update_layout(plot_bgcolor="#0d0d0d", paper_bgcolor="#0d0d0d", font_color="#e6eef8")
            st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard page
# ---------------------------
elif menu == "City Dashboard":
    st.title("City Dashboard — detailed view")
    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        # city selector: show full list even if not yet present (so admin can create)
        city_options = list(cities_districts.keys())
        # prefer cities present in df first
        present = [c for c in city_options if c in df.get("City Name", [])]
        not_present = [c for c in city_options if c not in present]
        ordered = present + not_present
        city = st.selectbox("Select City", ordered, index=0)

        # try to get row
        if city in df.get("City Name", []):
            row = df[df["City Name"] == city].iloc[0]
        else:
            # empty placeholder row
            row = pd.Series({c: None for c in df.columns})

        st.header(f"{city} — overview")
        with st.expander("Basic info", expanded=True):
            st.write(f"**District:** {cities_districts.get(city, get_val(row, 'District'))}")
            st.write(f"**Population (2011):** {fmt_pop(get_val(row, 'Population'))}")
            st.write(f"**ULB Category:** {get_val(row, 'ULB Category')}")
            st.write(f"**CAP Status:** {get_val(row, 'CAP Status')}")
            st.write(f"**Environment Dept Exists:** {get_val(row, 'Environment Department Exist')}")
            st.write(f"**Department Name:** {get_val(row, 'Department Name')}")
            st.write(f"**Department Email:** {get_val(row, 'Department Email')}")

        # Show CAP raw-data if exists (sectoral)
        cap_df = st.session_state.cap_data
        if not cap_df.empty and city in cap_df.get("City Name", []):
            city_cap = cap_df[cap_df["City Name"] == city].iloc[0]
            with st.expander("Sectoral raw data (CAP preparation inputs)"):
                # display essential fields if present
                for col in city_cap.index:
                    if col == "City Name": continue
                    st.write(f"**{col}:** {city_cap[col]}")
        else:
            st.info("No CAP raw data saved for this city yet (use CAP Preparation).")

        # Show high-level computed GHG inventory if possible
        if not cap_df.empty and city in cap_df.get("City Name", []):
            # compute using the same logic as CAP page
            cap_row = cap_df[cap_df["City Name"] == city].iloc[0]
            # read default EFs (editable via admin later)
            ef_elec = DEFAULT_EF["electricity_kg_per_kwh"]
            ef_diesel = DEFAULT_EF["diesel_kg_per_l"]
            ef_petrol = DEFAULT_EF["petrol_kg_per_l"]

            # Try compute electricity emissions (kWh * ef -> kg -> MT)
            elec = pd.to_numeric(cap_row.get("Energy Electricity (kWh)", 0), errors="coerce")
            elec_co2_mt = 0.0
            if pd.notna(elec):
                elec_co2_mt = (elec * ef_elec) / 1000.0  # convert kg -> metric ton

            # Transport fuel
            transport_fuel_l = pd.to_numeric(cap_row.get("Transport Fuel (L)", 0), errors="coerce")
            # assume diesel for heavy / petrol for light — for simplicity we treat total as diesel-equivalent using diesel EF
            transport_co2_mt = 0.0
            if pd.notna(transport_fuel_l):
                transport_co2_mt = (transport_fuel_l * ef_diesel) / 1000.0

            # Buildings & industry electricity
            industry_elec = pd.to_numeric(cap_row.get("Industry Energy (kWh)", 0), errors="coerce")
            industry_co2_mt = (industry_elec * ef_elec) / 1000.0 if pd.notna(industry_elec) else 0.0
            buildings_elec = pd.to_numeric(cap_row.get("Buildings Electricity (kWh)", 0), errors="coerce") \
                             if "Buildings Electricity (kWh)" in cap_row.index else 0
            buildings_co2_mt = (pd.to_numeric(buildings_elec, errors="coerce") * ef_elec) / 1000.0 if pd.notna(buildings_elec) else 0.0

            # Waste & other (if provided as MTCO2e use directly)
            other_mt = pd.to_numeric(cap_row.get("Other Emissions (MTCO2e)", 0), errors="coerce")
            other_mt = other_mt if pd.notna(other_mt) else 0.0

            total_mtco2e = sum([elec_co2_mt, transport_co2_mt, industry_co2_mt, buildings_co2_mt, other_mt])
            st.markdown("### Computed GHG Inventory (quick estimate)")
            st.write(f"- **Electricity (city)**: {elec_co2_mt:.2f} MTCO2e")
            st.write(f"- **Transport (fuel burn)**: {transport_co2_mt:.2f} MTCO2e")
            st.write(f"- **Industry (electric + fuel)**: {industry_co2_mt:.2f} MTCO2e")
            st.write(f"- **Buildings (electric)**: {buildings_co2_mt:.2f} MTCO2e")
            st.write(f"- **Other / Waste / Land-use (reported)**: {other_mt:.2f} MTCO2e")
            st.markdown(f"**Total (quick): {total_mtco2e:.2f} MTCO2e**")

        # Last updated month & year
        if os.path.exists(DATA_FILE):
            last_updated = pd.to_datetime(os.path.getmtime(DATA_FILE), unit="s")
            st.markdown(f"*Last Updated: {last_updated.strftime('%B %Y')}*")

# ---------------------------
# Admin Panel (login or manage city table & EFs)
# ---------------------------
elif menu == "Admin Panel":
    # If not authenticated, show login
    if not st.session_state.authenticated:
        admin_login_block()
    else:
        st.title("Admin Panel — manage city table & emission factors")
        df = st.session_state.data
        cities_list = list(cities_districts.keys())

        st.markdown("#### Emission factor defaults (editable)")
        col_ef1, col_ef2, col_ef3 = st.columns(3)
        with col_ef1:
            ef_elec = st.number_input("Electricity EF (kg CO2e / kWh)", value=float(DEFAULT_EF["electricity_kg_per_kwh"]), step=0.01, format="%.3f")
        with col_ef2:
            ef_diesel = st.number_input("Diesel EF (kg CO2 / litre)", value=float(DEFAULT_EF["diesel_kg_per_l"]), step=0.01, format="%.3f")
        with col_ef3:
            ef_petrol = st.number_input("Petrol EF (kg CO2 / litre)", value=float(DEFAULT_EF["petrol_kg_per_l"]), step=0.01, format="%.3f")

        # Save EF edits in memory (not persisted to file by default)
        DEFAULT_EF["electricity_kg_per_kwh"] = ef_elec
        DEFAULT_EF["diesel_kg_per_l"] = ef_diesel
        DEFAULT_EF["petrol_kg_per_l"] = ef_petrol

        st.markdown("---")
        st.markdown("#### Add / update city (this table is the public dashboard source)")
        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list, key="admin_city_select")
            district = st.text_input("District", value=cities_districts.get(city_name, ""), disabled=True)
            # fetch defaults from data frame if present
            existing_row = df[df["City Name"] == city_name] if "City Name" in df.columns else pd.DataFrame()
            population_val = int(existing_row["Population"].values[0]) if (not existing_row.empty and "Population" in existing_row.columns and pd.notna(existing_row["Population"].values[0])) else 0
            population = st.number_input("Population (2011 census)", min_value=0, value=population_val, step=1000, format="%d")
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"], index=0)
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"], index=0)
            ghg = st.text_input("GHG Emissions (MTCO2e) - optional (leave blank to compute from CAP raw data)", value=str(existing_row["GHG Emissions"].values[0]) if (not existing_row.empty and "GHG Emissions" in existing_row.columns and pd.notna(existing_row["GHG Emissions"].values[0])) else "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"], index=0)
            # auto-fill department name if env_exist == Yes
            dept_name_default = existing_row["Department Name"].values[0] if (not existing_row.empty and "Department Name" in existing_row.columns and pd.notna(existing_row["Department Name"].values[0])) else ""
            if env_exist == "Yes" and dept_name_default == "":
                dept_name_default = "Environment"
            dept_name = st.text_input("Department Name", value=dept_name_default)
            head_name = st.text_input("Head Name", value=existing_row["Head Name"].values[0] if (not existing_row.empty and "Head Name" in existing_row.columns and pd.notna(existing_row["Head Name"].values[0])) else "")
            dept_email = st.text_input("Department Email", value=existing_row["Department Email"].values[0] if (not existing_row.empty and "Department Email" in existing_row.columns and pd.notna(existing_row["Department Email"].values[0])) else "")

            submit = st.form_submit_button("Add/Update City")
        if submit:
            new_row = {
                "City Name": city_name,
                "District": district,
                "Population": population,
                "ULB Category": ulb_cat,
                "CAP Status": cap_status,
                "GHG Emissions": ghg if ghg != "" else 0,
                "Environment Department Exist": env_exist,
                "Department Name": dept_name,
                "Head Name": head_name,
                "Department Email": dept_email
            }
            # update or append
            if city_name in df.get("City Name", []):
                idx = df[df["City Name"] == city_name].index[0]
                df.loc[idx] = new_row
                st.success(f"{city_name} updated.")
            else:
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"{city_name} added.")
            save_city_table(df)

        # Admin: export / import city CSV
        st.markdown("---")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Download city table CSV"):
                st.write("Preparing download...")
                st.download_button("Download city CSV", data=st.session_state.data.to_csv(index=False).encode('utf-8'),
                                   file_name="cities_data.csv", mime="text/csv")
        with c2:
            uploaded = st.file_uploader("Upload city CSV to replace table (CSV)", type=["csv"])
            if uploaded is not None:
                try:
                    new_df = pd.read_csv(uploaded)
                    # basic validation
                    if "City Name" not in new_df.columns:
                        st.error("Uploaded CSV must contain 'City Name' column.")
                    else:
                        st.session_state.data = new_df
                        new_df.to_csv(DATA_FILE, index=False)
                        st.success("City table replaced from uploaded CSV.")
                except Exception as e:
                    st.error(f"Failed to read uploaded CSV: {e}")

# ---------------------------
# CAP Preparation (detailed raw input & compute inventory)
# note: download button placed OUTSIDE the form to avoid Streamlit form error.
# ---------------------------
elif menu == "CAP Preparation":
    if not st.session_state.authenticated:
        admin_login_block()
    else:
        st.title("CAP Preparation — detailed raw data input (aligned to GPC/C40/ICLEI)")
        st.markdown("Enter raw activity data for the city. Each input has an optional file uploader to attach supporting docs.")
        df_cap = st.session_state.cap_data.copy()

        # city choices come from the main city list (all 43)
        city_choice = st.selectbox("Select City", list(cities_districts.keys()), index=0)

        # We use a single form to save — but the download action must be outside the form.
        with st.form("cap_detail_form"):
            st.subheader("A. Administrative / overview")
            reporting_year = st.number_input("Reporting year (e.g., 2024)", min_value=2000, max_value=2100, value=datetime.now().year)
            data_source = st.text_input("Primary data source / notes (brief)")

            st.subheader("B. Energy (stationary) — electricity & fuels")
            energy_elec = st.number_input("Electricity consumed by city services (kWh/year)", min_value=0, value=0, key="cap_energy_elec")
            energy_elec_upload = st.file_uploader("Upload electricity bill / data (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_elec")

            energy_fuel_diesel = st.number_input("Stationary diesel consumption (litres/year)", min_value=0, value=0, key="cap_energy_diesel")
            energy_fuel_petrol = st.number_input("Stationary petrol consumption (litres/year)", min_value=0, value=0, key="cap_energy_petrol")
            energy_fuel_upload = st.file_uploader("Upload stationary fuel logs (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_fuel")

            st.subheader("C. Transport (on-road)")
            trans_vehicles_total = st.number_input("Total registered vehicles (city-wide)", min_value=0, value=0, key="cap_trans_veh")
            trans_fuel_diesel = st.number_input("Annual diesel consumed by transport (litres)", min_value=0, value=0, key="cap_trans_diesel")
            trans_fuel_petrol = st.number_input("Annual petrol consumed by transport (litres)", min_value=0, value=0, key="cap_trans_petrol")
            trans_vkt = st.number_input("Vehicle-km traveled (estimate) (vehicle-km/year)", min_value=0, value=0, key="cap_trans_vkt")
            transport_upload = st.file_uploader("Upload transport data (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_transport")

            st.subheader("D. Buildings")
            buildings_count = st.number_input("Total buildings (estimate)", min_value=0, value=0, key="cap_build_count")
            buildings_elec = st.number_input("Buildings electricity consumption (kWh/year) — if available", min_value=0, value=0, key="cap_build_elec")
            buildings_upload = st.file_uploader("Upload building energy data (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_build")

            st.subheader("E. Industry")
            industry_units = st.number_input("Industrial units (count)", min_value=0, value=0, key="cap_ind_units")
            industry_energy = st.number_input("Industry electricity consumption (kWh/year)", min_value=0, value=0, key="cap_ind_elec")
            industry_fuel_diesel = st.number_input("Industry diesel (litres/year)", min_value=0, value=0, key="cap_ind_diesel")
            industry_upload = st.file_uploader("Upload industry data (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_ind")

            st.subheader("F. Waste")
            waste_gen_t = st.number_input("Municipal solid waste generated (tonnes/year)", min_value=0, value=0, key="cap_waste_gen")
            waste_recycled_t = st.number_input("Waste recycled (tonnes/year)", min_value=0, value=0, key="cap_waste_recyc")
            waste_landfilled_t = st.number_input("Waste landfilled (tonnes/year)", min_value=0, value=0, key="cap_waste_land")
            waste_upload = st.file_uploader("Upload waste reports (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_waste")

            st.subheader("G. Water & Wastewater")
            water_supply_ml = st.number_input("Water supplied (ML/year)", min_value=0, value=0, key="cap_water_supply")
            wastewater_ml = st.number_input("Wastewater treated / generated (ML/year)", min_value=0, value=0, key="cap_water_ww")
            water_upload = st.file_uploader("Upload water/wastewater data (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_water")

            st.subheader("H. Urban forestry / land-use")
            green_cover_ha = st.number_input("Urban green cover (ha)", min_value=0, value=0, key="cap_green_ha")
            landuse_upload = st.file_uploader("Upload land-use / forestry data (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_land")

            st.subheader("I. Other emissions (enter as MTCO2e)")
            other_emissions_mt = st.number_input("Other emissions reported (MTCO2e/year)", min_value=0.0, value=0.0, step=0.1, key="cap_other_mt")
            other_upload = st.file_uploader("Upload other sector evidence (optional)", type=["csv", "xlsx", "pdf"], key="cap_file_other")

            form_submit = st.form_submit_button("Save CAP raw data")

        # -- after form submission (outside) --
        if form_submit:
            # Compose record (keep consistent columns)
            rec = {
                "City Name": city_choice,
                "Reporting Year": reporting_year,
                "Data Source": data_source,
                "Energy Electricity (kWh)": energy_elec,
                "Energy Diesel (L)": energy_fuel_diesel,
                "Energy Petrol (L)": energy_fuel_petrol,
                "Transport Vehicles (count)": trans_vehicles_total,
                "Transport Diesel (L)": trans_fuel_diesel,
                "Transport Petrol (L)": trans_fuel_petrol,
                "Transport VKT": trans_vkt,
                "Buildings Count": buildings_count,
                "Buildings Electricity (kWh)": buildings_elec,
                "Industry Units": industry_units,
                "Industry Electricity (kWh)": industry_energy,
                "Industry Diesel (L)": industry_fuel_diesel,
                "Waste Generated (t)": waste_gen_t,
                "Waste Recycled (t)": waste_recycled_t,
                "Waste Landfilled (t)": waste_landfilled_t,
                "Water Supplied (ML)": water_supply_ml,
                "Wastewater (ML)": wastewater_ml,
                "Green Cover (ha)": green_cover_ha,
                "Other Emissions (MTCO2e)": other_emissions_mt
            }

            # update cap_data table
            if city_choice in df_cap.get("City Name", []):
                idx = df_cap[df_cap["City Name"] == city_choice].index[0]
                df_cap.loc[idx] = rec
            else:
                df_cap = pd.concat([df_cap, pd.DataFrame([rec])], ignore_index=True)

            save_cap_table(df_cap)
            st.success(f"CAP raw data saved for {city_choice}.")

        # Show quick computed inventory summary for selected city (if present)
        if city_choice in st.session_state.cap_data.get("City Name", []):
            cap_row = st.session_state.cap_data[st.session_state.cap_data["City Name"] == city_choice].iloc[0]
            st.markdown("### Quick GHG inventory (computed using current emission factors)")
            # read EF values from DEFAULT_EF
            ef_e = DEFAULT_EF["electricity_kg_per_kwh"]
            ef_d = DEFAULT_EF["diesel_kg_per_l"]
            ef_p = DEFAULT_EF["petrol_kg_per_l"]

            # compute
            elec = pd.to_numeric(cap_row.get("Energy Electricity (kWh)", 0), errors="coerce")
            elec_mt = (elec * ef_e) / 1000.0 if pd.notna(elec) else 0.0

            trans_d = pd.to_numeric(cap_row.get("Transport Diesel (L)", 0), errors="coerce")
            trans_p = pd.to_numeric(cap_row.get("Transport Petrol (L)", 0), errors="coerce")
            trans_mt = ((trans_d * ef_d) + (trans_p * ef_p)) / 1000.0

            bld_e = pd.to_numeric(cap_row.get("Buildings Electricity (kWh)", 0), errors="coerce")
            bld_mt = (bld_e * ef_e) / 1000.0 if pd.notna(bld_e) else 0.0

            ind_e = pd.to_numeric(cap_row.get("Industry Electricity (kWh)", 0), errors="coerce")
            ind_d = pd.to_numeric(cap_row.get("Industry Diesel (L)", 0), errors="coerce")
            ind_mt = ((ind_e * ef_e) + (ind_d * ef_d)) / 1000.0

            other = pd.to_numeric(cap_row.get("Other Emissions (MTCO2e)", 0), errors="coerce")
            other = other if pd.notna(other) else 0.0

            waste_em = 0.0
            # If user hasn't provided waste emissions directly, we may approximate
            # (Note: accurate CH4 requires detailed anaerobic decay modelling — this is a placeholder)
            waste_t = pd.to_numeric(cap_row.get("Waste Generated (t)", 0), errors="coerce")
            if pd.notna(waste_t) and waste_t > 0:
                # simple proxy: 0.05 MTCO2e per tonne (50 kg CO2e/tonne) - conservative placeholder
                waste_em = (waste_t * 0.05)

            total = sum([elec_mt, trans_mt, bld_mt, ind_mt, other, waste_em])
            st.write(f"- Electricity: **{elec_mt:.2f}** MTCO2e")
            st.write(f"- Transport fuels: **{trans_mt:.2f}** MTCO2e")
            st.write(f"- Buildings (electric): **{bld_mt:.2f}** MTCO2e")
            st.write(f"- Industry: **{ind_mt:.2f}** MTCO2e")
            st.write(f"- Waste (proxy): **{waste_em:.2f}** MTCO2e")
            st.write(f"- Other (reported): **{other:.2f}** MTCO2e")
            st.markdown(f"**Estimated total (quick): {total:.2f} MTCO2e per year**")

        # Download CAP raw-data CSV (OUTSIDE the form)
        if st.session_state.cap_data is not None and not st.session_state.cap_data.empty:
            st.markdown("---")
            st.download_button(
                "Download full CAP raw-data CSV",
                data=st.session_state.cap_data.to_csv(index=False).encode("utf-8"),
                file_name="cap_raw_data.csv",
                mime="text/csv"
            )

# End of app
