import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# ---------------------------
# Page Configuration
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

# Load city data
if os.path.exists(DATA_FILE):
    st.session_state.data = pd.read_csv(DATA_FILE)
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
        "Environment Department Exist", "Department Name", "Head Name", "Department Email"
    ])

# Load CAP raw data
if os.path.exists(CAP_DATA_FILE):
    st.session_state.cap_data = pd.read_csv(CAP_DATA_FILE)
else:
    st.session_state.cap_data = pd.DataFrame()

# ---------------------------
# Helper Functions
# ---------------------------
def get_val(row: pd.Series, target: str, default="—"):
    return row[target] if target in row and pd.notna(row[target]) else default

def format_population(num):
    if pd.isna(num) or num == "":
        return "—"
    return "{:,}".format(int(num))

# ---------------------------
# Dark Theme CSS
# ---------------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background-color: #121212; color: #E0E0E0;}
[data-testid="stSidebar"] {background-color: #1C1C1C; color: #E0E0E0;}

.stButton>button {background-color: #228B22 !important; color: #FFFFFF !important; width: 100% !important; margin-bottom: 5px !important; height: 40px !important; font-size: 16px !important; border-radius: 5px !important;}
.stButton>button:hover {background-color: #196619 !important;}

[data-testid="stMetricValue"] {color: #4169E1 !important; font-weight: bold;}
.stExpander>div>div>div>div {background-color: #1E1E1E !important; color: #E0E0E0 !important;}
h1, h2, h3, h4, h5, h6 {color: #7CFC00 !important;}

.stTextInput>div>input, .stNumberInput>div>input {background-color: #1C1C1C !important; color: #E0E0E0 !important; border-color: #228B22 !important;}
.stFileUploader>div>div {background-color:#1C1C1C !important; color:#E0E0E0 !important;}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Admin Login
# ---------------------------
def admin_login():
    with st.form("login_form"):
        password = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Admin login successful")
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar (unchanged)
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)
if st.sidebar.button("Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("City Dashboard"):
    st.session_state.menu = "City Dashboard"
if st.sidebar.button("Admin Panel"):
    st.session_state.menu = "Admin Panel"
if st.session_state.authenticated:
    if st.sidebar.button("CAP Preparation"):
        st.session_state.menu = "CAP Preparation"

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")
menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra Climate Action Plan Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")
    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        if "GHG Emissions" in df.columns:
            df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors='coerce').fillna(0)
        st.metric("Total Cities", df.shape[0])
        st.metric("Cities with CAP Completed", df[df["CAP Status"]=="Completed"].shape[0])
        if "GHG Emissions" in df.columns:
            fig = px.bar(df, x="City Name", y="GHG Emissions", text="GHG Emissions", title="GHG Emissions by City", color_discrete_sequence=["#7CFC00"])
            fig.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="#E0E0E0")
            st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        st.header("City Dashboard")
        city = st.selectbox("Select City", df["City Name"].dropna().unique())
        city_row = df[df["City Name"] == city].iloc[0]

        with st.expander("Basic Info", expanded=True):
            st.write(f"**District:** {get_val(city_row, 'District')}")
            st.write(f"**Population:** {format_population(get_val(city_row, 'Population'))}")
            st.write(f"**ULB Category:** {get_val(city_row, 'ULB Category')}")
            st.write(f"**CAP Status:** {get_val(city_row, 'CAP Status')}")

        with st.expander("Environment Department"):
            st.write(f"**Exists:** {get_val(city_row, 'Environment Department Exist')}")
            st.write(f"**Dept Name:** {get_val(city_row, 'Department Name')}")
            st.write(f"**Head Name:** {get_val(city_row, 'Head Name')}")
            st.write(f"**Email:** {get_val(city_row, 'Department Email')}")

        if os.path.exists(DATA_FILE):
            last_updated = pd.to_datetime(os.path.getmtime(DATA_FILE), unit='s')
            st.markdown(f"*Last Updated: {last_updated.strftime('%B %Y')}*")

        # Sector-wise emissions pie chart if CAP data available
        df_cap = st.session_state.cap_data
        if not df_cap.empty and city in df_cap["City Name"].values:
            row = df_cap[df_cap["City Name"]==city].iloc[0]
            sectors = {k:v for k,v in row.items() if k.endswith("Emissions (tCO2e)")}
            if sectors:
                pie_df = pd.DataFrame({"Sector": list(sectors.keys()), "Emissions": list(sectors.values())})
                fig2 = px.pie(pie_df, names="Sector", values="Emissions", title="Sector-wise GHG Emissions")
                fig2.update_layout(plot_bgcolor="#121212", paper_bgcolor="#121212", font_color="#E0E0E0")
                st.plotly_chart(fig2, use_container_width=True)

            # ---------------- PDF Download Section ----------------
            st.subheader("📥 Download GHG Inventory Report (PDF)")
            with st.form("download_form"):
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                contact = st.text_input("Contact Number")
                submit_download = st.form_submit_button("Generate PDF Report")

            if submit_download:
                if not name or not email or not contact:
                    st.error("Please fill in all details before downloading.")
                else:
                    # Generate PDF
                    buffer = io.BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=A4)
                    styles = getSampleStyleSheet()
                    elements = []

                    elements.append(Paragraph("City GHG Inventory Report", styles['Title']))
                    elements.append(Spacer(1, 12))
                    elements.append(Paragraph(f"City: {city}", styles['Normal']))
                    elements.append(Paragraph(f"District: {city_row['District']}", styles['Normal']))
                    elements.append(Paragraph(f"Generated for: {name}", styles['Normal']))
                    elements.append(Paragraph(f"Email: {email}", styles['Normal']))
                    elements.append(Paragraph(f"Contact: {contact}", styles['Normal']))
                    elements.append(Paragraph(f"Last Updated: {last_updated.strftime('%B %Y')}", styles['Normal']))
                    elements.append(Spacer(1, 12))

                    # Table of emissions
                    table_data = [["Sector", "Emissions (tCO2e)"]]
                    total = 0
                    for sector, value in sectors.items():
                        table_data.append([sector, f"{value:.2f}"])
                        total += float(value)

                    table_data.append(["Total Emissions", f"{total:.2f}"])
                    table = Table(table_data, hAlign="LEFT")
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#1E1E1E")),
                        ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ]))

                    elements.append(table)
                    doc.build(elements)

                    buffer.seek(0)
                    st.download_button(
                        label="⬇️ Download PDF",
                        data=buffer,
                        file_name=f"{city}_GHG_Inventory.pdf",
                        mime="application/pdf"
                    )

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("Admin Panel")
        df = st.session_state.data
        cities_list = list(cities_districts.keys())
        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list)
            district = st.text_input("District", value=cities_districts[city_name], disabled=True)
            population = st.number_input("Population(as per 2011 census)", min_value=0, step=1000, format="%d")
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            ghg = st.text_input("GHG Emissions (MTCO2e)", "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"], index=0)
            dept_name = st.text_input("Department Name", "")
            head_name = st.text_input("Head Name", "")
            dept_email = st.text_input("Department Email", "")
            submit = st.form_submit_button("Add/Update City")
            if submit:
                new_row = {
                    "City Name": city_name, "District": district, "Population": population, "ULB Category": ulb_cat,
                    "CAP Status": cap_status, "GHG Emissions": ghg, "Environment Department Exist": env_exist,
                    "Department Name": dept_name, "Head Name": head_name, "Department Email": dept_email
                }
                df = df[df["City Name"] != city_name]
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df
                df.to_csv(DATA_FILE, index=False)
                st.success(f"{city_name} saved successfully.")

# ---------------------------
# CAP Preparation (fixed)
# ---------------------------
elif menu == "CAP Preparation":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("CAP Preparation - Unified Input Form")
        df_cap = st.session_state.cap_data

        # Default emission factors
        EF = {
            "electricity": 0.82,      # tCO2e/MWh
            "diesel": 2.68,          # kgCO2e/litre
            "petrol": 2.31,          # kgCO2e/litre
            "waste": 1.2,            # tCO2e/tonne MSW
            "water": 0.5,            # tCO2e/ML
            "wastewater": 0.7,       # tCO2e/ML
            "industry_energy": 0.82  # tCO2e/MWh
        }

        with st.form("cap_form"):
            city_name = st.selectbox("Select City", st.session_state.data["City Name"].dropna().unique(), key="cap_city_select")

            st.subheader("Energy Sector")
            energy_elec = st.number_input("Annual Electricity Consumption (MWh)", min_value=0, key="energy_elec")
            energy_diesel = st.number_input("Diesel Consumption (litres)", min_value=0, key="energy_diesel")
            energy_petrol = st.number_input("Petrol Consumption (litres)", min_value=0, key="energy_petrol")

            st.subheader("Transport Sector")
            transport_fuel_diesel = st.number_input("Transport Diesel Consumption (litres)", min_value=0, key="transport_diesel")
            transport_fuel_petrol = st.number_input("Transport Petrol Consumption (litres)", min_value=0, key="transport_petrol")

            st.subheader("Buildings Sector")
            buildings_area = st.number_input("Total Built-up Area (sq.m)", min_value=0, key="buildings_area")

            st.subheader("Water Sector")
            water_consumption = st.number_input("Water Consumption (ML/year)", min_value=0, key="water_consumption")
            wastewater_generated = st.number_input("Wastewater Generated (ML/year)", min_value=0, key="wastewater_generated")

            st.subheader("Waste Sector")
            waste_generated = st.number_input("Solid Waste Generated (tonnes/year)", min_value=0, key="waste_generated")

            st.subheader("Industry Sector")
            industry_energy = st.number_input("Industrial Energy Consumption (MWh/year)", min_value=0, key="industry_energy")

            st.subheader("Urban Green & Other")
            other_emissions = st.number_input("Other Emissions (tCO2e)", min_value=0, key="other_emissions")

            submit = st.form_submit_button("Save & Calculate Emissions")

        if submit:
            # Emission calculations
            emissions = {}
            emissions["Energy Emissions (tCO2e)"] = energy_elec * EF["electricity"] + (energy_diesel * EF["diesel"]/1000) + (energy_petrol * EF["petrol"]/1000)
            emissions["Transport Emissions (tCO2e)"] = (transport_fuel_diesel * EF["diesel"]/1000) + (transport_fuel_petrol * EF["petrol"]/1000)
            emissions["Buildings Emissions (tCO2e)"] = (buildings_area * 0.05)/
