import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF  # fpdf2
from io import BytesIO
from datetime import datetime
import random

# -------------------------------
# Load Secrets (Local or Streamlit Cloud)
# -------------------------------
try:
    CLIENT_ID = st.secrets["CLIENT_ID"]
    CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
    SHAREPOINT_SITE = st.secrets["SHAREPOINT_SITE"]
    SHAREPOINT_DOC = st.secrets["SHAREPOINT_DOC"]
except:
    from dotenv import load_dotenv
    import os
    load_dotenv()
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    SHAREPOINT_SITE = os.getenv("SHAREPOINT_SITE")
    SHAREPOINT_DOC = os.getenv("SHAREPOINT_DOC")

# SharePoint imports
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

credentials = ClientCredential(CLIENT_ID, CLIENT_SECRET)
ctx = ClientContext(SHAREPOINT_SITE).with_credentials(credentials)

def upload_to_sharepoint(city_name, file_buffer, file_name):
    folder_url = f"{SHAREPOINT_DOC}/{city_name}"
    try:
        ctx.web.folders.add(folder_url).execute_query()
    except:
        pass
    file_content = file_buffer.getvalue()
    ctx.web.get_folder_by_server_relative_url(folder_url).upload_file(file_name, file_content).execute_query()

# -------------------------------
# App Config & Theme
# -------------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", layout="wide")
st.markdown("""
<style>
body {background-color: #0A0A0A; color: #E5E5E5;}
.stButton>button {background-color:#00BFA6; color:white;}
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
# DataFrames Initialization
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

sector_columns = ["Energy","Transport","Waste","Industry","Buildings","Agriculture","Water","Other"]
sector_emissions = pd.DataFrame([{ "City Name": city, **{s:0 for s in sector_columns} } for city in cities_districts.keys()])

EMISSION_FACTORS = {s: random.uniform(0.1,1.2) for s in sector_columns}
recommended_actions = {s:{"Short":[f"Action {i}" for i in range(1,11)],
                           "Mid":[f"Action {i}" for i in range(11,21)],
                           "Long":[f"Action {i}" for i in range(21,31)]} for s in EMISSION_FACTORS.keys()}

# -------------------------------
# Sidebar
# -------------------------------
st.sidebar.title("Maharashtra CAP Dashboard")
page = st.sidebar.radio("Navigate", ["Home", "City Information", "Admin"])
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 EinTrust Foundation")

# -------------------------------
# Helper Functions
# -------------------------------
def calculate_city_emissions(city_inputs):
    return {sector: city_inputs.get(sector,0)*EMISSION_FACTORS[sector] for sector in EMISSION_FACTORS.keys()}

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
    # Map
    map_df = pd.DataFrame({
        "City": list(city_coords.keys()),
        "Lat":[c[0] for c in city_coords.values()],
        "Lon":[c[1] for c in city_coords.values()],
        "Total Emissions":[sector_emissions.loc[sector_emissions["City Name"]==c, sector_columns].sum(axis=1).values[0] for c in city_coords.keys()]
    })
    st.subheader("City-wise Emissions Map")
    st.map(map_df.rename(columns={"Lat":"lat","Lon":"lon"}))
    # Top 10 Emitters
    map_df = map_df.sort_values("Total Emissions", ascending=False)
    st.subheader("Top 10 Highest Emitting Cities")
    st.bar_chart(map_df.head(10).set_index("City")["Total Emissions"])

elif page == "City Information":
    st.title("City Information")
    st.markdown(f"**Last Updated: {LAST_UPDATED}**")
    city_options = list(cities_districts.keys())
    selected_city = st.selectbox("Select City", city_options)
    st.dataframe(city_data[city_data["City Name"]==selected_city])
    
    st.subheader("Download CAP PDF")
    name = st.text_input("Your Name")
    email = st.text_input("Official Email")
    if st.button("Download CAP PDF"):
        if not name or not email:
            st.warning("Please provide your name and official email")
        else:
            pdf_buffer = generate_cap_pdf(selected_city, name, email)
            st.download_button("Download PDF", pdf_buffer, file_name=f"CAP_{selected_city}.pdf", mime="application/pdf")
            upload_to_sharepoint(selected_city, pdf_buffer, f"CAP_{selected_city}.pdf")

elif page == "Admin":
    st.title("Admin Panel - EinTrust Only")
    st.markdown(f"**Last Updated: {LAST_UPDATED}**")
    password = st.text_input("Enter Admin Password", type="password")
    if password != ADMIN_PASSWORD:
        st.warning("Incorrect password")
    else:
        admin_tab = st.radio("Select Admin Function", ["CAP Update","Data Collection","GHG Inventory","Actions"])
        selected_city = st.selectbox("Select City", list(cities_districts.keys()))
        if admin_tab == "CAP Update":
            city_row = city_data[city_data["City Name"]==selected_city].iloc[0]
            for col in city_data_columns[2:10]:
                city_row[col] = st.text_input(col, city_row[col])
            if st.button("Save City Info"):
                for col in city_data_columns[2:10]:
                    city_data.loc[city_data["City Name"]==selected_city,col] = city_row[col]
                st.success(f"Updated {selected_city}")
        elif admin_tab == "Data Collection":
            st.write("Enter sector-wise data for GHG inventory")
            city_inputs = {}
            for sector in sector_columns:
                city_inputs[sector] = st.number_input(f"{sector} Consumption/Activity Data", min_value=0.0, value=0.0)
            if st.button("Save Data"):
                emissions = calculate_city_emissions(city_inputs)
                for sector, value in emissions.items():
                    sector_emissions.loc[sector_emissions["City Name"]==selected_city, sector] = value
                st.success(f"Data saved for {selected_city}")
        elif admin_tab == "GHG Inventory":
            st.subheader("Sector-wise GHG Emissions")
            st.dataframe(sector_emissions[sector_emissions["City Name"]==selected_city])
        elif admin_tab == "Actions":
            st.subheader("Recommended Actions")
            for sector in recommended_actions.keys():
                st.markdown(f"**{sector} Sector**")
                for term in ["Short","Mid","Long"]:
                    st.write(f"{term}-term: {', '.join(recommended_actions[sector][term])}")
