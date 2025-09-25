import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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
    [data-testid="stSidebar"] {
        background-color: #111827; 
        color: #ffffff; 
        width: 260px; 
        min-width: 260px; 
        max-width: 260px;
    }
    [data-testid="stSidebarCollapseButton"] {display: none;}

    .sidebar-logo {
        display: flex; 
        justify-content: center; 
        align-items: center; 
        margin: 20px 0 30px 0;
    }
    .sidebar-logo img {
        max-width: 190px; 
        height: auto; 
        border-radius: 15px;
    }

    /* Menu Button Styling */
    .menu-btn, .menu-btn-active {
        display: block;
        width: 100%;
        height: 48px;                   /* fixed height for all buttons */
        padding: 12px 20px;
        margin: 8px 0;
        background: transparent;
        color: #e5e7eb;
        text-align: left;               /* left aligned text */
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
        box-shadow: 0 0 12px rgba(239, 68, 68, 0.6);
    }

    /* Active button */
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
    .sidebar-footer strong {color: #ffffff;}
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
    st.markdown("<style>body {background-color: #121212; color: #ffffff;}</style>", unsafe_allow_html=True)
    st.header("Climate Action Plan Dashboard")
    st.caption("Maharashtra's Net Zero Journey")

    status_counts = {"Not Started": 0, "In Progress": 0, "Completed": 0}
    for c in cities:
        status = st.session_state.city_data.get(c, {}).get("CAP_Status", "Not Started")
        if status in status_counts:
            status_counts[status] += 1

    total_cities = 43
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

    # Maharashtra Basic Info
    st.markdown("### Maharashtra Basic Information")
    total_population = sum([st.session_state.city_data.get(c, {}).get("Population", {}).get("Total", 0) for c in cities])
    total_area = sum([st.session_state.city_data.get(c, {}).get("Area", 0) for c in cities])
    dept_name = dept_email = website = cap_link = cap_status = ""
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

    # --- GHG by Sector ---
    ghg_sectors = ["Energy", "Transport", "Waste", "Water"]
    ghg_values = [sum([st.session_state.city_data.get(c, {}).get("GHG", {}).get(s, 0) for c in cities]) for s in ghg_sectors]
    fig = px.bar(x=ghg_sectors, y=ghg_values, labels={"x":"Sector","y":"tCO2e"}, title="Maharashtra GHG Emissions by Sector", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # --- RCP Scenarios ---
    st.markdown("### RCP Scenario Projections")
    years = list(range(2020,2051))
    rcp_45 = np.linspace(1.0,2.0,len(years))
    rcp_60 = np.linspace(1.0,2.5,len(years))
    rcp_85 = np.linspace(1.0,3.5,len(years))
    fig2 = px.line(x=years, y=rcp_45, labels={"x":"Year","y":"Temp Rise (°C)"}, title="Projected RCP Scenarios", template="plotly_dark")
    fig2.add_scatter(x=years, y=rcp_60, mode="lines", name="RCP 6.0")
    fig2.add_scatter(x=years, y=rcp_85, mode="lines", name="RCP 8.5")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"<div style='position:fixed; bottom:10px; centre:10px; color:#aaaaaa; font-size:12px;'>Last Updated: {last_updated()}</div>", unsafe_allow_html=True)

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

    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False
    if 'current_admin_tab' not in st.session_state:
        st.session_state.current_admin_tab = 0
    if 'last_selected_city' not in st.session_state:
        st.session_state.last_selected_city = "Maharashtra"
    if 'city_data' not in st.session_state:
        st.session_state.city_data = {}

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

    st.header("Admin Panel")
    admin_tabs = st.tabs(["Add/Update City","Generate CAP","GHG Inventory","Logout"])

    # --- Add/Update City ---
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


    # --- Generate CAP  ---
    with admin_tabs[1]:
        st.subheader("Generate CAP")
        city_select = st.selectbox("Select City for CAP", cities, key="cap_city_select")
        city_info = st.session_state.city_data.get(city_select, {})

        cap_tabs = st.tabs([
            "1. Basic Info","2. Energy & Buildings","3. Green Cover & Biodiversity",
            "4. Sustainable Mobility","5. Water Resources","6. Waste Management","7. Climate Data"
        ])

        # -------------------- 1. Basic Info --------------------
    with cap_tabs[0]:
        population = st.number_input("Population", min_value=0, value=city_info.get("Basic Info",{}).get("Population",0), key="cap_pop")
        area = st.number_input("Area (sq km)", min_value=0, value=city_info.get("Basic Info",{}).get("Area",0), key="cap_area")
        gdp = st.number_input("GDP (₹ Crores)", min_value=0, value=city_info.get("Basic Info",{}).get("GDP",0), key="cap_gdp")
        density = st.number_input("Population Density (people/km²)", min_value=0, key="cap_density")
        climate_zone = st.text_input("Climate Zone", value=city_info.get("Basic Info",{}).get("Climate_Zone",""), key="cap_climate_zone")
        admin_structure = st.text_input("Administrative Structure", value=city_info.get("Basic Info",{}).get("Admin",""), key="cap_admin_structure")
        cap_status_options = ["Not Started","In Progress","Completed"]
        cap_status_form_default = city_info.get("CAP_Status","Not Started")
        if cap_status_form_default not in cap_status_options:
            cap_status_form_default = "Not Started"
        cap_status_form = st.selectbox("CAP Status", cap_status_options, index=cap_status_options.index(cap_status_form_default), key="cap_status_form")
        last_updated_input = st.date_input("Last Updated", datetime.date.today(), key="cap_last_updated")

        # New comprehensive fields
        population_5yr = st.number_input("Projected Population in 5 years", min_value=0, key="pop_5yr")
        cap_targets = st.text_area("Overall CAP Goals / Targets (aligned with SDGs/NDCs)", key="cap_targets")
        cap_mer_indicators = st.text_area("Overall MER Indicators for CAP", key="cap_mer")
        basic_budget_allocation = st.number_input("Budget Allocation for CAP Implementation (₹ Crores)", min_value=0, key="cap_budget")
        upload_basic = st.file_uploader("Upload any supporting documents for Basic Info", type=["pdf","xlsx","docx"], key="upload_basic")

        if st.button("Save Basic Info Data"):
            st.session_state.city_data[city_select]["Basic Info"] = {
                "Population":population,"Area":area,"GDP":gdp,"Density":density,"Climate_Zone":climate_zone,
                "Admin":admin_structure,"CAP_Status":cap_status_form,"Last_Updated":last_updated_input.strftime("%B %Y"),
                "Population_5yr":population_5yr,"CAP_Targets":cap_targets,"MER_Indicators":cap_mer_indicators,
                "Budget":basic_budget_allocation,"Upload":upload_basic
            }
            st.success("Basic Info saved successfully!")

    # -------------------- 2. Energy & Buildings --------------------
    with cap_tabs[1]:
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

        # New comprehensive fields
        energy_emission_target = st.number_input("Energy Sector Emission Reduction Target (%)", min_value=0, max_value=100, key="energy_target")
        energy_action_plan = st.text_area("Detailed Action Plan (timeline, responsible dept.)", key="energy_action_plan")
        energy_implementation_strategy = st.text_area("Implementation Strategy (short/mid/long-term)", key="energy_strategy")
        energy_budget = st.number_input("Energy Sector Budget Allocation (₹ Crores)", min_value=0, key="energy_budget")
        energy_mer_indicators = st.text_area("MER Indicators for Energy & Buildings", key="energy_mer")
        upload_energy = st.file_uploader("Upload supporting documents for Energy & Buildings", type=["pdf","xlsx","docx"], key="upload_energy")

        if st.button("Save Energy & Buildings Data"):
            st.session_state.city_data[city_select]["Energy_Buildings"] = {
                "Residential":res_energy,"Commercial":com_energy,"Industrial":ind_energy,"Renewable_Share":renewable_share,
                "EE_Buildings":ee_buildings,"Street_Lighting_Type":street_lighting_type,"Street_Lighting_Coverage":street_lighting_coverage,
                "Fuel_Types":fuel_types,"Public_Building_Energy":public_building_energy,"Green_Policy":green_policy,
                "Emission_Target":energy_emission_target,"Action_Plan":energy_action_plan,"Implementation_Strategy":energy_implementation_strategy,
                "Budget":energy_budget,"MER_Indicators":energy_mer_indicators,"Upload":upload_energy
            }
            st.success("Energy & Buildings data saved successfully!")

    # -------------------- 3. Green Cover & Biodiversity --------------------
    with cap_tabs[2]:
        green_cover_area = st.number_input("Total Green Cover Area (ha)", min_value=0, key="green_cover")
        tree_density = st.number_input("Tree Density (trees/km²)", min_value=0, key="tree_density")
        protected_areas = st.number_input("Protected Areas (ha)", min_value=0, key="protected_areas")
        biodiversity_programs = st.text_area("Biodiversity Programs", key="biodiversity_programs")
        urban_forests = st.number_input("Urban Forests Area (ha)", min_value=0, key="urban_forests")

        # New comprehensive fields
        green_cover_target = st.number_input("Target Increase in Green Cover (%)", min_value=0, max_value=100, key="green_target")
        urban_forest_plan = st.text_area("Urban Forests & Biodiversity Improvement Actions", key="urban_forest_plan")
        green_implementation_strategy = st.text_area("Implementation Strategy (short/mid/long-term)", key="green_strategy")
        green_budget = st.number_input("Budget Allocation for Green Cover & Biodiversity (₹ Crores)", min_value=0, key="green_budget")
        green_mer_indicators = st.text_area("MER Indicators for Green Cover & Biodiversity", key="green_mer")
        upload_green = st.file_uploader("Upload supporting documents for Green Cover & Biodiversity", type=["pdf","xlsx","docx"], key="upload_green")

        if st.button("Save Green Cover & Biodiversity Data"):
            st.session_state.city_data[city_select]["Green_Biodiversity"] = {
                "Green_Cover":green_cover_area,"Tree_Density":tree_density,"Protected_Areas":protected_areas,
                "Programs":biodiversity_programs,"Urban_Forests":urban_forests,
                "Target":green_cover_target,"Urban_Forest_Plan":urban_forest_plan,"Implementation_Strategy":green_implementation_strategy,
                "Budget":green_budget,"MER_Indicators":green_mer_indicators,"Upload":upload_green
            }
            st.success("Green Cover & Biodiversity data saved successfully!")

    # -------------------- 4. Sustainable Mobility --------------------
    with cap_tabs[3]:
        public_transport_coverage = st.slider("Public Transport Coverage (%)",0,100,0, key="pt_coverage")
        non_motorized_infra = st.slider("Non-Motorized Infrastructure (%)",0,100,0, key="nmi")
        ev_charging_stations = st.number_input("No. of EV Charging Stations", min_value=0, key="ev_stations")
        veh_emissions = st.number_input("Average Vehicle Emissions (gCO2/km)", min_value=0, key="veh_emissions")
        smart_transport_projects = st.text_area("Smart Transport Projects", key="smart_projects")

        # New comprehensive fields
        transport_emission_target = st.number_input("Transport Sector Emission Reduction Target (%)", min_value=0, max_value=100, key="transport_target")
        mobility_action_plan = st.text_area("Transport & Mobility Action Plan (timeline, responsible dept.)", key="mobility_action_plan")
        mobility_strategy = st.text_area("Implementation Strategy (short/mid/long-term)", key="mobility_strategy")
        mobility_budget = st.number_input("Budget Allocation for Transport & Mobility (₹ Crores)", min_value=0, key="mobility_budget")
        mobility_mer_indicators = st.text_area("MER Indicators for Sustainable Mobility", key="mobility_mer")
        upload_mobility = st.file_uploader("Upload supporting documents for Sustainable Mobility", type=["pdf","xlsx","docx"], key="upload_mobility")

        if st.button("Save Sustainable Mobility Data"):
            st.session_state.city_data[city_select]["Mobility"] = {
                "Public_Transport":public_transport_coverage,"Non_Motorized":non_motorized_infra,
                "EV_Stations":ev_charging_stations,"Vehicle_Emissions":veh_emissions,"Smart_Projects":smart_transport_projects,
                "Emission_Target":transport_emission_target,"Action_Plan":mobility_action_plan,
                "Implementation_Strategy":mobility_strategy,"Budget":mobility_budget,"MER_Indicators":mobility_mer_indicators,
                "Upload":upload_mobility
            }
            st.success("Sustainable Mobility data saved successfully!")

    # -------------------- 5. Water Resources --------------------
    with cap_tabs[4]:
        water_consumption = st.number_input("Total Water Consumption (ML/year)", min_value=0, key="water_cons")
        wastewater_treatment = st.slider("Wastewater Treatment Coverage (%)",0,100,0, key="wwt")
        rainwater_harvesting = st.selectbox("Rainwater Harvesting Implementation", ["Yes","No"], key="rwh")
        leakage_ratio = st.slider("Water Leakage Ratio (%)",0,100,0, key="leakage_ratio")
        water_policy = st.text_area("Water Management Policies", key="water_policy")

        # New comprehensive fields
        water_emission_target = st.number_input("Water Sector Emission Reduction Target (%)", min_value=0, max_value=100, key="water_target")
        water_action_plan = st.text_area("Water Sector Action Plan (timeline, responsible dept.)", key="water_action_plan")
        water_strategy = st.text_area("Implementation Strategy (short/mid/long-term)", key="water_strategy")
        water_budget = st.number_input("Budget Allocation for Water Sector (₹ Crores)", min_value=0, key="water_budget")
        water_mer_indicators = st.text_area("MER Indicators for Water Resources", key="water_mer")
        upload_water = st.file_uploader("Upload supporting documents for Water Resources", type=["pdf","xlsx","docx"], key="upload_water")

        if st.button("Save Water Resources Data"):
            st.session_state.city_data[city_select]["Water"] = {
                "Consumption":water_consumption,"WWT":wastewater_treatment,"RWH":rainwater_harvesting,
                "Leakage":leakage_ratio,"Policy":water_policy,
                "Emission_Target":water_emission_target,"Action_Plan":water_action_plan,
                "Implementation_Strategy":water_strategy,"Budget":water_budget,"MER_Indicators":water_mer_indicators,
                "Upload":upload_water
            }
            st.success("Water Resources data saved successfully!")

    # -------------------- 6. Waste Management --------------------
    with cap_tabs[5]:
        total_waste = st.number_input("Total Waste Generated (t/year)", min_value=0, key="total_waste")
        waste_recycled = st.slider("Waste Recycled (%)",0,100,0, key="waste_recycled")
        waste_treatment_facilities = st.number_input("No. of Treatment Facilities", min_value=0, key="waste_facilities")
        composting_infra = st.selectbox("Composting Infrastructure", ["Yes","No"], key="composting")
        hazardous_waste_policy = st.text_area("Hazardous Waste Policy", key="hazardous_policy")

        # New comprehensive fields
        waste_emission_target = st.number_input("Waste Sector Emission Reduction Target (%)", min_value=0, max_value=100, key="waste_target")
        waste_action_plan = st.text_area("Waste Management Action Plan (timeline, responsible dept.)", key="waste_action_plan")
        waste_strategy = st.text_area("Implementation Strategy (short/mid/long-term)", key="waste_strategy")
        waste_budget = st.number_input("Budget Allocation for Waste Sector (₹ Crores)", min_value=0, key="waste_budget")
        waste_mer_indicators = st.text_area("MER Indicators for Waste Management", key="waste_mer")
        upload_waste = st.file_uploader("Upload supporting documents for Waste Management", type=["pdf","xlsx","docx"], key="upload_waste")

        if st.button("Save Waste Management Data"):
            st.session_state.city_data[city_select]["Waste"] = {
                "Total":total_waste,"Recycled":waste_recycled,"Facilities":waste_treatment_facilities,
                "Composting":composting_infra,"Hazardous":hazardous_waste_policy,
                "Emission_Target":waste_emission_target,"Action_Plan":waste_action_plan,
                "Implementation_Strategy":waste_strategy,"Budget":waste_budget,"MER_Indicators":waste_mer_indicators,
                "Upload":upload_waste
            }
            st.success("Waste Management data saved successfully!")

    # -------------------- 7. Climate Data --------------------
    with cap_tabs[6]:
        avg_temp = st.number_input("Average Temperature (°C)", key="avg_temp")
        rainfall = st.number_input("Annual Rainfall (mm)", key="rainfall")
        extreme_events = st.text_area("Extreme Events History", key="extreme_events")
        rcp_scenario = [st.number_input(f"RCP Year {year}", min_value=-10.0, max_value=10.0, value=0.0, key=f"rcp_{year}") for year in range(2020,2051)]

        # New comprehensive fields
        sectoral_vulnerability = st.text_area("Sectoral Vulnerability & Risk Assessment", key="sectoral_risk")
        adaptation_plan = st.text_area("Adaptation & Resilience Action Plan", key="adaptation_plan")
        climate_finance_allocation = st.number_input("Climate Budget Allocation (₹ Crores)", min_value=0, key="climate_budget")
        climate_mer_indicators = st.text_area("MER Indicators for Climate Adaptation", key="climate_mer")
        upload_climate = st.file_uploader("Upload supporting documents for Climate Data", type=["pdf","xlsx","docx"], key="upload_climate")

        if st.button("Save Climate Data"):
            st.session_state.city_data[city_select]["Climate_Data"] = {
                "Avg_Temp":avg_temp,"Rainfall":rainfall,"Extreme_Events":extreme_events,"RCP":rcp_scenario,
                "Vulnerability":sectoral_vulnerability,"Adaptation":adaptation_plan,
                "Budget":climate_finance_allocation,"MER_Indicators":climate_mer_indicators,"Upload":upload_climate
            }
            st.success("Climate Data saved successfully!")

        # Final Submit Button -> redirect to GHG Inventory page
        if st.button("Submit All CAP Data"):
            st.success("All CAP data submitted successfully! Redirecting to GHG Inventory page...")
            st.experimental_set_query_params(page="ghg_inventory")
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
