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

meta_cols = [
    "City Name", "District", "Population", "ULB Category",
    "CAP Status", "GHG Emissions", "Environment Department Exist",
    "Department Name", "Head Name", "Department Email"
]
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
    total_selected = len(cities_districts)
    reporting = df.shape[0]
    completed = df[df["CAP Status"].str.lower() == "completed"].shape[0] if "CAP Status" in df.columns else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Cities Selected", f"{total_selected}")
    col2.metric("Cities Reporting", f"{reporting}")
    col3.metric("CAPs Completed", f"{completed}")

    if not df.empty and "GHG Emissions" in df.columns:
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        fig2 = px.bar(
            df.sort_values("GHG Emissions", ascending=False),
            x="City Name",
            y="GHG Emissions",
            title="City-level GHG (tCO2e)",
            text="GHG Emissions",
            color_discrete_sequence=["#3E6BE6"]
        )
        fig2.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig2, use_container_width=True)

# ---------------- Estimated GHG Emissions Chart ----------------
    if not df.empty and "Population" in df.columns:
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce").fillna(0)

        # Use an assumed emission factor (tCO2e per person/year)
        EMISSION_FACTOR = 2.5
        df["Estimated GHG Emissions"] = df["Population"] * EMISSION_FACTOR

        fig3 = px.bar(
            df.sort_values("Estimated GHG Emissions", ascending=False),
            x="City Name",
            y="Estimated GHG Emissions",
            title=f"Estimated GHG Emissions (tCO2e) — based on {EMISSION_FACTOR} tCO2e/person",
            text="Estimated GHG Emissions",
            color_discrete_sequence=["#E67E22"]
        )
        fig3.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
        st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# City Dashboard
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

            fig_bar = px.bar(chart_df, x="Sector", y="Emissions", text="Emissions",
                             title="Sector Emissions (tCO2e)", color_discrete_sequence=["#3E6BE6"])
            fig_bar.update_layout(plot_bgcolor="#0f0f10", paper_bgcolor="#0f0f10", font_color="#E6E6E6")
            st.plotly_chart(fig_bar, use_container_width=True)

            st.write("### Emissions by Sector")
            st.table(chart_df.assign(Emissions=lambda d: d["Emissions"].map(lambda v: f"{v:,.2f}")))

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
                    data = [["Sector", "Emissions (tCO2e)"]] + [[s, f"{v:,.2f}"] for s, v in sectors.items()]
                    t = Table(data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3E6BE6")),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.white)
                    ]))
                    elements.append(t)
                    doc.build(elements)
                    buffer.seek(0)
                    st.download_button("Download PDF", buffer,
                                       file_name=f"{city}_GHG_Report.pdf",
                                       mime="application/pdf")
        else:
            st.warning("PDF generation not available. Install reportlab library.")

# ---------------------------
# Admin Panel
# ---------------------------
if menu == "Admin":
    st.header("🔑 Admin Login")

    # If not logged in, show password field
    if not st.session_state.get("logged_in", False):
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == "admin123":   # <-- you can change this password
                st.session_state.logged_in = True
                st.success("✅ Login successful!")
                st.experimental_rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")

    else:
        # If logged in, show admin controls
        st.header("Admin Panel – Manage City Data")

        df = st.session_state.data

        if df.empty:
            st.info("No city records found. Please add data from the Input Form.")
        else:
            # ---------------------------
            # 1) Overview Table
            # ---------------------------
            st.subheader("📋 All City Records (Overview)")
            st.dataframe(df, use_container_width=True)

            st.markdown("---")

            # ---------------------------
            # 2) Editable Table with Actions
            # ---------------------------
            st.subheader("✏️ Manage Entries")

            for idx, row in df.iterrows():
                with st.container():
                    cols = st.columns(len(df.columns) + 2)  # extra 2 cols for Edit/Delete

                    # Show existing values
                    for i, colname in enumerate(df.columns):
                        cols[i].write(row[colname])

                    # --- Edit Option ---
                    if cols[-2].button("✏️ Edit", key=f"edit_{idx}"):
                        with st.form(f"edit_form_{idx}"):
                            st.write(f"Editing entry for **{row['City Name']}**")

                            new_name = st.text_input("City Name", row["City Name"])
                            new_pop = st.number_input(
                                "Population",
                                value=int(row["Population"]) if "Population" in df.columns else 0
                            )
                            new_ghg = st.number_input(
                                "GHG Emissions (tCO2e)",
                                value=float(row["GHG Emissions"]) if "GHG Emissions" in df.columns else 0.0
                            )
                            new_status = st.selectbox(
                                "CAP Status",
                                ["Not Started", "In Progress", "Completed"],
                                index=["Not Started", "In Progress", "Completed"].index(row["CAP Status"])
                                if "CAP Status" in df.columns and row["CAP Status"] in ["Not Started", "In Progress", "Completed"] else 0
                            )

                            submitted = st.form_submit_button("Save Changes")
                            if submitted:
                                df.loc[idx, "City Name"] = new_name
                                if "Population" in df.columns:
                                    df.loc[idx, "Population"] = new_pop
                                if "GHG Emissions" in df.columns:
                                    df.loc[idx, "GHG Emissions"] = new_ghg
                                if "CAP Status" in df.columns:
                                    df.loc[idx, "CAP Status"] = new_status

                                st.session_state.data = df
                                st.success(f"✅ {new_name} updated successfully!")
                                st.experimental_rerun()

                    # --- Delete Option ---
                    if cols[-1].button("🗑️ Delete", key=f"delete_{idx}"):
                        df = df.drop(idx)
                        st.session_state.data = df
                        st.success(f"✅ {row['City Name']} deleted successfully!")
                        st.experimental_rerun()

# ---------------------------
# CAP Preparation Page
# ---------------------------
elif menu == "CAP Preparation":
    st.header("CAP : Data Collection")

    if not st.session_state.authenticated:
        admin_login()
    else:
        with st.form("cap_form", clear_on_submit=False):
            city = st.selectbox("Select City", list(cities_districts.keys()))
            st.markdown("### Enter Emissions (tCO2e) for each sector")

            sectors = ["Energy", "Transport", "Buildings", "Industry", "Water", "Waste", "Urban Green / Other"]
            cap_values = {}
            for sec in sectors:
                cap_values[sec] = st.number_input(f"{sec} Emissions (tCO2e)", min_value=0.0, value=0.0, step=1.0)

            file_upload = st.file_uploader("Attach verification file (optional)", type=["pdf", "xlsx", "csv"])

            submit_cap = st.form_submit_button("Save CAP Data")
            if submit_cap:
                new_row = {"City Name": city}
                for sec, val in cap_values.items():
                    new_row[f"{sec} Emissions (tCO2e)"] = val

                df_cap = st.session_state.cap_data
                if not df_cap.empty and city in df_cap["City Name"].values:
                    for k, v in new_row.items():
                        df_cap.loc[df_cap["City Name"] == city, k] = v
                else:
                    df_cap = pd.concat([df_cap, pd.DataFrame([new_row])], ignore_index=True)

                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE, index=False)
                st.session_state.last_updated = datetime.now()
                st.success(f"CAP data for {city} saved successfully!")
