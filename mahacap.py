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
except Exception:
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
def load_meta_data():
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception:
            return pd.DataFrame(columns=[
                "City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
                "Environment Department Exist", "Department Name", "Head Name", "Department Email"
            ])
    else:
        return pd.DataFrame(columns=[
            "City Name", "District", "Population", "ULB Category", "CAP Status", "GHG Emissions",
            "Environment Department Exist", "Department Name", "Head Name", "Department Email"
        ])

def load_cap_data():
    if os.path.exists(CAP_DATA_FILE):
        try:
            return pd.read_csv(CAP_DATA_FILE)
        except Exception:
            return pd.DataFrame()
    else:
        return pd.DataFrame()

st.session_state.data = load_meta_data()
st.session_state.cap_data = load_cap_data()

# ---------------------------
# Helper Functions
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
# Dark / Professional CSS
# ---------------------------
st.markdown("""
<style>
/* App background */
[data-testid="stAppViewContainer"] {
  background-color: #0B0C0E;
  color: #E6E6E6;
}
/* Sidebar */
[data-testid="stSidebar"] {
  background-color: #111214;
  color: #E6E6E6;
}
/* Buttons */
.stButton>button {
  background-color: #3E6BE6 !important;
  color: #FFFFFF !important;
  border-radius: 6px !important;
  height: 40px !important;
  font-size: 14px !important;
}
.stButton>button:hover {
  background-color: #2E50B2 !important;
}
/* Metrics color */
[data-testid="stMetricValue"] {
  color: #1F7A1F !important;
  font-weight: 700;
}
/* Expander */
.stExpander>div>div>div>div {
  background-color: #141518 !important;
  color: #E6E6E6 !important;
}
/* Inputs */
input, textarea, select {
  background-color: #141518 !important;
  color: #E6E6E6 !important;
  border-color: #3E6BE6 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Admin Login Form
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
st.sidebar.image(
    "https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)
if st.sidebar.button("🏠 Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("🏙️ City Dashboard"):
    st.session_state.menu = "City Dashboard"
if st.sidebar.button("🛠️ Admin Panel"):
    st.session_state.menu = "Admin Panel"
if st.session_state.authenticated:
    if st.sidebar.button("📊 CAP Preparation"):
        st.session_state.menu = "CAP Preparation"

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra Climate Action Plan Dashboard")
    st.markdown("Maharashtra's Net Zero Journey — Professional Government Dashboard")
    df = st.session_state.data.copy()

    total_selected = len(cities_districts)
    reporting = df.shape[0]
    completed = df[df["CAP Status"].str.lower() == "completed"].shape[0] if "CAP Status" in df.columns else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Cities Selected", f"{total_selected}")
    col2.metric("Cities Reporting", f"{reporting}")
    col3.metric("CAPs Completed", f"{completed}")

    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig = px.bar(df.sort_values("GHG Emissions", ascending=False),
                     x="City Name", y="GHG Emissions",
                     title="City-level GHG (tCO2e)",
                     text="GHG Emissions",
                     color_discrete_sequence=["#3E6BE6"])
        fig.update_layout(plot_bgcolor="#0B0C0E", paper_bgcolor="#0B0C0E", font_color="#E6E6E6")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    st.header("City Dashboard")
    df_meta = st.session_state.data.copy()
    df_cap = st.session_state.cap_data.copy() if not st.session_state.cap_data.empty else pd.DataFrame()

    city = st.selectbox("Select City", list(cities_districts.keys()))

    meta_row = df_meta[df_meta["City Name"] == city].iloc[0] if (not df_meta.empty and city in df_meta["City Name"].values) else None
    st.subheader(f"{city} — Overview")
    if meta_row is not None:
        st.write(f"**District:** {safe_get(meta_row, 'District')}")
        st.write(f"**Population (2011):** {format_population(safe_get(meta_row, 'Population'))}")
        st.write(f"**ULB Category:** {safe_get(meta_row, 'ULB Category')}")
        st.write(f"**CAP Status:** {safe_get(meta_row, 'CAP Status')}")
    else:
        st.write(f"**District:** {cities_districts.get(city, '—')}")

    if not df_cap.empty and city in df_cap["City Name"].values:
        cap_row = df_cap[df_cap["City Name"] == city].iloc[0]
        sector_cols = [c for c in cap_row.index if c.endswith("Emissions (tCO2e)")]
        sectors = {c.replace(" Emissions (tCO2e)", ""): float(cap_row[c]) for c in sector_cols}

        if sectors:
            chart_df = pd.DataFrame({"Sector": list(sectors.keys()), "Emissions": list(sectors.values())})
            fig_pie = px.pie(chart_df, names="Sector", values="Emissions",
                             title="Sector-wise Emissions (tCO2e)",
                             color_discrete_sequence=px.colors.sequential.Blues)
            fig_pie.update_layout(plot_bgcolor="#0B0C0E", paper_bgcolor="#0B0C0E", font_color="#E6E6E6")
            st.plotly_chart(fig_pie, use_container_width=True)

            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions",
                             title="Sector Emissions (tCO2e)",
                             color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0B0C0E", paper_bgcolor="#0B0C0E", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v: f"{v:,.2f}")))

            if st.session_state.last_updated:
                st.markdown(f"*Last Updated: {st.session_state.last_updated.strftime('%B %Y')}*")
            elif os.path.exists(CAP_DATA_FILE):
                last_mod = datetime.fromtimestamp(os.path.getmtime(CAP_DATA_FILE))
                st.markdown(f"*Last Updated: {last_mod.strftime('%B %Y')}*")

            # PDF download
            st.subheader("Download GHG Inventory Report (PDF)")
            if not PDF_AVAILABLE:
                st.warning("PDF generation library not available. Install `reportlab` to enable downloads.")
            else:
                with st.form("pdf_form"):
                    user_name = st.text_input("Full Name")
                    user_email = st.text_input("Work Email")
                    user_contact = st.text_input("Contact Number")
                    pdf_submit = st.form_submit_button("Generate PDF")

                if pdf_submit:
                    if not user_name or not user_email or not user_contact:
                        st.error("Please provide Name, Email, and Contact Number.")
                    else:
                        buffer = io.BytesIO()
                        doc = SimpleDocTemplate(buffer, pagesize=A4)
                        styles = getSampleStyleSheet()
                        elements = [
                            Paragraph(f"City GHG Inventory — {city}", styles["Title"]),
                            Spacer(1, 6),
                            Paragraph(f"District: {cities_districts.get(city, '—')}", styles["Normal"]),
                            Paragraph(f"Generated for: {user_name}", styles["Normal"]),
                            Paragraph(f"Email: {user_email}", styles["Normal"]),
                            Paragraph(f"Contact: {user_contact}", styles["Normal"]),
                            Paragraph(f"Generated on: {datetime.now().strftime('%d %b %Y %H:%M')}", styles["Normal"]),
                            Spacer(1, 12)
                        ]
                        table_data = [["Sector", "Emissions (tCO2e)"]] + [[s, f"{e:,.2f}"] for s, e in sectors.items()] + [["Total", f"{sum(sectors.values()):,.2f}"]]
                        table = Table(table_data, hAlign="LEFT", colWidths=[300, 150])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#3E6BE6")),
                            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                            ('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                            ('BOTTOMPADDING', (0,0), (-1,0), 12),
                            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#141518")),
                            ('TEXTCOLOR',(0,1),(-1,-1), colors.white),
                            ('GRID', (0,0), (-1,-1), 0.5, colors.gray)
                        ]))
                        elements.append(table)
                        doc.build(elements)
                        st.download_button("⬇️ Download PDF", buffer.getvalue(), file_name=f"{city}_GHG_Report.pdf", mime="application/pdf")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
    st.header("Admin Panel — Manage Data")
    if not st.session_state.authenticated:
        st.warning("Admin login required to access this panel.")
        admin_login()
    else:
        st.success("Admin Authenticated")
        st.subheader("Upload/Update City Data")
        uploaded_file = st.file_uploader("Upload CSV", type="csv")
        if uploaded_file:
            try:
                df_new = pd.read_csv(uploaded_file)
                df_new.to_csv(DATA_FILE, index=False)
                st.session_state.data = df_new
                st.success("City data uploaded successfully!")
            except Exception as e:
                st.error(f"Error uploading file: {e}")
