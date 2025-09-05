import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import random

# -----------------------
# SharePoint Integration
# -----------------------
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

SHAREPOINT_SITE = "https://eintrusts.sharepoint.com/sites/EinTrust"
SHAREPOINT_DOC = "/sites/EinTrust/Shared Documents/General/Work/CAP/CAP Dashboard"
CLIENT_ID = "<YOUR_CLIENT_ID>"
CLIENT_SECRET = "<YOUR_CLIENT_SECRET>"

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

# -----------------------
# App Config & Theme
# -----------------------
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

# -----------------------
# Cities & Dummy Coordinates
# -----------------------
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

# -----------------------
# DataFrames Initialization
# -----------------------
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

# -----------------------
# Sidebar
# -----------------------
st.sidebar.title("Maharashtra CAP Dashboard")
page = st.sidebar.radio("Navigate", ["Home", "City Information", "Admin"])
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 EinTrust Foundation")

# -----------------------
# Helper Functions
# -----------------------
def calculate_city_emissions(city_inputs):
    return {sector: city_inputs.get(sector,0)*EMISSION_FACTORS[sector] for sector in EMISSION_FACTORS.keys()}

def generate_cap_pdf(city_name, name, email):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width/2, height-2*cm, f"Maharashtra Climate Action Plan - {city_name}")
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, height-3*cm, f"Generated for: {name} ({email})")
    c.drawString(2*cm, height-3.5*cm, f"Last Updated: {LAST_UPDATED}")
    city_info = city_data[city_data["City Name"]==city_name].iloc[0]
    y = height-5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "City Information:")
    c.setFont("Helvetica", 10)
    y -= 0.5*cm
    for key in ["District","Population (2011)","Estimated Population (2025)","Environment Department Exists?",
                "Responsible Department","Contact Person","CAP Status","CAP Link","City Website"]:
        c.drawString(2*cm, y, f"{key}: {city_info.get(key,'')}")
        y -= 0.4*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "Sector-wise GHG Emissions (tCO₂e):")
    c.setFont("Helvetica", 10)
    y -= 0.5*cm
    sectors = sector_emissions[sector_emissions["City Name"]==city_name].iloc[0,1:]
    for sector, value in sectors.items():
        c.drawString(2*cm, y, f"{sector}: {round(value,2)}")
        y -= 0.4*cm
    c.setFont("Helvetica-Bold", 12)
    y -= 0.2*cm
    c.drawString(2*cm, y, "Recommended Actions:")
    c.setFont("Helvetica", 10)
    y -= 0.5*cm
    for sector in recommended_actions.keys():
        c.drawString(2*cm, y, f"{sector}:")
        y -= 0.4*cm
        for term in ["Short","Mid","Long"]:
            c.drawString(3*cm, y, f"{term}-term: {', '.join(recommended_actions[sector][term])}")
            y -= 0.3*cm
        y -= 0.1*cm
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 1*cm, "© 2025 EinTrust Foundation")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def generate_ghg_inventory_excel(city_name):
    buffer = BytesIO()
    df = sector_emissions[sector_emissions["City Name"]==city_name].copy()
    df["Total Emissions"] = df[sector_columns].sum(axis=1)
    df["Per Capita Emissions"] = df["Total Emissions"] / max(1, city_data.loc[city_data["City Name"]==city_name,"Estimated Population (2025)"].values[0])
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def generate_actions_excel(city_name):
    buffer = BytesIO()
    rows = []
    for sector in recommended_actions.keys():
        for term in ["Short","Mid","Long"]:
            for action in recommended_actions[sector][term]:
                rows.append({"Sector":sector, "Term":term, "Action":action})
    pd.DataFrame(rows).to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

# -----------------------
# Pages
# -----------------------
if page == "Home":
    st.title("Maharashtra CAP Dashboard - Home")
    st.markdown(f"**Last Updated:** {LAST_UPDATED}")
    city_data["Total Emissions"] = city_data["Estimated Population (2025)"] * 1.2
    top10 = city_data.sort_values("Total Emissions", ascending=False).head(10)
    fig_bar = px.bar(top10, x="City Name", y="Total Emissions", color="District")
    st.plotly_chart(fig_bar, use_container_width=True)
    map_df = city_data.copy()
    map_df["lat"] = map_df["City Name"].apply(lambda x: city_coords[x][0])
    map_df["lon"] = map_df["City Name"].apply(lambda x: city_coords[x][1])
    fig_map = px.scatter_mapbox(map_df, lat="lat", lon="lon", size="Total Emissions",
                                hover_name="City Name", hover_data=["Total Emissions"],
                                color="Total Emissions", color_continuous_scale="Viridis", zoom=5)
    fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

elif page == "City Information":
    st.title("City Information")
    st.markdown(f"**Last Updated:** {LAST_UPDATED}")
    district_filter = st.selectbox("Filter by District", ["All"] + list(set(city_data["District"])))
    cap_status_filter = st.selectbox("Filter by CAP Status", ["All","Not Started","Planned","In Progress","Completed"])
    df_filtered = city_data.copy()
    if district_filter != "All":
        df_filtered = df_filtered[df_filtered["District"]==district_filter]
    if cap_status_filter != "All":
        df_filtered = df_filtered[df_filtered["CAP Status"]==cap_status_filter]
    st.dataframe(df_filtered)
    
    selected_city = st.selectbox("Select City to Download CAP PDF", city_data["City Name"])
    name = st.text_input("Enter Your Name")
    email = st.text_input("Enter Official Email")
    if st.button("Download CAP PDF"):
        if not name or not email:
            st.error("Please enter name and official email")
        else:
            pdf_buffer = generate_cap_pdf(selected_city, name, email)
            st.download_button("Download PDF", pdf_buffer, file_name=f"{selected_city}_CAP.pdf")
            upload_to_sharepoint(selected_city, pdf_buffer, f"{selected_city}_CAP.pdf")
            # Also upload GHG Inventory and Actions Excel
            ghg_buffer = generate_ghg_inventory_excel(selected_city)
            upload_to_sharepoint(selected_city, ghg_buffer, f"{selected_city}_GHG_Inventory.xlsx")
            actions_buffer = generate_actions_excel(selected_city)
            upload_to_sharepoint(selected_city, actions_buffer, f"{selected_city}_Actions.xlsx")
            st.success(f"CAP PDF, GHG Inventory, and Actions uploaded to SharePoint for {selected_city}")

elif page == "Admin":
    st.title("Admin Page - EinTrust Only")
    pwd = st.text_input("Enter Admin Password", type="password")
    if pwd != ADMIN_PASSWORD:
        st.warning("Incorrect Password")
    else:
        st.success("Access Granted")
        admin_tab = st.radio("Admin Functions", ["CAP Update","Data Collection","GHG Inventory","Actions"])
        selected_city = st.selectbox("Select City", city_data["City Name"])
        if admin_tab == "CAP Update":
            city_row = city_data[city_data["City Name"]==selected_city].iloc[0]
            updated_status = st.selectbox("CAP Status", ["Not Started","Planned","In Progress","Completed"], index=["Not Started","Planned","In Progress","Completed"].index(city_row["CAP Status"]))
            city_data.loc[city_data["City Name"]==selected_city,"CAP Status"] = updated_status
            st.success(f"CAP Status Updated for {selected_city}")
        elif admin_tab == "Data Collection":
            st.subheader("Comprehensive Data Collection")
            city_inputs = {}
            for sector in sector_columns:
                city_inputs[sector] = st.number_input(f"{sector} consumption/emission value", min_value=0.0, step=0.1)
            if st.button("Save Data"):
                emissions = calculate_city_emissions(city_inputs)
                for sector, value in emissions.items():
                    sector_emissions.loc[sector_emissions["City Name"]==selected_city, sector] = value
                # Upload Data Collection Excel
                excel_buffer = BytesIO()
                pd.DataFrame([city_inputs]).to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                upload_to_sharepoint(selected_city, excel_buffer, f"{selected_city}_DataCollection.xlsx")
                # Upload GHG Inventory
                ghg_buffer = generate_ghg_inventory_excel(selected_city)
                upload_to_sharepoint(selected_city, ghg_buffer, f"{selected_city}_GHG_Inventory.xlsx")
                # Upload Recommended Actions
                actions_buffer = generate_actions_excel(selected_city)
                upload_to_sharepoint(selected_city, actions_buffer, f"{selected_city}_Actions.xlsx")
                st.success(f"All files uploaded to SharePoint for {selected_city}")
        elif admin_tab == "GHG Inventory":
            st.dataframe(sector_emissions[sector_emissions["City Name"]==selected_city])
        elif admin_tab == "Actions":
            for sector in recommended_actions.keys():
                st.markdown(f"**{sector} Sector**")
                for term in ["Short","Mid","Long"]:
                    st.write(f"{term}-term: {', '.join(recommended_actions[sector][term])}")
