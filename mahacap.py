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
    "Bhiwandi": "Thane",
    "Ulhasnagar": "Thane",
    "Ambernath Council": "Thane",
    "Vasai-Virar": "Thane",
    "Thane": "Thane",
    "Badlapur Council": "Thane",
    "Pune": "Pune",
    "Pimpri-Chinchwad": "Pune",
    "Panvel": "Raigad",
    "Raigad Council": "Raigad",
    "Malegaon": "Nashik",
    "Nashik": "Nashik",
    "Nandurbar Council": "Nandurbar",
    "Bhusawal Council": "Jalgaon",
    "Jalgaon": "Jalgaon",
    "Dhule": "Dhule",
    "Ahmednagar": "Ahmednagar",
    "Aurangabad": "Aurangabad",
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
    "Osmanabad Council": "Osmanabad",
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
if "selected_city" not in st.session_state:
    st.session_state.selected_city = ""

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

meta_cols = ["City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions", "Environment Department Exist", "Department Name", "Head Name", "Department Email"]
cap_cols = []
st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# ---------------------------
# Helper Functions
# ---------------------------
def format_population(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        num = int(num)
        # Indian number format
        s = str(num)[::-1]
        parts = [s[:3]]
        s = s[3:]
        while s:
            parts.append(s[:2])
            s = s[2:]
        return ','.join(parts)[::-1]
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
        num = float(num)
        if num < 1000:
            return f"{num:,.2f}"
        s = str(int(num))[::-1]
        parts = [s[:3]]
        s = s[3:]
        while s:
            parts.append(s[:2])
            s = s[2:]
        return ','.join(parts)[::-1]
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

# Always visible buttons
for btn, name in [("Home","Home"), ("City Dashboard","City Dashboard"), ("Admin Panel","Admin Panel")]:
    if st.sidebar.button(btn):
        st.session_state.menu = name

# Admin-only buttons
if st.session_state.authenticated:
    for btn, name in [("CAP Preparation","CAP Preparation"), ("GHG Inventory","GHG Inventory"), ("Actions","Actions")]:
        if st.sidebar.button(btn):
            st.session_state.menu = name

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
    completed = df[df["CAP Status"].str.lower()=="completed"].shape[0] if "CAP Status" in df.columns else 0
    col1, col2, col3 = st.columns(3)
    col1.metric("Cities Selected", f"{total_selected}")
    col2.metric("Cities Reporting", f"{reporting}")
    col3.metric("CAPs Completed", f"{completed}")
    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig2 = px.bar(df.sort_values("GHG Emissions", ascending=False), x="City Name", y="GHG Emissions", title="City-level GHG (tCO2e)", text="GHG Emissions", color_discrete_sequence=["#3E6BE6"])
        fig2.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard
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
        st.write(f"**Population (2011):** {format_population(safe_get(meta_row,'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row,'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row,'CAP Status')}")
    else:
        st.write(f"**District:** {cities_districts.get(city,'—')}")

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
            cap_status = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"])
            ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)
            dept_exist = st.selectbox("Environment Department Exist?", ["Yes","No"])
            dept_name = st.text_input("Department Name")
            head_name = st.text_input("Department Head Name")
            dept_email = st.text_input("Department Email")
            submit_admin = st.form_submit_button("Save CAP Metadata")
            if submit_admin:
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "—"),
                    "CAP Status": cap_status,
                    "GHG Emissions": ghg_val,
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
# CAP Preparation
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
                st.session_state.menu = "GHG Inventory"
                st.session_state.selected_city = city
                st.experimental_rerun()

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu=="GHG Inventory":
    st.header("GHG Inventory — City Overview")
    if not st.session_state.authenticated:
        admin_login()
    else:
        df_cap = st.session_state.cap_data
        cities_for_select = list(cities_districts.keys())
        city = st.selectbox("Select City", cities_for_select)
        if not df_cap.empty and city in df_cap["City Name"].values:
            cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
            sector_cols = [c for c in cap_row.index if c.endswith("Emissions (tCO2e)")]
            sectors = {c.replace(" Emissions (tCO2e)",""): max(float(cap_row[c]),0) for c in sector_cols}
            
            total_emissions = sum(sectors.values())
            
            col1, col2 = st.columns(2)
            col1.metric("Total GHG Emissions (tCO2e)", format_indian_number(total_emissions))
            col2.metric("Number of Sectors Reported", len(sectors))
            
            chart_df = pd.DataFrame({"Sector":list(sectors.keys()),"Emissions":list(sectors.values())})
            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)
            
            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions",
                             title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)
            
            st.write("### Sector-wise Emissions")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v:f"{v:,.2f}")))
            
            last_mod = st.session_state.last_updated or datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
            st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")
            
            col1b, col2b = st.columns(2)
            if PDF_AVAILABLE:
                with col1b:
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4)
                    elements = []
                    styles = getSampleStyleSheet()
                    elements.append(Paragraph(f"{city} — GHG Inventory Report", styles["Title"]))
                    elements.append(Spacer(1,12))
                    data = [["Sector","Emissions (tCO2e)"]]+[[s,f"{v:,.2f}"] for s,v in sectors.items()]
                    t = Table(data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                        ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                        ('GRID',(0,0),(-1,-1),0.5,colors.white)
                    ]))
                    elements.append(t)
                    doc.build(elements)
                    buffer.seek(0)
                    st.download_button("Download GHG Inventory (PDF)", buffer, file_name=f"{city}_GHG_Report.pdf", mime="application/pdf")
            if col2b.button("Suggested Actions"):
                st.session_state.menu = "Actions"
                st.session_state.selected_city = city
                st.experimental_rerun()

# ---------------------------
# Actions Page
# ---------------------------
elif menu=="Actions":
    st.header("Suggested Actions — Achieving Net Zero by 2050")
    if not st.session_state.authenticated:
        admin_login()
    else:
        city = st.session_state.get("selected_city","")
        if city=="":
            st.warning("Please select a city first in GHG Inventory page.")
        else:
            st.subheader(f"{city} — CAP Suggested Actions")
            
            sectors = ["Energy","Transport","Buildings","Industry","Water","Waste","Urban Green / Other"]
            budget_percent = {"Energy":25,"Transport":20,"Buildings":15,"Industry":15,"Water":5,"Waste":10,"Urban Green / Other":10}
            short_term_actions = {s:[f"{s} Short-term action {i+1}" for i in range(10)] for s in sectors}
            mid_term_actions = {s:[f"{s} Mid-term action {i+1}" for i in range(10)] for s in sectors}
            long_term_actions = {s:[f"{s} Long-term action {i+1}" for i in range(10)] for s in sectors}
            
            st.write("### Recommended Budget Allocation (%) per sector")
            st.table(pd.DataFrame(list(budget_percent.items()),columns=["Sector","Recommended Budget %"]))
            
            st.write("### Short-term Actions (by 2030)")
            for s in sectors:
                st.write(f"**{s}**")
                for act in short_term_actions[s]:
                    st.markdown(f"- {act}")
            
            st.write("### Mid-term Actions (by 2040)")
            for s in sectors:
                st.write(f"**{s}**")
                for act in mid_term_actions[s]:
                    st.markdown(f"- {act}")
            
            st.write("### Long-term Actions (by 2050)")
            for s in sectors:
                st.write(f"**{s}**")
                for act in long_term_actions[s]:
                    st.markdown(f"- {act}")
            
            if PDF_AVAILABLE:
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                elements.append(Paragraph(f"{city} — Climate Action Plan Summary", styles["Title"]))
                elements.append(Spacer(1,12))
                
                df_cap = st.session_state.cap_data
                cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
                sector_cols = [c for c in cap_row.index if c.endswith("Emissions (tCO2e)")]
                sectors_em = {c.replace(" Emissions (tCO2e)",""): max(float(cap_row[c]),0) for c in sector_cols}
                elements.append(Paragraph("GHG Inventory", styles["Heading2"]))
                data = [["Sector","Emissions (tCO2e)"]]+[[s,f"{v:,.2f}"] for s,v in sectors_em.items()]
                t = Table(data, hAlign="LEFT")
                t.setStyle(TableStyle([
                    ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                    ('GRID',(0,0),(-1,-1),0.5,colors.white)
                ]))
                elements.append(t)
                elements.append(Spacer(1,12))
                
                for term_name, actions in [("Short-term (by 2030)", short_term_actions),
                                           ("Mid-term (by 2040)", mid_term_actions),
                                           ("Long-term (by 2050)", long_term_actions)]:
                    elements.append(Paragraph(term_name, styles["Heading2"]))
                    for s, acts in actions.items():
                        elements.append(Paragraph(f"<b>{s}</b>", styles["Heading3"]))
                        for act in acts:
                            elements.append(Paragraph(f"- {act}", styles["Normal"]))
                        elements.append(Spacer(1,6))
                
                doc.build(elements)
                buffer.seek(0)
                st.download_button("Download CAP (PDF)", buffer, file_name=f"{city}_CAP_Summary.pdf", mime="application/pdf")
            else:
                st.warning("PDF generation not available. Install reportlab library.")
