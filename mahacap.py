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
st.sidebar.image("eintrust_logo.png", use_column_width=True)
page = st.sidebar.radio("Menu", ["Home","City","Admin"])

# -------------------- Home Page --------------------
if page=="Home":
    st.header("Maharashtra Net Zero Journey")
    
    cap_status = pd.DataFrame({
        "City": cities,
        "CAP Status": [st.session_state.city_data.get(c, {}).get("CAP_Status","Not Started") for c in cities]
    })
    st.subheader("CAP Status of Various Cities")
    st.dataframe(cap_status)
    
    st.subheader("Maharashtra Basic Information")
    total_population = sum([st.session_state.city_data.get(c, {}).get("Basic Info", {}).get("Population",0) for c in cities])
    total_area = sum([st.session_state.city_data.get(c, {}).get("Basic Info", {}).get("Area",0) for c in cities])
    st.write(f"Population: {format_inr(total_population)}")
    st.write(f"Area (sq km): {format_inr(total_area)}")
    st.write(f"Last Updated: {last_updated()}")
    
    ghg_sectors = ["Energy","Transport","Waste","Water","Buildings","Industry"]
    ghg_values = [sum([st.session_state.city_data.get(c, {}).get("GHG", {}).get(s,0) for c in cities]) for s in ghg_sectors]
    fig = px.bar(x=ghg_sectors, y=ghg_values, labels={"x":"Sector","y":"tCO2e"}, title="Maharashtra GHG Emissions by Sector")
    st.plotly_chart(fig)
    
    st.subheader("RCP Scenario")
    years = list(range(2020,2051))
    rcp_values = [np.random.uniform(1,3) for _ in years]
    fig2 = px.line(x=years, y=rcp_values, labels={"x":"Year","y":"Temp Rise (°C)"}, title="Projected RCP Scenario")
    st.plotly_chart(fig2)

# -------------------- City Page --------------------
elif page=="City":
    st.header("City-Level CAP Dashboard")
    selected_city = st.selectbox("Select City", cities)
    city_info = st.session_state.city_data.get(selected_city, {})
    
    st.subheader(f"{selected_city} Net Zero Journey")
    st.write(f"CAP Status: {city_info.get('CAP_Status','Not Started')}")
    st.write(f"Last Updated: {city_info.get('Last_Updated',last_updated())}")
    
    basic = city_info.get("Basic Info",{})
    st.write(f"Population: {format_inr(basic.get('Population',0))}")
    st.write(f"Area (sq km): {format_inr(basic.get('Area',0))}")
    
    ghg = city_info.get("GHG",{})
    if ghg:
        fig = px.bar(x=list(ghg.keys()), y=list(ghg.values()), labels={"x":"Sector","y":"tCO2e"}, title=f"{selected_city} GHG Emissions by Sector")
        st.plotly_chart(fig)
    
    st.subheader("RCP Scenario")
    climate = city_info.get("Climate Data",{})
    years = list(range(2020,2051))
    rcp_values = climate.get("RCP",[np.random.uniform(1,3) for _ in years])
    fig2 = px.line(x=years, y=rcp_values, labels={"x":"Year","y":"Temp Rise (°C)"}, title=f"{selected_city} RCP Scenario")
    st.plotly_chart(fig2)

# -------------------- Admin Panel --------------------
elif page=="Admin":
    st.header("Admin Panel")
    admin_tabs = st.tabs(["Add/Update City","Generate CAP","GHG Inventory"])
    
    # ---------------- Add/Update City -----------------
    with admin_tabs[0]:
        st.subheader("Add / Update City")
        city_select = st.selectbox("Select City", cities)
        population = st.number_input("Population", min_value=0)
        area = st.number_input("Area (sq km)", min_value=0)
        gdp = st.number_input("GDP (₹ Crores)", min_value=0)
        cap_status = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"])
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
        city_select = st.selectbox("Select City for CAP", cities)
        city_info = st.session_state.city_data.get(city_select, {})
        
        cap_form_tabs = st.tabs([
            "1. Basic Info","2. Energy & Buildings","3. Green Cover & Biodiversity",
            "4. Sustainable Mobility","5. Water Resources","6. Waste Management","7. Climate Data"
        ])

       # -------------------- Generate CAP -----------------
with admin_tabs[1]:
    st.subheader("Generate CAP")
    city_select = st.selectbox("Select City for CAP", cities)
    city_info = st.session_state.city_data.get(city_select, {})

    cap_form_tabs = st.tabs([
        "1. Basic Info",
        "2. Energy & Buildings",
        "3. Green Cover & Biodiversity",
        "4. Sustainable Mobility",
        "5. Water Resources",
        "6. Waste Management",
        "7. Climate Data"
    ])

    # ---------------- 1. Basic Info -----------------
    with cap_form_tabs[0]:
        population = st.number_input("Population", min_value=0, value=city_info.get("Basic Info",{}).get("Population",0))
        area = st.number_input("Area (sq km)", min_value=0, value=city_info.get("Basic Info",{}).get("Area",0))
        gdp = st.number_input("GDP (₹ Crores)", min_value=0, value=city_info.get("Basic Info",{}).get("GDP",0))
        density = st.number_input("Population Density (people/km²)", min_value=0)
        climate_zone = st.text_input("Climate Zone")
        admin_structure = st.text_input("Administrative Structure")
        cap_status = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"])
        last_updated_input = st.date_input("Last Updated", datetime.date.today())

    # ---------------- 2. Energy & Buildings -----------------
    with cap_form_tabs[1]:
        res_energy = st.number_input("Residential Electricity Consumption (kWh/year)", min_value=0)
        com_energy = st.number_input("Commercial Electricity Consumption (kWh/year)", min_value=0)
        ind_energy = st.number_input("Industrial Electricity Consumption (kWh/year)", min_value=0)
        renewable_share = st.slider("Renewable Energy Share (%)", 0,100,0)
        ee_buildings = st.number_input("No. of Energy-Efficient Buildings Certified", min_value=0)
        street_lighting_type = st.selectbox("Street Lighting Type", ["LED","CFL","Other"])
        street_lighting_coverage = st.slider("Street Lighting Coverage (%)",0,100,0)
        fuel_types = st.multiselect("Fuel Types Used", ["Coal","Gas","Biomass","Electricity","Petroleum"])
        public_building_energy = st.number_input("Public Building Energy Consumption (kWh/year)", min_value=0)
        green_policy = st.selectbox("Green Building Policies in Place", ["Yes","No"])

    # ---------------- 3. Green Cover & Biodiversity -----------------
    with cap_form_tabs[2]:
        green_cover_area = st.number_input("Total Green Cover Area (ha)", min_value=0)
        tree_density = st.number_input("Tree Density (trees/km²)", min_value=0)
        protected_areas = st.number_input("Protected / Forest Areas within City (ha)", min_value=0)
        wetlands_area = st.number_input("Wetlands / Water Bodies Coverage (ha)", min_value=0)
        species_richness = st.text_area("Species Richness (flora & fauna)")
        urban_parks = st.number_input("Number of Urban Parks / Community Gardens", min_value=0)
        afforestation_programs = st.number_input("Trees Planted per Year", min_value=0)
        biodiversity_committees = st.selectbox("Biodiversity Management Committees", ["Yes","No"])

    # ---------------- 4. Sustainable Mobility -----------------
    with cap_form_tabs[3]:
        vehicles_2w = st.number_input("2-Wheelers", min_value=0)
        vehicles_3w = st.number_input("3-Wheelers", min_value=0)
        vehicles_4w = st.number_input("4-Wheelers", min_value=0)
        buses = st.number_input("Buses", min_value=0)
        trucks = st.number_input("Trucks", min_value=0)
        public_transport_share = st.slider("Public Transport Share (%)", 0,100,0)
        modal_split = st.text_area("Modal Split (Walking/Cycling/Public/Private Vehicles)")
        avg_commute = st.number_input("Average Commute Distance (km/day)", min_value=0)
        ev_infra = st.number_input("EV Charging Stations", min_value=0)
        ev_share = st.slider("EV Share (%)",0,100,0)
        road_length = st.number_input("Road Length (km)", min_value=0)
        traffic_congestion_index = st.slider("Traffic Congestion Index",0,10,0)
        bicycle_lanes = st.number_input("Bicycle Lanes & Pedestrian-Friendly Areas (km)", min_value=0)
        transport_emissions = st.number_input("Estimated Transport Emissions (tCO₂e/year)", min_value=0)

    # ---------------- 5. Water Resources -----------------
    with cap_form_tabs[4]:
        water_domestic = st.number_input("Domestic Water Consumption (MLD)", min_value=0)
        water_industrial = st.number_input("Industrial Water Consumption (MLD)", min_value=0)
        water_commercial = st.number_input("Commercial Water Consumption (MLD)", min_value=0)
        water_supply_coverage = st.slider("Water Supply Coverage (%)",0,100,0)
        groundwater_depth = st.number_input("Groundwater Table Depth (m)", min_value=0)
        water_treatment_plants = st.number_input("Functional Water Treatment Plants", min_value=0)
        rainwater_harvesting = st.number_input("Rainwater Harvesting Structures", min_value=0)
        sewage_coverage = st.slider("Sewage Treatment Coverage (%)",0,100,0)
        recycled_water = st.slider("Recycled / Reused Water (%)",0,100,0)
        flood_prone_areas = st.text_area("Flood-Prone Areas")
        drought_prone_areas = st.text_area("Drought-Prone Areas")
        water_quality = st.text_area("Water Quality Parameters (BOD,COD,TDS,pH)")

    # ---------------- 6. Waste Management -----------------
    with cap_form_tabs[5]:
        msw_generated = st.number_input("Municipal Solid Waste Generated (TPD)", min_value=0)
        waste_composition = st.text_area("Waste Composition (% Organic, Plastic, Metal, Paper, Others)")
        collection_coverage = st.slider("Collection Coverage (%)",0,100,0)
        recycling_rate = st.slider("Recycling Rate (%)",0,100,0)
        compost_units = st.number_input("Composting Units", min_value=0)
        landfill_area = st.number_input("Landfill Usage (ha)", min_value=0)
        waste_to_energy = st.selectbox("Waste-to-Energy Plants", ["Yes","No"])
        hazardous_waste = st.selectbox("Hazardous & Biomedical Waste Management", ["Yes","No"])
        citizen_awareness = st.selectbox("Citizen Awareness Programs", ["Yes","No"])

    # ---------------- 7. Climate Data -----------------
    with cap_form_tabs[6]:
        avg_temp = st.number_input("Average Annual Temperature (°C)", min_value=-50, max_value=60)
        heatwave_days = st.number_input("Heatwave Days per Year", min_value=0)
        annual_rainfall = st.number_input("Annual Rainfall (mm)", min_value=0)
        flood_prone = st.text_area("Flood-Prone Areas")
        drought_prone = st.text_area("Drought-Prone Areas")
        extreme_events = st.text_area("Extreme Weather Events History (last 10 years)")
        rcp_values = [st.number_input(f"Projected Temp {year} (°C)", min_value=0.0, max_value=10.0, value=1.5) for year in range(2020,2051)]
        vulnerability_social = st.text_area("Social Vulnerability Assessment")
        vulnerability_economic = st.text_area("Economic Vulnerability Assessment")
        vulnerability_ecological = st.text_area("Ecological Vulnerability Assessment")
        vulnerability_urban = st.text_area("Urban Landscape Vulnerability")
        disaster_plans = st.selectbox("Disaster Risk Management Plans in Place", ["Yes","No"])

    # ---------------- Save All -----------------
    if st.button("Save Generate CAP Data"):
        st.session_state.city_data[city_select]["Basic Info"] = {
            "Population":population, "Area":area, "GDP":gdp, "Density":density,
            "Climate_Zone":climate_zone, "Admin":admin_structure
        }
        st.session_state.city_data[city_select]["Energy & Buildings"] = {
            "Residential":res_energy,"Commercial":com_energy,"Industrial":ind_energy,
            "Renewable":renewable_share,"EE_Buildings":ee_buildings,
            "Street_Lighting_Type":street_lighting_type,"Street_Lighting_Coverage":street_lighting_coverage,
            "Fuel_Types":fuel_types,"Public_Building_Energy":public_building_energy,
            "Green_Policy":green_policy
        }
        st.session_state.city_data[city_select]["Green Cover & Biodiversity"] = {
            "Green_Cover":green_cover_area,"Tree_Density":tree_density,"Protected_Areas":protected_areas,
            "Wetlands":wetlands_area,"Species_Richness":species_richness,"Urban_Parks":urban_parks,
            "Afforestation":afforestation_programs,"Biodiversity_Committees":biodiversity_committees
        }
        st.session_state.city_data[city_select]["Sustainable Mobility"] = {
            "2W":vehicles_2w,"3W":vehicles_3w,"4W":vehicles_4w,"Buses":buses,"Trucks":trucks,
            "Public_Transport":public_transport_share,"Modal_Split":modal_split,"Commute":avg_commute,
            "EV_Infra":ev_infra,"EV_Share":ev_share,"Road_Length":road_length,
            "Traffic_Index":traffic_congestion_index,"Bicycle_Lanes":bicycle_lanes,"Transport_Emissions":transport_emissions
        }
        st.session_state.city_data[city_select]["Water Resources"] = {
            "Domestic":water_domestic,"Industrial":water_industrial,"Commercial":water_commercial,
            "Supply_Coverage":water_supply_coverage,"Groundwater":groundwater_depth,
            "Treatment_Plants":water_treatment_plants,"Rainwater_Harvesting":rainwater_harvesting,
            "Sewage_Coverage":sewage_coverage,"Recycled_Water":recycled_water,
            "Flood":flood_prone_areas,"Drought":drought_prone_areas,"Quality":water_quality
        }
        st.session_state.city_data[city_select]["Waste Management"] = {
            "MSW_Generated":msw_generated,"Composition":waste_composition,"Collection":collection_coverage,
            "Recycling":recycling_rate,"Compost":compost_units,"Landfill":landfill_area,
            "Waste_to_Energy":waste_to_energy,"Hazardous":hazardous_waste,"Awareness":citizen_awareness
        }
        st.session_state.city_data[city_select]["Climate Data"] = {
            "Avg_Temp":avg_temp,"Heatwave_Days":heatwave_days,"Rainfall":annual_rainfall,
            "Flood":flood_prone,"Drought":drought_prone,"Extreme_Events":extreme_events,
            "RCP":rcp_values,"Vuln_Social":vulnerability_social,"Vuln_Econ":vulnerability_economic,
            "Vuln_Eco":vulnerability_ecological,"Vuln_Urban":vulnerability_urban,"Disaster_Plans":disaster_plans
        }
        st.success(f"{city_select} CAP Data Saved Successfully!")

        st.info("Generate CAP form tabs loaded here (use previous comprehensive form).")
        
        if st.button("Save Generate CAP Data"):
            st.success(f"{city_select} CAP Data Saved Successfully!")

    # ---------------- GHG Inventory -----------------
    with admin_tabs[2]:
        st.subheader("GHG Inventory")
        city_select = st.selectbox("Select City", cities)
        city_info = st.session_state.city_data.get(city_select,{})
        
        if st.button("Calculate GHG Inventory"):
            # Example: calculate using inputs from Generate CAP form
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


