import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
import plotly.express as px
from datetime import datetime
import locale
import io

# ---------------------------
# Indian Number Format
# ---------------------------
locale.setlocale(locale.LC_ALL, 'en_IN')
def format_inr(number):
    return locale.format_string("%d", number, grouping=True)

# ---------------------------
# Maharashtra Cities
# ---------------------------
cities = ["Mumbai","Kalyan-Dombivli","Mira-Bhayandar","Navi Mumbai","Bhiwandi-Nizampur",
          "Ulhasnagar","Ambernath Council","Vasai-Virar","Thane","Badlapur Council",
          "Pune","Pimpri-Chinchwad","Panvel","Malegaon","Nashik","Nandurbar Council",
          "Bhusawal Council","Jalgaon","Dhule","Ahilyanagar","Chh. Sambhajinagar",
          "Jalna","Beed Council","Satara Council","Sangli-Miraj-Kupwad","Kolhapur",
          "Ichalkaranji","Solapur","Barshi Council","Nanded-Waghala","Yawatmal Council",
          "Dharashiv","Latur","Udgir Coumcil","Akola","Parbhani Council","Amravati",
          "Achalpur Council","Wardha Coumcil","Hinganghat Ciuncil","Nagpur","Chandrapur",
          "Gondia Council"]

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", layout="wide", page_icon="🌍")

# ---------------------------
# Sidebar Navigation
# ---------------------------
st.sidebar.title("EinTrust")
menu_choice = st.sidebar.radio("Navigation", ["Home", "City", "Admin Login"])

# ---------------------------
# Last Updated Placeholder
# ---------------------------
last_updated = datetime.now().strftime("%B %Y")

# ---------------------------
# GHG Calculation Function (Indian Emission Factors)
# ---------------------------
def calculate_ghg(data):
    EF_energy = 820  # kgCO2/MWh
    EF_transport = 2.31  # kgCO2/km/vehicle
    EF_waste = 0.5  # tCO2/tonne

    energy_emissions = sum(data["Energy"].values()) * EF_energy / 1000
    transport_emissions = data["Transport"]["Vehicles"] * data["Transport"]["AvgKmPerDay"] * 365 * EF_transport / 1000
    waste_emissions = data["Waste"]["WasteGenerated"] * EF_waste
    total = energy_emissions + transport_emissions + waste_emissions
    return {"Energy": energy_emissions, "Transport": transport_emissions, "Waste": waste_emissions, "Total": total}

# ---------------------------
# Home Page
# ---------------------------
if menu_choice == "Home":
    st.title("Maharashtra's Net Zero Journey")
    st.subheader(f"Last Updated: {last_updated}")
    st.markdown("### CAP Status of Cities")
    st.write("CAP/GHG status table for all 43 cities will appear here after admin input.")
    st.markdown("### KPIs & RCP Graph")
    st.write("Placeholder for Maharashtra-wide sectoral KPIs, RCP graphs, and visualizations.")

# ---------------------------
# City Page
# ---------------------------
elif menu_choice == "City":
    st.title("City Net Zero Journey")
    selected_city = st.selectbox("Select City", cities)
    st.subheader(f"{selected_city}'s CAP Status | Last Updated: {last_updated}")
    st.write("City-specific CAP status, sectoral KPIs, GHG Inventory, and RCP graphs will appear here after admin input.")

# ---------------------------
# Admin Login
# ---------------------------
elif menu_choice == "Admin Login":
    password = st.text_input("Enter Admin Password", type="password")
    if st.button("Login"):
        if password == "eintrust123":
            st.success("Admin Logged In Successfully")
            
            # Admin Tabs
            tabs = st.tabs(["Add/Update City","Generate CAP","GHG Inventory"])
            
            # ----------------- Tab 1: Add/Update City -----------------
            with tabs[0]:
                st.header("Add / Update City Information")
                city_select = st.selectbox("Select City", cities)
                population = st.number_input("Population (No. of People)", min_value=0)
                area = st.number_input("City Area (sq km)", min_value=0)
                gdp = st.number_input("GDP (in ₹ Crores)", min_value=0)
                climate_budget = st.number_input("Annual Climate Budget (₹ Crores)", min_value=0)
                if st.button("Save City Info"):
                    st.success(f"{city_select} information updated successfully")
            
            # ----------------- Tab 2: Generate CAP -----------------
            with tabs[1]:
                st.header("Generate CAP - Raw Data Collection")
                city_select = st.selectbox("Select City for CAP", cities, key="cap_city")

                # 7 Tabs for Comprehensive Data
                cap_tabs = st.tabs(["1. Basic Info","2. Energy & Buildings","3. Green Cover & Biodiversity",
                                    "4. Sustainable Mobility","5. Water Resources","6. Waste Management","7. Climate Data"])
                
                # ----------------- Tab 1: Basic Info -----------------
                with cap_tabs[0]:
                    st.markdown("### Basic City Information (CSCAF, MoHUA, SDG11)")
                    population = st.number_input("Total Population", min_value=0)
                    households = st.number_input("Number of Households", min_value=0)
                    area = st.number_input("City Area (sq km)", min_value=0)
                    gdp = st.number_input("City GDP (₹ Crores)", min_value=0)
                    climate_budget = st.number_input("Annual Climate Budget (₹ Crores)", min_value=0)
                    governance_structure = st.text_area("Municipal Governance Structure / Departments")

                # ----------------- Tab 2: Energy & Buildings -----------------
                with cap_tabs[1]:
                    st.markdown("### Energy Consumption & Buildings (IPCC 2006, MoEFCC, ECBC)")
                    res_energy = st.number_input("Residential Energy Consumption (MWh/year)")
                    com_energy = st.number_input("Commercial Energy Consumption (MWh/year)")
                    ind_energy = st.number_input("Industrial Energy Consumption (MWh/year)")
                    public_energy = st.number_input("Public Buildings Energy Consumption (MWh/year)")
                    building_floor_area = st.number_input("Total Built-up Floor Area (sq.m)")
                    green_buildings = st.number_input("Number of Green-Certified Buildings")
                    renewable_energy = st.number_input("Installed Renewable Energy Capacity (MW)")

                # ----------------- Tab 3: Green Cover & Biodiversity -----------------
                with cap_tabs[2]:
                    st.markdown("### Green Cover & Biodiversity (CSCAF, UN SDG 15, MoEFCC)")
                    total_green_area = st.number_input("Total Green Cover Area (ha)")
                    parks = st.number_input("Number of Public Parks/Gardens")
                    street_trees = st.number_input("Number of Street Trees")
                    protected_areas = st.number_input("Area under Protected Zones (ha)")
                    biodiversity_programs = st.text_area("Biodiversity Programs / Initiatives")

                # ----------------- Tab 4: Sustainable Mobility -----------------
                with cap_tabs[3]:
                    st.markdown("### Sustainable Mobility (CSCAF, NUTP, NITI Aayog)")
                    total_vehicles = st.number_input("Total Registered Vehicles")
                    public_transport_users = st.number_input("Daily Public Transport Users")
                    avg_km_per_vehicle = st.number_input("Average km Travelled per Vehicle per Day")
                    cycling_infra = st.number_input("Length of Cycling Lanes (km)")
                    pedestrian_infra = st.number_input("Length of Pedestrian Walkways (km)")

                # ----------------- Tab 5: Water Resources -----------------
                with cap_tabs[4]:
                    st.markdown("### Water Resource Management (MoUD, CSCAF)")
                    total_water_supply = st.number_input("Total Water Supplied (MLD)")
                    per_capita_supply = st.number_input("Per Capita Water Supply (L/day)")
                    wastewater_treated = st.number_input("Wastewater Treated (MLD)")
                    reuse_percentage = st.number_input("Wastewater Reuse (%)")
                    rainwater_harvesting = st.number_input("Buildings with RWH (No.)")

                # ----------------- Tab 6: Waste Management -----------------
                with cap_tabs[5]:
                    st.markdown("### Waste Management (MoHUA, SWM Rules 2016)")
                    municipal_waste_generated = st.number_input("Municipal Waste Generated (T/day)")
                    municipal_waste_treated = st.number_input("Municipal Waste Treated (T/day)")
                    recycling_rate = st.number_input("Recycling Rate (%)")
                    composting = st.number_input("Organic Waste Composting (T/day)")

                # ----------------- Tab 7: Climate Data -----------------
                with cap_tabs[6]:
                    st.markdown("### Climate Data (IMD, IPCC, Paris Agreement)")
                    rcp_pathway = st.selectbox("RCP Pathway", ["RCP2.6","RCP4.5","RCP6.0","RCP8.5"])
                    urban_heat_intensity = st.number_input("Urban Heat Island Intensity (°C)")
                    avg_temperature = st.number_input("Average Annual Temperature (°C)")
                    rainfall = st.number_input("Annual Rainfall (mm)")
                    flood_frequency = st.number_input("Flood Events per Decade")
                    drought_frequency = st.number_input("Drought Events per Decade")
                    extreme_weather_events = st.text_area("Other Extreme Weather Events Observed")

                # ----------------- Calculate GHG Inventory -----------------
                if st.button("Calculate GHG Inventory"):
                    cap_data = {
                        "Energy": {"Residential": res_energy, "Commercial": com_energy, "Industrial": ind_energy, "Public": public_energy},
                        "Transport": {"Vehicles": total_vehicles, "AvgKmPerDay": avg_km_per_vehicle},
                        "Waste": {"WasteGenerated": municipal_waste_generated},
                        "Climate": {"RCP": rcp_pathway, "UrbanHeat": urban_heat_intensity, "Flood": flood_frequency, "Drought": drought_frequency},
                        "Balances": {"Ecological": "To Be Calculated", "Social": "To Be Calculated", "Economic": "To Be Calculated", "Urban": "To Be Calculated"}
                    }
                    ghg = calculate_ghg(cap_data)
                    st.markdown("### Sectoral GHG Emissions (tCO₂)")
                    for sector, val in ghg.items():
                        st.write(f"{sector}: {format_inr(int(val))}")
                    fig = px.pie(values=list(ghg.values())[:-1], names=list(ghg.keys())[:-1], title="Sectoral GHG Emissions")
                    st.plotly_chart(fig, use_container_width=True)

                    # ----------------- Scenario-Based Decision Support -----------------
                    st.markdown("## Scenario-Based Decision Support (SDS)")
                    scenario_type = st.selectbox("Select Scenario", 
                                                 ["Business-as-Usual (BAU)",
                                                  "Renewable Energy Expansion",
                                                  "Waste Reduction Plan",
                                                  "Sustainable Transport Boost",
                                                  "Integrated Sustainability Plan"])
                    scenario_energy_reduction = st.slider("Energy Consumption Reduction (%)", 0, 50, 10)
                    scenario_renewable_increase = st.slider("Increase in Renewable Energy Capacity (%)", 0, 100, 20)
                    scenario_transport_shift = st.slider("Increase Public Transport Usage (%)", 0, 100, 15)
                    scenario_waste_reduction = st.slider("Increase Recycling/Composting (%)", 0, 100, 20)
                    scenario_green_cover_increase = st.slider("Increase Green Cover Area (%)", 0, 50, 10)

                    # Projected GHG calculations
                    projected_energy = res_energy * (1 - scenario_energy_reduction / 100) - renewable_energy * (scenario_renewable_increase / 100)
                    projected_transport = total_vehicles * (1 - scenario_transport_shift / 100) * avg_km_per_vehicle
                    projected_waste = municipal_waste_generated * (1 - scenario_waste_reduction / 100)
                    ghg_projected = calculate_ghg({
                        "Energy": {"Residential": projected_energy, "Commercial": projected_energy/2, "Industrial": projected_energy/3, "Public": projected_energy/4},
                        "Transport": {"Vehicles": total_vehicles*(1-scenario_transport_shift/100), "AvgKmPerDay": avg_km_per_vehicle},
                        "Waste": {"WasteGenerated": projected_waste}
                    })
                    st.markdown("### Projected GHG Emissions (tCO₂)")
                    for sector, val in ghg_projected.items():
                        st.write(f"{sector}: {format_inr(int(val))}")
                    fig_proj = px.bar(x=list(ghg_projected.keys())[:-1], y=list(ghg_projected.values())[:-1],
                                      labels={"x":"Sector","y":"tCO₂"}, title="Projected GHG Emissions per Sector")
                    st.plotly_chart(fig_proj, use_container_width=True)

                    # RCP Graph
                    st.markdown("### Projected RCP Pathway")
                    rcp_values = {"RCP2.6":1.0, "RCP4.5":1.1, "RCP6.0":1.2, "RCP8.5":1.5}
                    st.line_chart(pd.DataFrame({"Year": list(range(2025,2051)),
                                                "Projected Temperature Rise (°C)":[rcp_values[rcp_pathway]*0.02*i for i in range(26)]}))

                    # Recommendations
                    st.markdown("### Automated Recommendations")
                    recommendations = []
                    if scenario_energy_reduction > 0:
                        recommendations.append(f"Reduce energy consumption by {scenario_energy_reduction}% via efficiency measures")
                    if scenario_renewable_increase > 0:
                        recommendations.append(f"Increase renewable energy capacity by {scenario_renewable_increase}%")
                    if scenario_transport_shift > 0:
                        recommendations.append(f"Promote public transport to shift {scenario_transport_shift}% of vehicle usage")
                    if scenario_waste_reduction > 0:
                        recommendations.append(f"Enhance waste recycling/composting to cover additional {scenario_waste_reduction}%")
                    if scenario_green_cover_increase > 0:
                        recommendations.append(f"Expand green cover by {scenario_green_cover_increase}% to improve ecological balance")
                    for rec in recommendations:
                        st.write(f"- {rec}")

                    # Download CAP PDF
                    if st.button("Download CAP PDF"):
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial",'B',16)
                        pdf.cell(0,10,f"{city_select} Climate Action Plan", ln=True, align='C')
                        pdf.ln(10)
                        pdf.set_font("Arial",'B',14)
                        pdf.cell(0,10,"Sectoral GHG Emissions (tCO₂)", ln=True)
                        pdf.set_font("Arial",'',12)
                        for k,v in ghg_projected.items():
                            pdf.cell(0,10,f"{k}: {format_inr(int(v))}", ln=True)
                        pdf.ln(5)
                        pdf.set_font("Arial",'B',14)
                        pdf.cell(0,10,"Recommendations", ln=True)
                        pdf.set_font("Arial",'',12)
                        for rec in recommendations:
                            pdf.cell(0,10,rec, ln=True)
                        pdf_buffer = io.BytesIO()
                        pdf.output(pdf_buffer)
                        pdf_buffer.seek(0)
                        st.download_button("Download CAP PDF", pdf_buffer, file_name=f"{city_select}_CAP.pdf", mime="application/pdf")
                        st.success("CAP PDF generated successfully!")

# ---------------------------
# End of Dashboard
# ---------------------------
