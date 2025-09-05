import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
import random
import os

# Optional SharePoint integration
try:
    from dotenv import load_dotenv
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.client_credential import ClientCredential
    load_dotenv()
    SHAREPOINT_SITE = os.getenv("SHAREPOINT_SITE")
    SHAREPOINT_DOC = os.getenv("SHAREPOINT_DOC")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    if SHAREPOINT_SITE and CLIENT_ID and CLIENT_SECRET and SHAREPOINT_DOC:
        credentials = ClientCredential(CLIENT_ID, CLIENT_SECRET)
        ctx = ClientContext(SHAREPOINT_SITE).with_credentials(credentials)
        SHAREPOINT_ENABLED = True
    else:
        SHAREPOINT_ENABLED = False
except:
    SHAREPOINT_ENABLED = False

def upload_to_sharepoint(file_buffer, file_name):
    if not SHAREPOINT_ENABLED:
        return
    target_folder = ctx.web.get_folder_by_server_relative_url(SHAREPOINT_DOC)
    target_folder.upload_file(file_name, file_buffer.read()).execute_query()

# -------------------------------
# Streamlit config & theme
# -------------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", layout="wide")
st.markdown("""
<style>
body {background-color: #0A0A0A; color: #E5E5E5; font-family: 'Arial';}
.stButton>button {background-color:#00BFA6; color:white; border:none;}
.stDataFrame div{color:white;}
.stSelectbox>div>div>div>span {color:white;}
.stTextInput>div>input, .stNumberInput>div>input, .stTextArea>div>textarea {background-color:#1F1F1F; color:white; border:none;}
</style>
""", unsafe_allow_html=True)

LAST_UPDATED = "September 2025"
ADMIN_PASSWORD = "eintrust123"

# -------------------------------
# Cities & Dummy Coordinates
# -------------------------------
cities_districts = {
    "Mumbai": "Mumbai","Kalyan-Dombivli": "Thane","Mira-Bhayandar": "Thane","Navi Mumbai": "Thane",
    "Bhiwandi": "Thane","Ulhasnagar": "Thane","Ambernath Council": "Thane","Vasai-Virar": "Thane",
    "Thane": "Thane","Badlapur Council": "Thane","Pune": "Pune","Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad","Malegaon": "Nashik","Nashik": "Nashik","Nandurbar Council": "Nandurbar",
    "Bhusawal Council": "Jalgaon","Jalgaon": "Jalgaon","Dhule": "Dhule","Ahmednagar": "Ahmednagar",
    "Aurangabad": "Aurangabad","Jalna": "Jalna","Beed Council": "Beed","Satara Council": "Satara",
    "Sangli-Miraj-Kupwad": "Sangli","Kolhapur": "Kolhapur","Ichalkaranji": "Kolhapur","Solapur": "Solapur",
    "Barshi Council": "Solapur","Nanded-Waghala": "Nanded","Yawatmal Council": "Yawatmal","Osmanabad Council": "Osmanabad",
    "Latur": "Latur","Udgir Council": "Latur","Akola": "Akola","Parbhani Council": "Parbhani",
    "Amravati": "Amravati","Achalpur Council": "Amravati","Wardha Council": "Wardha","Hinganghat Council": "Wardha",
    "Nagpur": "Nagpur","Chandrapur": "Chandrapur","Gondia Council": "Gondia"
}
city_coords = {city:(19+random.random()*5, 73+random.random()*5) for city in cities_districts.keys()}

# -------------------------------
# DataFrames
# -------------------------------
city_data_columns = ["City Name","District","Population (2011)","Estimated Population (2025)",
                     "Environment Department Exists?","Responsible Department","Contact Person",
                     "CAP Status","CAP Link","City Website","Total Emissions","Per Capita Emissions"]
city_data = pd.DataFrame([{ 
    "City Name": city, "District": cities_districts[city],
    "Population (2011)":0,"Estimated Population (2025)":0,
    "Environment Department Exists?":"No","Responsible Department":"",
    "Contact Person":"","CAP Status":"Not Started","CAP Link":"","City Website":"",
    "Total Emissions":0,"Per Capita Emissions":0
} for city in cities_districts.keys()], columns=city_data_columns)

# -------------------------------
# Sector columns for comprehensive GHG data
# -------------------------------
sector_columns = [
    # Energy
    "Electricity_Residential","Electricity_Commercial","Electricity_Industrial","Electricity_StreetLighting",
    "FossilFuel_Diesel","FossilFuel_Petrol","FossilFuel_LPG","FossilFuel_Coal","FossilFuel_Biomass",
    "RenewableEnergy_Usage",
    # Transport
    "VehicleKM_2W","VehicleKM_3W","VehicleKM_Car","VehicleKM_Bus","VehicleKM_Truck",
    "Fuel_2W","Fuel_3W","Fuel_Car","Fuel_Bus","Fuel_Truck",
    "PublicTransport_PassengerKM","EV_Number","EV_KM","NonMotorized_KM",
    # Waste
    "MSW_Generated","Waste_Organic","Waste_Recyclable","Waste_Inert",
    "Landfill","Composting","Recycling","Incineration","LandfillGasRecovery",
    # Industry
    "Industry_Energy","Industry_ProcessEmissions","Industry_WastewaterEmissions",
    # Buildings
    "Buildings_Energy","Buildings_CoolingHeating","Buildings_EnergyEfficiency",
    # Agriculture
    "Fertilizer_N","Fertilizer_P","Fertilizer_K","Livestock_Numbers","RiceCultivationArea","CropResidueManagement",
    # Water & Wastewater
    "Water_EnergyUse","Wastewater_Emissions","RecycledWater_Use",
    # Other
    "Aviation","Rail","Port","Fugitive_Emissions"
]

sector_emissions = pd.DataFrame([{ "City Name": city, **{s:0 for s in sector_columns} } for city in cities_districts.keys()])

EMISSION_FACTORS = {s: random.uniform(0.1,1.2) for s in sector_columns}

recommended_actions = {s:{"Short":[f"Action {i}" for i in range(1,11)],
                           "Mid":[f"Action {i}" for i in range(11,21)],
                           "Long":[f"Action {i}" for i in range(21,31)]} for s in EMISSION_FACTORS.keys()}

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.image("https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png", use_column_width=True)
st.sidebar.title("Maharashtra CAP Dashboard")
page = st.sidebar.radio("Navigate", ["Home", "City Information", "Admin"])
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 EinTrust Foundation")

# -------------------------------
# Helper functions
# -------------------------------
def generate_cap_pdf(city_name, name, email):
    buffer = BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,f"Maharashtra Climate Action Plan - {city_name}", ln=True, align="C")
    pdf.set_font("Arial","",10)
    pdf.cell(0,6,f"Generated for: {name} ({email})", ln=True)
    pdf.cell(0,6,f"Last Updated: {LAST_UPDATED}", ln=True)
    city_info = city_data[city_data["City Name"]==city_name].iloc[0]
    pdf.ln(4)
    pdf.set_font("Arial","B",12)
    pdf.cell(0,6,"City Information:", ln=True)
    pdf.set_font("Arial","",10)
    for key in ["District","Population (2011)","Estimated Population (2025)","Environment Department Exists?",
                "Responsible Department","Contact Person","CAP Status","CAP Link","City Website"]:
        pdf.cell(0,5,f"{key}: {city_info.get(key,'')}", ln=True)
    pdf.ln(2)
    pdf.set_font("Arial","B",12)
    pdf.cell(0,6,"Sector-wise GHG Emissions (tCO₂e):", ln=True)
    pdf.set_font("Arial","",10)
    sectors = sector_emissions[sector_emissions["City Name"]==city_name].iloc[0,1:]
    for sector, value in sectors.items():
        pdf.cell(0,5,f"{sector}: {round(value,2)}", ln=True)
    pdf.ln(2)
    pdf.set_font("Arial","B",12)
    pdf.cell(0,6,"Recommended Actions:", ln=True)
    pdf.set_font("Arial","",10)
    for sector in recommended_actions.keys():
        pdf.cell(0,5,f"{sector}:", ln=True)
        for term in ["Short","Mid","Long"]:
            pdf.cell(0,5,f"  {term}-term: {', '.join(recommended_actions[sector][term])}", ln=True)
        pdf.ln(1)
    pdf.set_font("Arial","I",8)
    pdf.cell(0,10,"© 2025 EinTrust Foundation", ln=True, align="C")
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# -------------------------------
# Pages
# -------------------------------
if page == "Home":
    st.title("Maharashtra CAP Dashboard")
    st.markdown(f"**Last Updated: {LAST_UPDATED}**")
    map_df = pd.DataFrame({
        "City": list(city_coords.keys()),
        "Lat":[c[0] for c in city_coords.values()],
        "Lon":[c[1] for c in city_coords.values()],
        "Total Emissions":[sector_emissions.loc[sector_emissions["City Name"]==c, sector_columns].sum(axis=1).values[0] for c in city_coords.keys()]
    })
    st.subheader("City-wise Emissions Map")
    st.map(map_df.rename(columns={"Lat":"lat","Lon":"lon"}))
    map_df = map_df.sort_values("Total Emissions", ascending=False)
    st.subheader("Top 10 Highest Emitting Cities")
    st.bar_chart(map_df.head(10).set_index("City")["Total Emissions"])

elif page == "City Information":
    st.title("City Information")
    st.markdown(f"**Last Updated: {LAST_UPDATED}**")
    st.dataframe(city_data)

    selected_city = st.selectbox("Select City for CAP PDF", city_data["City Name"])
    st.markdown("### Download CAP PDF")
    with st.form("download_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Official Email ID")
        submitted = st.form_submit_button("Download PDF")
        if submitted:
            pdf_buffer = generate_cap_pdf(selected_city, name, email)
            st.download_button("Download CAP PDF", data=pdf_buffer, file_name=f"{selected_city}_CAP.pdf", mime="application/pdf")
            if SHAREPOINT_ENABLED:
                upload_to_sharepoint(pdf_buffer, f"{selected_city}_CAP.pdf")

elif page == "Admin":
    st.title("Admin Panel (EinTrust Only)")
    password = st.text_input("Enter Admin Password", type="password")
    if password != ADMIN_PASSWORD:
        st.warning("Incorrect password")
    else:
        st.success("Access granted")
        sub_page = st.selectbox("Admin Pages", ["CAP Update","Data Collection","GHG Inventory","Actions"])
        # Admin page code for CAP Update, Data Collection (comprehensive), GHG Inventory, Actions
        st.info("Admin functionality (CAP Update, Data Collection, GHG Inventory, Actions) goes here.")
