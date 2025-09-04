# mahacap.py

import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin Password
# ---------------------------
ADMIN_PASSWORD = "eintrust123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

# ---------------------------
# Column normalization helpers
# ---------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
    )
    return df

ALIASES = {
    "City Name": ["City Name", "City", "ULB", "City_Name"],
    "District": ["District", "District Name", "Dist"],
    "Population(as per 2011)": ["Population(as per 2011)", "Population (2011)", "Population 2011"],
    "ULB Category": ["ULB Category", "ULB Type", "ULB_Category"],
    "Environment Department Exist": ["Environment Department Exist", "Env Dept Exists", "Environment Dept Exists"],
    "Department Name": ["Department Name", "Environment Department Name"],
    "Head Name": ["Head Name", "Department Head Name"],
    "Head Designantion": ["Head Designantion", "Head Designation"],
    "Head Qualification": ["Head Qualification"],
    "Department Email": ["Department Email", "Dept Email"],
    "Dedicated Climate Officer": ["Dedicated Climate Officer", "Climate Officer"],
    "Total Budget": ["Total Budget", "Budget Total", "Overall Budget", "ULB Total Budget"],
    "Environment Budget": ["Environment Budget", "Env Budget", "Environmental Budget"],
    "Budget % of Total": [
        "Budget % of Total", "Budget Percent of Total", "Budget Percentage of Total",
        "Environment Budget % of Total", "Env Budget % of Total", "Env Budget %", "Environment Budget %", "Budget %"
    ],
    "ESR Prepared": ["ESR Prepared"],
    "Latest ESR Year": ["Latest ESR Year", "ESR Year"],
    "CAP Status": ["CAP Status", "CAPStatus"],
    "CAP Consultant (If Any)": ["CAP Consultant (If Any)", "CAP Consultant"],
    "CSCAF Participation": ["CSCAF Participation"],
    "CSCAF Rank (If Any)": ["CSCAF Rank (If Any)", "CSCAF Rank"],
    "Majhi Vasundhara Abhiyan Participation": ["Majhi Vasundhara Abhiyan Participation", "MV Participation"],
    "Majhi Vasundhara Abhiyan Rank (If Any)": ["Majhi Vasundhara Abhiyan Rank (If Any)", "MV Rank"],
    "No. of Commissioner Transfers (Last 3 Years)": ["No. of Commissioner Transfers (Last 3 Years)", "Commissioner Transfers (3Y)"],
    "Political Support": ["Political Support"],
    "Any Green Initiative by Mayor/MLA": ["Any Green Initiative by Mayor/MLA", "Green Initiative by Mayor/MLA"],
    "Political Party in Power": ["Political Party in Power", "Ruling Party"],
    "Climate Risk Zone": ["Climate Risk Zone", "Risk Zone"],
    "Recent Climate Disaster": ["Recent Climate Disaster", "Recent Disaster"],
    "Citizen Awareness Programs Held": ["Citizen Awareness Programs Held", "Citizen Awareness Programs"],
    "Active NGOs": ["Active NGOs", "Active NGO's", "Active NGO’S"],
    "Climate Content on Website/Socials": ["Climate Content on Website/Socials", "Climate Content on Website", "Climate Content on Socials"],
    "School/College Partnerships": ["School/College Partnerships", "School Partnerships", "College Partnerships"],
    "City’s Top 3 Development Priorities": ["City’s Top 3 Development Priorities", "City's Top 3 Development Priorities", "Top 3 Development Priorities"],
    "Environment Mentioned in ULB Vision/Mission": ["Environment Mentioned in ULB Vision/Mission", "Environment in ULB Vision/Mission"],
    "Remarks": ["Remarks", "Comments"],
    "Data Source": ["Data Source", "Source"],
    "GHG Emissions": ["GHG Emissions", "Total Emissions"]
}

def canon(s: str) -> str:
    s = str(s).lower().strip()
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[’'`\"()%/\.]", "", s)
    return s

def find_col(df: pd.DataFrame, target: str) -> str | None:
    for alias in ALIASES.get(target, [target]):
        for col in df.columns:
            if canon(col) == canon(alias):
                return col
    for col in df.columns:
        if canon(col) == canon(target):
            return col
    return None

def get_val(row: pd.Series, df_cols: pd.Index, target: str, default="—"):
    col = find_col(pd.DataFrame(columns=df_cols), target)
    if col is None:
        return default
    val = row.get(col, default)
    if pd.isna(val):
        return default
    return val

# ---------------------------
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    try:
        return normalize_columns(pd.read_excel("data/cities_data.xlsx"))
    except FileNotFoundError:
        st.warning("Data file not found. Admin must upload cities_data.xlsx")
        return None

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ---------------------------
# Admin Login
# ---------------------------
def login():
    with st.form("login_form"):
        password = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.admin_mode = True
                st.success("Admin login successful")
            else:
                st.error("Incorrect password")

# ---------------------------
# UI
# ---------------------------
st.title("🌍 Maharashtra CAP Dashboard")
st.markdown("### Engage • Enlighten • Empower")

# ---------------------------
# Sidebar Logo
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

menu = st.sidebar.radio("Navigate", ["Home", "City Dashboard", "Admin Login"])

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("📊 State & District Overview")
    df = st.session_state.data
    if df is not None:
        total_cities = df.shape[0]
        cities_done = df[df["CAP Status"] == "Approved"].shape[0]
        st.metric("Total Cities", total_cities)
        st.metric("Cities with CAP Completed", cities_done)

        if "District" in df.columns:
            district_summary = df.groupby("District")["CAP Status"].apply(lambda x: (x=="Approved").sum()).reset_index()
            district_summary.columns = ["District", "CAPs Done"]
            fig = px.bar(district_summary, x="District", y="CAPs Done", text="CAPs Done",
                         title="District-wise CAP Completion")
            st.plotly_chart(fig, use_container_width=True)

        ghg_col = find_col(df, "GHG Emissions")
        if ghg_col:
            fig2 = px.bar(df, x="City Name", y=ghg_col, title="GHG Emissions by City", text=ghg_col)
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No data loaded. Admin must upload dataset.")

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    df = st.session_state.data
    if df is not None:
        city_col = find_col(df, "City Name")
        if city_col:
            city = st.selectbox("Select City", df[city_col].dropna().unique())
            city_row = df[df[city_col] == city].iloc[0]

            st.subheader(f"🏙️ {city} Details")

            with st.expander("🏠 Basic Info", expanded=True):
                st.write(f"**District:** {get_val(city_row, df.columns, 'District')}")
                st.write(f"**Population (2011):** {get_val(city_row, df.columns, 'Population(as per 2011)')}")
                st.write(f"**ULB Category:** {get_val(city_row, df.columns, 'ULB Category')}")

            with st.expander("🏢 Environment Dept"):
                st.write(f"**Exists:** {get_val(city_row, df.columns, 'Environment Department Exist')}")
                st.write(f"**Dept Name:** {get_val(city_row, df.columns, 'Department Name')}")
                st.write(f"**Head Name:** {get_val(city_row, df.columns, 'Head Name')}")
                st.write(f"**Head Designation:** {get_val(city_row, df.columns, 'Head Designantion')}")
                st.write(f"**Head Qualification:** {get_val(city_row, df.columns, 'Head Qualification')}")
                st.write(f"**Email:** {get_val(city_row, df.columns, 'Department Email')}")
                st.write(f"**Dedicated Climate Officer:** {get_val(city_row, df.columns, 'Dedicated Climate Officer')}")

            with st.expander("💰 Budget & ESR"):
                st.write(f"**Total Budget:** {get_val(city_row, df.columns, 'Total Budget')}")
                st.write(f"**Environment Budget:** {get_val(city_row, df.columns, 'Environment Budget')}")
                st.write(f"**% of Total:** {get_val(city_row, df.columns, 'Budget % of Total')}")
                st.write(f"**ESR Prepared:** {get_val(city_row, df.columns, 'ESR Prepared')}")
                st.write(f"**Latest ESR Year:** {get_val(city_row, df.columns, 'Latest ESR Year')}")

            with st.expander("📑 CAP / CSCAF / Majhi Vasundhara"):
                st.write(f"**CAP Status:** {get_val(city_row, df.columns, 'CAP Status')}")
                st.write(f"**CAP Consultant:** {get_val(city_row, df.columns, 'CAP Consultant (If Any)')}")
                st.write(f"**CSCAF Participation:** {get_val(city_row, df.columns, 'CSCAF Participation')}")
                st.write(f"**CSCAF Rank:** {get_val(city_row, df.columns, 'CSCAF Rank (If Any)')}")
                st.write(f"**MV Participation:** {get_val(city_row, df.columns, 'Majhi Vasundhara Abhiyan Participation')}")
                st.write(f"**MV Rank:** {get_val(city_row, df.columns, 'Majhi Vasundhara Abhiyan Rank (If Any)')}")

            with st.expander("🌡️ GHG & CAP Actions"):
                st.write(f"**Total GHG Emissions:** {get_val(city_row, df.columns, 'GHG Emissions')} MTCO2e")
                sectors = ["Energy", "Transport", "Waste", "Industry", "Other"]
                emissions = [0.3, 0.25, 0.15, 0.2, 0.1]
                total = pd.to_numeric(get_val(city_row, df.columns, 'GHG Emissions'), errors="coerce")
                sector_values = [total*v if pd.notna(total) else 0 for v in emissions]
                sector_df = pd.DataFrame({"Sector": sectors, "Emissions": sector_values})
                fig3 = px.bar(sector_df, x="Sector", y="Emissions", title="Sectoral GHG Emissions")
                st.plotly_chart(fig3, use_container_width=True)

                st.write("**Suggested CAP Actions to reach Net Zero 2050:**")
                st.write("- Increase renewable energy share")
                st.write("- Enhance public transport & EV adoption")
                st.write("- Waste to energy initiatives")
                st.write("- Energy efficiency programs in buildings & industry")
                st.write("- Urban forestry and green cover enhancement")

    else:
        st.info("No data loaded. Admin must upload dataset.")

# ---------------------------
# Admin Login / Upload
# ---------------------------
elif menu == "Admin Login":
    if not st.session_state.authenticated:
        login()
    else:
        st.header("🔑 Admin Panel")
        st.write("Upload or update the dataset for all cities.")
        uploaded = st.file_uploader("Upload Excel (cities_data.xlsx)", type=["xlsx"])
        if uploaded:
            df_up = pd.read_excel(uploaded)
            df_up = normalize_columns(df_up)
            st.session_state.data = df_up
            st.success("Data updated successfully!")
