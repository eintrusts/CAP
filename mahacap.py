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
    "Mumbai": "Mumbai", "Kalyan-Dombivli": "Thane", "Mira-Bhayandar": "Thane",
    "Navi Mumbai": "Thane", "Bhiwandi": "Thane", "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane", "Vasai-Virar": "Thane", "Thane": "Thane",
    "Badlapur Council": "Thane", "Pune": "Pune", "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad", "Raigad Council": "Raigad", "Malegaon": "Nashik",
    "Nashik": "Nashik", "Nandurbar Council": "Nandurbar", "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon", "Dhule": "Dhule", "Ahmednagar": "Ahmednagar",
    "Aurangabad": "Aurangabad", "Jalna": "Jalna", "Beed Council": "Beed",
    "Satara Council": "Satara", "Sangli-Miraj-Kupwad": "Sangli", "Kolhapur": "Kolhapur",
    "Ichalkaranji": "Kolhapur", "Solapur": "Solapur", "Barshi Council": "Solapur",
    "Nanded-Waghala": "Nanded", "Yawatmal Council": "Yawatmal", "Osmanabad Council": "Osmanabad",
    "Latur": "Latur", "Udgir Council": "Latur", "Akola": "Akola",
    "Parbhani Council": "Parbhani", "Amravati": "Amravati", "Achalpur Council": "Amravati",
    "Wardha Council": "Wardha", "Hinganghat Council": "Wardha", "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur", "Gondia Council": "Gondia"
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

meta_cols = ["City Name", "District", "Population", "ULB Category", "CAP Status",
             "GHG Emissions", "Per Capita GHG (tCO2e/person)",
             "Environment Department Exist", "Department Name",
             "Head Name", "Department Email"]
cap_cols = []

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# ---------------------------
# Helper Functions
# ---------------------------
def format_indian_number(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        s, *d = str(round(num,2)).split(".")
        n = ""
        while len(s) > 3:
            n = "," + s[-2:] + n
            s = s[:-2]
        n = s + n
        return n + ("." + d[0] if d else "")
    except:
        return str(num)

def safe_get(row, col, default="—"):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else val
    except:
        return default

def calculate_ghg(df):
    """Automatically calculate GHG emissions based on population"""
    df = df.copy()
    if "Population" in df.columns:
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce").fillna(0)
        df["GHG Emissions"] = df["Population"] * 1.5  # 1.5 tCO2e per capita
        df["Per Capita GHG (tCO2e/person)"] = df["GHG Emissions"] / df["Population"].replace({0:1})
    else:
        df["GHG Emissions"] = 0
        df["Per Capita GHG (tCO2e/person)"] = 0
    return df

# ---------------------------
# CSS
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
for btn, name in [("Home","Home"), ("City Dashboard","City Dashboard"), ("Admin Panel","Admin Panel")]:
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
if menu=="Home":
    st.header("Maharashtra Climate Action Plan Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")
    df = calculate_ghg(st.session_state.data)

    total_cities = len(cities_districts)
    reporting_cities = df.shape[0]
    completed_caps = df[df["CAP Status"].str.lower()=="completed"].shape[0] if "CAP Status" in df.columns else 0
    total_ghg = df["GHG Emissions"].sum()
    avg_per_capita = df["Per Capita GHG (tCO2e/person)"].mean() if not df.empty else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Cities Selected", f"{total_cities}")
    col2.metric("Cities Reporting", f"{reporting_cities}")
    col3.metric("CAPs Completed", f"{completed_caps}")
    col4.metric("Total GHG Emissions", f"{format_indian_number(total_ghg)} tCO₂e")
    col5.metric("Average Per Capita GHG", f"{avg_per_capita:.4f} tCO₂e/person")

    # Total GHG Bar Chart
    if not df.empty:
        df_sorted = df.sort_values("GHG Emissions", ascending=False)
        fig_total = px.bar(df_sorted, x="City Name", y="GHG Emissions",
                           text=df_sorted["GHG Emissions"].map(format_indian_number),
                           title="City-wise Total GHG Emissions (tCO₂e)",
                           color="City Name", color_discrete_sequence=px.colors.qualitative.Bold)
        fig_total.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig_total, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu=="City Dashboard":
    st.header("City Dashboard")
    df_meta = calculate_ghg(st.session_state.data)
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()
    cities_for_select = list(cities_districts.keys())
    city = st.selectbox("Select City", cities_for_select)
    meta_row = df_meta[df_meta["City Name"]==city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None

    st.subheader(f"{city} — Overview")
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row,'District')}")
        st.write(f"**Population (2011):** {format_indian_number(safe_get(meta_row,'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row,'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row,'CAP Status')}")
        st.write(f"**Total GHG Emissions:** {format_indian_number(meta_row['GHG Emissions'])} tCO₂e")
        st.write(f"**Per Capita GHG:** {meta_row['Per Capita GHG (tCO2e/person)']:.4f} tCO₂e/person")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu=="Admin Panel":
    st.header("Admin Panel")
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.subheader("Upload / Update CAP Data")
        with st.form("admin_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            pop = st.number_input("Population", min_value=0, value=100000, step=1000)
            cap_status = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"])
            dept_exist = st.selectbox("Environment Department Exist?", ["Yes","No"])
            dept_name = st.text_input("Department Name")
            head_name = st.text_input("Department Head Name")
            dept_email = st.text_input("Department Email")
            submit_admin = st.form_submit_button("Save CAP Metadata")
            if submit_admin:
                ghg_val = pop * 1.5
                per_capita = ghg_val / (pop if pop>0 else 1)
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "—"),
                    "Population": pop,
                    "CAP Status": cap_status,
                    "GHG Emissions": ghg_val,
                    "Per Capita GHG (tCO2e/person)": per_capita,
                    "Environment Department Exist": dept_exist,
                    "Department Name": dept_name,
                    "Head Name": head_name,
                    "Department Email": dept_email
                }
                df_meta = st.session_state.data
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"]==city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE,index=False)
                st.success(f"{city} data updated successfully!")

# ---------------------------
# CAP Preparation Page
# ---------------------------
elif menu=="CAP Preparation":
    st.header("CAP Preparation — Sectoral Emissions Input")
    if not st.session_state.authenticated:
        admin_login()
    else:
        with st.form("cap_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            st.markdown("### Enter Emissions (tCO2e) for each sector")
            sectors = ["Energy","Transport","Buildings","Industry","Water","Waste","Urban Green / Other"]
            cap_values = {}
            for sec in sectors:
                cap_values[sec] = st.number_input(f"{sec} Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)
            file_upload = st.file_uploader("Attach verification file (optional)", type=["pdf","xlsx","csv"])
            submit_cap = st.form_submit_button("Save CAP Data")
            if submit_cap:
                new_row = {"City Name":city}
                for sec,val in cap_values.items():
                    new_row[f"{sec} Emissions (tCO2e)"] = val
                df_cap = st.session_state.cap_data
                if not df_cap.empty and city in df_cap["City Name"].values:
                    for k,v in new_row.items():
                        df_cap.loc[df_cap["City Name"]==city,k] = v
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE,index=False)
                st.session_state.last_updated = datetime.now()
                st.success(f"CAP data for {city} saved successfully!")
