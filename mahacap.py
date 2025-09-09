# mahacap.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from datetime import datetime

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
    "Bhiwandi-Nizampur": "Thane",
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
def reset_all_data():
    # Clear session state
    st.session_state.clear()
    
    # Optionally, reset CSV files
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
    if os.path.exists(CAP_DATA_FILE):
        os.remove(CAP_DATA_FILE)
    
    st.success("All data has been reset successfully!")
    st.experimental_rerun()  # Refresh the app

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
# Dark / Professional SaaS CSS
# ---------------------------
st.markdown("""
<style>
/* ------------------- Main App ------------------- */
[data-testid="stAppViewContainer"] {
    background-color: #1E1E2F;  /* Deep dark background */
    color: #E6E6E6;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* ------------------- Sidebar ------------------- */
[data-testid="stSidebar"] {
    background-color: #2B2B3B; 
    color: #E6E6E6;
    padding-top: 20px;
    font-size: 18px;
    font-weight: 500;
}
[data-testid="stSidebar"] img {
    margin-bottom: 25px;
    border-radius: 6px;
}
[data-testid="stSidebar"] hr {
    border: 0.5px solid #3A3A4A;
    margin: 20px 0;
}
.sidebar-footer {
    color: #B0BEC5;
    font-size: 13px;
    text-align: center;
    margin-top: 30px;
}

/* ------------------- Buttons ------------------- */
.stButton>button {
    background-color: #3A8B34; /* Primary green */
    color: #FFFFFF; 
    border-radius: 8px; 
    height: 45px;
    font-size: 18px;
    font-weight: 600;
    width: 100%;
    transition: all 0.2s ease-in-out;
}
.stButton>button:hover {
    background-color: #2E6B29;
}

/* Active/selected sidebar buttons */
.stButton>button[data-active="true"] {
    background-color: #42A5F5; 
    color: #FFFFFF;
}

/* ------------------- Metrics / Cards ------------------- */
[data-testid="stMetricValue"] {
    color: #54c750; 
    font-weight: 700;
    font-size: 26px;
}
.stCard {
    background-color: #2B2B3B;
    padding: 18px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 12px;
    transition: all 0.2s ease-in-out;
}
.stCard:hover {
    background-color: #353548;
}
.stCard h4 {
    margin: 0;
    font-weight: 500;
    color: #E6E6E6;
    font-size: 16px;
}
.stCard h2 {
    margin: 6px 0 0 0;
    font-weight: 700;
    color: #54c750;
    font-size: 28px;
}

/* ------------------- Inputs & Forms ------------------- */
input, textarea, select {
    background-color: #2B2B3B; 
    color: #E6E6E6; 
    border: 1px solid #54c750;
    border-radius: 6px;
    padding: 6px 10px;
}
.stExpander>div>div>div>div {
    background-color: #2B2B3B; 
    color: #E6E6E6;
}

/* ------------------- Tables ------------------- */
.stDataFrame, .stTable {
    color: #E6E6E6;
    background-color: #1E1E2F;
    border-radius: 8px;
}

/* ------------------- Links ------------------- */
a {
    color: #42A5F5;
    text-decoration: none;
}
a:hover {
    text-decoration: underline;
}

/* ------------------- Headers ------------------- */
h2, h3, h4 {
    color: #CFD8DC;
    font-weight: 600;
}

/* ------------------- Scrollbar ------------------- */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: #1E1E2F;
}
::-webkit-scrollbar-thumb {
    background-color: #42A5F5;
    border-radius: 6px;
}

/* ------------------- Dark theme consistency for charts ------------------- */
[data-testid="stPlotlyChart"] {
    background-color: #1E1E2F !important;
}
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
# Sidebar (Premium SaaS Dark Gradient Style)
# ---------------------------
st.markdown("""
<style>
/* Sidebar background */
[data-testid="stSidebar"] {
    background-color: #1B1F23;
    color: #ECEFF1;
    padding-top: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Sidebar logo */
[data-testid="stSidebar"] img {
    margin-bottom: 25px;
    border-radius: 8px;
}

/* Sidebar buttons */
[data-testid="stSidebar"] button {
    background: linear-gradient(90deg, #2A2E33 0%, #2A2E33 100%);
    color: #ECEFF1;
    width: 100%;
    height: 55px;
    margin-bottom: 12px;
    border-radius: 6px;
    font-size: 20px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease-in-out;
    text-align: left;
    padding-left: 25px;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    position: relative;
    overflow: hidden;
}

/* Hover effect with subtle gradient */
[data-testid="stSidebar"] button:hover {
    background: linear-gradient(90deg, #3A3F46 0%, #2F343C 100%);
    transform: translateX(3px);
    cursor: pointer;
}

/* Active button sliding indicator */
[data-testid="stSidebar"] button[data-active="true"]::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 5px;
    height: 100%;
    background-color: #42A5F5;
    border-radius: 6px 0 0 6px;
    transition: all 0.3s ease-in-out;
}

/* Active button gradient */
[data-testid="stSidebar"] button[data-active="true"] {
    background: linear-gradient(90deg, #3A3F46 0%, #343A42 100%);
    color: #FFFFFF;
    font-weight: 700;
}

/* Separator lines */
[data-testid="stSidebar"] hr {
    border: 0.5px solid #546E7A;
    margin: 20px 0;
}

/* Sidebar footer */
.sidebar-footer {
    color: #B0BEC5;
    font-size: 13px;
    text-align: center;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Sidebar Logo
# ---------------------------
st.sidebar.image(
    "https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

# ---------------------------
# Sidebar Menu Buttons
# ---------------------------
menu_items = [("Home", "Home"), ("City Information", "City Information"), ("Admin", "Admin")]
if st.session_state.authenticated:
    menu_items.append(("CAP Generation", "CAP Generation"))

for label, page_name in menu_items:
    is_active = st.session_state.menu == page_name
    if st.sidebar.button(label, key=label):
        st.session_state.menu = page_name
        is_active = True
    st.markdown(f"""
    <script>
    const btn = window.parent.document.querySelector('button[key="{label}"]');
    if (btn) {{
        btn.setAttribute('data-active', {'true' if is_active else 'false'});
    }}
    </script>
    """, unsafe_allow_html=True)

# ---------------------------
# Sidebar Footer
# ---------------------------
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-footer'>EinTrust | © 2025</div>", unsafe_allow_html=True)

# ---------------------------
# Current Menu
# ---------------------------
menu = st.session_state.menu


# ---------------------------
# Home Page: Maharashtra Dashboard (Professional SaaS Look)
# ---------------------------
if menu == "Home":
    st.header("Maharashtra's Net Zero Journey")
    st.markdown("Climate Action Plan Dashboard")

    df = st.session_state.data.copy()

    # =====================
    # CAP Status Summary Cards with Gradient
    # =====================
    if not df.empty and "CAP Status" in df.columns:
        c1, c2, c3, c4 = st.columns(4)
        status_counts = {
            "Total Cities": len(df),
            "Not Started": df[df["CAP Status"].str.lower() == "not started"].shape[0],
            "In Progress": df[df["CAP Status"].str.lower() == "in progress"].shape[0],
            "Completed": df[df["CAP Status"].str.lower() == "completed"].shape[0]
        }

        card_colors = {
            "Total Cities": ["#4B8BF4", "#2C6BE0"],
            "Not Started": ["#FF6B6B", "#FF3B3B"],
            "In Progress": ["#FFA500", "#FF8C00"],
            "Completed": ["#28A745", "#1E7E34"]
        }

        for col, (title, val) in zip([c1, c2, c3, c4], status_counts.items()):
            color1, color2 = card_colors[title]
            col.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, {color1}, {color2});
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    color: white;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                ">
                    <h5>{title}</h5>
                    <h2>{format_indian_number(val)}</h2>
                </div>
                """, unsafe_allow_html=True
            )

    st.markdown("---")

    # =====================
    # Maharashtra Summary Metrics
    # =====================
    if "Maharashtra" in df["City Name"].values:
        maha_row = df[df["City Name"] == "Maharashtra"].iloc[0]
        population = maha_row.get("Population", 0)
        ghg_total = maha_row.get("GHG Emissions", 0)
        cap_status = maha_row.get("CAP Status", "—")
        cap_link = maha_row.get("CAP Link", "—")
        vulnerability_score = maha_row.get("Vulnerability Score", 0)

        est_ghg = round(population * (ghg_total/population if population else 0), 2)

        st.subheader("Maharashtra Overview")

        # Metrics row 1
        col1, col2, col3, col4 = st.columns(4)
        metrics = [
            ("CAP Status", cap_status),
            ("CAP Link", cap_link),
            ("GHG Emissions (tCO2e)", format_indian_number(ghg_total)),
            ("Estimated GHG by Population", format_indian_number(est_ghg))
        ]
        for col, (title, val) in zip([col1, col2, col3, col4], metrics):
            col.markdown(
                f"""
                <div style="
                    background-color:#f5f5f5;
                    padding:15px;
                    border-radius:10px;
                    text-align:center;
                    border:1px solid #ddd;
                ">
                    <h5>{title}</h5>
                    <h3>{val}</h3>
                </div>
                """, unsafe_allow_html=True
            )

        # Metrics row 2
        col5, col6 = st.columns(2)
        col5.metric("Vulnerability Assessment Score", round(vulnerability_score, 2))
        col6.metric("Population", format_indian_number(population))

        st.markdown("---")

        # =====================
        # Environmental Metrics
        # =====================
        st.subheader("Environmental Metrics")
        env_cols = ["Renewable Energy (MWh)", "Urban Green Area (ha)", "Municipal Solid Waste (tons)",
                    "Waste Landfilled (%)", "Waste Composted (%)", "Wastewater Treated (m3)"]
        col_groups = st.columns(3)
        for i, col_name in enumerate(env_cols):
            value = maha_row.get(col_name, 0)
            display_val = f"{value}%" if "%" in col_name else format_indian_number(value)
            col_groups[i % 3].metric(col_name, display_val)

        st.markdown("---")

        # =====================
        # Social Metrics
        # =====================
        st.subheader("Social Metrics")
        males = maha_row.get("Males", 0)
        females = maha_row.get("Females", 0)
        total_pop = males + females

        children_m = maha_row.get("Children Male", 0)
        children_f = maha_row.get("Children Female", 0)
        total_children = children_m + children_f

        literacy_m = maha_row.get("Male Literacy (%)", 0)
        literacy_f = maha_row.get("Female Literacy (%)", 0)
        literacy_avg = round((literacy_m + literacy_f)/2, 2)

        col1, col2, col3 = st.columns(3)
        col1.metric("Male Population", format_indian_number(males))
        col2.metric("Female Population", format_indian_number(females))
        col3.metric("Total Population", format_indian_number(total_pop))

        col4, col5, col6 = st.columns(3)
        col4.metric("Children (0-6 Male)", format_indian_number(children_m))
        col5.metric("Children (0-6 Female)", format_indian_number(children_f))
        col6.metric("Total Children (0-6)", format_indian_number(total_children))

        col7, col8, col9 = st.columns(3)
        col7.metric("Male Literacy (%)", f"{literacy_m}%")
        col8.metric("Female Literacy (%)", f"{literacy_f}%")
        col9.metric("Average Literacy (%)", f"{literacy_avg}%")

        col10, col11 = st.columns(2)
        col10.metric("Migrant Population (%)", f"{maha_row.get('Migrant (%)',0)}%")
        col11.metric("Slum Population (%)", f"{maha_row.get('Slum (%)',0)}%")

        col12, col13 = st.columns(2)
        col12.metric("BPL Households (%)", f"{maha_row.get('BPL Households (%)',0)}%")
        col13.metric("Urbanization Rate (%)", f"{maha_row.get('Urbanization Rate (%)',0)}%")

        st.markdown("---")

        # =====================
        # Contact Information
        # =====================
        st.subheader("Contact Information")
        col1, col2 = st.columns(2)
        col1.metric("Department Exist", maha_row.get("Department Exist", "—"))
        col2.metric("Department Name", maha_row.get("Department Name", "—"))

        col3, col4 = st.columns(2)
        col3.metric("Email", maha_row.get("Email", "—"))
        col4.metric("Contact Number", maha_row.get("Contact Number", "—"))

        st.metric("Website", maha_row.get("Website", "—"))

        st.markdown("---")

        # =====================
        # Charts with Hover Tooltips & Rounded Bars
        # =====================
        import plotly.express as px
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        df["Per Capita GHG"] = df.apply(lambda x: (x["GHG Emissions"]/x["Population"]) if x["Population"] else 0, axis=1)
        df["Estimated GHG"] = df["Population"] * df["Per Capita GHG"]

        # Total GHG Chart
        fig_ghg = px.bar(
            df,
            x="City Name",
            y="GHG Emissions",
            text=df["GHG Emissions"].apply(lambda x: format_indian_number(round(x,0))),
            title="City-wise Total GHG Emissions",
            color="GHG Emissions",
            color_continuous_scale="Blues"
        )
        fig_ghg.update_traces(marker_line_width=0, textposition="outside", hovertemplate="%{y:,} tCO2e")
        st.plotly_chart(fig_ghg, use_container_width=True)

        # Estimated GHG by Population Chart
        fig_est = px.bar(
            df,
            x="City Name",
            y="Estimated GHG",
            text=df["Estimated GHG"].apply(lambda x: format_indian_number(round(x,0))),
            title="Estimated GHG Emissions by Population",
            color="Estimated GHG",
            color_continuous_scale="Oranges"
        )
        fig_est.update_traces(marker_line_width=0, textposition="outside", hovertemplate="%{y:,} tCO2e")
        st.plotly_chart(fig_est, use_container_width=True)

        # Vulnerability Scores Chart
        evs_cols = ["GHG Emissions", "Municipal Solid Waste (tons)", "Wastewater Treated (m3)"]
        for col in evs_cols:
            if col not in df.columns:
                df[col] = 0
        max_vals_env = {col: df[col].max() or 1 for col in evs_cols}
        df["EVS"] = (
            df["GHG Emissions"]/max_vals_env["GHG Emissions"]*0.5 +
            df["Municipal Solid Waste (tons)"]/max_vals_env["Municipal Solid Waste (tons)"]*0.25 +
            df["Wastewater Treated (m3)"]/max_vals_env["Wastewater Treated (m3)"]*0.25
        ) * 100

        social_factors = {
            "Population": 0.3,
            "Households": 0.2,
            "Urbanization Rate (%)": 0.2,
            "Literacy Rate (%)": 0.15,
            "Poverty Rate (%)": 0.15
        }
        for col in social_factors:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        max_vals_social = {col: df[col].max() or 1 for col in social_factors}
        df["SVS"] = (
            (df["Population"]/max_vals_social["Population"])*0.3 +
            (df["Households"]/max_vals_social["Households"])*0.2 +
            (df["Urbanization Rate (%)"]/max_vals_social["Urbanization Rate (%)"])*0.2 +
            (1 - df["Literacy Rate (%)"]/max_vals_social["Literacy Rate (%)"])*0.15 +
            (df["Poverty Rate (%)"]/max_vals_social["Poverty Rate (%)"])*0.15
        ) * 100

        vuln_df = df[["City Name", "EVS", "SVS"]].melt(id_vars="City Name", var_name="Score Type", value_name="Score")
        fig_vuln = px.bar(
            vuln_df,
            x="City Name",
            y="Score",
            color="Score Type",
            barmode="group",
            text=vuln_df["Score"].apply(lambda x: f"{round(x,1)}"),
            title="City Vulnerability Scores (Environmental vs Social)",
            color_discrete_map={"EVS":"#1f77b4","SVS":"#ff7f0e"}
        )
        fig_vuln.update_traces(textposition="outside", hovertemplate="%{y:.1f}")
        fig_vuln.update_layout(
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            font_color="#000000",
            xaxis_title=None,
            yaxis_title="Vulnerability Score (0-100)"
        )
        st.plotly_chart(fig_vuln, use_container_width=True)

# ---------------------------
# City Information Page
# ---------------------------
elif menu == "City Information":
    st.markdown("<h2 style='margin-bottom:15px;'>City Information Dashboard</h2>", unsafe_allow_html=True)
    df_meta = st.session_state.data.copy()
    city = st.selectbox("Select City", list(cities_districts.keys()))

    if not df_meta.empty and city in df_meta["City Name"].values:
        row = df_meta[df_meta["City Name"] == city].iloc[0]
        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- Card Rendering Function ----------
        def render_card(col, label, value, inputed_value=True, bg_color="#34495E"):
            """
            col           : Streamlit column to render the card
            label         : Metric label
            value         : Metric value
            inputed_value : If True, value is actual inputed data (shows bold + colored)
            bg_color      : Background color of card
            """
            value_html = f"<b style='color:#2E7D32; font-size:16px;'>{value}</b>" if inputed_value else f"{value}"
            card_html = f"""
            <div style='
                background-color:{bg_color};
                color:#ECEFF1;
                padding:14px 10px;
                border-radius:10px;
                font-size:15px;
                text-align:center;
                min-height:70px;
                margin-bottom:10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.4);
                transition: transform 0.2s, box-shadow 0.2s;
            '
            onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 10px rgba(0,0,0,0.5)';"
            onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.4)';"
            >
                {label}<br>{value_html}
            </div>
            """
            col.markdown(card_html, unsafe_allow_html=True)

        # ---------- BASIC INFORMATION ----------
        st.markdown("<h4>Basic Information</h4>", unsafe_allow_html=True)
        population = row.get("Population", 0)
        area = row.get("Area (sq.km)", row.get("Geographical Area (sq. km)", 0))
        density = round(population / area) if area else "—"
        est_year = int(row.get("Est. Year", 0))
        cap_status = row.get("CAP Status", "—")
        cap_link = row.get("CAP Link", "")

        cap_colors = {"completed": "#66BB6A", "in progress": "#FFA726", "not started": "#EF5350"}
        cap_color = cap_colors.get(cap_status.lower(), "#34495E")

        basic_metrics = [
            ("District", row.get("District", "—")),
            ("ULB Category", row.get("ULB Category", "—")),
            ("Population", format_indian_number(population)),
            ("Area (sq.km)", format_indian_number(area)),
            ("Density (/sq.km)", format_indian_number(density)),
            ("Est. Year", est_year),
            ("CAP Status", cap_status)
        ]

        for i in range(0, len(basic_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, basic_metrics[i:i+3]):
                bg = cap_color if label == "CAP Status" else "#34495E"
                inputed = True if label not in ["District", "ULB Category"] else False
                render_card(col, label, value, inputed_value=inputed, bg_color=bg)

        # CAP Link
        if cap_link:
            link_html = f"""
            <div style='
                background-color:#34495E;
                color:#42A5F5;
                padding:12px;
                border-radius:10px;
                font-size:14px;
                text-align:center;
                margin-top:6px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.4);
                transition: transform 0.2s, box-shadow 0.2s;
            '
            onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 10px rgba(0,0,0,0.5)';"
            onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.4)';"
            >
                <a href='{cap_link}' target='_blank' style='color:#42A5F5; text-decoration:underline;'>View CAP Document</a>
            </div>
            """
            st.markdown(link_html, unsafe_allow_html=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- ENVIRONMENTAL INFORMATION ----------
        st.markdown("<h4>Environmental Information</h4>", unsafe_allow_html=True)
        ghg_total = row.get("GHG Emissions", 0)
        per_capita_ghg = round(ghg_total / population) if population else 0
        renewable_energy = row.get("Renewable Energy (MWh)", 0)
        urban_green = row.get("Urban Green Area (ha)", 0)
        solid_waste = row.get("Municipal Solid Waste (tons)", 0)
        wastewater = row.get("Wastewater Treated (m3)", 0)
        waste_landfilled = row.get("Waste Landfilled (%)", 0)
        waste_composted = row.get("Waste Composted (%)", 0)

        env_metrics = [
            ("GHG Emissions (tCO2e)", format_indian_number(ghg_total)),
            ("Per Capita Emissions (tCO2e)", format_indian_number(per_capita_ghg)),
            ("Renewable Energy (MWh)", format_indian_number(renewable_energy)),
            ("Urban Green Area (ha)", format_indian_number(urban_green)),
            ("Solid Waste (tons)", format_indian_number(solid_waste)),
            ("Wastewater Treated (m³)", format_indian_number(wastewater)),
            ("Waste Landfilled (%)", f"{waste_landfilled}%"),
            ("Waste Composted (%)", f"{waste_composted}%")
        ]

        for i in range(0, len(env_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, env_metrics[i:i+3]):
                render_card(col, label, value, inputed_value=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- SOCIAL INFORMATION ----------
        st.markdown("<h4>Social Information</h4>", unsafe_allow_html=True)
        males = row.get("Males", 0)
        females = row.get("Females", 0)
        total_pop = males + females
        children_m = row.get("Children Male",0)
        children_f = row.get("Children Female",0)
        total_children = children_m + children_f
        literacy_m = row.get("Male Literacy (%)",0)
        literacy_f = row.get("Female Literacy (%)",0)
        literacy_total = round((literacy_m + literacy_f)/2,2)

        social_metrics = [
            ("Male Population", format_indian_number(males)),
            ("Female Population", format_indian_number(females)),
            ("Total Population", format_indian_number(total_pop)),
            ("Children (0–6 Male)", format_indian_number(children_m)),
            ("Children (0–6 Female)", format_indian_number(children_f)),
            ("Total Children", format_indian_number(total_children)),
            ("Male Literacy (%)", literacy_m),
            ("Female Literacy (%)", literacy_f),
            ("Overall Literacy (%)", literacy_total),
            ("Slum Population (%)", row.get("Slum (%)",0)),
            ("Migrant Population (%)", row.get("Migrant (%)",0)),
            ("BPL Households (%)", row.get("BPL Households (%)",0))
        ]

        for i in range(0, len(social_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, social_metrics[i:i+3]):
                render_card(col, label, value, inputed_value=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- CONTACT INFORMATION ----------
        st.markdown("<h4>Contact Information</h4>", unsafe_allow_html=True)
        contact_metrics = [
            ("Department Exist", row.get("Department Exist","—")),
            ("Department Name", row.get("Department Name","—")),
            ("Email", row.get("Email","—")),
            ("Contact Number", row.get("Contact Number","—")),
            ("Website", row.get("Website","—"))
        ]

        for i in range(0, len(contact_metrics), 2):
            cols = st.columns(2)
            for col, (label, value) in zip(cols, contact_metrics[i:i+2]):
                render_card(col, label, value, inputed_value=False)

# ---------------------------
# Admin Panel Page
# ---------------------------
elif menu == "Admin":
    st.header("Admin Dashboard")
    
    if not st.session_state.get("authenticated", False):
        admin_login()  # your existing login function
    else:
        st.subheader("Add / Update City / Maharashtra Data")

        with st.form("admin_form", clear_on_submit=False):
            city = st.selectbox(
                "Select City",
                ["Maharashtra"] + list(cities_districts.keys())
            )

            # ---------- Tabs for organized input ----------
            tabs = st.tabs(["Basic", "Environmental", "Social", "Contact"])

            # ---------- Basic Info ----------
            with tabs[0]:
                st.markdown("### Basic Information")
                population = st.number_input("Population (2011 Census)", min_value=0, step=1000)
                area = st.number_input("Geographical Area (sq. km)", min_value=0.0, step=0.1)
                ulb_category = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council", "Nagar Panchayat", "State"])
                est_year = st.number_input("Year of Establishment of ULB", min_value=1800, max_value=2100, step=1)
                
                # CAP Status and Link
                cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
                cap_link = st.text_input("CAP Link")

            # ---------- Environmental Info ----------
            with tabs[1]:
                st.markdown("### Environmental Information")
                ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, step=100.0)
                renewable_energy = st.number_input("Renewable Energy Generated (MWh/year)", min_value=0, step=10)
                green_area = st.number_input("Urban Green Area (ha)", min_value=0, step=1)
                solid_waste = st.number_input("Municipal Solid Waste (tons/year)", min_value=0, step=10)
                waste_landfilled = st.number_input("Waste Landfilled (%)", min_value=0.0, max_value=100.0, step=0.1)
                waste_composted = st.number_input("Waste Composted (%)", min_value=0.0, max_value=100.0, step=0.1)
                wastewater = st.number_input("Wastewater Treated (m³/year)", min_value=0, step=1000)

            # ---------- Social Info ----------
            with tabs[2]:
                st.markdown("### Social Information")
                males = st.number_input("Male Population", min_value=0, step=100)
                females = st.number_input("Female Population", min_value=0, step=100)
                children_m = st.number_input("Children (0–6 Male)", min_value=0, step=10)
                children_f = st.number_input("Children (0–6 Female)", min_value=0, step=10)
                literacy = st.number_input("Overall Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
                literacy_m = st.number_input("Male Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
                literacy_f = st.number_input("Female Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
                bpl = st.number_input("BPL Households (%)", min_value=0.0, max_value=100.0, step=0.1)
                migrant = st.number_input("Migrant Population (%)", min_value=0.0, max_value=100.0, step=0.1)
                slum = st.number_input("Slum Population (%)", min_value=0.0, max_value=100.0, step=0.1)
                urban_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, step=0.1)
                households = st.number_input("Total Households", min_value=0, step=100)

            # ---------- Contact Info ----------
            with tabs[3]:
                st.markdown("### Contact Information")
                dept_exist = st.selectbox("Environment Department Exist?", ["Yes", "No"])
                dept_name = st.text_input("Department Name")
                dept_email = st.text_input("Department Email")
                contact_number = st.text_input("Contact Number")
                official_website = st.text_input("Official Website")

            submit_admin = st.form_submit_button("Save / Update")

            if submit_admin:
                new_row = {
                    "City Name": city,
                    "District": cities_districts.get(city, "Maharashtra") if city != "Maharashtra" else "State",
                    "Population": population,
                    "Area (sq.km)": area,
                    "ULB Category": ulb_category,
                    "CAP Status": cap_status,
                    "CAP Link": cap_link,
                    "Est. Year": est_year,
                    "GHG Emissions": ghg_val,
                    "Renewable Energy (MWh)": renewable_energy,
                    "Urban Green Area (ha)": green_area,
                    "Municipal Solid Waste (tons)": solid_waste,
                    "Waste Landfilled (%)": waste_landfilled,
                    "Waste Composted (%)": waste_composted,
                    "Wastewater Treated (m3)": wastewater,
                    "Males": males,
                    "Females": females,
                    "Children Male": children_m,
                    "Children Female": children_f,
                    "Literacy (%)": literacy,
                    "Male Literacy (%)": literacy_m,
                    "Female Literacy (%)": literacy_f,
                    "Migrant (%)": migrant,
                    "Slum (%)": slum,
                    "BPL Households (%)": bpl,
                    "Urbanization Rate (%)": urban_rate,
                    "Households": households,
                    "Department Exist": dept_exist,
                    "Department Name": dept_name,
                    "Email": dept_email,
                    "Contact Number": contact_number,
                    "Website": official_website,
                }

                df_meta = st.session_state.data.copy()
                if city in df_meta["City Name"].values:
                    df_meta.loc[df_meta["City Name"] == city, list(new_row.keys())[1:]] = list(new_row.values())[1:]
                else:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE, index=False)
                st.success(f"{city} data updated successfully!")
                

# ---------------------------
# CAP Generation Page
# ---------------------------
if menu == "CAP Generation":
    st.header("CAP Generation : Comprehensive Data Collection")

    if not st.session_state.get("authenticated", False):
        admin_login()
    else:
        st.markdown("""
        Collect detailed city-level raw data for generating a comprehensive GHG inventory.
        Each sector below can be expanded to enter multiple data points.
        """)

        with st.form("cap_comprehensive_form", clear_on_submit=False):

            # -------------------
            # 1. General City Info
            # -------------------
            with st.expander("1. General City Info", expanded=True):
                city = st.selectbox("City Name", list(cities_districts.keys()))
                state = st.text_input("State")
                population = st.number_input("Population", min_value=0, value=0, step=1000)
                area_km2 = st.number_input("Area (km²)", min_value=0.0, value=0.0, step=0.1)
                admin_type = st.selectbox("Administrative Type", ["Municipal Corporation", "Municipal Council", "Other"])
                inventory_year = st.number_input("Year of Inventory", min_value=2000, max_value=2100, value=datetime.now().year)

            # -------------------
            # 2. Energy Sector
            # -------------------
            with st.expander("2. Energy Sector"):
                # Electricity & Heat Consumption
                st.subheader("Electricity & Heat Consumption (kWh/year or GJ/year)")
                municipal_electricity = st.number_input("Municipal Buildings", min_value=0, value=0, step=100)
                residential_electricity = st.number_input("Residential", min_value=0, value=0, step=100)
                commercial_electricity = st.number_input("Commercial", min_value=0, value=0, step=100)
                industrial_electricity = st.number_input("Industrial", min_value=0, value=0, step=100)
                purchased_heat_gj = st.number_input("Purchased Heat/Steam (GJ/year)", min_value=0, value=0, step=10)

                # On-site generation
                st.subheader("On-site Generation")
                diesel_gen_mwh = st.number_input("Diesel Generators (MWh/year)", min_value=0, value=0, step=10)
                gas_turbine_mwh = st.number_input("Gas Turbines (MWh/year)", min_value=0, value=0, step=10)

                # Renewable Energy Production
                st.subheader("Renewable Energy Production")
                solar_mwh = st.number_input("Solar Rooftops (MWh/year)", min_value=0, value=0, step=10)
                wind_mwh = st.number_input("Wind Energy (MWh/year)", min_value=0, value=0, step=10)
                biomass_mwh = st.number_input("Biomass (MWh/year)", min_value=0, value=0, step=10)

                # Stationary Fuel Combustion
                st.subheader("Stationary Fuel Combustion (municipal, industrial, residential, commercial)")
                diesel_l = st.number_input("Diesel (L/year)", min_value=0, value=0, step=10)
                petrol_l = st.number_input("Petrol (L/year)", min_value=0, value=0, step=10)
                lpg_l = st.number_input("LPG (L/year)", min_value=0, value=0, step=10)
                natural_gas_m3 = st.number_input("Natural Gas (m3/year)", min_value=0, value=0, step=10)
                coal_t = st.number_input("Coal (tons/year)", min_value=0, value=0, step=1)

            # -------------------
            # 3. Transport Sector
            # -------------------
            with st.expander("3. Transport Sector"):
                st.subheader("Public & Private Transport")
                cars = st.number_input("Cars", min_value=0, value=0, step=10)
                buses = st.number_input("Buses", min_value=0, value=0, step=5)
                trucks = st.number_input("Trucks", min_value=0, value=0, step=5)
                two_wheelers = st.number_input("2/3-Wheelers", min_value=0, value=0, step=10)

                avg_km_cars = st.number_input("Average km traveled by Cars per Year", min_value=0, value=0, step=100)
                avg_km_buses = st.number_input("Average km traveled by Buses per Year", min_value=0, value=0, step=100)
                avg_km_trucks = st.number_input("Average km traveled by Trucks per Year", min_value=0, value=0, step=100)
                avg_km_2w = st.number_input("Average km traveled by 2/3-Wheelers per Year", min_value=0, value=0, step=100)

                st.subheader("Freight & Logistics")
                freight_distance_km = st.number_input("Goods Vehicles Distance Traveled (km/year)", min_value=0, value=0, step=100)
                freight_fuel_diesel_l = st.number_input("Diesel Fuel for Freight (L/year)", min_value=0, value=0, step=10)
                freight_fuel_cng_m3 = st.number_input("CNG Fuel for Freight (m3/year)", min_value=0, value=0, step=10)
                freight_fuel_electric_mwh = st.number_input("Electricity for Freight (MWh/year)", min_value=0, value=0, step=10)

            # -------------------
            # 4. Waste Sector
            # -------------------
            with st.expander("4. Waste Sector"):
                st.subheader("Solid Waste")
                msw_tons = st.number_input("Municipal Solid Waste Generated (tons/year)", min_value=0, value=0, step=10)
                landfill_frac = st.number_input("Fraction Landfilled (%)", min_value=0.0, max_value=100.0, value=0.0)
                recycling_frac = st.number_input("Fraction Recycled (%)", min_value=0.0, max_value=100.0, value=0.0)
                compost_frac = st.number_input("Fraction Composted (%)", min_value=0.0, max_value=100.0, value=0.0)
                incineration_frac = st.number_input("Fraction Incinerated (%)", min_value=0.0, max_value=100.0, value=0.0)
                landfill_methane_capture = st.number_input("Landfill Methane Capture Rate (%)", min_value=0.0, max_value=100.0, value=0.0)

                st.subheader("Wastewater")
                sewage_m3 = st.number_input("Sewage Generated (m³/year)", min_value=0, value=0, step=1000)
                treatment_type = st.selectbox("Treatment Type", ["Primary", "Secondary", "Tertiary"])
                sludge_tons = st.number_input("Sludge Generated (tons/year)", min_value=0, value=0, step=10)
                energy_wastewater_kwh = st.number_input("Energy Use in Treatment (kWh/year)", min_value=0, value=0, step=10)

            # -------------------
            # 5. Industrial Sector
            # -------------------
            with st.expander("5. Industrial Sector"):
                coal_ind = st.number_input("Coal Consumption (tons/year)", min_value=0, value=0, step=1)
                gas_ind = st.number_input("Natural Gas Consumption (m3/year)", min_value=0, value=0, step=10)
                electricity_ind = st.number_input("Electricity Consumption (kWh/year)", min_value=0, value=0, step=100)
                biomass_ind = st.number_input("Biomass (tons/year)", min_value=0, value=0, step=1)
                st.text_area("Industrial Process Emissions (cement, chemical, metal)", value="", height=80)
                st.text_area("Fugitive Emissions (refrigeration, industrial processes)", value="", height=80)

            # -------------------
            # 6. Agriculture & Land Use
            # -------------------
            with st.expander("6. Agriculture & Land Use"):
                cropland_ha = st.number_input("Cropland (ha)", min_value=0, value=0, step=1)
                livestock_count = st.number_input("Livestock (number of animals)", min_value=0, value=0, step=1)
                manure_management = st.text_input("Manure Management Type", value="")
                fertilizer_tons = st.number_input("Fertilizer Use (tons/year)", min_value=0, value=0, step=1)
                afforestation_ha = st.number_input("Afforestation (ha)", min_value=0, value=0, step=1)
                deforestation_ha = st.number_input("Deforestation (ha)", min_value=0, value=0, step=1)
                soil_carbon_sequestration = st.number_input("Soil Carbon Sequestration (optional, tons/year)", min_value=0, value=0, step=1)

            # -------------------
            # 7. City Infrastructure
            # -------------------
            with st.expander("7. City Infrastructure"):
                street_lights_count = st.number_input("Number of Street Lights", min_value=0, value=0, step=10)
                street_lights_energy = st.number_input("Street Lights Energy (kWh/year)", min_value=0, value=0, step=10)
                municipal_fleet_fuel = st.text_input("Municipal Vehicle Fleet Fuel & Consumption")
                water_pumping_energy = st.number_input("Water Pumping & Treatment Energy (kWh/year)", min_value=0, value=0, step=10)
                cooling_heating_energy = st.number_input("Cooling/Heating in Municipal Buildings (kWh/year)", min_value=0, value=0, step=10)

            # -------------------
            # 8. Optional Co-Benefit Indicators
            # -------------------
            with st.expander("8. Optional Co-Benefit Indicators"):
                air_pollution_reduction = st.number_input("Air Pollution Reduction (%)", min_value=0.0, max_value=100.0, value=0.0)
                renewable_energy_share = st.number_input("Renewable Energy Share (%)", min_value=0.0, max_value=100.0, value=0.0)
                water_usage = st.number_input("Water Usage (m³/year)", min_value=0, value=0, step=100)

            # -------------------
            # File upload
            # -------------------
            file_upload = st.file_uploader("Attach supporting documents (optional)", type=["pdf","xlsx","csv"])

            # -------------------
            # Submit button
            # -------------------
            submit_cap = st.form_submit_button("Generate GHG Inventory")

            if submit_cap:
                raw_data = {
                    "City": city,
                    "State": state,
                    "Population": population,
                    "Area_km2": area_km2,
                    "Admin_Type": admin_type,
                    "Inventory_Year": inventory_year,
                    "Municipal_Electricity": municipal_electricity,
                    "Residential_Electricity": residential_electricity,
                    "Commercial_Electricity": commercial_electricity,
                    "Industrial_Electricity": industrial_electricity,
                    "Purchased_Heat_GJ": purchased_heat_gj,
                    "Diesel_Gen_MWh": diesel_gen_mwh,
                    "Gas_Turbine_MWh": gas_turbine_mwh,
                    "Solar_MWh": solar_mwh,
                    "Wind_MWh": wind_mwh,
                    "Biomass_MWh": biomass_mwh,
                    "Diesel_L": diesel_l,
                    "Petrol_L": petrol_l,
                    "LPG_L": lpg_l,
                    "Natural_Gas_m3": natural_gas_m3,
                    "Coal_t": coal_t,
                    "Cars": cars,
                    "Buses": buses,
                    "Trucks": trucks,
                    "Two_Wheelers": two_wheelers,
                    "Avg_Km_Cars": avg_km_cars,
                    "Avg_Km_Buses": avg_km_buses,
                    "Avg_Km_Trucks": avg_km_trucks,
                    "Avg_Km_2W": avg_km_2w,
                    "Freight_Distance_km": freight_distance_km,
                    "Freight_Fuel_Diesel_L": freight_fuel_diesel_l,
                    "Freight_Fuel_CNG_m3": freight_fuel_cng_m3,
                    "Freight_Fuel_Electric_MWh": freight_fuel_electric_mwh,
                    "MSW_tons": msw_tons,
                    "Landfill_Frac": landfill_frac,
                    "Recycling_Frac": recycling_frac,
                    "Compost_Frac": compost_frac,
                    "Incineration_Frac": incineration_frac,
                    "Landfill_Methane_Capture": landfill_methane_capture,
                    "Sewage_m3": sewage_m3,
                    "Treatment_Type": treatment_type,
                    "Sludge_tons": sludge_tons,
                    "Energy_Wastewater_kWh": energy_wastewater_kwh,
                    "Coal_Ind_t": coal_ind,
                    "Gas_Ind_m3": gas_ind,
                    "Electricity_Ind_kWh": electricity_ind,
                    "Biomass_Ind_t": biomass_ind,
                    "Cropland_ha": cropland_ha,
                    "Livestock_Count": livestock_count,
                    "Manure_Management": manure_management,
                    "Fertilizer_tons": fertilizer_tons,
                    "Afforestation_ha": afforestation_ha,
                    "Deforestation_ha": deforestation_ha,
                    "Soil_Carbon_Sequestration": soil_carbon_sequestration,
                    "Street_Lights_Count": street_lights_count,
                    "Street_Lights_Energy": street_lights_energy,
                    "Municipal_Fleet_Fuel": municipal_fleet_fuel,
                    "Water_Pumping_Energy": water_pumping_energy,
                    "Cooling_Heating_Energy": cooling_heating_energy,
                    "Air_Pollution_Reduction": air_pollution_reduction,
                    "Renewable_Energy_Share": renewable_energy_share,
                    "Water_Usage": water_usage,
                    "File": file_upload.name if file_upload else None,
                    "Submission_Date": datetime.now()
                }

                df_cap = st.session_state.get("cap_data", pd.DataFrame())
                df_cap = pd.concat([df_cap, pd.DataFrame([raw_data])], ignore_index=True)
                st.session_state.cap_data = df_cap
                df_cap.to_csv(CAP_DATA_FILE, index=False)

                st.success(f"Raw data for {city} submitted successfully! Redirecting to GHG Inventory dashboard...")
                st.session_state.menu = "GHG Inventory"
                st.experimental_rerun()
                

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu == "GHG Inventory":
    st.header("City GHG Inventory Generation")

    if not st.session_state.authenticated:
        admin_login()
    else:
        # Load CAP raw data safely
        CAP_DATA_FILE = "cap_raw_data.csv"
        try:
            cap_df = pd.read_csv(CAP_DATA_FILE)
        except FileNotFoundError:
            cap_df = pd.DataFrame()

        # Save in session state
        st.session_state.cap_data = cap_df

        # Check if CAP data exists
        if cap_df.empty or "City Name" not in cap_df.columns:
            st.warning("No CAP raw data found or 'City Name' column missing. Please submit raw data first in 'CAP Generation'.")
        else:
            # Only show cities with submitted data
            city_list = cap_df["City Name"].astype(str).tolist()
            selected_city = st.selectbox("Select City to Generate GHG Inventory", city_list)

            if st.button("Generate GHG Inventory"):
                city_data = cap_df[cap_df["City Name"] == selected_city].iloc[0]

                st.subheader(f"GHG Inventory for {selected_city}")

                # --- 1. General City Info ---
                st.markdown(f"""
                **Population:** {city_data.get('Population', 'N/A')}  
                **Area (km²):** {city_data.get('Area (km²)', 'N/A')}  
                **Administrative Type:** {city_data.get('Administrative Type', 'N/A')}  
                **Year of Inventory:** {city_data.get('Year of Inventory', 'N/A')}  
                """)

                # --- 2. Energy Sector ---
                st.subheader("Energy Sector")
                st.markdown(f"""
                **Electricity Consumption (kWh/year)**  
                Residential: {city_data.get('Residential Electricity (MWh)', 0)*1000}  
                Commercial: {city_data.get('Commercial Electricity (MWh)', 0)*1000}  
                Industrial: {city_data.get('Industrial Electricity (MWh)', 0)*1000}  
                Municipal Buildings/Streetlights: {city_data.get('Streetlights Energy (MWh)', 0)*1000}  

                **Purchased Heat/Steam (GJ/year):** {city_data.get('Purchased Heat (GJ)', 'N/A')}  
                **On-site Generation:** Diesel: {city_data.get('Diesel Generators (litres)', 'N/A')}  
                Gas Turbines: {city_data.get('Gas Turbines Fuel', 'N/A')}  
                **Renewable Energy Production (kWh/year):** {city_data.get('Renewable Energy (MWh)', 0)*1000}  
                """)

                # --- 3. Transport Sector ---
                st.subheader("Transport Sector")
                st.markdown(f"""
                **Vehicle Counts by Type**  
                Diesel Vehicles: {city_data.get('Diesel Vehicles', 0)}  
                Petrol Vehicles: {city_data.get('Petrol Vehicles', 0)}  
                CNG Vehicles: {city_data.get('CNG Vehicles', 0)}  
                LPG Vehicles: {city_data.get('LPG Vehicles', 0)}  
                Electric Vehicles: {city_data.get('Electric Vehicles', 0)}  

                **Average km per Vehicle per Year:** {city_data.get('Avg km/Vehicle', 0)} km  

                **Public Transport Fuel/Electricity:** {city_data.get('Public Transport Energy', 'N/A')}  
                **Freight & Logistics Fuel:** {city_data.get('Freight Fuel', 'N/A')}  
                """)

                # --- 4. Waste Sector ---
                st.subheader("Waste Sector")
                st.markdown(f"""
                **Municipal Solid Waste Generated (tons/year):** {city_data.get('Municipal Solid Waste (tons)', 0)}  
                Landfilled: {city_data.get('Waste Landfilled (%)', 0)}%  
                Composted: {city_data.get('Waste Composted (%)', 0)}%  
                **Landfill Methane Capture Rate:** {city_data.get('Landfill Methane Capture (%)', 'N/A')}  
                **Wastewater Treated (m³/year):** {city_data.get('Wastewater Treated (m3)', 0)}  
                Treatment Type: {city_data.get('Wastewater Treatment Type', 'N/A')}  
                """)

                # --- 5. Industrial Sector ---
                st.subheader("Industrial Sector")
                st.markdown(f"""
                **Industrial Fuel Consumption:**  
                Diesel: {city_data.get('Industrial Diesel (tons)', 0)}  
                Petrol: {city_data.get('Industrial Petrol (tons)', 0)}  
                CNG: {city_data.get('Industrial CNG (tons)', 0)}  
                LPG: {city_data.get('Industrial LPG (tons)', 0)}  
                Electricity (MWh): {city_data.get('Industrial Energy (MWh)', 0)}  

                **Industrial Process Emissions:** {city_data.get('Industrial Process Emissions', 'N/A')}  
                **Fugitive Emissions:** {city_data.get('Fugitive Emissions', 'N/A')}  
                """)

                # --- 6. Agriculture & Land Use ---
                st.subheader("Agriculture & Land Use")
                st.markdown(f"""
                Cropland Area: {city_data.get('Cropland Area', 'N/A')}  
                Livestock: {city_data.get('Livestock', 'N/A')}  
                Fertilizer Use (tons/year): {city_data.get('Fertilizer Use (tons)', 'N/A')}  
                Afforestation/Deforestation (ha): {city_data.get('Land Use Change (ha)', 'N/A')}  
                Soil Carbon Sequestration: {city_data.get('Soil Carbon Sequestration', 'N/A')}  
                """)

                # --- 7. City Infrastructure ---
                st.subheader("City Infrastructure")
                st.markdown(f"""
                Street Lights: {city_data.get('Street Lights', 'N/A')}  
                Municipal Vehicle Fleet Fuel: {city_data.get('Municipal Vehicles Fuel', 'N/A')}  
                Water Pumping & Treatment Energy (MWh): {city_data.get('Energy for Water (MWh)', 0)}  
                Cooling/Heating Municipal Buildings: {city_data.get('Cooling/Heating Energy', 'N/A')}  
                """)

                # --- 8. Optional Co-benefits ---
                st.subheader("Optional Co-benefit Indicators")
                st.markdown(f"""
                Renewable Energy Share: {city_data.get('Renewable Energy Share (%)', 'N/A')}  
                Air Pollution Reduction: {city_data.get('Air Pollution Reduction', 'N/A')}  
                Water Usage Efficiency: {city_data.get('Water Usage Efficiency', 'N/A')}  
                """)

                st.success(f"GHG Inventory for {selected_city} generated successfully!")

                # --- Action Button to Goals Page ---
        st.markdown("---")
        st.markdown("### Next Step")
        if st.button("View Actions / Goals to Achieve Net-Zero by 2050"):
            st.session_state.menu = "Actions / Goals"
            st.experimental_rerun()


# ---------------------------
# Actions / Goals Page (Professional)
# ---------------------------
elif menu == "Actions / Goals":
    st.header("City Climate Action Goals for Net Zero by 2050")
    st.markdown("""
    This page summarizes **sector-wise short, mid, and long-term goals** for achieving net-zero emissions by 2050.
    You can **download a consolidated CAP report** including City details, GHG inventory, and sectoral goals.
    """)

    import io
    import pandas as pd
    from datetime import datetime

    # ---------------------------
    # Sector-wise goals
    # ---------------------------
    sector_goals = {
        "Energy": {
            "Short-term (2030)": [
                "Increase rooftop solar adoption in residential buildings",
                "Upgrade municipal street lighting to LED",
                "Retrofit public buildings for energy efficiency",
                "Promote solar water heating in households",
                "Implement energy audits in industrial units",
                "Encourage net-metering for rooftop solar",
                "Promote solar PV in commercial buildings",
                "Replace diesel generators with grid electricity",
                "Introduce smart electricity meters",
                "Develop city-level renewable energy action plan"
            ],
            "Mid-term (2040)": [
                "Increase renewable share in city electricity to 50%",
                "Transition municipal heating to low-carbon sources",
                "Mandate net-zero energy standards for new buildings",
                "Electrify municipal vehicle fleets",
                "Promote community solar parks",
                "Deploy large-scale solar + battery systems in industries",
                "Introduce district heating/cooling with renewable energy",
                "Upgrade grid infrastructure for smart city management",
                "Support renewable energy for commercial clusters",
                "Encourage large-scale biomass energy projects"
            ],
            "Long-term (2050)": [
                "Achieve 100% renewable electricity in city",
                "Phase out fossil fuel use in municipal energy supply",
                "Achieve net-zero energy status in all public buildings",
                "Fully electrify industrial and commercial operations",
                "Deploy city-wide microgrids with renewable integration",
                "Support local energy storage & battery projects",
                "Achieve net-zero for district heating/cooling",
                "Implement smart city-wide energy management",
                "Support zero-carbon energy in all industrial parks",
                "Promote city-wide energy efficiency culture"
            ]
        },
        "Transport": {
            "Short-term (2030)": [
                "Expand public bus fleet with CNG/Electric buses",
                "Promote e-2/3-wheelers through subsidies",
                "Develop dedicated bicycle lanes",
                "Enhance pedestrian walkways",
                "Implement carpooling initiatives",
                "Introduce EV charging stations in public areas",
                "Phase out old diesel vehicles gradually",
                "Implement congestion management in city centers",
                "Upgrade metro/light rail infrastructure",
                "Promote last-mile connectivity using EVs"
            ],
            "Mid-term (2040)": [
                "Electrify 50% of city transport fleet",
                "Develop integrated multi-modal transport system",
                "Expand metro and light rail lines",
                "Implement urban freight consolidation hubs",
                "Promote shared EV mobility programs",
                "Increase non-motorized transport share",
                "Introduce low-emission zones",
                "Encourage electric buses for inter-city routes",
                "Deploy smart traffic management systems",
                "Offer incentives for EV taxis and delivery fleets"
            ],
            "Long-term (2050)": [
                "100% electric or zero-emission public fleet",
                "Phase out fossil-fueled private vehicles",
                "Achieve 80% modal share for public transport",
                "Develop fully integrated EV charging network",
                "Promote autonomous electric buses for efficiency",
                "Ensure net-zero freight transport emissions",
                "Expand pedestrian-only zones in city centers",
                "Implement city-wide EV infrastructure monitoring",
                "Support hydrogen-based heavy transport if feasible",
                "Achieve complete low-carbon mobility for city residents"
            ]
        },
        "Waste": {
            "Short-term (2030)": [
                "Segregate municipal solid waste at source",
                "Increase composting and biogas generation",
                "Capture landfill methane for energy use",
                "Promote recycling of plastics, paper, metals",
                "Upgrade wastewater treatment to secondary level",
                "Reduce open dumping of waste",
                "Engage citizens in community waste management",
                "Reduce single-use plastics in municipal operations",
                "Implement waste audits for commercial establishments",
                "Introduce energy recovery from sewage sludge"
            ],
            "Mid-term (2040)": [
                "Achieve 70% recycling rate city-wide",
                "Implement energy recovery from organic waste at scale",
                "Upgrade wastewater treatment to tertiary level",
                "Capture 80% methane from landfills",
                "Promote circular economy for construction waste",
                "Encourage industrial waste minimization",
                "Use waste-derived fuels in industries",
                "Promote city-wide composting programs",
                "Reduce plastic consumption to minimal levels",
                "Ensure sludge management with energy co-benefits"
            ],
            "Long-term (2050)": [
                "Zero-waste city initiatives implemented",
                "100% landfill methane capture",
                "All wastewater treated to tertiary standards",
                "Maximized recycling for all solid waste streams",
                "Circular economy fully integrated in industrial zones",
                "Energy recovery from all organic waste",
                "Phased elimination of non-recyclable plastics",
                "Advanced waste-to-energy solutions operational",
                "City-wide citizen engagement for sustainable waste",
                "Net-zero GHG emissions from waste sector"
            ]
        }
    }

    # ---------------------------
    # Display sector-wise tables
    # ---------------------------
    for sector, goals in sector_goals.items():
        st.subheader(f"{sector} Sector Goals")
        df = pd.DataFrame(goals)
        st.table(df)

    # ---------------------------
    # Generate CAP Report Button
    # ---------------------------
    st.markdown("### Generate Consolidated CAP Report")

    if st.button("Generate CAP Report", key="download_cap_report"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Save GHG Inventory
            if "cap_data" in st.session_state and not st.session_state.cap_data.empty:
                st.session_state.cap_data.to_excel(writer, index=False, sheet_name="GHG Inventory")
            else:
                pd.DataFrame().to_excel(writer, index=False, sheet_name="GHG Inventory")

            # Save sector-wise goals
            for sector, goals in sector_goals.items():
                df_goals = pd.DataFrame(goals)
                df_goals.to_excel(writer, index=False, sheet_name=f"{sector} Goals")

            writer.save()

        st.download_button(
            label="Download CAP Report (Excel)",
            data=output.getvalue(),
            file_name=f"CAP_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_cap_report_btn"
        )

    st.markdown("**Note:** This report includes City details, GHG inventory, and sector-wise Actions/Goals.")
