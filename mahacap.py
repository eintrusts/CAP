import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import datetime, io

# -------------------- Page Config --------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", layout="wide")

# -------------------- Dark Theme --------------------
st.markdown("""
<style>
body {background-color:#0e1117; color:#ffffff;}
h1,h2,h3,h4,h5,h6{color:#ffffff;}
.stButton>button{background-color:#1f2937;color:#ffffff;}
.stTextInput>div>input{background-color:#1f2937;color:#ffffff;}
.stSelectbox>div>div>select{background-color:#1f2937;color:#ffffff;}
.stSlider>div>div>input{background-color:#1f2937;color:#ffffff;}
.stNumberInput>div>input{background-color:#1f2937;color:#ffffff;}
.footer {position: fixed; bottom: 5px; right: 10px; color: #888888; font-size:12px;}
</style>
""", unsafe_allow_html=True)

# -------------------- Utilities --------------------
def format_inr(value):
    return "{:,}".format(value)

def last_updated():
    return datetime.datetime.now().strftime("%B %Y")

# -------------------- Data Storage --------------------
if 'city_data' not in st.session_state:
    st.session_state.city_data = {}

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
st.sidebar.markdown("## EinTrust")
st.sidebar.image("https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true", use_container_width=True)
st.sidebar.markdown("---")
page = st.sidebar.radio("Menu", ["Home","City","Admin"])
st.sidebar.markdown("<div style='position:fixed; bottom:10px;'>© EinTrust</div>", unsafe_allow_html=True)

# -------------------- Admin Login --------------------
ADMIN_PASSWORD = "eintrust123"
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if page=="Admin" and not st.session_state.admin_logged_in:
    st.header("Admin Login")
    password_input = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Incorrect password")

# -------------------- Home Page --------------------
if page=="Home":
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
    st.plotly_chart(fig)
    
    st.subheader("RCP Scenario")
    years = list(range(2020,2051))
    rcp_values = [np.random.uniform(1,3) for _ in years]
    fig2 = px.line(x=years, y=rcp_values, labels={"x":"Year","y":"Temp Rise (°C)"}, title="Projected RCP Scenario")
    st.plotly_chart(fig2)
    
    st.markdown(f"<div class='footer'>Last Updated: {last_updated()}</div>", unsafe_allow_html=True)

# -------------------- City Page --------------------
elif page=="City":
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
        st.plotly_chart(fig)
    
    st.subheader("RCP Scenario")
    climate = city_info.get("Climate_Data",{})
    years = list(range(2020,2051))
    rcp_values = climate.get("RCP",[np.random.uniform(1,3) for _ in years])
    fig2 = px.line(x=years, y=rcp_values, labels={"x":"Year","y":"Temp Rise (°C)"}, title=f"{selected_city} RCP Scenario")
    st.plotly_chart(fig2)
    
    st.markdown(f"<div class='footer'>Last Updated: {city_info.get('Last_Updated', last_updated())}</div>", unsafe_allow_html=True)

# -------------------- Admin Panel --------------------
elif page=="Admin" and st.session_state.admin_logged_in:
    st.header("Admin Panel")
    admin_tabs = st.tabs(["Add/Update City","Generate CAP","GHG Inventory"])
    
    # ---------------- Add/Update City -----------------
    with admin_tabs[0]:
        st.subheader("Add / Update City")
        city_select = st.selectbox("Select City", cities, key="add_update_city")
        population = st.number_input("Population", min_value=0, key="population")
        area = st.number_input("Area (sq km)", min_value=0, key="area")
        gdp = st.number_input("GDP (₹ Crores)", min_value=0, key="gdp")
        cap_status = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"], key="cap_status_add")
        if st.button("Save City Info"):
            st.session_state.city_data[city_select] = {
                "Basic Info":{"Population":population,"Area":area,"GDP":gdp},
                "CAP_Status":cap_status,
                "Last_Updated":last_updated()
            }
            st.success(f"{city_select} information saved!")

    # ---------------- Generate CAP -----------------
    with admin_tabs[1]:
        st.subheader("Generate CAP")
        city_select = st.selectbox("Select City for CAP", cities, key="cap_city_select")
        city_info = st.session_state.city_data.get(city_select, {})

        cap_form_tabs = st.tabs([
            "1. Basic Info","2. Energy & Buildings","3. Green Cover & Biodiversity",
            "4. Sustainable Mobility","5. Water Resources","6. Waste Management","7. Climate Data"
        ])

        # ---------------- CAP Form -----------------
        # 1. Basic Info
        with cap_form_tabs[0]:
            population = st.number_input("Population", min_value=0, value=city_info.get("Basic Info",{}).get("Population",0), key="cap_pop")
            area = st.number_input("Area (sq km)", min_value=0, value=city_info.get("Basic Info",{}).get("Area",0), key="cap_area")
            gdp = st.number_input("GDP (₹ Crores)", min_value=0, value=city_info.get("Basic Info",{}).get("GDP",0), key="cap_gdp")
            density = st.number_input("Population Density (people/km²)", min_value=0, key="cap_density")
            climate_zone = st.text_input("Climate Zone", key="cap_climate_zone")
            admin_structure = st.text_input("Administrative Structure", key="cap_admin_structure")
            cap_status_form = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"], key="cap_status_form")
            last_updated_input = st.date_input("Last Updated", datetime.date.today(), key="cap_last_updated")

        # 2. Energy & Buildings
        with cap_form_tabs[1]:
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

        # 3. Green Cover & Biodiversity
        with cap_form_tabs[2]:
            green_cover_area = st.number_input("Total Green Cover Area (ha)", min_value=0, key="green_cover")
            tree_density = st.number_input("Tree Density (trees/km²)", min_value=0, key="tree_density")
            protected_areas = st.number_input("Protected / Forest Areas within City (ha)", min_value=0, key="protected_areas")
            wetlands_area = st.number_input("Wetlands / Water Bodies Coverage (ha)", min_value=0, key="wetlands_area")
            species_richness = st.text_area("Species Richness (flora & fauna)", key="species_richness")
            urban_parks = st.number_input("Number of Urban Parks / Community Gardens", min_value=0, key="urban_parks")
            afforestation_programs = st.number_input("Trees Planted per Year", min_value=0, key="afforestation")
            biodiversity_committees = st.selectbox("Biodiversity Management Committees", ["Yes","No"], key="biodiversity_committees")

        # 4. Sustainable Mobility
        with cap_form_tabs[3]:
            modal_share = st.slider("Modal Share of Public Transport (%)",0,100,0,key="modal_share")
            electric_vehicles = st.number_input("No. of Electric Vehicles",min_value=0,key="electric_vehicles")
            bike_lanes = st.number_input("Length of Bike Lanes (km)",min_value=0,key="bike_lanes")
            pedestrian_infra = st.selectbox("Pedestrian Infrastructure",["Yes","No"],key="pedestrian_infra")
            congestion_pricing = st.selectbox("Congestion Pricing in Place",["Yes","No"],key="congestion_pricing")
            traffic_emission_reduction = st.slider("Traffic Emission Reduction (%)",0,100,0,key="traffic_emission_reduction")

        # 5. Water Resources
        with cap_form_tabs[4]:
            water_consumption = st.number_input("Total Water Consumption (ML/year)",min_value=0,key="water_consumption")
            water_reuse = st.slider("Water Reuse / Recycling (%)",0,100,0,key="water_reuse")
            rainwater_harvesting = st.selectbox("Rainwater Harvesting Mandated",["Yes","No"],key="rainwater_harvesting")
            groundwater_recharge = st.number_input("Groundwater Recharge (ML/year)",min_value=0,key="groundwater_recharge")
            leakage_loss = st.slider("Water Loss due to Leakage (%)",0,100,0,key="leakage_loss")
            wastewater_treatment = st.number_input("Wastewater Treated (ML/year)",min_value=0,key="wastewater_treatment")

        # 6. Waste Management
        with cap_form_tabs[5]:
            municipal_solid_waste = st.number_input("Municipal Solid Waste Generated (T/year)",min_value=0,key="msw_generated")
            recycling_rate = st.slider("Recycling Rate (%)",0,100,0,key="recycling_rate")
            composting_rate = st.slider("Composting Rate (%)",0,100,0,key="composting_rate")
            waste_to_energy = st.selectbox("Waste-to-Energy Plants",["Yes","No"],key="waste_to_energy")
            hazardous_waste = st.number_input("Hazardous Waste Generated (T/year)",min_value=0,key="hazardous_waste")
            e_waste = st.number_input("E-Waste Generated (T/year)",min_value=0,key="e_waste")

        # 7. Climate Data
        with cap_form_tabs[6]:
            annual_temp = st.number_input("Average Annual Temperature (°C)",key="annual_temp")
            avg_rainfall = st.number_input("Average Annual Rainfall (mm)",key="avg_rainfall")
            extreme_events = st.text_area("Extreme Climate Events Observed",key="extreme_events")
            rcp_scenario = st.selectbox("RCP Scenario",["RCP2.6","RCP4.5","RCP6.0","RCP8.5"],key="rcp_scenario")
            projected_temp_increase = st.slider("Projected Temp Increase by 2050 (°C)",0,5,1,key="projected_temp_increase")

        # ---------------- Save Generate CAP Form -----------------
        if st.button("Save Generate CAP Data"):
            st.session_state.city_data[city_select]["Basic Info"] = {
                "Population":population,"Area":area,"GDP":gdp,"Density":density,
                "Climate_Zone":climate_zone,"Admin":admin_structure
            }
            st.session_state.city_data[city_select]["CAP_Status"] = cap_status_form
            st.session_state.city_data[city_select]["Last_Updated"] = last_updated()
            # Energy & Buildings
            st.session_state.city_data[city_select]["Energy_Buildings"] = {
                "Residential_Energy":res_energy,"Commercial_Energy":com_energy,"Industrial_Energy":ind_energy,
                "Renewable_Share":renewable_share,"EE_Buildings":ee_buildings,"Street_Lighting_Type":street_lighting_type,
                "Street_Lighting_Coverage":street_lighting_coverage,"Fuel_Types":fuel_types,"Public_Building_Energy":public_building_energy,
                "Green_Building_Policy":green_policy
            }
            # Green Cover
            st.session_state.city_data[city_select]["Green_Biodiversity"] = {
                "Green_Cover_Area":green_cover_area,"Tree_Density":tree_density,"Protected_Areas":protected_areas,
                "Wetlands_Area":wetlands_area,"Species_Richness":species_richness,"Urban_Parks":urban_parks,
                "Afforestation_Programs":afforestation_programs,"Biodiversity_Committees":biodiversity_committees
            }
            # Mobility
            st.session_state.city_data[city_select]["Mobility"] = {
                "Modal_Share_Public":modal_share,"EVs":electric_vehicles,"Bike_Lanes":bike_lanes,
                "Pedestrian_Infra":pedestrian_infra,"Congestion_Pricing":congestion_pricing,
                "Traffic_Emission_Reduction":traffic_emission_reduction
            }
            # Water
            st.session_state.city_data[city_select]["Water"] = {
                "Total_Water_Consumption":water_consumption,"Water_Reuse":water_reuse,
                "Rainwater_Harvesting":rainwater_harvesting,"Groundwater_Recharge":groundwater_recharge,
                "Leakage_Loss":leakage_loss,"Wastewater_Treatment":wastewater_treatment
            }
            # Waste
            st.session_state.city_data[city_select]["Waste"] = {
                "MSW_Generated":municipal_solid_waste,"Recycling_Rate":recycling_rate,
                "Composting_Rate":composting_rate,"Waste_to_Energy":waste_to_energy,
                "Hazardous_Waste":hazardous_waste,"E_Waste":e_waste
            }
            # Climate Data
            st.session_state.city_data[city_select]["Climate_Data"] = {
                "Annual_Temp":annual_temp,"Avg_Rainfall":avg_rainfall,"Extreme_Events":extreme_events,
                "RCP_Scenario":rcp_scenario,"Projected_Temp_Increase":projected_temp_increase
            }
            st.success(f"{city_select} CAP Data Saved Successfully!")

    # ---------------- GHG Inventory -----------------
    with admin_tabs[2]:
        st.subheader("GHG Inventory")
        city_select = st.selectbox("Select City", cities, key="ghg_city")
        city_info = st.session_state.city_data.get(city_select,{})
        
        if st.button("Calculate GHG Inventory"):
            city_info["GHG"] = {"Energy":10000,"Transport":5000,"Waste":2000,"Water":500,"Buildings":1500,"Industry":3000}
            st.session_state.city_data[city_select] = city_info
            st.success("GHG Inventory Calculated!")
            st.write(city_info["GHG"])
        
        if st.button("Generate CAP PDF"):
            if city_info.get("GHG"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial","B",16)
                pdf.cell(0,10,f"{city_select} Climate Action Plan", ln=True, align="C")
                pdf.set_font("Arial","",12)
                pdf.ln(5)
                pdf.multi_cell(0,8,"Scenario-Based Recommendations:\n- Renewable energy expansion\n- Energy efficiency\n- Sustainable mobility\n- Water conservation\n- Waste management\n- Green cover enhancement")
                pdf_output = io.BytesIO()
                pdf.output(pdf_output)
                pdf_output.seek(0)
                st.download_button("Download CAP PDF", pdf_output, file_name=f"{city_select}_CAP.pdf", mime="application/pdf")
            else:
                st.warning("Please calculate GHG inventory first.")
