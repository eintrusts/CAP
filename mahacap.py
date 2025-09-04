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
# Data Files
# ---------------------------
DATA_FILE = "cities_data.csv"
CAP_FILE = "cap_preparation_data.csv"

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
if "admin_section" not in st.session_state:
    st.session_state.admin_section = "For Dashboard"

# Load data
if os.path.exists(DATA_FILE):
    st.session_state.data = pd.read_csv(DATA_FILE)
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Department Email"
    ])

if os.path.exists(CAP_FILE):
    st.session_state.cap_data = pd.read_csv(CAP_FILE)
else:
    st.session_state.cap_data = pd.DataFrame()

# ---------------------------
# Helper Functions
# ---------------------------
def get_val(row: pd.Series, target: str, default="—"):
    return row[target] if target in row and pd.notna(row[target]) else default

def format_population(num):
    if pd.isna(num) or num == "":
        return "—"
    return "{:,}".format(int(num))

def update_last_updated():
    st.session_state.last_updated = pd.Timestamp.now()

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

# Sidebar navigation
if st.sidebar.button("Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("City Dashboard"):
    st.session_state.menu = "City Dashboard"
if st.sidebar.button("Admin Panel"):
    st.session_state.menu = "Admin Panel"

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
        st.markdown("View detailed information for each city.")

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

        # Display last updated month & year
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
        st.write("Select the admin section below:")

        # Closed access buttons for admin sections
        st.session_state.admin_section = st.radio("Choose Section", ["For Dashboard", "For CAP Preparation"])

        # ---------------------------
        # Admin Dashboard Section
        # ---------------------------
        if st.session_state.admin_section == "For Dashboard":
            st.subheader("City Data Management")

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
             
                    # Save data
                    st.session_state.data = df
                    df.to_csv(DATA_FILE, index=False)
                    update_last_updated()

        # ---------------------------
        # CAP Preparation Section
        # ---------------------------
        elif st.session_state.admin_section == "For CAP Preparation":
            st.subheader("CAP Preparation - GHG Inventory & Action Plan")

            df = st.session_state.data
            cities_list = list(cities_districts.keys())

            with st.form("cap_form"):
                city_name = st.selectbox("Select City for CAP Preparation", cities_list)
                district = st.text_input("District", value=cities_districts[city_name], disabled=True)
                population_val = df[df["City Name"]==city_name]["Population"].values[0] if city_name in df.get("City Name", []) else 0
                population = st.number_input("Population(as per 2011 census)", min_value=0, value=int(population_val), step=1000, format="%d")

                st.markdown("### Scope 1: Direct Emissions")
                diesel = st.number_input("Diesel Consumption (liters)", min_value=0, value=0)
                petrol = st.number_input("Petrol Consumption (liters)", min_value=0, value=0)
                natural_gas = st.number_input("Natural Gas Consumption (m³)", min_value=0, value=0)
                fugitive = st.number_input("Fugitive Emissions (kg CO2e)", min_value=0, value=0)

                st.markdown("### Scope 2: Indirect Emissions")
                electricity = st.number_input("Electricity Consumption (kWh)", min_value=0, value=0)
                heat = st.number_input("Purchased Heat/Steam/Cooling (GJ)", min_value=0, value=0)

                st.markdown("### Scope 3: Other Indirect Emissions")
                waste = st.number_input("Waste Generated (tons)", min_value=0, value=0)
                water = st.number_input("Water & Wastewater Treatment Emissions (kg CO2e)", min_value=0, value=0)
                transport = st.number_input("Municipal Transportation Emissions (kg CO2e)", min_value=0, value=0)
                procurement = st.number_input("Procurement & Supply Chain Emissions (kg CO2e)", min_value=0, value=0)

                st.markdown("### Sectoral Breakdown")
                buildings = st.number_input("Buildings Energy Use (kg CO2e)", min_value=0, value=0)
                transport_sector = st.number_input("Transport Sector Emissions (kg CO2e)", min_value=0, value=0)
                waste_sector = st.number_input("Waste Management Emissions (kg CO2e)", min_value=0, value=0)
                industry = st.number_input("Industry Emissions (kg CO2e)", min_value=0, value=0)
                green_cover = st.number_input("Urban Forestry & Green Cover (kg CO2e)", min_value=0, value=0)

                st.markdown("### CAP Goals & Actions")
                renewable = st.text_area("Renewable Energy Targets")
                ev_transport = st.text_area("EV & Public Transport Targets")
                energy_efficiency = st.text_area("Energy Efficiency Programs")
                waste_energy = st.text_area("Waste-to-Energy Initiatives")
                urban_greening = st.text_area("Urban Greening / Forestry Targets")
                additional_notes = st.text_area("Additional Notes / References")

                submit_cap = st.form_submit_button("Save CAP Preparation Data")
                if submit_cap:
                    new_cap_row = {
                        "City Name": city_name,
                        "District": district,
                        "Population": population,
                        "Diesel Consumption (liters)": diesel,
                        "Petrol Consumption (liters)": petrol,
                        "Natural Gas Consumption (m³)": natural_gas,
                        "Fugitive Emissions (kg CO2e)": fugitive,
                        "Electricity Consumption (kWh)": electricity,
                        "Purchased Heat/Steam/Cooling (GJ)": heat,
                        "Waste Generated (tons)": waste,
                        "Water & Wastewater Treatment Emissions (kg CO2e)": water,
                        "Municipal Transportation Emissions (kg CO2e)": transport,
                        "Procurement & Supply Chain Emissions (kg CO2e)": procurement,
                        "Buildings Energy Use (kg CO2e)": buildings,
                        "Transport Sector Emissions (kg CO2e)": transport_sector,
                        "Waste Management Emissions (kg CO2e)": waste_sector,
                        "Industry Emissions (kg CO2e)": industry,
                        "Urban Forestry & Green Cover (kg CO2e)": green_cover,
                        "Renewable Energy Targets": renewable,
                        "EV & Public Transport Targets": ev_transport,
                        "Energy Efficiency Programs": energy_efficiency,
                        "Waste-to-Energy Initiatives": waste_energy,
                        "Urban Greening / Forestry Targets": urban_greening,
                        "Additional Notes": additional_notes
                    }

                    cap_df = st.session_state.cap_data
                    cap_df = pd.concat([cap_df, pd.DataFrame([new_cap_row])], ignore_index=True)
                    st.session_state.cap_data = cap_df
                    cap_df.to_csv(CAP_FILE, index=False)
                    update_last_updated()
                    st.success(f"CAP Preparation Data for {city_name} saved successfully.")
