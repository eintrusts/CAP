# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

# Try importing reportlab for PDF generation; if missing, we'll disable PDF feature
try:
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    PDF_AVAILABLE = True
except Exception:
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
# Data Files (persistence)
# ---------------------------
DATA_FILE = "cities_data.csv"        # city meta (District, Population etc.)
CAP_DATA_FILE = "cap_raw_data.csv"   # CAP raw inputs + computed emissions

# ---------------------------
# Cities & Districts (selected list)
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
# Session State initialization
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if "last_updated" not in st.session_state:
    st.session_state.last_updated = None

# Load city meta
if os.path.exists(DATA_FILE):
    try:
        st.session_state.data = pd.read_csv(DATA_FILE)
    except Exception:
        st.session_state.data = pd.DataFrame(columns=[
            "City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
            "Environment Department Exist", "Department Name", "Head Name", "Department Email"
        ])
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
        "Environment Department Exist", "Department Name", "Head Name", "Department Email"
    ])

# Load CAP raw data if present
if os.path.exists(CAP_DATA_FILE):
    try:
        st.session_state.cap_data = pd.read_csv(CAP_DATA_FILE)
    except Exception:
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
    except Exception:
        return str(num)

def safe_get(df_row, col, default="—"):
    try:
        val = df_row.get(col, default)
        if pd.isna(val):
            return default
        return val
    except Exception:
        return default

# ---------------------------
# Dark / Energy-saving CSS (keeps sidebar/logo untouched)
# ---------------------------
st.markdown("""
<style>
/* App background */
[data-testid="stAppViewContainer"] {
  background-color: #0f0f10;
  color: #E6E6E6;
}
/* Sidebar */
[data-testid="stSidebar"] {
  background-color: #101213;
  color: #E6E6E6;
}
/* Buttons (forest green) */
.stButton>button {
  background-color: #1F7A1F !important;
  color: #FFFFFF !important;
  border-radius: 8px !important;
  height: 40px !important;
  font-size: 14px !important;
}
.stButton>button:hover {
  background-color: #155915 !important;
}
/* Metrics color (royal blue) */
[data-testid="stMetricValue"] {
  color: #3E6BE6 !important;
  font-weight: 700;
}
/* Expander background */
.stExpander>div>div>div>div {
  background-color: #141518 !important;
  color: #E6E6E6 !important;
}
/* Inputs */
input, textarea, select {
  background-color: #141518 !important;
  color: #E6E6E6 !important;
  border-color: #1F7A1F !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Admin login form function
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
# Sidebar (unchanged placement of logo/navigation)
# ---------------------------
st.sidebar.image(
    "https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)
if st.sidebar.button("Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("City Dashboard"):
    st.session_state.menu = "City Dashboard"
if st.sidebar.button("Admin Panel"):
    st.session_state.menu = "Admin Panel"
# CAP Preparation only visible if logged in
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
    st.markdown("Maharashtra's Net Zero Journey — CAP tracking for selected cities.")
    df = st.session_state.data.copy()

    # Show counts: total selected vs reporting
    total_selected = len(cities_districts)
    reporting = df.shape[0]
    completed = 0
    if "CAP Status" in df.columns:
        completed = df[df["CAP Status"].str.lower() == "completed"].shape[0]
    col1, col2, col3 = st.columns(3)
    col1.metric("Cities Selected", f"{total_selected}")
    col2.metric("Cities Reporting (in DB)", f"{reporting}")
    col3.metric("CAPs Completed", f"{completed}")

    # District-wise CAP completion if we have data
    if not df.empty and "District" in df.columns:
        # count per district how many completed
        district_summary = df.groupby("District")["CAP Status"].apply(lambda x: (x.str.lower() == "completed").sum()).reset_index()
        district_summary.columns = ["District", "CAPs Done"]
        if not district_summary.empty:
            fig = px.bar(district_summary.sort_values("CAPs Done", ascending=False),
                         x="District", y="CAPs Done", text="CAPs Done",
                         title="District-wise CAP Completion",
                         color_discrete_sequence=["#3E6BE6"])
            fig.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig, use_container_width=True)

    # State-level GHG stacked (if available)
    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig2 = px.bar(df.sort_values("GHG Emissions", ascending=False),
                      x="City Name", y="GHG Emissions",
                      title="City-level GHG (tCO2e)", text="GHG Emissions",
                      color_discrete_sequence=["#7CFC00"])
        fig2.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    st.header("City Dashboard")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()

    # select city from selected list so district remains fixed
    cities_for_select = list(cities_districts.keys())
    city = st.selectbox("Select City", cities_for_select)

    # show meta info (if present in meta DB)
    meta_row = df_meta[df_meta["City Name"] == city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None
    st.subheader(f"{city} — Overview")
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row, 'District')}")
        st.write(f"**Population (2011):** {format_population(safe_get(meta_row, 'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row, 'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row, 'CAP Status')}")
    else:
        # show district from cities_districts
        st.write(f"**District:** {cities_districts.get(city, '—')}")

    # If CAP data exists for the city, show sector-wise chart and table
    if not df_cap.empty and city in df_cap["City Name"].values:
        cap_row = df_cap[df_cap["City Name"] == city].iloc[0]

        # Extract sector emission columns (we prefix them consistently when saving)
        sector_cols = [c for c in cap_row.index if c.endswith(" Emissions (tCO2e)")]
        sectors = {}
        for c in sector_cols:
            try:
                val = float(cap_row[c])
            except Exception:
                val = 0.0
            sectors[c.replace(" Emissions (tCO2e)", "")] = max(val, 0.0)

        # DataFrame for charts
        if sectors:
            chart_df = pd.DataFrame({"Sector": list(sectors.keys()), "Emissions": list(sectors.values())})
            # Pie
            fig_pie = px.pie(chart_df, names="Sector", values="Emissions", title="Sector-wise Emissions (tCO2e)")
            fig_pie.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Bar
            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions", title="Sector Emissions (tCO2e)",
                             color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Show table
            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v: f"{v:,.2f}")))

            # Last updated
            if st.session_state.last_updated:
                st.markdown(f"*Last Updated: {st.session_state.last_updated.strftime('%B %Y')}*")
            elif os.path.exists(CAP_DATA_FILE):
                last_mod = datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
                st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")

            # PDF download with mandatory contact form
            st.subheader("📥 Download GHG Inventory Report (PDF)")
            if not PDF_AVAILABLE:
                st.warning("PDF generation library not available on this environment. Install `reportlab` to enable PDF downloads.")
            else:
                with st.form("pdf_form"):
                    user_name = st.text_input("Your Full Name")
                    user_email = st.text_input("Your Work Email")
                    user_contact = st.text_input("Contact Number")
                    pdf_submit = st.form_submit_button("Generate PDF")

                if pdf_submit:
                    if not user_name or not user_email or not user_contact:
                        st.error("Please provide Name, Work Email and Contact Number to download the PDF.")
                    else:
                        # Build PDF
                        buffer = io.BytesIO()
                        doc = SimpleDocTemplate(buffer, pagesize=A4)
                        styles = getSampleStyleSheet()
                        elements = []
                        elements.append(Paragraph(f"City GHG Inventory — {city}", styles["Title"]))
                        elements.append(Spacer(1, 6))
                        elements.append(Paragraph(f"District: {cities_districts.get(city, '—')}", styles["Normal"]))
                        elements.append(Paragraph(f"Generated for: {user_name}", styles["Normal"]))
                        elements.append(Paragraph(f"Email: {user_email}", styles["Normal"]))
                        elements.append(Paragraph(f"Contact: {user_contact}", styles["Normal"]))
                        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d %b %Y %H:%M')}", styles["Normal"]))
                        elements.append(Spacer(1, 12))

                        table_data = [["Sector", "Emissions (tCO2e)"]]
                        total = 0.0
                        for sec, val in sectors.items():
                            table_data.append([sec, f"{float(val):,.2f}"])
                            total += float(val)
                        table_data.append(["Total", f"{total:,.2f}"])

                        table = Table(table_data, hAlign="LEFT", colWidths=[300, 150])
                        table.setStyle(TableStyle([
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F7A1F")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#141518")),
                            ("TEXTCOLOR", (0, 1), (-1, -1), colors.white),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ]))
                        elements.append(table)
                        doc.build(elements)
                        buffer.seek(0)
                        st.download_button("⬇️ Download PDF Report", data=buffer, file_name=f"{city}_GHG_Inventory.pdf", mime="application/pdf")
        else:
            st.info("CAP raw data present for this city but sector emissions not found. Please check CAP data.")

    else:
        st.info("No CAP raw data for this city. Go to 'CAP Preparation' (admin) to input raw data.")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("Admin Panel — City Metadata")
        df_meta = st.session_state.data.copy()
        cities_list = list(cities_districts.keys())

        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list)
            district = st.text_input("District", value=cities_districts.get(city_name, ""), disabled=True)
            population = st.number_input("Population (2011 census)", min_value=0, step=1000, value=int(df_meta[df_meta["City Name"]==city_name]["Population"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else 0, format="%d")
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            ghg = st.text_input("GHG Emissions (tCO2e) — optional", value=str(df_meta[df_meta["City Name"]==city_name]["GHG Emissions"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"], index=0)
            dept_name = st.text_input("Department Name", value=str(df_meta[df_meta["City Name"]==city_name]["Department Name"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")
            head_name = st.text_input("Head Name", value=str(df_meta[df_meta["City Name"]==city_name]["Head Name"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")
            dept_email = st.text_input("Department Email", value=str(df_meta[df_meta["City Name"]==city_name]["Department Email"].values[0]) if (not df_meta.empty and city_name in df_meta["City Name"].values) else "")

            submit_meta = st.form_submit_button("Add / Update City Metadata")

        if submit_meta:
            # remove existing entry for city (if any) then append new
            df_meta = df_meta[df_meta["City Name"] != city_name]
            new_row = {
                "City Name": city_name,
                "District": district,
                "Population": int(population),
                "ULB Category": ulb_cat,
                "CAP Status": cap_status,
                "GHG Emissions": ghg,
                "Environment Department Exist": env_exist,
                "Department Name": dept_name,
                "Head Name": head_name,
                "Department Email": dept_email
            }
            df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
            st.session_state.data = df_meta
            df_meta.to_csv(DATA_FILE, index=False)
            st.session_state.last_updated = datetime.now()
            st.success(f"{city_name} metadata saved.")

# ---------------------------
# CAP Preparation (Unified) — only accessible if admin logged in and clicked CAP Preparation
# ---------------------------
if menu == "CAP Preparation":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("CAP Preparation — Unified Raw Data Input (per city)")
        st.markdown("Enter raw activity data for the city. Uploads are optional verification files; calculations use only entered numeric inputs.")

        df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()

        # inline emission factors (units: electricity tCO2e/MWh; fuels kgCO2e/litre; waste tCO2e/ton; water/wastewater tCO2e/ML)
        EF = {
            "electricity_tCO2_per_MWh": 0.82,   # tCO2e per MWh
            "diesel_kgCO2_per_l": 2.68,        # kgCO2e per litre
            "petrol_kgCO2_per_l": 2.31,        # kgCO2e per litre
            "cng_kgCO2_per_l": 2.75,           # approx
            "waste_tCO2_per_ton": 1.2,
            "water_tCO2_per_ML": 0.35,
            "wastewater_tCO2_per_ML": 0.5,
            "building_kWh_per_m2_per_year": 50,  # proxy energy intensity
            "sequestration_per_tree_tCO2_per_year": -0.025
        }

        with st.form("cap_form_full"):
            city_name = st.selectbox("Select City", list(cities_districts.keys()), key="cap_city_full_select")

            st.subheader("Energy")
            electricity_mwh = st.number_input("Electricity consumption (MWh/year)", min_value=0.0, step=1.0, key="cap_elec")
            diesel_l = st.number_input("Diesel consumption (litres/year)", min_value=0.0, step=1.0, key="cap_diesel")
            petrol_l = st.number_input("Petrol consumption (litres/year)", min_value=0.0, step=1.0, key="cap_petrol")

            st.subheader("Transport")
            transport_diesel_l = st.number_input("Transport diesel (litres/year)", min_value=0.0, step=1.0, key="cap_trans_diesel")
            transport_petrol_l = st.number_input("Transport petrol (litres/year)", min_value=0.0, step=1.0, key="cap_trans_petrol")
            transport_cng_l = st.number_input("Transport CNG (litres/year) - if applicable", min_value=0.0, step=1.0, key="cap_trans_cng")

            st.subheader("Buildings")
            built_area_m2 = st.number_input("Total built-up area (m²)", min_value=0.0, step=1.0, key="cap_built_area")

            st.subheader("Industry")
            industry_energy_mwh = st.number_input("Industrial electricity (MWh/year)", min_value=0.0, step=1.0, key="cap_ind_elec")

            st.subheader("Water")
            water_ML = st.number_input("Water supplied (ML/year)", min_value=0.0, step=0.1, key="cap_water")
            wastewater_ML = st.number_input("Wastewater treated (ML/year)", min_value=0.0, step=0.1, key="cap_wastewater")

            st.subheader("Waste")
            waste_t = st.number_input("Municipal solid waste generated (tonnes/year)", min_value=0.0, step=0.1, key="cap_waste")

            st.subheader("Urban Green / Other")
            trees_count = st.number_input("Number of urban trees (count)", min_value=0, step=1, key="cap_trees")
            other_emissions_t = st.number_input("Other emissions (tCO2e/year) - e.g., fugitive, process emissions", min_value=0.0, step=0.1, key="cap_other")

            st.write("**Optional verification files (one per sector)**")
            _file_energy = st.file_uploader("Energy file (optional)", type=["csv", "xlsx", "pdf"], key="file_energy")
            _file_transport = st.file_uploader("Transport file (optional)", type=["csv", "xlsx", "pdf"], key="file_transport")
            _file_buildings = st.file_uploader("Buildings file (optional)", type=["csv", "xlsx", "pdf"], key="file_buildings")
            _file_industry = st.file_uploader("Industry file (optional)", type=["csv", "xlsx", "pdf"], key="file_industry")
            _file_water = st.file_uploader("Water file (optional)", type=["csv", "xlsx", "pdf"], key="file_water")
            _file_waste = st.file_uploader("Waste file (optional)", type=["csv", "xlsx", "pdf"], key="file_waste")

            submit_cap = st.form_submit_button("Save & Calculate Emissions")

        # After form submission (download button cannot be inside form)
        if submit_cap:
            # compute emissions (convert fuel kg->t by /1000)
            energy_em = electricity_mwh * EF["electricity_tCO2_per_MWh"] + (diesel_l * EF["diesel_kgCO2_per_l"] / 1000.0) + (petrol_l * EF["petrol_kgCO2_per_l"] / 1000.0)
            transport_em = (transport_diesel_l * EF["diesel_kgCO2_per_l"] / 1000.0) + (transport_petrol_l * EF["petrol_kgCO2_per_l"] / 1000.0) + (transport_cng_l * EF["cng_kgCO2_per_l"] / 1000.0)
            buildings_em = (built_area_m2 * EF["building_kWh_per_m2_per_year"] / 1000.0) * EF["electricity_tCO2_per_MWh"]
            industry_em = industry_energy_mwh * EF["electricity_tCO2_per_MWh"]
            water_em = water_ML * EF["water_tCO2_per_ML"]
            wastewater_em = wastewater_ML * EF["wastewater_tCO2_per_ML"]
            waste_em = waste_t * EF["waste_tCO2_per_ton"]
            trees_seq = trees_count * EF["sequestration_per_tree_tCO2_per_year"]
            other_em = other_emissions_t

            totals = {
                "Energy Emissions (tCO2e)": round(energy_em, 3),
                "Transport Emissions (tCO2e)": round(transport_em, 3),
                "Buildings Emissions (tCO2e)": round(buildings_em, 3),
                "Industry Emissions (tCO2e)": round(industry_em, 3),
                "Water Emissions (tCO2e)": round(water_em + wastewater_em, 3),
                "Waste Emissions (tCO2e)": round(waste_em, 3),
                "UGB Sequestration (tCO2e)": round(trees_seq, 3),
                "Other Emissions (tCO2e)": round(other_em, 3)
            }
            total_emissions = sum([v for v in totals.values()])

            # Build a row to store raw inputs + emissions
            row = {
                "City Name": city_name,
                "Electricity (MWh)": electricity_mwh,
                "Diesel (L)": diesel_l,
                "Petrol (L)": petrol_l,
                "Transport Diesel (L)": transport_diesel_l,
                "Transport Petrol (L)": transport_petrol_l,
                "Transport CNG (L)": transport_cng_l,
                "Built-up Area (m2)": built_area_m2,
                "Industry Electricity (MWh)": industry_energy_mwh,
                "Water (ML)": water_ML,
                "Wastewater (ML)": wastewater_ML,
                "Waste (t)": waste_t,
                "Trees (count)": trees_count,
                "Other Emissions (tCO2e)": other_em,
                # Emission columns
                "Energy Emissions (tCO2e)": totals["Energy Emissions (tCO2e)"],
                "Transport Emissions (tCO2e)": totals["Transport Emissions (tCO2e)"],
                "Buildings Emissions (tCO2e)": totals["Buildings Emissions (tCO2e)"],
                "Industry Emissions (tCO2e)": totals["Industry Emissions (tCO2e)"],
                "Water Emissions (tCO2e)": totals["Water Emissions (tCO2e)"],
                "Waste Emissions (tCO2e)": totals["Waste Emissions (tCO2e)"],
                "UGB Sequestration (tCO2e)": totals["UGB Sequestration (tCO2e)"],
                "Other Emissions (tCO2e)": totals["Other Emissions (tCO2e)"],
                "Total Emissions (tCO2e)": round(total_emissions, 3),
                "Saved At": datetime.now().isoformat()
            }

            # update cap_data (replace existing city row)
            if df_cap is None or df_cap.empty:
                df_cap = pd.DataFrame([row])
            else:
                df_cap = df_cap[df_cap["City Name"] != city_name]  # remove duplicate if exists
                df_cap = pd.concat([df_cap, pd.DataFrame([row])], ignore_index=True)

            # persist
            st.session_state.cap_data = df_cap
            df_cap.to_csv(CAP_DATA_FILE, index=False)

            # Update meta GHG Emissions in meta DB too (so home page shows)
            meta_df = st.session_state.data.copy()
            if meta_df is None or meta_df.empty:
                meta_df = pd.DataFrame(columns=[
                    "City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
                    "Environment Department Exist", "Department Name", "Head Name", "Department Email"
                ])
            # ensure district exists
            district_val = cities_districts.get(city_name, "")
            meta_df = meta_df[meta_df["City Name"] != city_name]
            meta_df = pd.concat([meta_df, pd.DataFrame([{
                "City Name": city_name,
                "District": district_val,
                "Population": meta_df[meta_df["City Name"] == city_name]["Population"].values[0] if (city_name in meta_df["City Name"].values) else "",
                "ULB Category": meta_df[meta_df["City Name"] == city_name]["ULB Category"].values[0] if (city_name in meta_df["City Name"].values) else "",
                "CAP Status": meta_df[meta_df["City Name"] == city_name]["CAP Status"].values[0] if (city_name in meta_df["City Name"].values) else "In Progress",
                "GHG Emissions": row["Total Emissions (tCO2e)"],
                "Environment Department Exist": meta_df[meta_df["City Name"] == city_name]["Environment Department Exist"].values[0] if (city_name in meta_df["City Name"].values) else "",
                "Department Name": meta_df[meta_df["City Name"] == city_name]["Department Name"].values[0] if (city_name in meta_df["City Name"].values) else "",
                "Head Name": meta_df[meta_df["City Name"] == city_name]["Head Name"].values[0] if (city_name in meta_df["City Name"].values) else "",
                "Department Email": meta_df[meta_df["City Name"] == city_name]["Department Email"].values[0] if (city_name in meta_df["City Name"].values) else ""
            }])], ignore_index=True)
            st.session_state.data = meta_df
            meta_df.to_csv(DATA_FILE, index=False)

            st.session_state.last_updated = datetime.now()
            st.success(f"CAP raw data saved for {city_name}. Total Emissions: {row['Total Emissions (tCO2e)']:,.3f} tCO2e")

            # Offer CSV download outside the form
            csv_bytes = df_cap.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download all CAP raw data (CSV)", data=csv_bytes, file_name="cap_raw_data.csv", mime="text/csv")
