# mahacap.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

# PDF support
try:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except:
    PDF_AVAILABLE = False

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Maharashtra CAP Dashboard",
    page_icon="🌍",
    layout="wide"
)

# ---------------------------
# Admin Password
# ---------------------------
ADMIN_PASSWORD = "eintrust2025"

# ---------------------------
# Data Files
# ---------------------------
DATA_FILE = "cities_data.csv"
CAP_DATA_FILE = "cap_raw_data.csv"

# ---------------------------
# Cities & Districts
# ---------------------------
cities_districts = {
    "Mumbai": "Mumbai",
    "Kalyan-Dombivli": "Thane",
    "Mira-Bhayandar": "Thane",
    "Navi Mumbai": "Thane",
    "Bhiwandi-Nizampur": "Thane",
    "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane",
    "Vasai-Virar": "Palghar",
    "Thane": "Thane",
    "Badlapur Council": "Thane",
    "Pune": "Pune",
    "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad",
    "Malegaon": "Nashik",
    "Nashik": "Nashik",
    "Nandurbar Council": "Nandurbar",
    "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon",
    "Dhule": "Dhule",
    "Ahilyanagar": "Ahilyanagar",
    "Chh. Sambhajinagar": "Chh. Sambhajinagar",
    "Jalna": "Jalna",
    "Beed Council": "Beed",
    "Satara Council": "Satara",
    "Sangli-Miraj-Kupwad": "Sangli",
    "Kolhapur": "Kolhapur",
    "Ichalkaranji": "Kolhapur",
    "Solapur": "Solapur",
    "Barshi Council": "Solapur",
    "Nanded-Waghala": "Nanded",
    "Yawatmal Council": "Yawatmal",
    "Dharashiv Council": "Dharashiv",
    "Latur": "Latur",
    "Udgir Council": "Latur",
    "Akola": "Akola",
    "Parbhani Council": "Parbhani",
    "Amravati": "Amravati",
    "Achalpur Council": "Amravati",
    "Wardha Council": "Wardha",
    "Hinganghat Council": "Wardha",
    "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# ---------------------------
# Load Data
# ---------------------------
def load_csv(file_path, default_cols):
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except:
            return pd.DataFrame(columns=default_cols)
    else:
        return pd.DataFrame(columns=default_cols)

meta_cols = [
    "City Name", "District", "Population", "ULB Category",
    "CAP Status", "GHG Emissions", "Environment Department Exist",
    "Department Name", "Head Name", "Department Email"
]
cap_cols = []

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# Ensure city names in session data match updated cities_districts keys
st.session_state.data["City Name"] = st.session_state.data["City Name"].apply(
    lambda x: cities_districts.get(x, x)
)

# ---------------------------
# Helper Functions
# ---------------------------
def format_population(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        return "{:,}".format(int(num))
    except:
        return str(num)

def safe_get(row, col, default="—"):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else val
    except:
        return default

# Indian Number Format
def format_indian_number(num):
    try:
        num = int(num)
        s = str(num)[::-1]
        lst = []
        lst.append(s[:3])
        s = s[3:]
        while s:
            lst.append(s[:2])
            s = s[2:]
        return ','.join(lst)[::-1]
    except:
        return str(num)

# ---------------------------
# Dark / Professional CSS
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color: #0f0f10; color: #E6E6E6;}
[data-testid="stSidebar"] {background-color: #141518; color: #E6E6E6;}
.stButton>button {background-color:#3E6BE6; color:#FFFFFF; border-radius:8px; height:40px;}
.stButton>button:hover {background-color:#2e50b0;}
[data-testid="stMetricValue"] {color:#3E6BE6; font-weight:700;}
.stExpander>div>div>div>div {background-color:#141518; color:#E6E6E6;}
input, textarea, select {background-color:#141518; color:#E6E6E6; border-color:#3E6BE6;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Admin Login
# ---------------------------
def admin_login():
    with st.form("login_form", clear_on_submit=False):
        pw = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if pw == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Admin login successful")
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image(
    "https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

for btn, name in [("Home", "Home"), ("City Information", "City Information"), ("Admin", "Admin")]:
    if st.sidebar.button(btn):
        st.session_state.menu = name

if st.session_state.authenticated and st.sidebar.button("CAP Preparation"):
    st.session_state.menu = "CAP Preparation"

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra's Net Zero Journey")
    st.markdown("Climate Action Plan Dashboard")

    df = st.session_state.data.copy()

    # --- CAP Status Summary ---
    if not df.empty and "CAP Status" in df.columns:
        not_started = df[df["CAP Status"].str.lower() == "not started"].shape[0]
        in_progress = df[df["CAP Status"].str.lower() == "in progress"].shape[0]
        completed = df[df["CAP Status"].str.lower() == "completed"].shape[0]
        total_status = not_started + in_progress + completed

        st.markdown("### 📊 CAP Status Overview")
        c1, c2, c3, c4 = st.columns(4)

        block_style = """
            background-color:#141518; 
            padding:20px; 
            border-radius:12px; 
            text-align:center; 
        """
        title_style = "color:#E6E6E6; margin:0;"
        value_style = "font-size:28px; font-weight:bold; color:#3E6BE6;"

        c1.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Not Started</h3><p style='{value_style}'>{not_started}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>In Progress</h3><p style='{value_style}'>{in_progress}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Completed</h3><p style='{value_style}'>{completed}</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Total</h3><p style='{value_style}'>{total_status}</p></div>", unsafe_allow_html=True)

    # --- City-level Reported GHG Emissions ---
    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig_reported = px.bar(
            df.sort_values("GHG Emissions", ascending=False),
            x="City Name",
            y="GHG Emissions",
            title="City-level Reported GHG Emissions (tCO2e)",
            text=df["GHG Emissions"].apply(format_indian_number),
            color_discrete_sequence=["#3E6BE6"]
        )
        fig_reported.update_layout(
            plot_bgcolor="#0f0f10",
            paper_bgcolor="#0f0f10",
            font_color="#E6E6E6",
            title_font_size=18,
            xaxis_title="City",
            yaxis_title="GHG Emissions (tCO2e)"
        )
        st.plotly_chart(fig_reported, use_container_width=True)

    # --- Estimated GHG Emissions (Population x Factor) ---
    if not df.empty and "Population" in df.columns:
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce").fillna(0)

        EMISSION_FACTOR = 2.5  # tCO2e per person/year
        df["Estimated GHG Emissions"] = df["Population"] * EMISSION_FACTOR

        fig_estimated = px.bar(
            df.sort_values("Estimated GHG Emissions", ascending=False),
            x="City Name",
            y="Estimated GHG Emissions",
            title=f"Estimated GHG Emissions (tCO2e) — based on {EMISSION_FACTOR} tCO2e/person",
            text=df["Estimated GHG Emissions"].apply(format_indian_number),
            color_discrete_sequence=["#E67E22"]
        )
        fig_estimated.update_layout(
            plot_bgcolor="#0f0f10",
            paper_bgcolor="#0f0f10",
            font_color="#E6E6E6",
            title_font_size=18,
            xaxis_title="City",
            yaxis_title="Estimated GHG Emissions (tCO2e)"
        )
        st.plotly_chart(fig_estimated, use_container_width=True)

# ---------------------------
# City Information Page
# ---------------------------
elif menu == "City Information":
    st.header("City Information")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()

    cities_for_select = list(cities_districts.keys())
    city = st.selectbox("Select City", cities_for_select)

    meta_row = df_meta[df_meta["City Name"] == city].iloc[0] if not df_meta[df_meta["City Name"] == city].empty else None
    if meta_row is not None:
        st.markdown(f"**District:** {safe_get(meta_row, 'District')}")
        st.markdown(f"**Population:** {format_indian_number(safe_get(meta_row, 'Population'))}")
        st.markdown(f"**ULB Category:** {safe_get(meta_row, 'ULB Category')}")
        st.markdown(f"**CAP Status:** {safe_get(meta_row, 'CAP Status')}")
        st.markdown(f"**GHG Emissions (tCO2e):** {format_indian_number(safe_get(meta_row, 'GHG Emissions'))}")
        st.markdown(f"**Environment Dept Exist:** {safe_get(meta_row, 'Environment Department Exist')}")
        st.markdown(f"**Department Name:** {safe_get(meta_row, 'Department Name')}")
        st.markdown(f"**Head Name:** {safe_get(meta_row, 'Head Name')}")
        st.markdown(f"**Department Email:** {safe_get(meta_row, 'Department Email')}")

# ---------------------------
# Admin Page
# ---------------------------
elif menu == "Admin":
    st.header("Admin Panel")
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.markdown("✅ Admin authenticated")
        st.markdown("**Upload / Update City Data**")
        uploaded_file = st.file_uploader("Upload CSV with City Data", type="csv")
        if uploaded_file is not None:
            try:
                df_new = pd.read_csv(uploaded_file)
                # Ensure city names match updated dictionary
                df_new["City Name"] = df_new["City Name"].apply(lambda x: cities_districts.get(x, x))
                st.session_state.data = df_new
                st.success("City data updated successfully!")
            except Exception as e:
                st.error(f"Failed to upload: {e}")

# ---------------------------
# CAP Preparation Page
# ---------------------------
elif menu == "CAP Preparation" and st.session_state.authenticated:
    st.header("CAP Preparation")
    st.markdown("Prepare and update Climate Action Plans for selected cities")

    if not st.session_state.data.empty:
        city = st.selectbox("Select City", list(cities_districts.keys()))
        city_row_index = st.session_state.data.index[st.session_state.data["City Name"] == city].tolist()
        if city_row_index:
            idx = city_row_index[0]
            st.text_input("CAP Status", value=st.session_state.data.at[idx, "CAP Status"], key=f"cap_status_{city}")
            st.text_area("GHG Emissions Notes", value=st.session_state.data.at[idx, "GHG Emissions"], key=f"ghg_{city}")
            if st.button("Update CAP Data", key=f"update_{city}"):
                st.session_state.data.at[idx, "CAP Status"] = st.session_state[f"cap_status_{city}"]
                st.session_state.data.at[idx, "GHG Emissions"] = st.session_state[f"ghg_{city}"]
                st.success(f"CAP data updated for {city}")

