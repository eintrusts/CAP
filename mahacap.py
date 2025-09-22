import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Maharashtra CAP Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- Utilities --------------------
def format_inr(value):
    return "{:,}".format(value)

def last_updated():
    return datetime.datetime.now().strftime("%B %Y")

# -------------------- Data Storage --------------------
if 'city_data' not in st.session_state:
    st.session_state.city_data = {}

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Home"

cities = ["Mumbai","Kalyan-Dombivli","Mira-Bhayandar","Navi Mumbai","Bhiwandi-Nizampur",
          "Ulhasnagar","Ambernath Council","Vasai-Virar","Thane","Badlapur Council",
          "Pune","Pimpri-Chinchwad","Panvel","Malegaon","Nashik","Nandurbar Council",
          "Bhusawal Council","Jalgaon","Dhule","Ahilyanagar","Chh. Sambhajinagar",
          "Jalna","Beed Council","Satara Council","Sangli-Miraj-Kupwad","Kolhapur",
          "Ichalkaranji","Solapur","Barshi Council","Nanded-Waghala","Yawatmal Council",
          "Dharashiv","Latur","Udgir Coucil","Akola","Parbhani Council","Amravati",
          "Achalpur Council","Wardha Coumcil","Hinganghat Ciuncil","Nagpur","Chandrapur",
          "Gondia Council"]

# -------------------- Sidebar --------------------
def sidebar_section():
    # Ensure current_page persists across refresh
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    st.sidebar.markdown("""
    <style>
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #111827;  /* Dark background */
        color: #ffffff;
        width: 260px;
    }

    /* Sidebar Logo */
    .sidebar-logo {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 20px 0 30px 0;
    }
    .sidebar-logo img {
        max-width: 190px;
        height: auto;
    }

    /* Menu Buttons */
    .menu-btn {
        display: block;
        width: 100%;
        padding: 12px 20px;
        margin: 8px 0;
        background: linear-gradient(90deg, transparent 0%, transparent 100%);
        color: #e5e7eb;
        text-align: left;
        font-size: 16px;
        font-weight: 500;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        position: relative;
        transition: all 0.35s ease;
    }
    .menu-btn:hover {
        background: linear-gradient(90deg, #2563eb20 0%, #2563eb40 100%);
        color: #ffffff;
        transform: translateX(4px);
    }
    .menu-btn-active {
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: #ffffff !important;
        font-weight: 600;
    }

    /* Footer */
    .sidebar-footer {
        position: absolute;
        bottom: 30px;
        width: 100%;
        text-align: center;
        color: #9ca3af;
        font-size: 13px;
    }
    .sidebar-footer strong {
        color: #ffffff;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Logo
    st.sidebar.markdown(
        '<div class="sidebar-logo"><img src="https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true"></div>',
        unsafe_allow_html=True
    )

    # Sidebar Menu with Persistent Active State
    menu = ["Home", "City", "Admin"]
    for m in menu:
        btn_class = "menu-btn-active" if st.session_state.current_page == m else "menu-btn"
        if st.sidebar.button(m, key=f"menu_{m}"):
            st.session_state.current_page = m
        st.sidebar.markdown(
            f"<style>div[data-testid='stSidebar'] button[kind='secondary'][key='menu_{m}'] .st-emotion-cache-16txtl3{{"
            f"{'background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%) !important; color: white !important;' if st.session_state.current_page == m else ''}}"
            f"}}</style>",
            unsafe_allow_html=True
        )

    # Footer
    st.sidebar.markdown(
        '<div class="sidebar-footer"><strong>© EinTrust 2025</strong><br>All Rights Reserved</div>',
        unsafe_allow_html=True
    )

# -------------------- Home Page --------------------
def home_page():
    st.header("Maharashtra Net Zero Journey")
    
    # CAP Status count
    status_counts = {"Not Started":0,"In Progress":0,"Completed":0}
    for c in cities:
        status = st.session_state.city_data.get(c, {}).get("CAP_Status","Not Started")
        status_counts[status] +=1
    st.subheader("CAP Status Overview")
    st.write(f"Cities Not Started: {status_counts['Not Started']}")
    st.write(f"Cities In Progress: {status_counts['In Progress']}")
    st.write(f"Cities Completed: {status_counts['Completed']}")
    
    st.subheader("Maharashtra Basic Information")
    total_population = sum([st.session_state.city_data.get(c, {}).get("Basic Info", {}).get("Population",0) for c in cities])
    total_area = sum([st.session_state.city_data.get(c, {}).get("Basic Info", {}).get("Area",0) for c in cities])
    st.write(f"Population: {format_inr(total_population)}")
    st.write(f"Area (sq km): {format_inr(total_area)}")
    
    ghg_sectors = ["Energy","Transport","Waste","Water","Buildings","Industry"]
    ghg_values = [sum([st.session_state.city_data.get(c, {}).get("GHG", {}).get(s,0) for c in cities]) for s in ghg_sectors]
    fig = px.bar(x=ghg_sectors, y=ghg_values, labels={"x":"Sector","y":"tCO2e"}, title="Maharashtra GHG Emissions by Sector")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("RCP Scenario")
    years = list(range(2020,2051))
    rcp_values = [np.random.uniform(1,3) for _ in years]
    fig2 = px.line(x=years, y=rcp_values, labels={"x":"Year","y":"Temp Rise (°C)"}, title="Projected RCP Scenario")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown(f"<div style='position:fixed; bottom:10px; left:10px; color:#888888;'>{last_updated()}</div>", unsafe_allow_html=True)

# -------------------- City Page --------------------
def city_page():
    st.header("City-Level CAP Dashboard")
    selected_city = st.selectbox("Select City", cities, key="city_page_select")
    city_info = st.session_state.city_data.get(selected_city, {})
    
    st.subheader(f"{selected_city} Net Zero Journey")
    st.write(f"CAP Status: {city_info.get('CAP_Status','Not Started')}")
    st.write(f"Population: {format_inr(city_info.get('Basic Info',{}).get('Population',0))}")
    st.write(f"Area (sq km): {format_inr(city_info.get('Basic Info',{}).get('Area',0))}")
    st.write(f"Last Updated: {city_info.get('Last_Updated',last_updated())}")
    
    ghg = city_info.get("GHG",{})
    if ghg:
        fig = px.bar(x=list(ghg.keys()), y=list(ghg.values()), labels={"x":"Sector","y":"tCO2e"}, title=f"{selected_city} GHG Emissions by Sector")
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("RCP Scenario")
    climate = city_info.get("Climate_Data",{})
    years = list(range(2020,2051))
    rcp_values = climate.get("RCP",[np.random.uniform(1,3) for _ in years])
    fig2 = px.line(x=years, y=rcp_values, labels={"x":"Year","y":"Temp Rise (°C)"}, title=f"{selected_city} RCP Scenario")
    st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown(f"<div style='position:fixed; bottom:10px; left:10px; color:#888888;'>{last_updated()}</div>", unsafe_allow_html=True)

# -------------------- Admin Panel --------------------
def admin_panel():
    ADMIN_PASSWORD = "eintrust123"
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        st.header("Admin Login")
        password_input = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password_input == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect password")
        return

    st.header("Admin Panel")
    admin_tabs = st.tabs(["Add/Update City","Generate CAP","GHG Inventory","Logout"])

    # --- Add/Update City ---
    with admin_tabs[0]:
        st.subheader("Add / Update City")
        city_select = st.selectbox("Select City", cities, key="add_update_city")
        population = st.number_input("Population", min_value=0, key="population")
        area = st.number_input("Area (sq km)", min_value=0, key="area")
        gdp = st.number_input("GDP (₹ Crores)", min_value=0, key="gdp")
        cap_status_options = ["Not Started","In Progress","Completed"]
        cap_status_default = st.session_state.city_data.get(city_select, {}).get("CAP_Status","Not Started")
        if cap_status_default not in cap_status_options:
            cap_status_default = "Not Started"
        cap_status = st.selectbox("CAP Status", cap_status_options, index=cap_status_options.index(cap_status_default), key="cap_status_add")
        if st.button("Save City Info"):
            st.session_state.city_data[city_select] = {
                "Basic Info":{"Population":population,"Area":area,"GDP":gdp},
                "CAP_Status":cap_status,
                "Last_Updated":last_updated()
            }
            st.success(f"{city_select} information saved!")

    # --- Generate CAP ---
    with admin_tabs[1]:
        st.subheader("Generate CAP")
        city_select = st.selectbox("Select City for CAP", cities, key="cap_city_select")
        city_info = st.session_state.city_data.get(city_select, {})

        cap_tabs = st.tabs([
            "1. Basic Info","2. Energy & Buildings","3. Green Cover & Biodiversity",
            "4. Sustainable Mobility","5. Water Resources","6. Waste Management","7. Climate Data"
        ])

        # -------------------- 1. Basic Info --------------------
        with cap_tabs[0]:
            population = st.number_input("Population", min_value=0, value=city_info.get("Basic Info",{}).get("Population",0), key="cap_pop")
            area = st.number_input("Area (sq km)", min_value=0, value=city_info.get("Basic Info",{}).get("Area",0), key="cap_area")
            gdp = st.number_input("GDP (₹ Crores)", min_value=0, value=city_info.get("Basic Info",{}).get("GDP",0), key="cap_gdp")
            density = st.number_input("Population Density (people/km²)", min_value=0, key="cap_density")
            climate_zone = st.text_input("Climate Zone", value=city_info.get("Basic Info",{}).get("Climate_Zone",""), key="cap_climate_zone")
            admin_structure = st.text_input("Administrative Structure", value=city_info.get("Basic Info",{}).get("Admin",""), key="cap_admin_structure")
            cap_status_options = ["Not Started","In Progress","Completed"]
            cap_status_form_default = city_info.get("CAP_Status","Not Started")
            if cap_status_form_default not in cap_status_options:
                cap_status_form_default = "Not Started"
            cap_status_form = st.selectbox("CAP Status", cap_status_options, index=cap_status_options.index(cap_status_form_default), key="cap_status_form")
            last_updated_input = st.date_input("Last Updated", datetime.date.today(), key="cap_last_updated")

        # -------------------- 2. Energy & Buildings --------------------
        with cap_tabs[1]:
            res_energy = st.number_input("Residential Electricity Consumption (kWh/year)", min_value=0, key="res_energy")
            com_energy = st.number_input("Commercial Electricity Consumption (kWh/year)", min_value=0, key="com_energy")
            ind_energy = st.number_input("Industrial Electricity Consumption (kWh/year)", min_value=0, key="ind_energy")
            renewable_share = st.slider("Renewable Energy Share (%)", 0,100,0, key="renewable_share")
            ee_buildings = st.number_input("No. of Energy-Efficient Buildings Certified", min_value=0, key="ee_buildings")
            street_lighting_type = st.selectbox("Street Lighting Type", ["LED","CFL","Other"], key="street_type")
            street_lighting_coverage = st.slider("Street Lighting Coverage (%)",0,100,0, key="street_coverage")
            fuel_types = st.multiselect("Fuel Types Used", ["Coal","Gas","Biomass","Electricity","Petroleum"], key="fuel_types")
            public_building_energy = st.number_input("Public Building Energy Consumption (kWh/year)", min_value=0, key="public_energy")
            green_policy = st.selectbox("Green Building Policies in Place", ["Yes","No"], key="green_policy")

        # -------------------- 3. Green Cover & Biodiversity --------------------
        with cap_tabs[2]:
            green_cover_area = st.number_input("Total Green Cover Area (ha)", min_value=0, key="green_cover")
            tree_density = st.number_input("Tree Density (trees/km²)", min_value=0, key="tree_density")
            protected_areas = st.number_input("Protected Areas (ha)", min_value=0, key="protected_areas")
            biodiversity_programs = st.text_area("Biodiversity Programs", key="biodiversity_programs")
            urban_forests = st.number_input("Urban Forests Area (ha)", min_value=0, key="urban_forests")

        # -------------------- 4. Sustainable Mobility --------------------
        with cap_tabs[3]:
            public_transport_coverage = st.slider("Public Transport Coverage (%)",0,100,0, key="pt_coverage")
            non_motorized_infra = st.slider("Non-Motorized Infrastructure (%)",0,100,0, key="nmi")
            ev_charging_stations = st.number_input("No. of EV Charging Stations", min_value=0, key="ev_stations")
            veh_emissions = st.number_input("Average Vehicle Emissions (gCO2/km)", min_value=0, key="veh_emissions")
            smart_transport_projects = st.text_area("Smart Transport Projects", key="smart_projects")

        # -------------------- 5. Water Resources --------------------
        with cap_tabs[4]:
            water_consumption = st.number_input("Total Water Consumption (ML/year)", min_value=0, key="water_cons")
            wastewater_treatment = st.slider("Wastewater Treatment Coverage (%)",0,100,0, key="wwt")
            rainwater_harvesting = st.selectbox("Rainwater Harvesting Implementation", ["Yes","No"], key="rwh")
            leakage_ratio = st.slider("Water Leakage Ratio (%)",0,100,0, key="leakage_ratio")
            water_policy = st.text_area("Water Management Policies", key="water_policy")

        # -------------------- 6. Waste Management --------------------
        with cap_tabs[5]:
            total_waste = st.number_input("Total Waste Generated (t/year)", min_value=0, key="total_waste")
            waste_recycled = st.slider("Waste Recycled (%)",0,100,0, key="waste_recycled")
            waste_treatment_facilities = st.number_input("No. of Treatment Facilities", min_value=0, key="waste_facilities")
            composting_infra = st.selectbox("Composting Infrastructure", ["Yes","No"], key="composting")
            hazardous_waste_policy = st.text_area("Hazardous Waste Policy", key="hazardous_policy")

        # -------------------- 7. Climate Data --------------------
        with cap_tabs[6]:
            avg_temp = st.number_input("Average Temperature (°C)", key="avg_temp")
            rainfall = st.number_input("Annual Rainfall (mm)", key="rainfall")
            extreme_events = st.text_area("Extreme Events History", key="extreme_events")
            rcp_scenario = [st.number_input(f"RCP Year {year}", min_value=-10.0, max_value=10.0, value=0.0, key=f"rcp_{year}") for year in range(2020,2051)]

        if st.button("Save CAP Data"):
            st.session_state.city_data[city_select]["CAP"] = {
                "Basic Info":{"Population":population,"Area":area,"GDP":gdp,"Density":density,
                              "Climate_Zone":climate_zone,"Admin":admin_structure,"CAP_Status":cap_status_form,
                              "Last_Updated":last_updated_input.strftime("%B %Y")},
                "Energy_Buildings": {
                    "Residential":res_energy,"Commercial":com_energy,"Industrial":ind_energy,
                    "Renewable_Share":renewable_share,"EE_Buildings":ee_buildings,
                    "Street_Lighting_Type":street_lighting_type,"Street_Lighting_Coverage":street_lighting_coverage,
                    "Fuel_Types":fuel_types,"Public_Building_Energy":public_building_energy,"Green_Policy":green_policy
                },
                "Green_Biodiversity":{
                    "Green_Cover":green_cover_area,"Tree_Density":tree_density,"Protected_Areas":protected_areas,
                    "Programs":biodiversity_programs,"Urban_Forests":urban_forests
                },
                "Mobility":{
                    "Public_Transport":public_transport_coverage,"Non_Motorized":non_motorized_infra,
                    "EV_Stations":ev_charging_stations,"Vehicle_Emissions":veh_emissions,"Smart_Projects":smart_transport_projects
                },
                "Water":{
                    "Consumption":water_consumption,"WWT":wastewater_treatment,"RWH":rainwater_harvesting,
                    "Leakage":leakage_ratio,"Policy":water_policy
                },
                "Waste":{
                    "Total":total_waste,"Recycled":waste_recycled,"Facilities":waste_treatment_facilities,
                    "Composting":composting_infra,"Hazardous":hazardous_waste_policy
                },
                "Climate_Data":{"Avg_Temp":avg_temp,"Rainfall":rainfall,"Extreme_Events":extreme_events,"RCP":rcp_scenario}
            }
            st.success(f"CAP data for {city_select} saved successfully!")

    # --- GHG Inventory ---
    with admin_tabs[2]:
        st.subheader("GHG Inventory")
        sector = st.selectbox("Select Sector", ["Energy","Transport","Waste","Water","Buildings","Industry"], key="ghg_sector")
        ghg_values = [st.session_state.city_data.get(c, {}).get("GHG", {}).get(sector,np.random.randint(1000,10000)) for c in cities]
        df = pd.DataFrame({"City":cities, "tCO2e":ghg_values})
        st.dataframe(df)
        fig = px.bar(df, x="City", y="tCO2e", title=f"{sector} GHG Inventory by City")
        st.plotly_chart(fig, use_container_width=True)

    # --- Logout ---
    with admin_tabs[3]:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.success("Logged out successfully!")

# -------------------- Run App --------------------
sidebar_section()

if st.session_state.current_page == "Home":
    home_page()
elif st.session_state.current_page == "City":
    city_page()
elif st.session_state.current_page == "Admin":
    admin_panel()
else:
    st.title("Welcome to Maharashtra CAP Dashboard")
