# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu=="GHG Inventory":
    st.header("GHG Inventory")
    if not st.session_state.authenticated:
        admin_login()
    else:
        df_cap = st.session_state.cap_data
        if df_cap.empty:
            st.warning("No CAP data available. Please fill CAP data first.")
        else:
            city = st.selectbox("Select City", list(cities_districts.keys()))
            row = df_cap[df_cap["City Name"]==city].iloc[0] if city in df_cap["City Name"].values else None
            if row is not None:
                st.metric("Total GHG Emissions (tCO2e)", format_population(row["GHG Emissions"]))
                sectors = ["Energy","Transport","Buildings","Industry","Water","Waste","Urban Green / Other"]
                chart_df = pd.DataFrame({"Sector": sectors,
                                         "Emissions": [row.get(f"{s} Emissions",0) for s in sectors]})
                fig_pie = px.pie(chart_df, names="Sector", values="Emissions",
                                 title="Sector-wise Emissions (tCO2e)")
                fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
                st.plotly_chart(fig_pie, use_container_width=True)
                fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions",
                                 title="Sector-wise Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
                fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
                st.plotly_chart(fig_bar, use_container_width=True)
                st.write("### Emissions Table")
                st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v:f"{v:,.2f}")))
                
                # Download GHG Inventory PDF
                if PDF_AVAILABLE:
                    with st.form("pdf_ghg_form"):
                        submit_pdf = st.form_submit_button("Download GHG Inventory (PDF)")
                        if submit_pdf:
                            buffer = io.BytesIO()
                            doc = SimpleDocTemplate(buffer, pagesize=A4)
                            elements = []
                            styles = getSampleStyleSheet()
                            elements.append(Paragraph(f"{city} — GHG Inventory", styles["Title"]))
                            elements.append(Spacer(1,12))
                            data = [["Sector","Emissions (tCO2e)"]] + [[s,f"{v:,.2f}"] for s,v in zip(chart_df["Sector"], chart_df["Emissions"])]
                            t = Table(data, hAlign="LEFT")
                            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                                                   ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                                                   ('GRID',(0,0),(-1,-1),0.5,colors.white)]))
                            elements.append(t)
                            doc.build(elements)
                            buffer.seek(0)
                            st.download_button("Download GHG Inventory PDF", buffer,
                                               file_name=f"{city}_GHG_Inventory.pdf", mime="application/pdf")
                else:
                    st.warning("PDF generation not available. Install reportlab library.")
                
                if st.button("Actions →"):
                    st.session_state.selected_city = city
                    st.session_state.menu = "Actions"
                    st.experimental_rerun()
            else:
                st.warning("No data available for selected city.")

# ---------------------------
# Actions Page
# ---------------------------
elif menu=="Actions":
    st.header("Suggested Actions for Net Zero")
    if not st.session_state.authenticated:
        admin_login()
    else:
        city = st.session_state.get("selected_city", list(cities_districts.keys())[0])
        st.subheader(f"{city} — Climate Action Plan Recommendations")

        # Sector-wise suggestions (example placeholders, 10 per sector)
        sectors = ["Energy","Transport","Buildings","Industry","Water","Waste","Urban Green / Other"]
        short_term = {s:[f"Short-term action {i+1}" for i in range(10)] for s in sectors}
        mid_term = {s:[f"Mid-term action {i+1}" for i in range(10)] for s in sectors}
        long_term = {s:[f"Long-term action {i+1}" for i in range(10)] for s in sectors}

        budget_percentage = {s: f"{5+se*2}%" for se,s in enumerate(sectors)}

        st.markdown("### Short-term Actions (by 2030)")
        for s in sectors:
            st.markdown(f"**{s}** — Budget: {budget_percentage[s]}")
            for a in short_term[s]:
                st.write(f"- {a}")
        st.markdown("### Mid-term Actions (by 2040)")
        for s in sectors:
            st.markdown(f"**{s}** — Budget: {budget_percentage[s]}")
            for a in mid_term[s]:
                st.write(f"- {a}")
        st.markdown("### Long-term Actions (by 2050)")
        for s in sectors:
            st.markdown(f"**{s}** — Budget: {budget_percentage[s]}")
            for a in long_term[s]:
                st.write(f"- {a}")

        # Download CAP PDF (GHG + Actions)
        if PDF_AVAILABLE:
            with st.form("pdf_cap_form"):
                submit_pdf = st.form_submit_button("Download CAP (PDF)")
                if submit_pdf:
                    df_cap = st.session_state.cap_data
                    row = df_cap[df_cap["City Name"]==city].iloc[0] if city in df_cap["City Name"].values else None
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4)
                    elements = []
                    styles = getSampleStyleSheet()
                    elements.append(Paragraph(f"{city} — Climate Action Plan Summary", styles["Title"]))
                    elements.append(Spacer(1,12))
                    if row is not None:
                        data = [["Sector","Emissions (tCO2e)"]] + [[s,f"{row.get(f'{s} Emissions',0):,.2f}"] for s in sectors]
                        t = Table(data, hAlign="LEFT")
                        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor("#3E6BE6")),
                                               ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                                               ('GRID',(0,0),(-1,-1),0.5,colors.white)]))
                        elements.append(Paragraph("### GHG Inventory", styles["Heading2"]))
                        elements.append(t)
                        elements.append(Spacer(1,12))
                    elements.append(Paragraph("### Suggested Actions", styles["Heading2"]))
                    for term, actions_dict in [("Short-term (2030)", short_term),
                                               ("Mid-term (2040)", mid_term),
                                               ("Long-term (2050)", long_term)]:
                        elements.append(Paragraph(term, styles["Heading3"]))
                        for s in sectors:
                            elements.append(Paragraph(f"{s} — Budget: {budget_percentage[s]}", styles["Heading4"]))
                            for a in actions_dict[s]:
                                elements.append(Paragraph(f"- {a}", styles["Normal"]))
                            elements.append(Spacer(1,6))
                    doc.build(elements)
                    buffer.seek(0)
                    st.download_button("Download CAP PDF", buffer,
                                       file_name=f"{city}_CAP_Summary.pdf", mime="application/pdf")
        else:
            st.warning("PDF generation not available. Install reportlab library.")

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

meta_cols = ["City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
             "Energy Emissions", "Transport Emissions", "Buildings Emissions", "Industry Emissions",
             "Water Emissions", "Waste Emissions", "Urban Green Emissions"]
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
        # Indian number formatting
        if num < 1000:
            return str(num)
        else:
            s = str(num)[::-1]
            lst = [s[:3]]
            s = s[3:]
            while s:
                lst.append(s[:2])
                s = s[2:]
            return ','.join(lst)[::-1]
    except:
        return str(num)

def safe_get(row, col, default="—"):
    try:
        val = row.get(col, default)
        return default if pd.isna(val) else val
    except:
        return default

def calculate_emissions(raw_data):
    emissions = {}
    # Energy sector
    emissions["Energy"] = raw_data.get("Electricity Consumption (MWh)",0)*0.82
    # Transport
    emissions["Transport"] = (raw_data.get("Diesel (litres)",0)*2.68 + raw_data.get("Petrol (litres)",0)*2.31)/1000
    # Buildings
    emissions["Buildings"] = raw_data.get("Buildings Energy (MWh)",0)*0.82
    # Industry
    emissions["Industry"] = raw_data.get("Industry Energy (MWh)",0)*0.82
    # Water
    emissions["Water"] = raw_data.get("Water Consumption (ML)",0)*0.4
    # Waste
    emissions["Waste"] = raw_data.get("Waste Generated (t)",0)*0.5
    # Urban Green / Other
    emissions["Urban Green / Other"] = raw_data.get("Urban Green Area (ha)",0)*-0.8
    return emissions

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
for btn, name in [("Home","Home"), ("City Dashboard","City Dashboard"), ("Admin Panel","Admin Panel")]:
    if st.sidebar.button(btn):
        st.session_state.menu = name

# Admin only buttons
if st.session_state.authenticated:
    for btn, name in [("CAP Preparation","CAP Preparation"), ("GHG Inventory","GHG Inventory"), ("Actions","Actions")]:
        if st.sidebar.button(btn):
            st.session_state.menu = name

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
    if not df.empty:
        df.fillna(0, inplace=True)
        df["GHG Emissions"] = pd.to_numeric(df.get("GHG Emissions",0), errors="coerce").fillna(0)
        fig2 = px.bar(df.sort_values("GHG Emissions", ascending=False), x="City Name", y="GHG Emissions",
                      title="City-level GHG (tCO2e)", text="GHG Emissions", color_discrete_sequence=["#3E6BE6"])
        fig2.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu=="City Dashboard":
    st.header("City Dashboard")
    df_meta = st.session_state.data.copy()
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
        st.subheader("Upload / Update City Metadata")
        with st.form("admin_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            cap_status = st.selectbox("CAP Status", ["Not Started","In Progress","Completed"])
            population = st.number_input("Population (2011)", min_value=0, step=1)
            ulb_cat = st.text_input("ULB Category")
            submit_admin = st.form_submit_button("Save Metadata")
            if submit_admin:
                new_row = {"City Name": city, "District": cities_districts.get(city,"—"),
                           "CAP Status": cap_status, "Population": population, "ULB Category": ulb_cat}
                df_meta = st.session_state.data
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"]==city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE,index=False)
                st.success(f"{city} metadata updated successfully!")

# ---------------------------
# CAP Preparation Page
# ---------------------------
elif menu=="CAP Preparation":
    st.header("CAP Preparation — Raw Data Input")
    if not st.session_state.authenticated:
        admin_login()
    else:
        with st.form("cap_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            st.markdown("### Enter Raw Data for Emissions Calculation")
            raw_data = {}
            raw_data["Electricity Consumption (MWh)"] = st.number_input("Electricity Consumption (MWh)", min_value=0.0, step=1.0)
            raw_data["Diesel (litres)"] = st.number_input("Diesel Fuel (litres)", min_value=0.0, step=1.0)
            raw_data["Petrol (litres)"] = st.number_input("Petrol Fuel (litres)", min_value=0.0, step=1.0)
            raw_data["Buildings Energy (MWh)"] = st.number_input("Buildings Energy Consumption (MWh)", min_value=0.0, step=1.0)
            raw_data["Industry Energy (MWh)"] = st.number_input("Industry Energy Consumption (MWh)", min_value=0.0, step=1.0)
            raw_data["Water Consumption (ML)"] = st.number_input("Water Consumption (ML)", min_value=0.0, step=1.0)
            raw_data["Waste Generated (t)"] = st.number_input("Waste Generated (t)", min_value=0.0, step=1.0)
            raw_data["Urban Green Area (ha)"] = st.number_input("Urban Green Area (ha)", min_value=0.0, step=1.0)
            submit_cap = st.form_submit_button("Save CAP Data and Calculate Emissions")
            if submit_cap:
                emissions = calculate_emissions(raw_data)
                total_emissions = sum(emissions.values())
                new_row = {"City Name": city, "CAP Status": "In Progress", "GHG Emissions": total_emissions}
                for k,v in emissions.items():
                    new_row[f"{k} Emissions"] = v
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
                # Redirect to GHG Inventory
                st.session_state.menu = "GHG Inventory"
                st.experimental_rerun()
