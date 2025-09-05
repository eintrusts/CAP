# mahacap_pro.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

# ---------------------------
# PDF generation
# ---------------------------
try:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

# ---------------------------
# Page config
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin password
# ---------------------------
ADMIN_PASSWORD = "eintrust2025"

# ---------------------------
# Data files
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
# Session state init
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# ---------------------------
# Load city meta
# ---------------------------
if os.path.exists(DATA_FILE):
    try:
        st.session_state.data = pd.read_csv(DATA_FILE)
    except:
        st.session_state.data = pd.DataFrame(columns=[
            "City Name", "District", "Population", "ULB Category", "CAP Status",
            "GHG Emissions", "Environment Department Exist", "Department Name",
            "Head Name", "Department Email"
        ])
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Department Email"
    ])

# ---------------------------
# Load CAP raw data
# ---------------------------
if os.path.exists(CAP_DATA_FILE):
    try:
        st.session_state.cap_data = pd.read_csv(CAP_DATA_FILE)
    except:
        st.session_state.cap_data = pd.DataFrame()
else:
    st.session_state.cap_data = pd.DataFrame()

# ---------------------------
# Helper functions
# ---------------------------
def format_population(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        return "{:,}".format(int(num))
    except:
        return str(num)

def safe_get(df_row, col, default="—"):
    try:
        val = df_row.get(col, default)
        if pd.isna(val):
            return default
        return val
    except:
        return default

# ---------------------------
# Dark mode CSS (ChatGPT style)
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color: #0B0C0E; color: #E6E6E6;}
[data-testid="stSidebar"] {background-color: #0B0C0E; color: #E6E6E6;}
.stButton>button {background-color: #3E6BE6 !important; color: #FFFFFF !important; border-radius: 6px; height: 40px; font-size:14px;}
.stButton>button:hover {background-color: #2C4EBB !important;}
input, textarea, select {background-color: #141518 !important; color:#E6E6E6 !important; border-color:#3E6BE6 !important;}
.stDataFrame, .stTable {color:#E6E6E6;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Admin login
# ---------------------------
def admin_login():
    with st.form("login_form", clear_on_submit=False):
        pw = st.text_input("Enter Admin Password", type="password", key="admin_pw")
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
st.sidebar.image("https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true", use_container_width=True)
st.sidebar.markdown("---")
if st.sidebar.button("Home"): st.session_state.menu="Home"
if st.sidebar.button("City Dashboard"): st.session_state.menu="City Dashboard"
if st.sidebar.button("Admin Panel"): st.session_state.menu="Admin Panel"
if st.session_state.authenticated:
    if st.sidebar.button("CAP Preparation"): st.session_state.menu="CAP Preparation"
st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu=="Home":
    st.header("Maharashtra Climate Action Plan Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")
    df = st.session_state.data.copy()

    total_selected = len(cities_districts)
    reporting = df.shape[0]
    completed = 0
    if "CAP Status" in df.columns:
        completed = df[df["CAP Status"].str.lower() == "completed"].shape[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Cities Selected", f"{total_selected}")
    col2.metric("Cities Reporting", f"{reporting}")
    col3.metric("CAPs Completed", f"{completed}")

    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig = px.bar(df.sort_values("GHG Emissions", ascending=False),
                     x="City Name", y="GHG Emissions",
                     title="City-level GHG (tCO2e)",
                     color_discrete_sequence=["#3E6BE6"])
        fig.update_layout(plot_bgcolor="#0B0C0E", paper_bgcolor="#0B0C0E", font_color="#E6E6E6")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu=="City Dashboard":
    st.header("City Dashboard")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()

    city = st.selectbox("Select City", list(cities_districts.keys()))
    meta_row = df_meta[df_meta["City Name"]==city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None
    st.subheader(f"{city} — Overview")
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row,'District')}")
        st.write(f"**Population (2011):** {format_population(safe_get(meta_row,'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row,'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row,'CAP Status')}")
    else:
        st.write(f"**District:** {cities_districts.get(city,'—')}")

    if not df_cap.empty and city in df_cap["City Name"].values:
        cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
        sector_cols = [c for c in cap_row.index if c.endswith("Emissions (tCO2e)")]
        sectors = {c.replace(" Emissions (tCO2e)",""): float(cap_row[c]) for c in sector_cols}
        if sectors:
            chart_df = pd.DataFrame({"Sector":list(sectors.keys()),"Emissions":list(sectors.values())})
            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0B0C0E", paper_bgcolor="#0B0C0E", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)
            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions", title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0B0C0E", paper_bgcolor="#0B0C0E", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)
            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d:d["Emissions"].map(lambda v:f"{v:,.2f}")))
    else:
        st.info("No CAP raw data for this city. Go to 'CAP Preparation' (admin) to input raw data.")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu=="Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("Admin Panel — City Metadata")
        df_meta = st.session_state.data.copy()
        cities_list = list(cities_districts.keys())
        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list)
            district = st.text_input("District", value=cities_districts.get(city_name,""), disabled=True)
            population = st.number_input("Population (2011)", min_value=0, step=1000, value=int(df_meta[df_meta["City Name"]==city_name]["Population"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else 0, format="%d")
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            ghg = st.text_input("GHG Emissions (tCO2e)", value=str(df_meta[df_meta["City Name"]==city_name]["GHG Emissions"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes","No"])
            dept_name = st.text_input("Department Name", value=str(df_meta[df_meta["City Name"]==city_name]["Department Name"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")
            head_name = st.text_input("Head Name", value=str(df_meta[df_meta["City Name"]==city_name]["Head Name"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")
            dept_email = st.text_input("Department Email", value=str(df_meta[df_meta["City Name"]==city_name]["Department Email"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")
            submit = st.form_submit_button("Save")
            if submit:
                row_index = df_meta.index[df_meta["City Name"]==city_name].tolist()
                if row_index:
                    idx = row_index[0]
                    df_meta.loc[idx,"Population"]=population
                    df_meta.loc[idx,"ULB Category"]=ulb_cat
                    df_meta.loc[idx,"CAP Status"]=cap_status
                    df_meta.loc[idx,"GHG Emissions"]=ghg
                    df_meta.loc[idx,"Environment Department Exist"]=env_exist
                    df_meta.loc[idx,"Department Name"]=dept_name
                    df_meta.loc[idx,"Head Name"]=head_name
                    df_meta.loc[idx,"Department Email"]=dept_email
                else:
                    df_meta = pd.concat([df_meta,pd.DataFrame([{
                        "City Name": city_name, "District": district, "Population": population,
                        "ULB Category": ulb_cat, "CAP Status": cap_status,
                        "GHG Emissions": ghg, "Environment Department Exist": env_exist,
                        "Department Name": dept_name, "Head Name": head_name,
                        "Department Email": dept_email
                    }])], ignore_index=True)
                df_meta.to_csv(DATA_FILE,index=False)
                st.success("City metadata updated successfully.")
        st.subheader("All City Metadata")
        st.dataframe(df_meta, use_container_width=True)

# ---------------------------
# CAP Preparation
# ---------------------------
elif menu=="CAP Preparation":
    st.header("CAP Raw Data Entry (Admin Only)")
    if not st.session_state.authenticated:
        admin_login()
    else:
        df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()
        st.markdown("Upload CSV with columns: City Name, Sector1 Emissions (tCO2e), Sector2 Emissions (tCO2e), etc.")
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file is not None:
            try:
                df_new = pd.read_csv(uploaded_file)
                st.session_state.cap_data = df_new
                df_new.to_csv(CAP_DATA_FILE,index=False)
                st.success("CAP raw data uploaded successfully.")
            except Exception as e:
                st.error(f"Error reading CSV: {e}")

        if not df_cap.empty:
            st.subheader("Existing CAP Data")
            st.dataframe(df_cap, use_container_width=True)

            if PDF_AVAILABLE:
                def download_pdf(df):
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4)
                    elements = []
                    style = getSampleStyleSheet()
                    elements.append(Paragraph("Maharashtra CAP Raw Data", style['Title']))
                    elements.append(Spacer(1,12))
                    table_data = [df.columns.tolist()] + df.values.tolist()
                    t=Table(table_data, repeatRows=1)
                    t.setStyle(TableStyle([
                        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                        ('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('GRID',(0,0),(-1,-1),0.5,colors.grey)
                    ]))
                    elements.append(t)
                    doc.build(elements)
                    buffer.seek(0)
                    return buffer
                pdf_buf = download_pdf(df_cap)
                st.download_button("Download CAP Data as PDF", pdf_buf, file_name="CAP_Raw_Data.pdf", mime="application/pdf")
