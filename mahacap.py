# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os, io
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
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

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
    "Mumbai": "Mumbai","Kalyan-Dombivli": "Thane","Mira-Bhayandar": "Thane","Navi Mumbai": "Thane",
    "Bhiwandi": "Thane","Ulhasnagar": "Thane","Ambernath Council": "Thane","Vasai-Virar": "Thane",
    "Thane": "Thane","Badlapur Council": "Thane","Pune": "Pune","Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad","Raigad Council": "Raigad","Malegaon": "Nashik","Nashik": "Nashik",
    "Nandurbar Council": "Nandurbar","Bhusawal Council": "Jalgaon","Jalgaon": "Jalgaon",
    "Dhule": "Dhule","Ahmednagar": "Ahmednagar","Aurangabad": "Aurangabad","Jalna": "Jalna",
    "Beed Council": "Beed","Satara Council": "Satara","Sangli-Miraj-Kupwad": "Sangli",
    "Kolhapur": "Kolhapur","Ichalkaranji": "Kolhapur","Solapur": "Solapur","Barshi Council": "Solapur",
    "Nanded-Waghala": "Nanded","Yawatmal Council": "Yawatmal","Osmanabad Council": "Osmanabad",
    "Latur": "Latur","Udgir Council": "Latur","Akola": "Akola","Parbhani Council": "Parbhani",
    "Amravati": "Amravati","Achalpur Council": "Amravati","Wardha Council": "Wardha",
    "Hinganghat Council": "Wardha","Nagpur": "Nagpur","Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State
# ---------------------------
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "menu" not in st.session_state: st.session_state.menu = "Home"
if "last_updated" not in st.session_state: st.session_state.last_updated = None
if "selected_city" not in st.session_state: st.session_state.selected_city = None

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

meta_cols = ["City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
             "Environment Department Exist", "Department Name", "Head Name", "Department Email"]
cap_cols = ["City Name","Energy Emissions","Transport Emissions","Buildings Emissions","Industry Emissions",
            "Water Emissions","Waste Emissions","Urban Green / Other Emissions"]

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# ---------------------------
# Helper Functions
# ---------------------------
def format_number(num):
    try:
        x = float(num)
        s = f"{int(x):,}"
        if x>999:
            s = f"{int(x):,}".replace(",",":")
            s = s[::-1]
            parts = [s[:3]] + [s[i:i+2] for i in range(3,len(s),2)]
            s = ",".join(parts)[::-1].replace(":","")
        return s
    except:
        return str(num)

def safe_get(row, col, default="—"):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else val
    except:
        return default

def generate_ghg_pdf(city, sectors):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"{city} — GHG Inventory Report", styles["Title"]))
    elements.append(Spacer(1,12))
    data = [["Sector","Emissions (tCO2e)"]]+[[s,f"{v:,.2f}"] for s,v in sectors.items()]
    t = Table(data, hAlign="LEFT")
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                           ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                           ('GRID',(0,0),(-1,-1),0.5,colors.white)]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generate_cap_pdf(city, sectors, actions):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"{city} — Climate Action Plan Summary", styles["Title"]))
    elements.append(Spacer(1,12))
    # GHG Inventory Table
    elements.append(Paragraph("GHG Inventory", styles["Heading2"]))
    data = [["Sector","Emissions (tCO2e)"]]+[[s,f"{v:,.2f}"] for s,v in sectors.items()]
    t = Table(data,hAlign="LEFT")
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                           ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                           ('GRID',(0,0),(-1,-1),0.5,colors.white)]))
    elements.append(t)
    elements.append(Spacer(1,12))
    # Suggested Actions
    elements.append(Paragraph("Suggested Actions", styles["Heading2"]))
    for term, sector_actions in actions.items():
        elements.append(Paragraph(term, styles["Heading3"]))
        for sec, acts in sector_actions.items():
            elements.append(Paragraph(f"{sec}:", styles["Heading4"]))
            for act in acts:
                elements.append(Paragraph(f"- {act}", styles["Normal"]))
        elements.append(Spacer(1,6))
    doc.build(elements)
    buffer.seek(0)
    return buffer

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
            if pw==ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Admin login successful")
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar
# ---------------------------
st.sidebar.image("https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true", use_container_width=True)
st.sidebar.markdown("---")

# Always visible
for btn, name in [("Home","Home"), ("City Dashboard","City Dashboard"), ("Admin Panel","Admin Panel")]:
    if st.sidebar.button(btn):
        st.session_state.menu = name

# Admin only
if st.session_state.authenticated:
    for btn, name in [("CAP Preparation","CAP Preparation"),
                      ("GHG Inventory","GHG Inventory"),
                      ("Actions","Actions")]:
        if st.sidebar.button(btn):
            st.session_state.menu = name

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# HOME PAGE
# ---------------------------
if menu=="Home":
    st.header("Maharashtra Climate Action Plan Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")
    df = st.session_state.data.copy()
    total_selected = len(cities_districts)
    reporting = df.shape[0]
    completed = df[df["CAP Status"].str.lower()=="completed"].shape[0] if "CAP Status" in df.columns else 0
    col1,col2,col3 = st.columns(3)
    col1.metric("Cities Selected", f"{total_selected}")
    col2.metric("Cities Reporting", f"{reporting}")
    col3.metric("CAPs Completed", f"{completed}")
    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig2 = px.bar(df.sort_values("GHG Emissions", ascending=False), x="City Name", y="GHG Emissions",
                      title="City-level GHG (tCO2e)", text="GHG Emissions", color_discrete_sequence=["#3E6BE6"])
        fig2.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# CITY DASHBOARD
# ---------------------------
elif menu=="City Dashboard":
    st.header("City Dashboard")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()
    cities_for_select = list(cities_districts.keys())
    city = st.selectbox("Select City", cities_for_select)
    meta_row = df_meta[df_meta["City Name"]==city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None
    st.subheader(f"{city} — Overview")
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row,'District')}")
        st.write(f"**Population (2011):** {format_number(safe_get(meta_row,'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row,'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row,'CAP Status')}")
    else:
        st.write(f"**District:** {cities_districts.get(city,'—')}")

# ---------------------------
# ADMIN PANEL
# ---------------------------
elif menu=="Admin Panel":
    st.header("Admin Panel")
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.subheader("Upload / Update CAP Data")
        with st.form("admin_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            cap_status = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"])
            ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)
            dept_exist = st.selectbox("Environment Department Exist?", ["Yes","No"])
            dept_name = st.text_input("Department Name")
            head_name = st.text_input("Department Head Name")
            dept_email = st.text_input("Department Email")
            submit_admin = st.form_submit_button("Save CAP Metadata")
            if submit_admin:
                new_row = {"City Name":city,"District":cities_districts.get(city,"—"),
                           "CAP Status":cap_status,"GHG Emissions":ghg_val,
                           "Environment Department Exist":dept_exist,
                           "Department Name":dept_name,"Head Name":head_name,
                           "Department Email":dept_email}
                df_meta = st.session_state.data
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"]==city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE,index=False)
                st.success(f"{city} data updated successfully!")

# ---------------------------
# CAP PREPARATION PAGE
# ---------------------------
elif menu=="CAP Preparation":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("CAP Preparation — Sectoral Emissions Input & Raw Data Questions")
        with st.form("cap_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            st.markdown("### Enter Emissions (tCO2e) for each sector")
            sectors = ["Energy","Transport","Buildings","Industry","Water","Waste","Urban Green / Other"]
            cap_values = {}
            for sec in sectors:
                cap_values[sec] = st.number_input(f"{sec} Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)
            st.markdown("### Raw Data Questions (for Indian cities)")
            raw_questions = {
                "Population":"Total population (2011 census)",
                "ULB Category":"Urban Local Body Category",
                "Energy Consumption (MWh)":"Annual energy consumption",
                "Transport Vehicles":"Total registered vehicles",
                "Water Usage (MLD)":"Total water supplied per day",
                "Waste Generated (Tonnes)":"Total municipal solid waste generated",
                "Urban Green Area (Ha)":"Total urban green/parks area"
            }
            raw_data = {}
            for q in raw_questions:
                raw_data[q] = st.text_input(f"{q} ({raw_questions[q]})")
            file_upload = st.file_uploader("Attach verification file (optional)", type=["pdf","xlsx","csv"])
            submit_cap = st.form_submit_button("Save CAP Data")
            if submit_cap:
                new_row = {"City Name":city}
                for sec,val in cap_values.items():
                    new_row[f"{sec} Emissions"] = val
                df_cap = st.session_state.cap_data
                if not df_cap.empty and city in df_cap["City Name"].values:
                    for k,v in new_row.items():
                        df_cap.loc[df_cap["City Name"]==city,k] = v
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE,index=False)
                st.session_state.selected_city = city
                st.success(f"CAP data for {city} saved successfully!")
                st.experimental_rerun()

# ---------------------------
# GHG INVENTORY PAGE
# ---------------------------
elif menu=="GHG Inventory":
    if not st.session_state.authenticated:
        admin_login()
    else:
        city = st.session_state.selected_city
        if city is None:
            st.warning("Please select a city in CAP Preparation first.")
        else:
            st.header(f"{city} — GHG Inventory")
            df_cap = st.session_state.cap_data
            cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
            sectors = {s: max(float(cap_row[f"{s} Emissions"]),0) for s in ["Energy","Transport","Buildings","Industry","Water","Waste","Urban Green / Other"]}
            # Metrics
            st.metric("Total GHG Emissions (tCO2e)", f"{format_number(sum(sectors.values()))}")
            # Charts
            chart_df = pd.DataFrame({"Sector":list(sectors.keys()),"Emissions":list(sectors.values())})
            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)
            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions", title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)
            # Download PDF
            if PDF_AVAILABLE:
                buffer = generate_ghg_pdf(city,sectors)
                st.download_button("Download GHG Inventory PDF", buffer, file_name=f"{city}_GHG_Report.pdf", mime="application/pdf")
            else:
                st.warning("PDF generation not available. Install reportlab library.")
            # Actions button
            if st.button("Suggested Actions"):
                st.session_state.menu = "Actions"
                st.experimental_rerun()

# ---------------------------
# ACTIONS PAGE
# ---------------------------
elif menu=="Actions":
    if not st.session_state.authenticated:
        admin_login()
    else:
        city = st.session_state.selected_city
        if city is None:
            st.warning("Please select a city in CAP Preparation first.")
        else:
            st.header(f"{city} — Suggested Actions to Achieve Net Zero by 2050")
            # Sample Actions (10 per sector)
            sectors = ["Energy","Transport","Buildings","Industry","Water","Waste","Urban Green / Other"]
            terms = ["Short Term (by 2030)","Mid Term (by 2040)","Long Term (by 2050)"]
            actions = {}
            for term in terms:
                actions[term] = {s:[f"Action {i+1} for {s}" for i in range(10)] for s in sectors}
            budget = {"Short Term":10,"Mid Term":15,"Long Term":20} # Sample %
            st.markdown("### Recommended Budget Allocation")
            for term,val in budget.items():
                st.write(f"{term}: {val}% of city budget")
            # Display actions
            for term, sector_actions in actions.items():
                st.subheader(term)
                for sec, acts in sector_actions.items():
                    st.markdown(f"**{sec}**")
                    for act in acts:
                        st.markdown(f"- {act}")
            # Download CAP PDF
            if PDF_AVAILABLE:
                buffer = generate_cap_pdf(city,sectors,actions)
                st.download_button("Download CAP PDF", buffer, file_name=f"{city}_CAP_Summary.pdf", mime="application/pdf")
            else:
                st.warning("PDF generation not available. Install reportlab library.")
