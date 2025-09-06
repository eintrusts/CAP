# mahacap.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
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
# Cities & Districts (Updated)
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

# Apply city name mapping safely
st.session_state.data["City Name"] = st.session_state.data["City Name"].apply(
    lambda x: cities_districts[x] if pd.notna(x) and x in cities_districts else x
)

# Remove Raigad Council (if exists)
st.session_state.data = st.session_state.data[~st.session_state.data["City Name"].str.contains("Raigad Council", case=False, na=False)]

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
# HOME PAGE
# ---------------------------
if menu == "Home":
    st.header("Maharashtra's Net Zero Journey")
    st.markdown("Climate Action Plan Dashboard")

    df = st.session_state.data.copy()

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

    # Reported GHG
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
            title_font_size=18
        )
        st.plotly_chart(fig_reported, use_container_width=True)

    # Estimated GHG
    if not df.empty and "Population" in df.columns:
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce").fillna(0)
        EMISSION_FACTOR = 2.5
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
            title_font_size=18
        )
        st.plotly_chart(fig_estimated, use_container_width=True)

# ---------------------------
# CITY INFORMATION PAGE
# ---------------------------
elif menu == "City Information":
    st.header("City-wise CAP & Department Info")
    df = st.session_state.data.copy()

    if not df.empty:
        st.dataframe(df, use_container_width=True)

        if PDF_AVAILABLE and st.button("Download PDF Report"):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Maharashtra City-wise CAP Report", styles['Title']))
            elements.append(Spacer(1, 12))

            data_for_pdf = [df.columns.tolist()] + df.values.tolist()
            t = Table(data_for_pdf)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3E6BE6")),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
            ]))
            elements.append(t)
            doc.build(elements)
            buffer.seek(0)
            st.download_button(
                label="Download PDF",
                data=buffer,
                file_name="Maharashtra_CAP_Report.pdf",
                mime="application/pdf"
            )

# ---------------------------
# ADMIN PAGE
# ---------------------------
elif menu == "Admin":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.subheader("Admin Panel")
        st.markdown("Upload updated city CAP data here:")
        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file:
            try:
                df_new = pd.read_csv(uploaded_file)
                st.session_state.data = df_new
                df_new.to_csv(DATA_FILE, index=False)
                st.success("Data uploaded and saved successfully!")
            except Exception as e:
                st.error(f"Error uploading file: {e}")

# ---------------------------
# CAP PREPARATION PAGE
# ---------------------------
elif menu == "CAP Preparation":
    st.header("CAP Preparation")
    st.info("Edit city-wise CAP data below and save changes.")

    df = st.session_state.data.copy()

    if df.empty:
        st.warning("No data available. Upload data via Admin panel first.")
    else:
        # Select city to edit
        city_list = df["City Name"].unique().tolist()
        selected_city = st.selectbox("Select City to Edit", city_list)

        if selected_city:
            city_idx = df.index[df["City Name"] == selected_city][0]
            city_data = df.loc[city_idx]

            st.markdown(f"### Editing: {selected_city} ({city_data['District']})")

            cap_status = st.selectbox(
                "CAP Status",
                ["Not Started", "In Progress", "Completed"],
                index=["Not Started", "In Progress", "Completed"].index(
                    city_data.get("CAP Status", "Not Started")
                )
            )

            population = st.text_input(
                "Population",
                value=str(int(city_data.get("Population", 0))) if pd.notna(city_data.get("Population", 0)) else ""
            )

            ghg_emissions = st.text_input(
                "GHG Emissions (tCO2e)",
                value=str(city_data.get("GHG Emissions", 0))
            )

            dept_exists = st.selectbox(
                "Environment Department Exists?",
                ["Yes", "No"],
                index=0 if city_data.get("Environment Department Exist", "Yes") == "Yes" else 1
            )

            dept_name = st.text_input("Department Name", value=city_data.get("Department Name", ""))
            head_name = st.text_input("Head Name", value=city_data.get("Head Name", ""))
            dept_email = st.text_input("Department Email", value=city_data.get("Department Email", ""))

            if st.button("Save Changes"):
                # Update dataframe
                st.session_state.data.at[city_idx, "CAP Status"] = cap_status
                st.session_state.data.at[city_idx, "Population"] = int(population) if population.isdigit() else 0
                st.session_state.data.at[city_idx, "GHG Emissions"] = float(ghg_emissions) if ghg_emissions.replace(".", "", 1).isdigit() else 0
                st.session_state.data.at[city_idx, "Environment Department Exist"] = dept_exists
                st.session_state.data.at[city_idx, "Department Name"] = dept_name
                st.session_state.data.at[city_idx, "Head Name"] = head_name
                st.session_state.data.at[city_idx, "Department Email"] = dept_email

                # Save to CSV
                st.session_state.data.to_csv(DATA_FILE, index=False)
                st.success(f"Data for {selected_city} updated successfully!")
