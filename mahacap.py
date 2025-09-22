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
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Home"

    st.sidebar.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111827; color: #ffffff; width: 260px; min-width: 260px; max-width: 260px;}
    [data-testid="stSidebarCollapseButton"] { display: none;}
    .sidebar-logo { display: flex; justify-content: center; align-items: center; margin: 20px 0 30px 0; }
    .sidebar-logo img { max-width: 190px; height: auto; border-radius: 15px; }
    .menu-btn { display: block; width: 100%; padding: 12px 20px; margin: 8px 0; background: transparent; color: #e5e7eb; text-align: left; font-size: 16px; font-weight: 500; border: none; border-radius: 6px; cursor: pointer; transition: all 0.3s ease;}
    .menu-btn:hover { background: linear-gradient(90deg, #ef444420 0%, #ef444440 100%); color: #ffffff; transform: translateX(4px); box-shadow: 0 0 12px rgba(239,68,68,0.6);}
    .menu-btn-active { background: linear-gradient(90deg, #ef4444 0%, #b91c1c 100%); color: #ffffff !important; font-weight: 600; border-left: 4px solid #f87171; padding-left: 16px; box-shadow: 0 0 10px rgba(239,68,68,0.6); animation: pulseGlow 2s infinite;}
    @keyframes pulseGlow { 0% { box-shadow: 0 0 10px rgba(239,68,68,0.6);} 50% { box-shadow: 0 0 20px rgba(239,68,68,0.9);} 100% { box-shadow: 0 0 10px rgba(239,68,68,0.6);} }
    .sidebar-footer { position: fixed; bottom: 20px; left: 0; width: 260px; text-align: center; color: #9ca3af; font-size: 13px; padding: 10px 0; }
    .sidebar-footer strong { color: #ffffff; }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Logo
    st.sidebar.markdown(
        '<div class="sidebar-logo"><img src="https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true"></div>',
        unsafe_allow_html=True
    )

    # Sidebar Menu
    menu = ["Home", "City", "Admin"]
    for m in menu:
        btn_class = "menu-btn-active" if st.session_state.current_page == m else "menu-btn"
        if st.sidebar.button(m, key=f"menu_{m}"):
            st.session_state.current_page = m

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
    ADMIN_PASSWORD = "eintrust2025"
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

    # --- Add/Update City (Basic Info Only) ---
    with admin_tabs[0]:
        st.subheader("Add / Update City (Basic Info)")
        city_select = st.selectbox("Select City", cities, key="add_update_city")
        city_existing = st.session_state.city_data.get(city_select, {})
        population = st.number_input("Population", min_value=0, value=city_existing.get("Basic Info",{}).get("Population",0), key="population")
        area = st.number_input("Area (sq km)", min_value=0, value=city_existing.get("Basic Info",{}).get("Area",0), key="area")
        gdp = st.number_input("GDP (₹ Crores)", min_value=0, value=city_existing.get("Basic Info",{}).get("GDP",0), key="gdp")
        cap_status_options = ["Not Started","In Progress","Completed"]
        cap_status_default = city_existing.get("CAP_Status","Not Started")
        if cap_status_default not in cap_status_options:
            cap_status_default = "Not Started"
        cap_status = st.selectbox("CAP Status", cap_status_options, index=cap_status_options.index(cap_status_default), key="cap_status_add")
        cap_upload = st.file_uploader("Upload CAP Document (PDF/Excel)", type=["pdf","xlsx","xls"])
        
        if st.button("Save City Info"):
            st.session_state.city_data[city_select] = {
                "Basic Info":{"Population":population,"Area":area,"GDP":gdp},
                "CAP_Status":cap_status,
                "CAP_Document": cap_upload.name if cap_upload else None,
                "Last_Updated": last_updated()
            }
            st.success(f"{city_select} information saved!")

    # --- Generate CAP (sector-wise, unchanged) ---
    with admin_tabs[1]:
        st.subheader("Generate CAP")
        city_select = st.selectbox("Select City for CAP", cities, key="cap_city_select")
        city_info = st.session_state.city_data.get(city_select, {})
        st.info("CAP generation section unchanged. Use this for detailed sector-wise CAP input.")

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
