import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from io import BytesIO
from datetime import datetime
import random
import os

# Optional SharePoint upload
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
except Exception as e:
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
# Helper functions
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
        
        # CAP Update
        if sub_page == "CAP Update":
            selected_city = st.selectbox("Select City", city_data["City Name"])
            city_row = city_data[city_data["City Name"]==selected_city].iloc[0]
            with st.form("cap_update_form"):
                updated_population = st.number_input("Population (2011)", value=int(city_row["Population (2011)"]))
                updated_est_pop = st.number_input("Estimated Population (2025)", value=int(city_row["Estimated Population (2025)"]))
                env_dept = st.selectbox("Environment Department Exists?", ["Yes","No"], index=0 if city_row["Environment Department Exists?"]=="Yes" else 1)
                resp_dept = st.text_input("Responsible Department", value=city_row["Responsible Department"])
                contact = st.text_input("Contact Person (Name & Email)", value=city_row["Contact Person"])
                cap_status = st.selectbox("CAP Status", ["Not Started","Planned","In Progress","Completed"], index=["Not Started","Planned","In Progress","Completed"].index(city_row["CAP Status"]))
                cap_link = st.text_input("CAP Link", value=city_row["CAP Link"])
                city_website = st.text_input("City Website", value=city_row["City Website"])
                submitted = st.form_submit_button("Save/Update")
                if submitted:
                    city_data.loc[city_data["City Name"]==selected_city, ["Population (2011)","Estimated Population (2025)",
                        "Environment Department Exists?","Responsible Department","Contact Person","CAP Status","CAP Link","City Website"]] = [
                        updated_population, updated_est_pop, env_dept, resp_dept, contact, cap_status, cap_link, city_website]
                    st.success(f"{selected_city} CAP data updated successfully!")

        # Data Collection
        elif sub_page == "Data Collection":
            st.subheader("Collect City-level Data for GHG Inventory")
            selected_city = st.selectbox("Select City", city_data["City Name"])
            city_row = sector_emissions[sector_emissions["City Name"]==selected_city].iloc[0]
            with st.form("data_collection_form"):
                inputs = {}
                for s in sector_columns:
                    inputs[s] = st.number_input(f"{s} Emissions", value=float(city_row[s]))
                submitted = st.form_submit_button("Save Data")
                if submitted:
                    for s in sector_columns:
                        sector_emissions.loc[sector_emissions["City Name"]==selected_city, s] = inputs[s]
                    st.success(f"{selected_city} GHG data saved successfully!")

        # GHG Inventory
        elif sub_page == "GHG Inventory":
            st.subheader("Sector-wise GHG Inventory")
            selected_city = st.selectbox("Select City", city_data["City Name"])
            city_sector = sector_emissions[sector_emissions["City Name"]==selected_city]
            st.write("Sector-wise Emissions (tCO2e)")
            st.dataframe(city_sector.set_index("City Name").T)
            total_emissions = city_sector[sector_columns].sum(axis=1).values[0]
            est_pop = city_data.loc[city_data["City Name"]==selected_city, "Estimated Population (2025)"].values[0]
            per_capita = total_emissions / max(est_pop,1)
            st.metric("Total Emissions (tCO2e)", round(total_emissions,2))
            st.metric("Per Capita Emissions (tCO2e/person)", round(per_capita,2))
            st.subheader("Visuals")
            fig = px.pie(values=city_sector[sector_columns].values[0], names=sector_columns, title=f"{selected_city} Sector-wise Emissions")
            st.plotly_chart(fig)

        # Actions
        elif sub_page == "Actions":
            st.subheader("Recommended Actions")
            selected_city = st.selectbox("Select City", city_data["City Name"])
            for sector, terms in recommended_actions.items():
                st.markdown(f"**{sector}**")
                for term_name, action_list in terms.items():
                    st.markdown(f"- {term_name}-term: {', '.join(action_list)}")
