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
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #111827;  /* Dark background */
        color: #ffffff;
        width: 260px;
        min-width: 260px;
        max-width: 260px;
    }

    /* Hide collapse/expand button */
    [data-testid="stSidebarCollapseButton"] {
        display: none;
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
        border-radius: 15px; /* Rounded corners */
    }

    /* Menu Buttons */
    .menu-btn {
        display: block;
        width: 100%;
        padding: 12px 20px;
        margin: 8px 0;
        background: transparent;
        color: #e5e7eb;
        text-align: left;
        font-size: 16px;
        font-weight: 500;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .menu-btn:hover {
        background: linear-gradient(90deg, #ef444420 0%, #ef444440 100%);
        color: #ffffff;
        transform: translateX(4px);
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.6); /* Red glow on hover */
    }

    /* Active Button with Pulse Animation */
    .menu-btn-active {
        background: linear-gradient(90deg, #ef4444 0%, #b91c1c 100%);
        color: #ffffff !important;
        font-weight: 600;
        border-left: 4px solid #f87171;
        padding-left: 16px;
        box-shadow: 0 0 10px rgba(239,68,68,0.6);
        animation: pulseGlow 2s infinite;
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(239,68,68,0.6); }
        50% { box-shadow: 0 0 20px rgba(239,68,68,0.9); }
        100% { box-shadow: 0 0 10px rgba(239,68,68,0.6); }
    }

    /* Footer */
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 0;
        width: 260px;
        text-align: center;
        color: #9ca3af;
        font-size: 13px;
        padding: 10px 0;
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

    # Sidebar Menu with Active State
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
    # --- Dark Theme Body ---
    st.markdown("<style>body {background-color: #121212; color: #ffffff;}</style>", unsafe_allow_html=True)

    st.header("Climate Action Plan Dashboard")
    st.caption("Maharashtra's Net Zero Journey")

    # --- CAP Status Overview ---
    status_counts = {"Not Started": 0, "In Progress": 0, "Completed": 0}
    for c in cities:
        status = st.session_state.city_data.get(c, {}).get("CAP_Status", "Not Started")
        if status in status_counts:
            status_counts[status] += 1

    total_cities = 43  # fixed value
    st.markdown("### CAP Status Overview")

    cap_status_html = f"""
    <div style="display:flex; gap:15px; margin-bottom:15px;">
        <div style="flex:1; border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow: 0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Total Cities</div>
            <div style="font-size:22px; font-weight:600; color:#1f77b4;">{total_cities}</div>
        </div>
        <div style="flex:1; border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow: 0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Not Started</div>
            <div style="font-size:22px; font-weight:600; color:#d62728;">{status_counts['Not Started']}</div>
        </div>
        <div style="flex:1; border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow: 0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">In Progress</div>
            <div style="font-size:22px; font-weight:600; color:#ff7f0e;">{status_counts['In Progress']}</div>
        </div>
        <div style="flex:1; border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow: 0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Completed</div>
            <div style="font-size:22px; font-weight:600; color:#2ca02c;">{status_counts['Completed']}</div>
        </div>
    </div>
    """
    st.markdown(cap_status_html, unsafe_allow_html=True)

    # --- Maharashtra Basic Information ---
    st.markdown("### Maharashtra Basic Information")

    total_population = sum([
        st.session_state.city_data.get(c, {}).get("Population", {}).get("Total", 0)
        for c in cities
    ])
    total_area = sum([
        st.session_state.city_data.get(c, {}).get("Area", 0)
        for c in cities
    ])

    dept_name = ""
    dept_email = ""
    website = ""
    cap_link = ""
    cap_status = ""
    for c in cities:
        city_info = st.session_state.city_data.get(c, {})
        if city_info:
            cap_status = city_info.get("CAP_Status", "Not Started")
            cap_link = city_info.get("CAP_Link", "")
            dept_name = city_info.get("Dept_Name", "")
            dept_email = city_info.get("Dept_Email", "")
            website = city_info.get("Website", "")
            break

    basic_info_html = f"""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:15px;">
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">CAP Status</div>
            <div style="font-size:16px; font-weight:600; color:#ffffff;">{cap_status}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">CAP Link</div>
            <div><a href="{cap_link}" target="_blank" style="font-size:14px; color:#1f77b4; text-decoration:none;">Open Link</a></div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Total Population</div>
            <div style="font-size:16px; font-weight:600; color:#ffffff;">{total_population:,}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Area (sq km)</div>
            <div style="font-size:16px; font-weight:600; color:#ffffff;">{total_area:,}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Department Name</div>
            <div style="font-size:14px; color:#ffffff;">{dept_name}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Department Email</div>
            <div style="font-size:14px; color:#ffffff;">{dept_email}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Website</div>
            <div><a href="{website}" target="_blank" style="font-size:14px; color:#1f77b4; text-decoration:none;">{website}</a></div>
        </div>
    </div>
    """
    st.markdown(basic_info_html, unsafe_allow_html=True)

    # --- GHG by Sector ---
    ghg_sectors = ["Energy", "Transport", "Waste", "Water"]
    ghg_values = [
        sum([st.session_state.city_data.get(c, {}).get("GHG", {}).get(s, 0) for c in cities])
        for s in ghg_sectors
    ]
    fig = px.bar(
        x=ghg_sectors, 
        y=ghg_values, 
        labels={"x": "Sector", "y": "tCO2e"}, 
        title="Maharashtra GHG Emissions by Sector",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- RCP Scenarios ---
    st.markdown("### RCP Scenario Projections")
    years = list(range(2020, 2051))
    rcp_45 = np.linspace(1.0, 2.0, len(years))
    rcp_60 = np.linspace(1.0, 2.5, len(years))
    rcp_85 = np.linspace(1.0, 3.5, len(years))

    fig2 = px.line(x=years, y=rcp_45, labels={"x": "Year", "y": "Temp Rise (°C)"}, title="Projected RCP Scenarios", template="plotly_dark")
    fig2.add_scatter(x=years, y=rcp_60, mode="lines", name="RCP 6.0")
    fig2.add_scatter(x=years, y=rcp_85, mode="lines", name="RCP 8.5")

    st.plotly_chart(fig2, use_container_width=True)

    # --- Footer: Last Updated ---
    st.markdown(
        f"""
        <div style='position:fixed; bottom:10px; centre:10px; color:#aaaaaa; font-size:12px;'>
            Last Updated: {last_updated()}
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------- City Page --------------------
import plotly.graph_objects as go  # make sure this is at the top with other imports

def city_page():
    # --- Dark Theme Body ---
    st.markdown("<style>body {background-color: #121212; color: #ffffff;}</style>", unsafe_allow_html=True)

    st.header("City-Level CAP Dashboard")

    # Dropdown in alphabetical order
    selected_city = st.selectbox("Select City", sorted(cities), key="city_page_select")
    city_info = st.session_state.city_data.get(selected_city, {})

    st.subheader(f"{selected_city} Net Zero Journey")

    # --- Basic Information Cards ---
    cap_status = city_info.get("CAP_Status", "Not Started")
    cap_link = city_info.get("CAP_Link", "")
    population = city_info.get("Basic Info", {}).get("Population", 0)
    area = city_info.get("Basic Info", {}).get("Area", 0)
    dept_name = city_info.get("Dept_Name", "")
    dept_email = city_info.get("Dept_Email", "")
    website = city_info.get("Website", "")

    basic_info_html = f"""
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:15px; margin-bottom:20px;">
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">CAP Status</div>
            <div style="font-size:16px; font-weight:600; color:#ffffff;">{cap_status}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">CAP Link</div>
            <div><a href="{cap_link}" target="_blank" style="font-size:14px; color:#1f77b4; text-decoration:none;">Open Link</a></div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Population</div>
            <div style="font-size:16px; font-weight:600; color:#ffffff;">{population:,}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center; box-shadow:0 2px 6px rgba(0,0,0,0.5);">
            <div style="font-size:13px; color:#cccccc;">Area (sq km)</div>
            <div style="font-size:16px; font-weight:600; color:#ffffff;">{area:,}</div>
            </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center;">
            <div style="font-size:13px; color:#cccccc;">Department Name</div>
            <div style="font-size:14px; color:#ffffff;">{dept_name}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center;">
            <div style="font-size:13px; color:#cccccc;">Department Email</div>
            <div style="font-size:14px; color:#ffffff;">{dept_email}</div>
        </div>
        <div style="border-radius:8px; background:#1e1e1e; padding:16px; text-align:center;">
            <div style="font-size:13px; color:#cccccc;">Website</div>
            <div><a href="{website}" target="_blank" style="font-size:14px; color:#1f77b4; text-decoration:none;">{website}</a></div>
        </div>
    </div>
    """
    st.markdown(basic_info_html, unsafe_allow_html=True)

    # --- GHG Emissions by Sector ---
    st.markdown("### GHG Emissions by Sector")
    ghg_sectors = ["Energy", "Transport", "Waste", "Water", "Buildings", "Industry"]
    ghg_values = [city_info.get("GHG", {}).get(s, 0) for s in ghg_sectors]

    fig_ghg = px.bar(
        x=ghg_sectors,
        y=ghg_values,
        labels={"x": "Sector", "y": "tCO2e"},
        title=f"{selected_city} GHG Emissions by Sector",
        template="plotly_dark"
    )
    st.plotly_chart(fig_ghg, use_container_width=True)

    # --- RCP Scenario Projections ---
    st.markdown("### RCP Scenario Projections")
    years = list(range(2020, 2051))
    rcp_45 = np.linspace(1.0, 2.0, len(years))
    rcp_60 = np.linspace(1.0, 2.5, len(years))
    rcp_85 = np.linspace(1.0, 3.5, len(years))

    fig_rcp = go.Figure()
    fig_rcp.add_trace(go.Scatter(x=years, y=rcp_45, mode="lines", name="RCP 4.5"))
    fig_rcp.add_trace(go.Scatter(x=years, y=rcp_60, mode="lines", name="RCP 6.0"))
    fig_rcp.add_trace(go.Scatter(x=years, y=rcp_85, mode="lines", name="RCP 8.5"))

    fig_rcp.update_layout(
        template="plotly_dark",
        title=f"{selected_city} RCP Scenario Projections",
        xaxis_title="Year",
        yaxis_title="Temp Rise (°C)"
    )
    st.plotly_chart(fig_rcp, use_container_width=True)

    # --- Footer: Last Updated ---
    st.markdown(
        f"""
        <div style='position:fixed; bottom:10px; center:10px; color:#aaaaaa; font-size:12px;'>
            Last Updated: {last_updated()}
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------- Admin Panel --------------------
def admin_panel():
    ADMIN_PASSWORD = "eintrust2025"

    # ------------------- Initialize Session State -------------------
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    if 'current_admin_tab' not in st.session_state:
        st.session_state.current_admin_tab = 0
    if 'last_selected_city' not in st.session_state:
        st.session_state.last_selected_city = "Maharashtra"
    if 'city_data' not in st.session_state:
        st.session_state.city_data = {}

    # ------------------- Admin Login -------------------
    if not st.session_state.admin_logged_in:
        st.header("Admin Login")
        password_input = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password_input == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("Logged in successfully!")
                st.session_state.current_admin_tab = 0
            else:
                st.error("Incorrect password")
        return

    # ------------------- Admin Panel -------------------
    st.header("Admin Panel")
    admin_tabs = st.tabs(["Add/Update City","Generate CAP","GHG Inventory","Logout"])

    # ------------------- Add/Update City -------------------
    if st.session_state.current_admin_tab == 0:
        with admin_tabs[0]:
            # --- City Selection ---
            city_list = sorted(cities)
            if "Maharashtra" not in city_list:
                city_list = ["Maharashtra"] + city_list

            st.subheader("Add / Update City Data")
            city_select = st.selectbox(
                "Select City",
                city_list,
                index=city_list.index(st.session_state.last_selected_city),
                key="add_update_city"
            )
            st.session_state.last_selected_city = city_select
            city_info = st.session_state.city_data.get(city_select, {})

            
            district = st.text_input("District", value=city_info.get("District",""), key="district")
            year_est = st.number_input("Year of Establishment", min_value=1500, max_value=2050,
                                       value=city_info.get("Year_Establishment",2025), key="year_est")
            admin_types = ["State","Municipal Corporation","Municipal Council","Other"]
            type_admin = st.selectbox("Type of Administration", admin_types,
                                      index=admin_types.index(city_info.get("Type_Admin","State")), key="type_admin")
            cap_status_options = ["Not Started","In Progress","Completed"]
            cap_status = st.selectbox("CAP Status", cap_status_options,
                                      index=cap_status_options.index(city_info.get("CAP_Status","Not Started")), key="cap_status")
            cap_link = city_info.get("CAP_Link","")
            if cap_status == "Completed":
                cap_link = st.text_input("CAP Link", value=cap_link, key="cap_link")

           
            col1, col2, col3 = st.columns(3)
            with col1:
                male_pop = st.number_input("Male", min_value=0,
                                           value=city_info.get("Population",{}).get("Male",0), key="pop_male")
            with col2:
                female_pop = st.number_input("Female", min_value=0,
                                             value=city_info.get("Population",{}).get("Female",0), key="pop_female")
            total_pop = male_pop + female_pop
            with col3:
                st.metric("Total Population", total_pop)

            col1, col2 = st.columns(2)
            with col1:
                area = st.number_input("Area (sq km)", min_value=0,
                                       value=city_info.get("Area",0), key="area")
            with col2:
                density = total_pop / area if area > 0 else 0
                st.metric("Density (people/km²)", round(density,2))

            sex_ratio = st.number_input("Sex Ratio (F/M)", min_value=0,
                                        value=city_info.get("Sex_Ratio",0), key="sex_ratio")
            env_exist = st.selectbox("Environment Dept Exist", ["Yes","No"],
                                     index=0 if city_info.get("Env_Dept_Exist","Yes")=="Yes" else 1, key="env_exist")
            dept_name = ""
            if env_exist == "No":
                dept_name = st.text_input("Department Name", value=city_info.get("Dept_Name",""), key="dept_name")
            dept_person = st.text_input("Department Contact Person", value=city_info.get("Dept_Person",""), key="dept_person")
            dept_email = st.text_input("Department Email ID", value=city_info.get("Dept_Email",""), key="dept_email")
            website = st.text_input("Website", value=city_info.get("Website",""), key="website")

            # --- Save Button ---
            if st.button("Add/Update City"):
                prev_data = st.session_state.city_data.get(city_select, {})
                st.session_state.city_data[city_select] = {
                    "District": district,
                    "Year_Establishment": year_est,
                    "Type_Admin": type_admin,
                    "CAP_Status": cap_status,
                    "CAP_Link": cap_link if cap_status=="Completed" else "",
                    "Population":{"Male":male_pop,"Female":female_pop,"Total":total_pop},
                    "Area": area,
                    "Sex_Ratio": sex_ratio,
                    "Density": density,
                    "Env_Dept_Exist": env_exist,
                    "Dept_Name": dept_name if env_exist=="No" else "",
                    "Dept_Person": dept_person,
                    "Dept_Email": dept_email,
                    "Website": website
                }
                st.success(f"{city_select} data saved successfully!")

    # --- Generate CAP ---
    import streamlit as st
import datetime

# -------------------- Admin Tabs --------------------
admin_tabs = st.tabs(["Dashboard","Generate CAP","Reports"])

cities = list(st.session_state.city_data.keys()) if "city_data" in st.session_state else []

with admin_tabs[1]:
    st.subheader("Generate Comprehensive CAP - Raw Data Collection Form")
    city_select = st.selectbox("Select City for CAP", cities, key="cap_city_select")
    city_info = st.session_state.city_data.get(city_select, {})

    cap_tabs = st.tabs([
        "Basic Info","Energy & Buildings","Green Cover & Biodiversity",
        "Sustainable Mobility","Water Resources","Waste Management","Climate Data"
    ])

    # -------------------- 1. Basic Info --------------------
    with cap_tabs[0]:
        st.header("City Baseline & Demographics")
        population = st.number_input("Total Population", min_value=0, value=city_info.get("Basic Info",{}).get("Population",0), key="cap_pop")
        area = st.number_input("Total Area (sq km)", min_value=0, value=city_info.get("Basic Info",{}).get("Area",0), key="cap_area")
        gdp = st.number_input("GDP (₹ Crores)", min_value=0, value=city_info.get("Basic Info",{}).get("GDP",0), key="cap_gdp")
        density = st.number_input("Population Density (people/km²)", min_value=0, value=city_info.get("Basic Info",{}).get("Density",0), key="cap_density")
        climate_zone = st.text_input("Climate Zone", value=city_info.get("Basic Info",{}).get("Climate_Zone",""), key="cap_climate_zone")
        admin_structure = st.text_input("Administrative Structure", value=city_info.get("Basic Info",{}).get("Admin",""), key="cap_admin_structure")
        governance_level = st.selectbox("Governance Level", ["City Corporation","Municipal Council","Town Panchayat","Other"], key="cap_governance_level")
        baseline_year = st.number_input("Baseline Year for GHG Inventory", min_value=1990, max_value=datetime.datetime.now().year, value=city_info.get("Basic Info",{}).get("Baseline_Year",2020), key="cap_baseline_year")
        reporting_frameworks = st.multiselect("Reporting Frameworks Covered", ["IPCC","GPC","GHG Protocol","National Guidelines","State Guidelines","SDGs","Paris/NDC Alignment"], default=city_info.get("Basic Info",{}).get("Frameworks",[]), key="cap_frameworks")
        population_growth = st.number_input("Population Growth Rate (%)", min_value=0.0, max_value=10.0, step=0.01, value=city_info.get("Basic Info",{}).get("Population_Growth",0.0), key="cap_pop_growth")
        economic_growth = st.number_input("Economic Growth Rate (%)", min_value=0.0, max_value=20.0, step=0.01, value=city_info.get("Basic Info",{}).get("Economic_Growth",0.0), key="cap_econ_growth")
        boundary_scope = st.text_area("CAP Boundary & Scope (Administrative, Sectoral, GHG Scope 1/2/3)", value=city_info.get("Basic Info",{}).get("Boundary_Scope",""), key="cap_boundary_scope")
        mer_tracking_existing = st.selectbox("Existing MER System", ["Yes","No"], key="cap_mer_existing")
        
        if st.button("Save Basic Info Data"):
            st.session_state.city_data[city_select]["Basic Info"] = {
                "Population":population,"Area":area,"GDP":gdp,"Density":density,
                "Climate_Zone":climate_zone,"Admin":admin_structure,"Governance":governance_level,
                "Baseline_Year":baseline_year,"Frameworks":reporting_frameworks,
                "Population_Growth":population_growth,"Economic_Growth":economic_growth,
                "Boundary_Scope":boundary_scope,"MER_Existing":mer_tracking_existing
            }
            st.success("Basic Info saved!")

    # -------------------- 2. Energy & Buildings --------------------
    with cap_tabs[1]:
        st.header("Energy & Buildings Sector")
        res_energy = st.number_input("Residential Electricity (kWh/year)", min_value=0, key="res_energy")
        com_energy = st.number_input("Commercial Electricity (kWh/year)", min_value=0, key="com_energy")
        ind_energy = st.number_input("Industrial Electricity (kWh/year)", min_value=0, key="ind_energy")
        public_building_energy = st.number_input("Public Building Electricity (kWh/year)", min_value=0, key="public_energy")
        fuel_types = st.multiselect("Fuels Used", ["Coal","Gas","Biomass","Petroleum","Electricity","Other"], key="fuel_types")
        renewable_share = st.slider("Renewable Energy Share (%)",0,100,0,key="renewable_share")
        ee_buildings = st.number_input("Energy-Efficient Buildings Certified", min_value=0,key="ee_buildings")
        street_lighting_type = st.selectbox("Street Lighting Type", ["LED","CFL","Other"], key="street_type")
        street_lighting_coverage = st.slider("Street Lighting Coverage (%)",0,100,0,key="street_coverage")
        energy_emissions = st.number_input("Estimated Energy Sector GHG Emissions (tCO2e/year)", min_value=0,key="energy_emissions")
        energy_reduction_targets = st.number_input("Energy Reduction Targets (%)", min_value=0,max_value=100,key="energy_reduction_targets")
        energy_policy_notes = st.text_area("Existing Energy & Building Policies / Standards", key="energy_policy_notes")
        
        if st.button("Save Energy & Buildings Data"):
            st.session_state.city_data[city_select]["Energy_Buildings"] = {
                "Residential":res_energy,"Commercial":com_energy,"Industrial":ind_energy,
                "Public_Building_Energy":public_building_energy,"Fuel_Types":fuel_types,
                "Renewable_Share":renewable_share,"EE_Buildings":ee_buildings,
                "Street_Lighting_Type":street_lighting_type,"Street_Lighting_Coverage":street_lighting_coverage,
                "Energy_Emissions":energy_emissions,"Energy_Reduction_Targets":energy_reduction_targets,
                "Policy_Notes":energy_policy_notes
            }
            st.success("Energy & Buildings data saved!")

    # -------------------- 3. Green Cover & Biodiversity --------------------
    with cap_tabs[2]:
        st.header("Green Cover & Biodiversity")
        green_cover_area = st.number_input("Total Green Cover Area (ha)", min_value=0, key="green_cover")
        tree_density = st.number_input("Tree Density (trees/km²)", min_value=0, key="tree_density")
        protected_areas = st.number_input("Protected Areas (ha)", min_value=0, key="protected_areas")
        urban_forests = st.number_input("Urban Forests Area (ha)", min_value=0, key="urban_forests")
        biodiversity_programs = st.text_area("Biodiversity Programs", key="biodiversity_programs")
        carbon_sequestration = st.number_input("Estimated Carbon Sequestration (tCO2e/year)", min_value=0, key="carbon_seq")
        resilience_projects = st.text_area("Climate Resilience & Adaptation Projects", key="resilience_projects")
        
        if st.button("Save Green Cover Data"):
            st.session_state.city_data[city_select]["Green_Biodiversity"] = {
                "Green_Cover":green_cover_area,"Tree_Density":tree_density,"Protected_Areas":protected_areas,
                "Urban_Forests":urban_forests,"Programs":biodiversity_programs,
                "Carbon_Sequestration":carbon_sequestration,"Resilience_Projects":resilience_projects
            }
            st.success("Green Cover & Biodiversity data saved!")

    # -------------------- 4. Sustainable Mobility --------------------
    with cap_tabs[3]:
        st.header("Sustainable Mobility")
        public_transport_coverage = st.slider("Public Transport Coverage (%)",0,100,0, key="pt_coverage")
        non_motorized_infra = st.slider("Non-Motorized Infrastructure (%)",0,100,0, key="nmi")
        ev_charging_stations = st.number_input("EV Charging Stations Count", min_value=0,key="ev_stations")
        veh_emissions = st.number_input("Average Vehicle Emissions (gCO2/km)", min_value=0,key="veh_emissions")
        fuel_shift_targets = st.number_input("Target % Shift to Low Carbon Fuels",0,100,key="fuel_shift_targets")
        smart_transport_projects = st.text_area("Smart Mobility & ITS Projects", key="smart_projects")
        
        if st.button("Save Mobility Data"):
            st.session_state.city_data[city_select]["Mobility"] = {
                "Public_Transport":public_transport_coverage,"Non_Motorized":non_motorized_infra,
                "EV_Stations":ev_charging_stations,"Vehicle_Emissions":veh_emissions,
                "Fuel_Shift_Targets":fuel_shift_targets,"Smart_Projects":smart_transport_projects
            }
            st.success("Sustainable Mobility data saved!")

    # -------------------- 5. Water Resources --------------------
    with cap_tabs[4]:
        st.header("Water Resources")
        water_consumption = st.number_input("Total Water Consumption (ML/year)", min_value=0,key="water_cons")
        wastewater_treatment = st.slider("Wastewater Treatment Coverage (%)",0,100,0,key="wwt")
        rainwater_harvesting = st.selectbox("Rainwater Harvesting Implementation", ["Yes","No"], key="rwh")
        leakage_ratio = st.slider("Water Leakage Ratio (%)",0,100,0,key="leakage_ratio")
        water_energy_use = st.number_input("Energy Used for Water Supply & Treatment (kWh/year)", min_value=0,key="water_energy_use")
        water_emissions = st.number_input("GHG Emissions from Water Sector (tCO2e/year)", min_value=0,key="water_emissions")
        water_policy = st.text_area("Water Management Policies & Programs", key="water_policy")
        
        if st.button("Save Water Data"):
            st.session_state.city_data[city_select]["Water"] = {
                "Consumption":water_consumption,"WWT":wastewater_treatment,"RWH":rainwater_harvesting,
                "Leakage":leakage_ratio,"Energy_Use":water_energy_use,"Emissions":water_emissions,
                "Policy":water_policy
            }
            st.success("Water Resources data saved!")

    # -------------------- 6. Waste Management --------------------
    with cap_tabs[5]:
        st.header("Waste Management")
        total_waste = st.number_input("Total Waste Generated (t/year)", min_value=0,key="total_waste")
        waste_recycled = st.slider("Waste Recycled (%)",0,100,0,key="waste_recycled")
        treatment_facilities = st.number_input("Waste Treatment Facilities Count", min_value=0,key="waste_facilities")
        composting = st.selectbox("Composting Infrastructure", ["Yes","No"], key="composting")
        hazardous_policy = st.text_area("Hazardous Waste Policies & Guidelines", key="hazardous_policy")
        methane_recovery = st.text_area("Methane / Landfill Gas Recovery Projects", key="methane_projects")
        waste_emissions = st.number_input("GHG Emissions from Waste Sector (tCO2e/year)", min_value=0,key="waste_emissions")
        
        if st.button("Save Waste Data"):
            st.session_state.city_data[city_select]["Waste"] = {
                "Total":total_waste,"Recycled":waste_recycled,"Facilities":treatment_facilities,
                "Composting":composting,"Hazardous":hazardous_policy,"Methane_Projects":methane_recovery,
                "Emissions":waste_emissions
            }
            st.success("Waste Management data saved!")

    # -------------------- 7. Climate Data --------------------
    with cap_tabs[6]:
        st.header("Climate Data & Risk Assessment")
        avg_temp = st.number_input("Average Temperature (°C)", key="avg_temp")
        rainfall = st.number_input("Annual Rainfall (mm)", key="rainfall")
        extreme_events = st.text_area("Extreme Events History", key="extreme_events")
        rcp_scenario = [st.number_input(f"RCP Year {year}", min_value=-10.0, max_value=10.0, value=0.0, key=f"rcp_{year}") for year in range(2020,2051)]
        vulnerability_notes = st.text_area("Vulnerability & Climate Risk Notes", key="vulnerability_notes")
        climate_budget = st.number_input("Climate Budget Allocation (₹ Crores/year)", min_value=0,key="climate_budget")
        staff_count = st.number_input("No. of Staff Dedicated to Climate & Sustainability", min_value=0,key="staff_count")
        training_programs = st.text_area("Capacity Building / Training Programs", key="training_programs")
        existing_policies = st.text_area("Existing Policies / Regulations", key="existing_policies")
        sectoral_targets = st.text_area("Sectoral GHG Mitigation Targets & Goals", key="sectoral_targets")
        implementation_actions = st.text_area("Planned Actions & Implementation Strategies", key="implementation_actions")
        mer_tracking_plan = st.text_area("MER Plan", key="mer_tracking_plan")
        
        if st.button("Save Climate Data"):
            st.session_state.city_data[city_select]["Climate_Data"] = {
                "Avg_Temp":avg_temp,"Rainfall":rainfall,"Extreme_Events":extreme_events,
                "RCP":rcp_scenario,"Vulnerability_Notes":vulnerability_notes,
                "Climate_Budget":climate_budget,"Staff_Count":staff_count,
                "Training_Programs":training_programs,"Existing_Policies":existing_policies,
                "Sectoral_Targets":sectoral_targets,"Implementation_Actions":implementation_actions,
                "MER_Plan":mer_tracking_plan
            }
            st.success("Climate Data saved!")

        if st.button("Submit CAP and Go to GHG Inventory"):
            st.success(f"CAP for {city_select} submitted successfully!")
            st.session_state.current_page = "GHG Inventory"  # Example page redirection

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
