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

    if not df_cap.empty and city in df_cap["City Name"].values:
        cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
        sector_cols = [c for c in cap_row.index if c.endswith(" Emissions (tCO2e)")]
        sectors = {c.replace(" Emissions (tCO2e)",""): max(float(cap_row[c]),0) for c in sector_cols}
        
        if sectors:
            chart_df = pd.DataFrame({"Sector":list(sectors.keys()),"Emissions":list(sectors.values())})
            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions",
                             title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v:f"{v:,.2f}")))

    last_mod = st.session_state.last_updated or datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
    st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")

    # PDF Download
    if PDF_AVAILABLE:
        st.subheader("Download GHG Inventory Report (PDF)")
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
                st.download_button("Download PDF", buffer, file_name=f"{city}_GHG_Report.pdf", mime="application/pdf")
    else:
        st.warning("PDF generation not available. Install reportlab library.")

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
# CAP Preparation Page
# ---------------------------
elif menu=="CAP Preparation":
    st.header("CAP Preparation — City GHG Inventory Input")
    
    if not st.session_state.authenticated:
        admin_login()
    else:
        with st.form("cap_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            
            st.markdown("### 1️⃣ Energy & Buildings")
            elec_city_buildings = st.number_input("Electricity consumed by city-owned buildings (kWh/year)", min_value=0.0, step=1.0)
            elec_residential = st.number_input("Electricity consumed by residential sector (kWh/year, if available)", min_value=0.0, step=1.0)
            elec_commercial = st.number_input("Electricity consumed by commercial sector (kWh/year, if available)", min_value=0.0, step=1.0)
            lpg_buildings = st.number_input("LPG / Natural Gas consumed by municipal buildings (kg/year)", min_value=0.0, step=1.0)
            diesel_buildings = st.number_input("Diesel/Petrol/Coal consumed by municipal buildings (liters/tons/year)", min_value=0.0, step=1.0)
            streetlight_elec = st.number_input("Electricity for streetlights (kWh/year)", min_value=0.0, step=1.0)
            
            st.markdown("### 2️⃣ Transport Sector")
            st.write("Public Transport:")
            bus_count_diesel = st.number_input("Number of diesel buses", min_value=0, step=1)
            bus_count_cng = st.number_input("Number of CNG buses", min_value=0, step=1)
            bus_count_electric = st.number_input("Number of electric buses", min_value=0, step=1)
            bus_fuel_diesel = st.number_input("Diesel consumption by public buses (liters/year)", min_value=0.0, step=1.0)
            bus_fuel_cng = st.number_input("CNG consumption by public buses (kg/year)", min_value=0.0, step=1.0)
            bus_energy_electric = st.number_input("Electricity consumption by electric buses (kWh/year)", min_value=0.0, step=1.0)
            
            st.write("Municipal Vehicles:")
            municipal_diesel = st.number_input("Diesel consumed by municipal vehicles (liters/year)", min_value=0.0, step=1.0)
            municipal_petrol = st.number_input("Petrol consumed by municipal vehicles (liters/year)", min_value=0.0, step=1.0)
            municipal_electric = st.number_input("Electricity consumed by municipal vehicles (kWh/year)", min_value=0.0, step=1.0)
            
            st.markdown("### 3️⃣ Waste Management")
            total_solid_waste = st.number_input("Total municipal solid waste collected (tons/year)", min_value=0.0, step=1.0)
            fraction_landfill = st.number_input("Fraction of waste sent to landfill (%)", min_value=0.0, max_value=100.0, step=1.0)
            fraction_composted = st.number_input("Fraction of waste composted or processed (%)", min_value=0.0, max_value=100.0, step=1.0)
            fraction_incinerated = st.number_input("Fraction of waste incinerated (%)", min_value=0.0, max_value=100.0, step=1.0)
            landfill_gas_mgmt = st.selectbox("Landfill gas management", ["No", "Captured & flared", "Open"])
            
            wastewater_total = st.number_input("Total wastewater generated (ML/year)", min_value=0.0, step=1.0)
            wastewater_treated = st.number_input("Fraction treated (%)", min_value=0.0, max_value=100.0, step=1.0)
            wastewater_untreated = st.number_input("Fraction untreated (%)", min_value=0.0, max_value=100.0, step=1.0)
            wastewater_treatment_type = st.text_input("Type of wastewater treatment technology")
            
            st.markdown("### 4️⃣ Industrial & Commercial Sector")
            industrial_count = st.number_input("Total number of registered industries", min_value=0, step=1)
            industrial_fuel_diesel = st.number_input("Diesel consumed by industries (liters/year)", min_value=0.0, step=1.0)
            industrial_fuel_coal = st.number_input("Coal consumed by industries (tons/year)", min_value=0.0, step=1.0)
            industrial_fuel_gas = st.number_input("Gas consumed by industries (kg/year)", min_value=0.0, step=1.0)
            industrial_electricity = st.number_input("Electricity consumed by industries (kWh/year)", min_value=0.0, step=1.0)
            commercial_electricity = st.number_input("Electricity consumed by commercial buildings (kWh/year)", min_value=0.0, step=1.0)
            
            st.markdown("### 5️⃣ Urban Green / Land Use")
            urban_green_area = st.number_input("Urban forest / parks area (ha)", min_value=0.0, step=1.0)
            street_trees = st.number_input("Number of street trees planted / maintained by municipality", min_value=0, step=1)
            tree_species_type = st.selectbox("Tree species type", ["Native", "Exotic", "Mixed"])
            
            st.markdown("### Attach Verification Documents (Optional)")
            file_upload = st.file_uploader("Attach verification file (PDF, XLSX, CSV)", type=["pdf","xlsx","csv"])
            
            submit_cap = st.form_submit_button("Save CAP Data")
            
            if submit_cap:
                # Prepare new row
                new_row = {
                    "City Name": city,
                    # Energy & Buildings
                    "Elec_City_Buildings": elec_city_buildings,
                    "Elec_Residential": elec_residential,
                    "Elec_Commercial": elec_commercial,
                    "LPG_Buildings": lpg_buildings,
                    "Diesel_Buildings": diesel_buildings,
                    "Streetlight_Elec": streetlight_elec,
                    # Transport
                    "Bus_Diesel": bus_count_diesel,
                    "Bus_CNG": bus_count_cng,
                    "Bus_Electric": bus_count_electric,
                    "Bus_Fuel_Diesel": bus_fuel_diesel,
                    "Bus_Fuel_CNG": bus_fuel_cng,
                    "Bus_Energy_Electric": bus_energy_electric,
                    "Municipal_Diesel": municipal_diesel,
                    "Municipal_Petrol": municipal_petrol,
                    "Municipal_Electric": municipal_electric,
                    # Waste
                    "Total_Solid_Waste": total_solid_waste,
                    "Fraction_Landfill": fraction_landfill,
                    "Fraction_Composted": fraction_composted,
                    "Fraction_Incinerated": fraction_incinerated,
                    "Landfill_Gas_Mgmt": landfill_gas_mgmt,
                    "Wastewater_Total": wastewater_total,
                    "Wastewater_Treated": wastewater_treated,
                    "Wastewater_Untreated": wastewater_untreated,
                    "Wastewater_Treatment_Type": wastewater_treatment_type,
                    # Industry & Commercial
                    "Industrial_Count": industrial_count,
                    "Industrial_Fuel_Diesel": industrial_fuel_diesel,
                    "Industrial_Fuel_Coal": industrial_fuel_coal,
                    "Industrial_Fuel_Gas": industrial_fuel_gas,
                    "Industrial_Electricity": industrial_electricity,
                    "Commercial_Electricity": commercial_electricity,
                    # Urban Green
                    "Urban_Green_Area": urban_green_area,
                    "Street_Trees": street_trees,
                    "Tree_Species_Type": tree_species_type
                }
                
                df_cap = st.session_state.cap_data
                if not df_cap.empty and city in df_cap["City Name"].values:
                    for k,v in new_row.items():
                        df_cap.loc[df_cap["City Name"]==city, k] = v
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([new_row])], ignore_index=True)
                
                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE,index=False)
                st.session_state.last_updated = datetime.now()
                st.success(f"CAP data for {city} saved successfully!")

elif menu=="CAP Preparation":
    st.header("CAP Preparation — City GHG Inventory Input")
    
    if not st.session_state.authenticated:
        admin_login()
    else:
        with st.form("cap_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            
            # ... [all inputs from previous CAP Preparation code] ...
            
            submit_cap = st.form_submit_button("Save CAP Data")
            
            if submit_cap:
                # Prepare new row
                new_row = { ... }  # same as previous code
                
                df_cap = st.session_state.cap_data
                if not df_cap.empty and city in df_cap["City Name"].values:
                    for k,v in new_row.items():
                        df_cap.loc[df_cap["City Name"]==city, k] = v
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([new_row])], ignore_index=True)
                
                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE,index=False)
                st.session_state.last_updated = datetime.now()
                st.success(f"CAP data for {city} saved successfully!")
                
                # Redirect to GHG Inventory page
                st.session_state.menu = "GHG Inventory"
                st.experimental_rerun()

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu=="GHG Inventory":
    st.header("City GHG Inventory — Calculated Emissions")
    
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy()
    
    city = st.selectbox("Select City to view inventory", list(cities_districts.keys()))
    
    meta_row = df_meta[df_meta["City Name"]==city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None
    st.subheader(f"{city} — Overview")
    population = 0
    if meta_row is not None:
        population = safe_get(meta_row,'Population',0)
        st.write(f"**District:** {safe_get(meta_row,'District')}")
        st.write(f"**Population (2011):** {format_population(population)}")
        st.write(f"**CAP Status:** {safe_get(meta_row,'CAP Status')}")
    
    if not df_cap.empty and city in df_cap["City Name"].values:
        cap_row = df_cap[df_cap["City Name"]==city].iloc[0]
        
        # Calculate sector emissions (example, user can expand formulas)
        # Energy: convert kWh to tCO2e, Diesel/LPG etc to tCO2e
        CO2_ELEC_FACTOR = 0.82/1000  # tCO2e per kWh, example India grid factor
        CO2_DIESEL = 2.68 / 1000     # tCO2e per liter
        CO2_LPG = 1.51 / 1000        # tCO2e per kg
        CO2_CNG = 2.75 / 1000        # tCO2e per kg
        CO2_COAL = 2.33               # tCO2e per kg, example
        
        total_energy = (
            cap_row.get("Elec_City_Buildings",0) * CO2_ELEC_FACTOR +
            cap_row.get("Elec_Residential",0) * CO2_ELEC_FACTOR +
            cap_row.get("Elec_Commercial",0) * CO2_ELEC_FACTOR +
            cap_row.get("LPG_Buildings",0) * CO2_LPG +
            cap_row.get("Diesel_Buildings",0) * CO2_DIESEL +
            cap_row.get("Streetlight_Elec",0) * CO2_ELEC_FACTOR
        )
        
        total_transport = (
            cap_row.get("Bus_Fuel_Diesel",0) * CO2_DIESEL +
            cap_row.get("Bus_Fuel_CNG",0) * CO2_CNG +
            cap_row.get("Bus_Energy_Electric",0) * CO2_ELEC_FACTOR +
            cap_row.get("Municipal_Diesel",0) * CO2_DIESEL +
            cap_row.get("Municipal_Petrol",0) * CO2_DIESEL +
            cap_row.get("Municipal_Electric",0) * CO2_ELEC_FACTOR
        )
        
        total_waste = (
            cap_row.get("Total_Solid_Waste",0) * 0.1  # approximate tCO2e/ton landfill
        )
        
        total_industry = (
            cap_row.get("Industrial_Fuel_Diesel",0) * CO2_DIESEL +
            cap_row.get("Industrial_Fuel_Coal",0) * CO2_COAL +
            cap_row.get("Industrial_Fuel_Gas",0) * CO2_LPG +
            cap_row.get("Industrial_Electricity",0) * CO2_ELEC_FACTOR
        )
        
        total_commercial = cap_row.get("Commercial_Electricity",0) * CO2_ELEC_FACTOR
        
        total_ghg = total_energy + total_transport + total_waste + total_industry + total_commercial
        
        st.metric("Total GHG Emissions (tCO2e)", f"{total_ghg:,.2f}")
        if population:
            per_capita = total_ghg / int(population)
            st.metric("Per Capita GHG Emissions (tCO2e/person)", f"{per_capita:,.2f}")
        
        # Sector-wise bar chart
        sectors = {
            "Energy & Buildings": total_energy,
            "Transport": total_transport,
            "Waste": total_waste,
            "Industry": total_industry,
            "Commercial": total_commercial
        }
        chart_df = pd.DataFrame({"Sector": list(sectors.keys()), "Emissions": list(sectors.values())})
        fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions",
                         title="Sector-wise GHG Emissions (tCO2e)",
                         color="Sector", color_discrete_sequence=px.colors.qualitative.Bold)
        fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig_bar, use_container_width=True)
