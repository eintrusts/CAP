# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from datetime import datetime

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin password (simple)
# ---------------------------
ADMIN_PASSWORD = "eintrust2025"

# ---------------------------
# Files for persistence
# ---------------------------
CITIES_FILE = "cities_data.csv"
CAP_RAW_FILE = "cap_raw_data.csv"

# ---------------------------
# 43 Cities and their Districts
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
# Inline emission factors (user requested, default Indian/IPCC-like)
# Units noted in comments
# ---------------------------
EF = {
    # electricity: kg CO2 / kWh
    "elec_kg_per_kwh": 0.82,
    # fuels: kg CO2 / L
    "petrol_kg_per_l": 2.31,
    "diesel_kg_per_l": 2.68,
    "lpg_kg_per_l": 1.51,
    # transport fallback: kg CO2 / L
    "transport_default_kg_per_l": 2.5,
    # waste: tCO2e / tonne (landfill)
    "waste_tco2_per_tonne": 1.2,
    # water: tCO2e / ML
    "water_supply_tco2_per_ml": 0.5,
    "wastewater_tco2_per_ml": 0.3,
    # urban green: tCO2e / ha / year (sequestration)
    "green_tco2_per_ha": 2.5,
    # other default
    "other_tco2_per_unit": 1.0
}

# ---------------------------
# Helpers
# ---------------------------
def load_or_init(path, cols):
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.DataFrame(columns=cols)
    else:
        return pd.DataFrame(columns=cols)

def save_df(df, path):
    df.to_csv(path, index=False)

def format_pop_indian(n):
    try:
        if n is None or pd.isna(n) or n == "":
            return "—"
        return "{:,}".format(int(n))
    except Exception:
        return "—"

def safe_float(x):
    try:
        return float(x)
    except Exception:
        return 0.0

def compute_emissions_from_raw(raw):
    """
    raw: dict with keys used in CAP form (numbers)
    Returns dict of sector emissions (all in tCO2e)
    """
    out = {}
    # Energy (stationary) - electricity (kWh) and fuel (L)
    elec_kwh = safe_float(raw.get("energy_electricity_kwh", 0))
    elec_t = elec_kwh * (EF["elec_kg_per_kwh"] / 1000.0)
    petrol_l = safe_float(raw.get("petrol_l", 0))
    diesel_l = safe_float(raw.get("diesel_l", 0))
    lpg_l = safe_float(raw.get("lpg_l", 0))
    fuel_total_l = safe_float(raw.get("energy_fuel_l", 0))
    fuel_t = 0.0
    # prefer specific fuel fields if provided
    if petrol_l or diesel_l or lpg_l:
        fuel_t += petrol_l * (EF["petrol_kg_per_l"] / 1000.0)
        fuel_t += diesel_l * (EF["diesel_kg_per_l"] / 1000.0)
        fuel_t += lpg_l * (EF["lpg_kg_per_l"] / 1000.0)
    elif fuel_total_l:
        fuel_t += fuel_total_l * (EF["transport_default_kg_per_l"] / 1000.0)
    out["Energy (stationary)"] = elec_t + fuel_t

    # Transport - fuel (L)
    transport_petrol = safe_float(raw.get("transport_petrol_l", 0))
    transport_diesel = safe_float(raw.get("transport_diesel_l", 0))
    transport_fuel = safe_float(raw.get("transport_fuel_l", 0))
    transport_t = 0.0
    if transport_petrol or transport_diesel:
        transport_t += transport_petrol * (EF["petrol_kg_per_l"] / 1000.0)
        transport_t += transport_diesel * (EF["diesel_kg_per_l"] / 1000.0)
    elif transport_fuel:
        transport_t += transport_fuel * (EF["transport_default_kg_per_l"] / 1000.0)
    out["Transport"] = transport_t

    # Buildings - we assume building energy included in stationary energy; keep separate if building-specific energy provided
    building_elec_kwh = safe_float(raw.get("buildings_energy_kwh", 0))
    building_t = building_elec_kwh * (EF["elec_kg_per_kwh"] / 1000.0)
    out["Buildings"] = building_t

    # Industry - industry energy (kWh)
    industry_kwh = safe_float(raw.get("industry_energy_kwh", 0))
    industry_t = industry_kwh * (EF["elec_kg_per_kwh"] / 1000.0)
    out["Industry"] = industry_t

    # Waste - tonnes * factor * landfill share
    waste_tonnes = safe_float(raw.get("waste_generated_t", 0))
    waste_landfill_pct = safe_float(raw.get("waste_landfill_pct", 100))
    landfill_share = max(0.0, min(100.0, waste_landfill_pct)) / 100.0
    waste_t = waste_tonnes * landfill_share * EF["waste_tco2_per_tonne"]
    out["Waste"] = waste_t

    # Water & wastewater (ML)
    water_ml = safe_float(raw.get("water_consumption_ml", 0))
    wastewater_ml = safe_float(raw.get("wastewater_generated_ml", 0))
    water_t = water_ml * EF["water_supply_tco2_per_ml"]
    wastewater_t = wastewater_ml * EF["wastewater_tco2_per_ml"]
    out["Water & Wastewater"] = water_t + wastewater_t

    # Urban Green - sequestration (negative)
    green_ha = safe_float(raw.get("urban_green_ha", 0))
    sequestration_t = green_ha * EF["green_tco2_per_ha"]
    out["Urban Green (sequestration)"] = -sequestration_t

    # Other (entered directly as tCO2e)
    other_t = safe_float(raw.get("other_emissions_t", 0))
    out["Other"] = other_t

    # Total
    total = sum(out.values())
    out["Total"] = total
    return out

def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="GHG Inventory")
    return out.getvalue()

# ---------------------------
# Load or initialize dataframes
# ---------------------------
cities_cols = [
    "City Name", "District", "Population", "ULB Category", "CAP Status",
    "GHG Emissions", "Environment Department Exist", "Department Name", "Head Name", "Department Email"
]
cap_raw_cols = None  # will be dynamic; initial empty DF handled

cities_df = load_or_init(CITIES_FILE, cities_cols)
cap_raw_df = load_or_init(CAP_RAW_FILE, [])  # may be empty

# set defaults in session_state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# ---------------------------
# Styling: dark theme + accents
# ---------------------------
st.markdown(
    """
    <style>
    /* App backgrounds */
    [data-testid="stAppViewContainer"] { background-color: #0b0b0b; color: #e8e8e8; }
    [data-testid="stSidebar"] { background-color: #111111; color: #e8e8e8; }
    /* Buttons - forest green */
    .stButton>button { background-color:#1f7a1f !important; color: white !important; border-radius:6px !important; height:40px !important; }
    .stButton>button:hover { background-color:#165b16 !important; }
    /* Metric values - royal blue */
    [data-testid="stMetricValue"] { color:#3f6fe0 !important; font-weight:700; }
    /* Headings */
    h1, h2, h3, h4 { color:#9bdc9b !important; }
    /* Inputs dark */
    .stTextInput>div>input, .stNumberInput>div>input, .stSelectbox>div>div, .stFileUploader>div {
        background-color:#1b1b1b !important; color:#e8e8e8 !important; border-color:#1f7a1f !important;
    }
    /* Dataframe background */
    .stDataFrame table { background-color:#121212 !important; color:#e8e8e8 !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Top area: logo and admin trigger (logo image + small "Open Admin" button)
# ---------------------------
col_logo, col_title = st.columns([1, 8])
with col_logo:
    # display logo (click cannot be detected), so provide small button under logo to open admin
    st.image("https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true", use_column_width=True)
    if st.button("🔒 Admin login"):
        st.session_state.menu = "Admin Panel"
with col_title:
    st.title("Maharashtra CAP Dashboard")
    st.markdown("Unified CAP input → automatic GHG inventory (IPCC/CPCB defaults) → sectoral visualization")

# ---------------------------
# Sidebar navigation (no admin link)
# ---------------------------
with st.sidebar:
    st.markdown("## Navigate")
    if st.button("Home"):
        st.session_state.menu = "Home"
    if st.button("City Dashboard"):
        st.session_state.menu = "City Dashboard"
    if st.button("CAP Preparation"):
        # allow admin-only CAP Preparation; but showing it here is acceptable as navigation,
        # we will require admin login when accessing its form
        st.session_state.menu = "CAP Preparation"
    st.markdown("---")
    st.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# HOME page
# ---------------------------
if menu == "Home":
    st.header("State level overview — Maharashtra (43 selected cities)")
    if cities_df.empty:
        st.info("No city metadata yet. Click 'Admin login' near the logo to add city entries.")
    else:
        # ensure GHG Emissions numeric (fill 0 if missing)
        if "GHG Emissions" in cities_df.columns:
            cities_df["GHG Emissions"] = pd.to_numeric(cities_df["GHG Emissions"], errors="coerce").fillna(0)
        total = cities_df.shape[0]
        completed = int(cities_df[cities_df.get("CAP Status", "") == "Completed"].shape[0]) if "CAP Status" in cities_df.columns else 0
        c1, c2, c3 = st.columns(3)
        c1.metric("Cities loaded", total)
        c2.metric("CAPs completed", completed)
        # District-wise CAP completion
        if "District" in cities_df.columns and "CAP Status" in cities_df.columns:
            ds = cities_df.groupby("District").apply(lambda x: (x["CAP Status"] == "Completed").sum()).reset_index()
            ds.columns = ["District", "CAPs Completed"]
            fig = px.bar(ds, x="District", y="CAPs Completed", title="District-wise CAP completion", color_discrete_sequence=["#4f7ae6"])
            fig.update_layout(plot_bgcolor="#0b0b0b", paper_bgcolor="#0b0b0b", font_color="#e8e8e8")
            st.plotly_chart(fig, use_container_width=True)
        # GHG emissions by city (if available)
        if "GHG Emissions" in cities_df.columns:
            df_sorted = cities_df.sort_values("GHG Emissions", ascending=False)
            fig2 = px.bar(df_sorted, x="City Name", y="GHG Emissions", title="GHG Emissions by City (tCO₂e)", color_discrete_sequence=["#9bdc9b"])
            fig2.update_layout(plot_bgcolor="#0b0b0b", paper_bgcolor="#0b0b0b", font_color="#e8e8e8")
            st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# CITY DASHBOARD
# ---------------------------
elif menu == "City Dashboard":
    st.header("City Dashboard")
    if cities_df.empty:
        st.info("No city metadata; admin should add cities.")
    else:
        city_list = cities_df["City Name"].dropna().unique()
        city_sel = st.selectbox("Select city", city_list)
        meta_row = cities_df[cities_df["City Name"] == city_sel].iloc[0]

        st.subheader(f"{city_sel} — Overview")
        col1, col2, col3 = st.columns(3)
        col1.metric("District", meta_row.get("District", "—"))
        col2.metric("Population (2011)", format_pop_indian(meta_row.get("Population", None)))
        capstatus = meta_row.get("CAP Status", "—")
        col3.metric("CAP status", capstatus)

        # find CAP raw data (computed) for the city
        if (not cap_raw_df.empty) and ("City Name" in cap_raw_df.columns) and (city_sel in cap_raw_df["City Name"].values):
            row = cap_raw_df[cap_raw_df["City Name"] == city_sel].iloc[0].to_dict()
            # reconstruct raw dict needed for computation
            raw_for_calc = {
                "energy_electricity_kwh": row.get("Energy Electricity (kWh)", 0),
                "energy_fuel_l": row.get("Energy Fuel (L)", 0),
                "petrol_l": row.get("Petrol (L)", 0),
                "diesel_l": row.get("Diesel (L)", 0),
                "transport_fuel_l": row.get("Transport Fuel (L)", 0),
                "transport_petrol_l": row.get("Transport Petrol (L)", 0),
                "transport_diesel_l": row.get("Transport Diesel (L)", 0),
                "buildings_energy_kwh": row.get("Buildings Energy (kWh)", 0),
                "industry_energy_kwh": row.get("Industry Energy (kWh)", 0),
                "waste_generated_t": row.get("Waste Generated (t)", 0),
                "waste_landfill_pct": row.get("Waste to Landfill (%)", 100),
                "water_consumption_ml": row.get("Water Consumption (ML)", 0),
                "wastewater_generated_ml": row.get("Wastewater Generated (ML)", 0),
                "urban_green_ha": row.get("Urban Green Cover (ha)", 0),
                "other_emissions_t": row.get("Other Emissions (tCO2e)", 0)
            }
            emm = compute_emissions_from_raw(raw_for_calc)
            total_t = emm.get("Total", 0.0)
            # per-capita if population present
            pop_val = safe_float(meta_row.get("Population", 0))
            per_capita = total_t / pop_val if pop_val > 0 else None

            st.metric("Total GHG (tCO₂e/year)", f"{total_t:,.1f}")
            if per_capita:
                st.metric("Per-capita (tCO₂e / person / year)", f"{per_capita:.3f}")
            else:
                st.metric("Per-capita (tCO₂e / person / year)", "—")

            # sector bar chart (show positive values for bars; show sequestration in separate label)
            sector_items = {k: v for k, v in emm.items() if k != "Total"}
            sectors = list(sector_items.keys())
            # bar values: show positive numbers; for sequestration show 0 in bar but annotate separately
            bar_vals = [max(0.0, sector_items[s]) for s in sectors]
            fig_bar = px.bar(x=sectors, y=bar_vals, title="Sector-wise emissions (tCO₂e)", labels={"x":"Sector","y":"tCO₂e"}, color_discrete_sequence=["#9bdc9b"])
            fig_bar.update_layout(plot_bgcolor="#0b0b0b", paper_bgcolor="#0b0b0b", font_color="#e8e8e8", xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)

            # Pie chart (use absolute shares, show negative as separate slice labeled 'Sequestration')
            pie_names = []
            pie_vals = []
            for s, v in sector_items.items():
                if v < 0:
                    pie_names.append(s + " (removal)")
                    pie_vals.append(abs(v))
                else:
                    pie_names.append(s)
                    pie_vals.append(v)
            if sum(pie_vals) == 0:
                st.info("All sector emissions are zero or not entered.")
            else:
                fig_pie = px.pie(values=pie_vals, names=pie_names, title="Sector share (absolute tCO₂e)")
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(plot_bgcolor="#0b0b0b", paper_bgcolor="#0b0b0b", font_color="#e8e8e8")
                st.plotly_chart(fig_pie, use_container_width=True)

            # table
            em_df = pd.DataFrame([(k, v) for k, v in sector_items.items()], columns=["Sector","tCO2e"])
            st.dataframe(em_df.style.format({"tCO2e":"{:.2f}"}), height=300)

            # download inventory excel
            excel_bytes = df_to_excel_bytes(em_df.assign(City=city_sel)[["City","Sector","tCO2e"]])
            st.download_button("Download GHG inventory (Excel)", data=excel_bytes,
                               file_name=f"{city_sel}_GHG_inventory.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        else:
            st.info("No CAP raw data recorded for this city yet. Admin: go to CAP Preparation and save raw data.")

        # Last updated month & year (based on cities file)
        if os.path.exists(CITIES_FILE):
            lu = datetime.fromtimestamp(os.path.getmtime(CITIES_FILE))
            st.markdown(f"*Last Updated: {lu.strftime('%B %Y')}*")

# ---------------------------
# ADMIN PANEL (metadata updates) - opened via top logo button
# ---------------------------
elif menu == "Admin Panel":
    # login if not authenticated
    if not st.session_state.authenticated:
        with st.form("login_form"):
            pw = st.text_input("Admin password", type="password")
            ok = st.form_submit_button("Login")
            if ok:
                if pw == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("Admin logged in.")
                else:
                    st.error("Incorrect password.")
        st.stop()

    st.header("Admin panel — add / update city metadata")
    df = cities_df.copy()
    cities_list = list(cities_districts.keys())

    with st.form("admin_form"):
        city = st.selectbox("City", cities_list)
        district = st.text_input("District (auto)", value=cities_districts[city], disabled=True)
        # load existing population if present
        existing_pop = int(df[df["City Name"]==city]["Population"].values[0]) if (city in df.get("City Name", [])) and (not pd.isna(df[df["City Name"]==city]["Population"].values[0])) else 0
        population = st.number_input("Population (as per 2011)", min_value=0, value=existing_pop, step=1000, format="%d")
        ulb = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
        cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
        ghg_meta = st.text_input("Official/Reported total GHG (tCO2e) - optional", value=(str(df[df["City Name"]==city]["GHG Emissions"].values[0]) if city in df.get("City Name", []) and not pd.isna(df[df["City Name"]==city]["GHG Emissions"].values[0]) else ""))
        env_exist = st.selectbox("Environment Department exists?", ["Yes", "No"], index=0)
        dept_name = st.text_input("Department Name", value=(df[df["City Name"]==city]["Department Name"].values[0] if city in df.get("City Name", []) else ""))
        head_name = st.text_input("Head Name", value=(df[df["City Name"]==city]["Head Name"].values[0] if city in df.get("City Name", []) else ""))
        dept_email = st.text_input("Department Email", value=(df[df["City Name"]==city]["Department Email"].values[0] if city in df.get("City Name", []) else ""))
        submit_meta = st.form_submit_button("Save city metadata")
        if submit_meta:
            new_row = {
                "City Name": city,
                "District": district,
                "Population": population,
                "ULB Category": ulb,
                "CAP Status": cap_status,
                "GHG Emissions": ghg_meta,
                "Environment Department Exist": env_exist,
                "Department Name": dept_name,
                "Head Name": head_name,
                "Department Email": dept_email
            }
            if city in df.get("City Name", []):
                idx = df[df["City Name"] == city].index[0]
                df.loc[idx] = new_row
                st.success(f"{city} updated.")
            else:
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"{city} added.")
            cities_df = df
            save_df(cities_df, CITIES_FILE)
            st.session_state.last_updated = datetime.now()

# ---------------------------
# CAP PREPARATION - unified raw data form (admin-only)
# ---------------------------
elif menu == "CAP Preparation":
    # require admin login
    if not st.session_state.authenticated:
        with st.form("login_form_cap"):
            pw = st.text_input("Admin password", type="password")
            ok = st.form_submit_button("Login for CAP Preparation")
            if ok:
                if pw == ADMIN_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("Admin logged in.")
                else:
                    st.error("Incorrect password.")
        st.stop()

    st.header("CAP Preparation — Unified raw data input (all sectors)")
    st.markdown("Enter raw activity data here. Optional uploads are only for verification. After saving, emissions are computed automatically using inline default factors.")

    # load city list from cities metadata; if none, use cities_districts keys
    city_choices = cities_df["City Name"].dropna().unique() if not cities_df.empty else list(cities_districts.keys())
    if len(city_choices) == 0:
        city_choices = list(cities_districts.keys())

    with st.form("cap_unified_form"):
        city_sel = st.selectbox("Select city", city_choices, key="cap_city_sel")
        st.subheader("ENERGY (stationary)")
        energy_electricity_kwh = st.number_input("Electricity consumption — total (kWh / year)", min_value=0, value=0, step=1000, key="f_energy_elec")
        energy_fuel_l = st.number_input("Other fossil fuels — total (L / year) [if mixed fuels use total liters]", min_value=0, value=0, step=1000, key="f_energy_fuel")
        petrol_l = st.number_input("Petrol (L / year) — optional", min_value=0, value=0, key="f_petrol")
        diesel_l = st.number_input("Diesel (L / year) — optional", min_value=0, value=0, key="f_diesel")
        lpg_l = st.number_input("LPG (L / year) — optional", min_value=0, value=0, key="f_lpg")
        energy_upload = st.file_uploader("Upload energy supporting file (optional)", type=["xlsx","csv","pdf"], key="f_energy_upload")

        st.subheader("TRANSPORT")
        transport_fuel_l = st.number_input("Transport fuel — total (L / year)", min_value=0, value=0, step=1000, key="f_transport_fuel")
        transport_petrol_l = st.number_input("Transport petrol (L / year) — optional", min_value=0, value=0, key="f_transport_petrol")
        transport_diesel_l = st.number_input("Transport diesel (L / year) — optional", min_value=0, value=0, key="f_transport_diesel")
        total_vehicles = st.number_input("Total registered vehicles (approx)", min_value=0, value=0, key="f_total_vehicles")
        public_transport_ridership = st.number_input("Annual public transport ridership (passenger trips)", min_value=0, value=0, key="f_public_ridership")
        transport_upload = st.file_uploader("Upload transport supporting file (optional)", type=["xlsx","csv","pdf"], key="f_transport_upload")

        st.subheader("BUILDINGS")
        buildings_count = st.number_input("Number of buildings (approx)", min_value=0, value=0, key="f_buildings_count")
        buildings_area = st.number_input("Total built-up area (sq.m)", min_value=0, value=0, key="f_buildings_area")
        buildings_energy_kwh = st.number_input("Buildings electricity (kWh / year) — optional", min_value=0, value=0, key="f_buildings_energy")
        buildings_upload = st.file_uploader("Upload buildings supporting file (optional)", type=["xlsx","csv","pdf"], key="f_buildings_upload")

        st.subheader("WATER & WASTEWATER")
        water_consumption_ml = st.number_input("Water supplied (ML / year)", min_value=0, value=0, key="f_water_ml")
        wastewater_generated_ml = st.number_input("Wastewater treated/generated (ML / year)", min_value=0, value=0, key="f_wastewater_ml")
        water_upload = st.file_uploader("Upload water supporting file (optional)", type=["xlsx","csv","pdf"], key="f_water_upload")

        st.subheader("WASTE")
        waste_generated_t = st.number_input("MSW generated (tonnes / year)", min_value=0, value=0, key="f_waste_t")
        waste_recycled_t = st.number_input("MSW recycled/composted (tonnes / year)", min_value=0, value=0, key="f_waste_recycled")
        waste_landfill_pct = st.number_input("Share sent to landfill (%)", min_value=0, max_value=100, value=100, key="f_waste_landfill_pct")
        waste_upload = st.file_uploader("Upload waste supporting file (optional)", type=["xlsx","csv","pdf"], key="f_waste_upload")

        st.subheader("INDUSTRY")
        industry_units = st.number_input("Number of industrial units (approx)", min_value=0, value=0, key="f_industry_units")
        industry_energy_kwh = st.number_input("Industry electricity (kWh / year)", min_value=0, value=0, key="f_industry_energy")
        industry_upload = st.file_uploader("Upload industry supporting file (optional)", type=["xlsx","csv","pdf"], key="f_industry_upload")

        st.subheader("URBAN GREEN & LAND USE")
        urban_green_ha = st.number_input("Urban green cover / tree area (ha)", min_value=0, value=0, key="f_urban_green")
        urban_green_upload = st.file_uploader("Upload urban green supporting file (optional)", type=["xlsx","csv","pdf"], key="f_urban_green_upload")

        st.subheader("OTHER")
        other_emissions_t = st.number_input("Other emissions (tCO2e / year) — methane, fugitive etc.", min_value=0.0, value=0.0, key="f_other_t")
        other_upload = st.file_uploader("Upload other supporting file (optional)", type=["xlsx","csv","pdf"], key="f_other_upload")

        save = st.form_submit_button("Save raw data & compute emissions")

    # after form
    if save:
        # prepare raw row dict
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
            "Buildings Area (sq.m)": buildings_area,
            "Buildings Energy (kWh)": buildings_energy_kwh,
            "Water Consumption (ML)": water_consumption_ml,
            "Wastewater Generated (ML)": wastewater_generated_ml,
            "Waste Generated (t)": waste_generated_t,
            "Waste Recycled (t)": waste_recycled_t,
            "Waste to Landfill (%)": waste_landfill_pct,
            "Industry Units": industry_units,
            "Industry Energy (kWh)": industry_energy_kwh,
            "Urban Green Cover (ha)": urban_green_ha,
            "Other Emissions (tCO2e)": other_emissions_t
        }

        # compute emissions
        raw_for_calc = {
            "energy_electricity_kwh": energy_electricity_kwh,
            "energy_fuel_l": energy_fuel_l,
            "petrol_l": petrol_l,
            "diesel_l": diesel_l,
            "transport_fuel_l": transport_fuel_l,
            "transport_petrol_l": transport_petrol_l,
            "transport_diesel_l": transport_diesel_l,
            "buildings_energy_kwh": buildings_energy_kwh,
            "industry_energy_kwh": industry_energy_kwh,
            "waste_generated_t": waste_generated_t,
            "waste_landfill_pct": waste_landfill_pct,
            "water_consumption_ml": water_consumption_ml,
            "wastewater_generated_ml": wastewater_generated_ml,
            "urban_green_ha": urban_green_ha,
            "other_emissions_t": other_emissions_t
        }
        computed = compute_emissions_from_raw(raw_for_calc)

        # attach computed into raw_row
        for k, v in computed.items():
            raw_row[k] = v

        # update cap_raw_df (create if empty)
        cap_df = cap_raw_df.copy() if cap_raw_df is not None else pd.DataFrame()
        if "City Name" in cap_df.columns and (city_sel in cap_df["City Name"].values):
            idx = cap_df[cap_df["City Name"] == city_sel].index[0]
            cap_df.loc[idx] = raw_row
        else:
            cap_df = pd.concat([cap_df, pd.DataFrame([raw_row])], ignore_index=True)

        # persist
        cap_raw_df = cap_df
        save_df(cap_raw_df, CAP_RAW_FILE)

        # update cities meta GHG Emissions column with computed total
        cities_meta = cities_df.copy()
        total_t = computed.get("Total", 0.0)
        if city_sel in cities_meta.get("City Name", []):
            idxm = cities_meta[cities_meta["City Name"] == city_sel].index[0]
            cities_meta.at[idxm, "GHG Emissions"] = total_t
        else:
            # add minimal meta row if not present
            new_meta = {
                "City Name": city_sel,
                "District": cities_districts.get(city_sel, ""),
                "Population": 0,
                "ULB Category": "",
                "CAP Status": "Not Started",
                "GHG Emissions": total_t,
                "Environment Department Exist": "",
                "Department Name": "",
                "Head Name": "",
                "Department Email": ""
            }
            cities_meta = pd.concat([cities_meta, pd.DataFrame([new_meta])], ignore_index=True)
        save_df(cities_meta, CITIES_FILE)
        # update in-memory references
        cities_df = cities_meta
        cap_raw_df = cap_df
        st.success(f"Saved CAP raw data for {city_sel}. Computed total: {total_t:,.2f} tCO₂e/year")

        # allow download of this city's raw + computed row (outside form)
        city_row_df = cap_raw_df[cap_raw_df["City Name"] == city_sel]
        csv_bytes = city_row_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download this city's CAP raw data + computed emissions (CSV)", data=csv_bytes,
                           file_name=f"{city_sel}_CAP_raw_and_emissions.csv", mime="text/csv")

# ---------------------------
# End of file
# ---------------------------
