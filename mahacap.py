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
# Data File for Persistence
# ---------------------------
DATA_FILE = "cities_data.csv"
CAP_RAW_FILE = "cap_raw_data.csv"

# ---------------------------
# Cities and Districts
# ---------------------------
cities_districts = {
    "Mumbai": "Mumbai",
    "Kalyan-Dombivli": "Thane",
    "Mira-Bhayandar": "Thane",
    "Navi Mumbai": "Thane",
    "Bhiwandi": "Thane",
    "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane",
    "Vasai-Virar": "Thane",
    "Thane": "Thane",
    "Badlapur Council": "Thane",
    "Pune": "Pune",
    "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad",
    "Raigad Council": "Raigad",
    "Malegaon": "Nashik",
    "Nashik": "Nashik",
    "Nandurbar Council": "Nandurbar",
    "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon",
    "Dhule": "Dhule",
    "Ahmednagar": "Ahmednagar",
    "Aurangabad": "Aurangabad",
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
    "Osmanabad Council": "Osmanabad",
    "Latur": "Latur",
    "Udgir Coucil": "Latur",
    "Akola": "Akola",
    "Parbhani Council": "Parbhani",
    "Amravati": "Amravati",
    "Achalpur Council": "Amravati",
    "Wardha Coumcil": "Wardha",
    "Hinganghat Ciuncil": "Wardha",
    "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State Initialization
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if os.path.exists(DATA_FILE):
    st.session_state.data = pd.read_csv(DATA_FILE)
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Department Email"
    ])

if os.path.exists(CAP_RAW_FILE):
    st.session_state.cap_raw_data = pd.read_csv(CAP_RAW_FILE).set_index("City").T.to_dict()
else:
    st.session_state.cap_raw_data = {}

# ---------------------------
# Helper Functions
# ---------------------------
def get_val(row: pd.Series, target: str, default="—"):
    return row[target] if target in row and pd.notna(row[target]) else default

def format_population(num):
    if pd.isna(num) or num == "":
        return "—"
    return "{:,}".format(int(num))

def calculate_ghg_inventory(raw):
    """Estimate GHG inventory based on raw data (simplified factors)"""
    # Emission factors (simplified)
    diesel_factor = 2.68 / 1000  # tCO2e per liter
    petrol_factor = 2.31 / 1000
    electricity_factor = 0.82 / 1000  # tCO2e per kWh
    transport_factor = 0.0002  # tCO2e per km
    waste_factor = 0.25  # tCO2e per ton

    ghg_total = 0
    ghg_total += raw.get("Diesel consumption",0)*diesel_factor
    ghg_total += raw.get("Petrol consumption",0)*petrol_factor
    ghg_total += raw.get("Electricity consumption",0)*electricity_factor
    ghg_total += raw.get("Municipal vehicles km",0)*transport_factor
    ghg_total += raw.get("Public buses km",0)*transport_factor
    ghg_total += raw.get("Private vehicles km",0)*transport_factor
    ghg_total += raw.get("Freight km",0)*transport_factor
    ghg_total += raw.get("Waste generated",0)*waste_factor
    ghg_total += raw.get("Industrial fuel consumption",0)*diesel_factor
    ghg_total += raw.get("Industrial electricity",0)*electricity_factor
    ghg_total += raw.get("Process emissions",0)
    ghg_total -= raw.get("Carbon sequestration",0)  # subtract sequestration

    return round(ghg_total,2)

def suggest_cap_actions(raw):
    """Suggest basic CAP actions based on raw inputs"""
    actions = []
    if raw.get("Electricity consumption",0) > 1000000:
        actions.append("Increase renewable energy penetration")
    if raw.get("Private vehicles km",0) > 500000:
        actions.append("Promote public transport & EV adoption")
    if raw.get("Waste recycled %",0) < 50:
        actions.append("Enhance waste segregation & recycling programs")
    if raw.get("Urban green cover area",0) < 20:
        actions.append("Urban forestry and green cover expansion")
    if raw.get("Industrial electricity",0) > 500000:
        actions.append("Implement industrial energy efficiency programs")
    return actions if actions else ["General CAP actions: renewable energy, efficiency, transport, waste, forestry"]

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

st.sidebar.markdown(
    """
    <style>
    .css-1d391kg button { 
        background-color: #228B22 !important; 
        color: white !important; 
        width: 100%;
        margin-bottom: 5px;
        height: 40px;
        font-size: 16px;
        border-radius: 5px;
    }
    .css-1d391kg button:hover { 
        background-color: #196619 !important; 
        color: white !important; 
    }
    </style>
    """, unsafe_allow_html=True
)

# Sidebar buttons
if st.sidebar.button("Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("City Dashboard"):
    st.session_state.menu = "City Dashboard"
if st.sidebar.button("Admin Panel"):
    st.session_state.menu = "Admin Panel"
if st.session_state.authenticated:
    if st.sidebar.button("CAP Preparation"):
        st.session_state.menu = "CAP Preparation"

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")
menu = st.session_state.menu

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
            else:
                st.error("Incorrect password")

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra CAP Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")
    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        total_cities = df.shape[0]
        cities_done = df[df["CAP Status"] == "Completed"].shape[0]
        st.metric("Total Cities", total_cities)
        st.metric("Cities with CAP Completed", cities_done)

        if "GHG Emissions" in df.columns:
            fig2 = px.bar(df, x="City Name", y="GHG Emissions", title="GHG Emissions by City", text="GHG Emissions")
            st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        st.header("City Dashboard")
        city_col = "City Name"
        city = st.selectbox("Select City", df[city_col].dropna().unique())
        city_row = df[df[city_col] == city].iloc[0]

        st.subheader(f"{city} Details")
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
        
        # GHG inventory from CAP raw data
        if city in st.session_state.cap_raw_data:
            raw = st.session_state.cap_raw_data[city]
            ghg_total = calculate_ghg_inventory(raw)
            st.write(f"**Estimated Total GHG Emissions:** {ghg_total} tCO2e/year")
            st.write("**Suggested CAP Actions:**")
            for act in suggest_cap_actions(raw):
                st.write(f"- {act}")
        
        # Last updated
        if "last_updated" in st.session_state:
            last_updated = st.session_state.last_updated
        else:
            last_updated = pd.to_datetime(os.path.getmtime(DATA_FILE), unit='s')
        st.markdown(f"*Last Updated: {last_updated.strftime('%B %Y')}*")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("Admin Panel")
        st.write("Add or update city data below. Changes will reflect on the dashboard immediately.")
        df = st.session_state.data
        cities_list = list(cities_districts.keys())
        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list)
            district = st.text_input("District", value=cities_districts[city_name], disabled=True)
            population_val = df[df["City Name"]==city_name]["Population"].values[0] if city_name in df.get("City Name", []) else 0
            population = st.number_input("Population(as per 2011 census)", min_value=0, value=int(population_val), step=1000, format="%d")
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            ghg = st.text_input("GHG Emissions (MTCO2e)", df[df["City Name"]==city_name]["GHG Emissions"].values[0] if city_name in df.get("City Name", []) else "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"], index=0)
            dept_name = st.text_input("Department Name", df[df["City Name"]==city_name]["Department Name"].values[0] if city_name in df.get("City Name", []) else "")
            head_name = st.text_input("Head Name", df[df["City Name"]==city_name]["Head Name"].values[0] if city_name in df.get("City Name", []) else "")
            dept_email = st.text_input("Department Email", df[df["City Name"]==city_name]["Department Email"].values[0] if city_name in df.get("City Name", []) else "")
            submit = st.form_submit_button("Add/Update City")
            if submit:
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
                    idx = df[df["City Name"] == city_name].index[0]
                    df.loc[idx] = new_row
                    st.success(f"{city_name} updated successfully.")
                else:
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"{city_name} added successfully.")
                st.session_state.data = df
                df.to_csv(DATA_FILE, index=False)
                st.session_state.last_updated = pd.Timestamp.now()

# ---------------------------
# CAP Preparation
# ---------------------------
elif menu == "CAP Preparation":
    if not st.session_state.authenticated:
        st.info("Admin login required for CAP preparation.")
        admin_login()
    else:
        st.header("CAP Preparation - Detailed Raw Data Input")
        st.write("Fill in city-specific raw data to generate a comprehensive GHG inventory.")
        
        cities_list = list(cities_districts.keys())
        city_name = st.selectbox("Select City for CAP", cities_list)

        if city_name not in st.session_state.cap_raw_data:
            st.session_state.cap_raw_data[city_name] = {}

        raw_data = st.session_state.cap_raw_data[city_name]
        uploaded_files = {}

        with st.form("cap_form"):
            # Energy & Fuel
            st.subheader("1. Energy & Fuel")
            raw_data["Diesel consumption"] = st.number_input("Diesel consumption (liters/year)", min_value=0, value=raw_data.get("Diesel consumption",0))
            uploaded_files["Diesel proof"] = st.file_uploader("Upload proof for Diesel consumption (optional)", type=["csv","xlsx","pdf"])
            raw_data["Petrol consumption"] = st.number_input("Petrol consumption (liters/year)", min_value=0, value=raw_data.get("Petrol consumption",0))
            uploaded_files["Petrol proof"] = st.file_uploader("Upload proof for Petrol consumption (optional)", type=["csv","xlsx","pdf"])
            raw_data["Electricity consumption"] = st.number_input("Electricity consumption (kWh/year)", min_value=0, value=raw_data.get("Electricity consumption",0))
            uploaded_files["Electricity proof"] = st.file_uploader("Upload electricity bills/proof (optional)", type=["csv","xlsx","pdf"])

            # Transport
            st.subheader("2. Transport & Mobility")
            raw_data["Municipal vehicles km"] = st.number_input("Municipal fleet km traveled/year", min_value=0, value=raw_data.get("Municipal vehicles km",0))
            uploaded_files["Municipal vehicles proof"] = st.file_uploader("Upload proof for Municipal vehicles km (optional)", type=["csv","xlsx","pdf"])
            raw_data["Public buses km"] = st.number_input("Public buses km traveled/year", min_value=0, value=raw_data.get("Public buses km",0))
            uploaded_files["Public buses proof"] = st.file_uploader("Upload proof for Public buses km (optional)", type=["csv","xlsx","pdf"])
            raw_data["Private vehicles km"] = st.number_input("Private vehicles km/year", min_value=0, value=raw_data.get("Private vehicles km",0))
            uploaded_files["Private vehicles proof"] = st.file_uploader("Upload proof for Private vehicles km (optional)", type=["csv","xlsx","pdf"])
            raw_data["Freight km"] = st.number_input("Freight transport km/year", min_value=0, value=raw_data.get("Freight km",0))
            uploaded_files["Freight proof"] = st.file_uploader("Upload proof for Freight km (optional)", type=["csv","xlsx","pdf"])

            # Buildings
            st.subheader("3. Buildings & Infrastructure")
            raw_data["Residential electricity"] = st.number_input("Residential electricity consumption (kWh/year)", min_value=0, value=raw_data.get("Residential electricity",0))
            uploaded_files["Residential proof"] = st.file_uploader("Upload proof (optional)", type=["csv","xlsx","pdf"])
            raw_data["Commercial electricity"] = st.number_input("Commercial electricity consumption (kWh/year)", min_value=0, value=raw_data.get("Commercial electricity",0))
            uploaded_files["Commercial proof"] = st.file_uploader("Upload proof (optional)", type=["csv","xlsx","pdf"])
            raw_data["Municipal buildings electricity"] = st.number_input("Municipal buildings electricity (kWh/year)", min_value=0, value=raw_data.get("Municipal buildings electricity",0))
            uploaded_files["Municipal buildings proof"] = st.file_uploader("Upload proof (optional)", type=["csv","xlsx","pdf"])

            # Waste & Water
            st.subheader("4. Waste & Water")
            raw_data["Waste generated"] = st.number_input("Municipal solid waste generated (tons/year)", min_value=0, value=raw_data.get("Waste generated",0))
            uploaded_files["Waste proof"] = st.file_uploader("Upload proof (optional)", type=["csv","xlsx","pdf"])
            raw_data["Waste recycled %"] = st.slider("Waste recycled (%)", min_value=0, max_value=100, value=raw_data.get("Waste recycled %",0))
            raw_data["Waste to landfill"] = st.number_input("Waste sent to landfill (tons/year)", min_value=0, value=raw_data.get("Waste to landfill",0))
            raw_data["Sewage treated"] = st.number_input("Sewage treated (m³/year)", min_value=0, value=raw_data.get("Sewage treated",0))
            raw_data["Water consumption"] = st.number_input("Municipal water consumption (m³/year)", min_value=0, value=raw_data.get("Water consumption",0))

            # Industrial
            st.subheader("5. Industrial Emissions")
            raw_data["Industrial fuel consumption"] = st.number_input("Industrial fuel consumption (liters/year)", min_value=0, value=raw_data.get("Industrial fuel consumption",0))
            raw_data["Industrial electricity"] = st.number_input("Industrial electricity consumption (kWh/year)", min_value=0, value=raw_data.get("Industrial electricity",0))
            raw_data["Process emissions"] = st.number_input("Process-related emissions (tCO2e/year)", min_value=0, value=raw_data.get("Process emissions",0))

            # Land Use
            st.subheader("6. Land Use & Forestry")
            raw_data["Urban green cover area"] = st.number_input("Urban green cover area (ha)", min_value=0, value=raw_data.get("Urban green cover area",0))
            raw_data["Trees planted/year"] = st.number_input("Number of trees planted/year", min_value=0, value=raw_data.get("Trees planted/year",0))
            raw_data["Carbon sequestration"] = st.number_input("Estimated carbon sequestration (tCO2e/year)", min_value=0, value=raw_data.get("Carbon sequestration",0))

            # Other emissions
            st.subheader("7. Other Emission Sources")
            raw_data["Refrigerants HFCs"] = st.number_input("Refrigerants (HFCs) tCO2e/year", min_value=0, value=raw_data.get("Refrigerants HFCs",0))
            raw_data["Other emissions"] = st.number_input("Other emissions (tCO2e/year)", min_value=0, value=raw_data.get("Other emissions",0))

            submit = st.form_submit_button("Save CAP Raw Data & Generate Actions")
            if submit:
                st.session_state.cap_raw_data[city_name] = raw_data
                # Save to CSV
                pd.DataFrame.from_dict({city_name: raw_data}, orient="index").reset_index().rename(columns={"index":"City"}).to_csv(
                    CAP_RAW_FILE, mode='a', header=not os.path.exists(CAP_RAW_FILE), index=False
                )
                st.success(f"Raw data saved for {city_name}. You can now calculate GHG inventory and recommended CAP actions.")

        # Download CAP data
        st.subheader("Download CAP Raw Data")
        if os.path.exists(CAP_RAW_FILE):
            st.download_button(
                label="Download CAP CSV",
                data=open(CAP_RAW_FILE, "rb").read(),
                file_name="CAP_Raw_Data.csv",
                mime="text/csv"
            )
        else:
            st.info("No CAP data available to download yet.")
