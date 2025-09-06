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
    "Bhiwandi-Nozampur": "Thane",
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
    "Chh. Sambhajinagar": "Chh. Sambhajianagar",
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
    "City Name", "District", "Population", "ULB Category", "CAP Status",
    "GHG Emissions", "Environment Department Exist", "Department Name",
    "Head Name", "Department Email"
]
cap_cols = []

st.session_state.data = load_csv(DATA_FILE, meta_cols)
st.session_state.cap_data = load_csv(CAP_DATA_FILE, cap_cols)

# Remove Raigad Council (case-insensitive)
st.session_state.data = st.session_state.data[
    ~st.session_state.data["City Name"].str.contains("Raigad Council", case=False, na=False)
]

# ---------------------------
# Helper Functions
# ---------------------------
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

def format_population(num):
    try:
        if pd.isna(num) or num == "":
            return "—"
        return format_indian_number(num)
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

        st.markdown("### CAP Status Overview")
        c1, c2, c3, c4 = st.columns(4)

        block_style = """
            background-color:#141518;
            padding:20px;
            border-radius:12px;
            text-align:center;
        """
        title_style = "color:#E6E6E6; margin:0;"
        value_style = "font-size:28px; font-weight:bold; color:#3E6BE6;"

        c1.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Not Started</h3><p style='{value_style}'>{format_indian_number(not_started)}</p></div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>In Progress</h3><p style='{value_style}'>{format_indian_number(in_progress)}</p></div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Completed</h3><p style='{value_style}'>{format_indian_number(completed)}</p></div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='{block_style}'><h3 style='{title_style}'>Total</h3><p style='{value_style}'>{format_indian_number(total_status)}</p></div>", unsafe_allow_html=True)

    # --- Reported GHG ---
    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig_reported = px.bar(
            df.sort_values("GHG Emissions", ascending=False),
            x="City Name", y="GHG Emissions",
            title="City-level Reported GHG Emissions (tCO2e)",
            text=df["GHG Emissions"].apply(format_indian_number),
            color_discrete_sequence=["#3E6BE6"]
        )
        fig_reported.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig_reported, use_container_width=True)

    # --- Estimated GHG ---
    if not df.empty and "Population" in df.columns:
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce").fillna(0)
        EMISSION_FACTOR = 2.5
        df["Estimated GHG Emissions"] = df["Population"] * EMISSION_FACTOR
        fig_estimated = px.bar(
            df.sort_values("Estimated GHG Emissions", ascending=False),
            x="City Name", y="Estimated GHG Emissions",
            title=f"Estimated GHG Emissions (tCO2e) — based on {EMISSION_FACTOR} tCO2e/person",
            text=df["Estimated GHG Emissions"].apply(lambda x: format_indian_number(round(x))),
            color_discrete_sequence=["#E67E22"]
        )
        fig_estimated.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig_estimated, use_container_width=True)

# ---------------------------
# City Information
# ---------------------------
elif menu == "City Information":
    st.header("City Information")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()

    cities_for_select = list(cities_districts.keys())
    city = st.selectbox("Select City", cities_for_select)

    meta_row = df_meta[df_meta["City Name"] == city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None

    st.subheader(f"{city} — Overview")
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row, 'District')}")
        st.write(f"**Population (as per census 2011):** {format_population(safe_get(meta_row, 'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row, 'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row, 'CAP Status')}")
    else:
        st.write(f"**District:** {cities_districts.get(city, '—')}")

    if not df_cap.empty and city in df_cap["City Name"].values:
        cap_row = df_cap[df_cap["City Name"] == city].iloc[0]
        sector_cols = [c for c in cap_row.index if c.endswith(" Emissions (tCO2e)")]
        sectors = {c.replace(" Emissions (tCO2e)", ""): max(float(cap_row[c]), 0) for c in sector_cols}

        if sectors:
            chart_df = pd.DataFrame({"Sector": list(sectors.keys()), "Emissions": list(sectors.values())})

            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text=chart_df["Emissions"].apply(lambda x: format_indian_number(round(x))),
                             title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v: format_indian_number(round(v)))))

        last_mod = st.session_state.last_updated or datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
        st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")

        # PDF Download
        if PDF_AVAILABLE:
            st.subheader("Download GHG Inventory Report")
            with st.form("pdf_form"):
                user_name = st.text_input("Your Full Name")
                user_email = st.text_input("Your Work Email")
                user_contact = st.text_input("Contact Number")
                submit_pdf = st.form_submit_button("Generate PDF")
                if submit_pdf:
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4)
                    elements = []
                    styles = getSampleStyleSheet()
                    elements.append(Paragraph(f"{city} — GHG Inventory Report", styles["Title"]))
                    elements.append(Spacer(1, 12))
                    data = [["Sector", "Emissions (tCO2e)"]] + [[s, format_indian_number(round(v))] for s, v in sectors.items()]
                    t = Table(data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3E6BE6")),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.white)
                    ]))
                    elements.append(t)
                    doc.build(elements)
                    buffer.seek(0)
                    st.download_button("Download PDF", buffer, file_name=f"{city}_GHG_Report.pdf", mime="application/pdf")
        else:
            st.warning("PDF generation not available. Install reportlab library.")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin":
    st.header("Admin Board")
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.subheader("Add/Update City Data")
        with st.form("admin_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            population = st.number_input("Population (as per census 2011)", min_value=0, value=0, step=1000)
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)
            dept_exist = st.selectbox("Environment Department Exist?", ["Yes", "No"])
            dept_name = st.text_input("Department Name")
            head_name = st.text_input("Department Head Name")
            dept_email = st.text_input("Department Email")
            submit_admin = st.form_submit_button("Add/Update City Data")

            if submit_admin:
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "—"),
                    "Population": population,
                    "CAP Status": cap_status,
                    "GHG Emissions": ghg_val,
                    "Environment Department Exist": dept_exist,
                    "Department Name": dept_name,
                    "Head Name": head_name,
                    "Department Email": dept_email
                }
                df_meta = st.session_state.data.copy()
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"] == city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE, index=False)
                st.success(f"{city} data updated successfully!")

        st.write("### All Cities Data")
        st.table(st.session_state.data.assign)
            Population=lambda d: d["Population"].map(format_indian_number),
            GHG_Emissions=lambda d: d["GHG Emissions"].map(format_indian_number)

# ---------------------------
# CAP Preparation Page
# ---------------------------
elif menu == "CAP Preparation":
    st.header("CAP : Data Collection")
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.markdown("""
        Collect detailed city-level activity data for generating a comprehensive GHG inventory as per GPC/C40/ICLEI guidelines.
        """)

        with st.form("cap_raw_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))

            # --- Demographics ---
            st.subheader("Population & Demographics")
            population = st.number_input("Total Population", min_value=0, value=0, step=1000)
            households = st.number_input("Number of Households", min_value=0, value=0, step=100)
            urbanization_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

            # --- Energy ---
            st.subheader("Energy Consumption")
            electricity = st.number_input("Electricity Consumption (MWh)", min_value=0.0, step=0.1)
            lpg = st.number_input("LPG Consumption (tonnes)", min_value=0.0, step=0.1)
            petrol = st.number_input("Petrol Consumption (litres)", min_value=0.0, step=0.1)
            diesel = st.number_input("Diesel Consumption (litres)", min_value=0.0, step=0.1)
            coal = st.number_input("Coal Consumption (tonnes)", min_value=0.0, step=0.1)

            # --- Waste ---
            st.subheader("Waste Management")
            solid_waste = st.number_input("Solid Waste Generated (tonnes/day)", min_value=0.0, step=0.1)
            waste_treated = st.number_input("Waste Treated (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            wastewater = st.number_input("Wastewater Generated (MLD)", min_value=0.0, step=0.1)

            # --- Transport ---
            st.subheader("Transport")
            vehicles = st.number_input("Number of Registered Vehicles", min_value=0, step=1)
            public_transport = st.number_input("Public Transport Trips (per day)", min_value=0, step=1)

            # --- Industry ---
            st.subheader("Industrial Activity")
            industries = st.number_input("Number of Industries", min_value=0, step=1)
            industrial_energy = st.number_input("Industrial Energy Consumption (MWh)", min_value=0.0, step=0.1)

            # --- Agriculture & Others ---
            st.subheader("Agriculture & Other Sources")
            agri_residue = st.number_input("Agricultural Residue Burning (tonnes/year)", min_value=0.0, step=0.1)
            livestock = st.number_input("Number of Livestock", min_value=0, step=1)

            submit_cap = st.form_submit_button("Save GHG Inventory Data")

        if submit_cap:
            new_row = {
                "City Name": city,
                "Total Population": population,
                "Households": households,
                "Urbanization Rate (%)": urbanization_rate,
                "Electricity Consumption (MWh)": electricity,
                "LPG Consumption (tonnes)": lpg,
                "Petrol Consumption (litres)": petrol,
                "Diesel Consumption (litres)": diesel,
                "Coal Consumption (tonnes)": coal,
                "Solid Waste Generated (tonnes/day)": solid_waste,
                "Waste Treated (%)": waste_treated,
                "Wastewater Generated (MLD)": wastewater,
                "Number of Registered Vehicles": vehicles,
                "Public Transport Trips (per day)": public_transport,
                "Number of Industries": industries,
                "Industrial Energy Consumption (MWh)": industrial_energy,
                "Agricultural Residue Burning (tonnes/year)": agri_residue,
                "Number of Livestock": livestock
            }
            df_cap = st.session_state.cap_data.copy()
            if city in df_cap["City Name"].values:
                df_cap.loc[df_cap["City Name"] == city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
            else:
                df_cap = pd.concat([df_cap, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.cap_data = df_cap
            df_cap.to_csv(CAP_DATA_FILE, index=False)
            st.session_state.last_updated = datetime.now()
            st.success(f"{city} CAP data updated successfully!")

        # ---------------------------
        # Suggested Actions (ONLY HERE)
        # ---------------------------
        st.subheader("Suggested Actions Based on Inventory")
        st.markdown("""
        ✅ Promote renewable energy adoption  
        ✅ Improve solid waste management & treatment  
        ✅ Enhance public transport and non-motorized mobility  
        ✅ Energy efficiency in industries and households  
        ✅ Awareness programs for sustainable lifestyle  
        """)

        # ---------------------------
        # Report Generation
        # ---------------------------
        if not st.session_state.cap_data.empty and city in st.session_state.cap_data["City Name"].values:
            st.subheader("Download GHG Inventory Report")
            if PDF_AVAILABLE:
                with st.form("cap_pdf_form"):
                    user_name = st.text_input("Your Full Name")
                    user_email = st.text_input("Your Work Email")
                    user_contact = st.text_input("Contact Number")
                    submit_pdf = st.form_submit_button("Generate PDF Report")
                    if submit_pdf:
                        row = st.session_state.cap_data[st.session_state.cap_data["City Name"] == city].iloc[0]
                        buffer = io.BytesIO()
                        doc = SimpleDocTemplate(buffer, pagesize=A4)
                        elements = []
                        styles = getSampleStyleSheet()
                        elements.append(Paragraph(f"{city} — CAP GHG Inventory Report", styles["Title"]))
                        elements.append(Spacer(1, 12))
                        data = [[k, v] for k, v in row.items()]
                        t = Table(data, hAlign="LEFT")
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3E6BE6")),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.white)
                        ]))
                        elements.append(t)
                        doc.build(elements)
                        buffer.seek(0)
                        st.download_button("Download CAP Report PDF", buffer, file_name=f"{city}_CAP_Report.pdf", mime="application/pdf")
            else:
                st.warning("PDF generation not available. Install reportlab library.")
