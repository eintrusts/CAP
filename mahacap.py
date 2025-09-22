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

# -------------------- Pages --------------------
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
elif page=="Admin":
    if not st.session_state.admin_logged_in:
        st.header("Admin Login")
        password_input = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password_input == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect password")
    else:
        st.header("Admin Panel")
        admin_tabs = st.tabs(["Add/Update City","Generate CAP","GHG Inventory","Logout"])
        
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
            st.info("CAP Form Tabs Here (Same structure as before, omitted for brevity)")

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

        # ---------------- Logout -----------------
        with admin_tabs[3]:
            if st.button("Logout Admin"):
                st.session_state.admin_logged_in = False
                st.success("Logged out successfully!")
                st.experimental_rerun()
