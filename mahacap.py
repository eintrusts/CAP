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
    "Latur": "Latur", "Udgir Council": "Latur", "Akola": "Akola", "Parbhani Council": "Parbhani",
    "Amravati": "Amravati", "Achalpur Council": "Amravati", "Wardha Council": "Wardha",
    "Hinganghat Council": "Wardha", "Nagpur": "Nagpur", "Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State Initialization
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None
if "selected_city" not in st.session_state:
    st.session_state.selected_city = None

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
cap_cols = []

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# ---------------------------
# Helper Functions
# ---------------------------
def format_indian(num):
    try:
        return "{:,}".format(int(num))
    except:
        return str(num)

def safe_get(row, col, default="—"):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else val
    except:
        return default

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

# Always visible
for btn, name in [("Home", "Home"), ("City Dashboard", "City Dashboard"), ("Admin Panel", "Admin Panel")]:
    if st.sidebar.button(btn):
        st.session_state.menu = name

# Admin only
if st.session_state.authenticated:
    for btn, name in [("CAP Preparation", "CAP Preparation"), 
                      ("GHG Inventory", "GHG Inventory"), 
                      ("Actions", "Actions")]:
        if st.sidebar.button(btn):
            st.session_state.menu = name

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
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
        fig2 = px.bar(df.sort_values("GHG Emissions", ascending=False), 
                      x="City Name", y="GHG Emissions", 
                      title="City-level GHG (tCO2e)", text="GHG Emissions",
                      color_discrete_sequence=px.colors.qualitative.Plotly)
        fig2.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    st.header("City Dashboard")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()
    city = st.selectbox("Select City", list(cities_districts.keys()))
    st.subheader(f"{city} — Overview")
    meta_row = df_meta[df_meta["City Name"]==city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row,'District')}")
        st.write(f"**Population (2011):** {format_indian(safe_get(meta_row,'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row,'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row,'CAP Status')}")
    else:
        st.write(f"**District:** {cities_districts.get(city,'—')}")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
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
# CAP Preparation Page
# ---------------------------
elif menu == "CAP Preparation":
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
                st.session_state.selected_city = city  # store selected city
                st.session_state.last_updated = datetime.now()
                st.success(f"CAP data for {city} saved successfully!")
                st.session_state.menu = "GHG Inventory"
                st.experimental_rerun()

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu == "GHG Inventory":
    st.header("GHG Inventory")
    city = st.session_state.selected_city
    if not city:
        st.warning("Please select or enter a city in CAP Preparation first.")
    else:
        df_cap = st.session_state.cap_data
        if not df_cap.empty and city in df_cap["City Name"].values:
            cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
            sector_cols = [c for c in cap_row.index if c.endswith("Emissions (tCO2e)")]
            sectors = {c.replace(" Emissions (tCO2e)",""): max(float(cap_row[c]),0) for c in sector_cols}

            # Metrics
            total_emissions = sum(sectors.values())
            col1, col2 = st.columns(2)
            col1.metric("Total GHG Emissions (tCO2e)", f"{format_indian(total_emissions)}")
            col2.metric("City", city)

            # Pie chart
            chart_df = pd.DataFrame({"Sector": list(sectors.keys()), "Emissions": list(sectors.values())})
            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Bar chart
            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions", 
                             title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v: f"{v:,.2f}")))

            # Last Updated
            last_mod = st.session_state.last_updated or datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
            st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")

            # Buttons
            col1, col2 = st.columns(2)
            with col1:
                if PDF_AVAILABLE:
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
                else:
                    st.warning("PDF generation not available. Install reportlab library.")

            with col2:
                if st.button("Suggested Actions"):
                    st.session_state.menu = "Actions"
                    st.experimental_rerun()
        else:
            st.warning(f"No CAP data found for {city}. Please enter sectoral emissions first.")

# ---------------------------
# Actions Page
# ---------------------------
elif menu == "Actions":
    st.header("Suggested Actions to Achieve Net Zero by 2050")
    city = st.session_state.selected_city
    if not city:
        st.warning("Please select or enter a city first in CAP Preparation.")
    else:
        df_cap = st.session_state.cap_data
        if not df_cap.empty and city in df_cap["City Name"].values:
            cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
            sectors = [c.replace(" Emissions (tCO2e)","") for c in cap_row.index if c.endswith("Emissions (tCO2e)")]
            
            # Budget recommendation example (can be adjusted)
            st.subheader("Recommended Budget Allocation")
            budget_dict = {sec: f"{5+5*idx}%" for idx, sec in enumerate(sectors)}
            st.table(pd.DataFrame(list(budget_dict.items()), columns=["Sector","Recommended Budget %"]))

            # Suggested actions example
            timeframes = ["Short-term (by 2030)", "Mid-term (by 2040)", "Long-term (by 2050)"]
            actions_dict = {sec: {tf: [f"{sec} action {i+1} ({tf})" for i in range(10)] for tf in timeframes} for sec in sectors}

            for sec in sectors:
                st.markdown(f"### {sec}")
                for tf in timeframes:
                    st.markdown(f"**{tf}**")
                    for act in actions_dict[sec][tf]:
                        st.write(f"- {act}")

            # Download CAP (Inventory + Actions)
            if PDF_AVAILABLE:
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                elements.append(Paragraph(f"{city} — Climate Action Plan Summary", styles["Title"]))
                elements.append(Spacer(1,12))

                # Inventory
                data_inv = [["Sector","Emissions (tCO2e)"]]+[[s,f"{float(cap_row[f'{s} Emissions (tCO2e)']):,.2f}"] for s in sectors]
                t_inv = Table(data_inv, hAlign="LEFT")
                t_inv.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                                           ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                                           ('GRID',(0,0),(-1,-1),0.5,colors.white)]))
                elements.append(Paragraph("GHG Inventory", styles["Heading2"]))
                elements.append(t_inv)
                elements.append(Spacer(1,12))

                # Actions
                for sec in sectors:
                    elements.append(Paragraph(sec, styles["Heading3"]))
                    for tf in timeframes:
                        elements.append(Paragraph(tf, styles["Heading4"]))
                        for act in actions_dict[sec][tf]:
                            elements.append(Paragraph(f"- {act}", styles["Normal"]))
                        elements.append(Spacer(1,6))

                doc.build(elements)
                buffer.seek(0)
                st.download_button("Download CAP (PDF)", buffer, file_name=f"{city}_CAP_Summary.pdf", mime="application/pdf")
            else:
                st.warning("PDF generation not available. Install reportlab library.")
        else:
            st.warning(f"No CAP data found for {city}. Please enter sectoral emissions first.")
