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
# Sidebar
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
    menu_items.append(("Generate CAP", "Generate CAP"))

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
# Home Page: Maharashtra Dashboard
# ---------------------------
if menu == "Home":
    st.header("Maharashtra's Net Zero Journey")
    st.markdown("Climate Action Plan Dashboard")

    # ✅ Always use the session_state data (keeps Admin updates live)
    if "data" not in st.session_state:
        st.session_state.data = pd.read_csv(DATA_FILE)
    df = st.session_state.data.copy()

    # ---------- Utility: Render Card ----------
    def render_card(col, label, value, is_input=False, bg_color="#34495E"):
        """
        Reusable card renderer for uniform styling.
        - is_input: True for inputted values (highlighted in white, bold, larger font).
        """
        if is_input:
            value_html = f"<b style='color:#FFFFFF;font-size:20px;'>{value}</b>"
        else:
            value_html = f"<span style='font-size:15px;color:#FFFFFF;'>{value}</span>"

        card_html = f"""
        <div style='
            background-color:{bg_color};
            color:#ECEFF1;
            padding:14px 10px;
            border-radius:12px;
            text-align:center;
            min-height:70px;
            margin-bottom:12px;
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

    # ---------- Utility: Dark Layout for Charts ----------
    def dark_layout(fig, title=None):
        fig.update_layout(
            plot_bgcolor="#111111",
            paper_bgcolor="#111111",
            font=dict(color="white"),
            title=dict(text=title, font=dict(size=20, color="white")) if title else None,
            xaxis=dict(showgrid=False, color="white"),
            yaxis=dict(showgrid=False, color="white")
        )
        return fig

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
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                ">
                    <h5>{title}</h5>
                    <h2>{format_indian_number(val)}</h2>
                </div>
                """, unsafe_allow_html=True
            )

    st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

    # =====================
    # Maharashtra Summary Metrics
    # =====================
    if "Maharashtra" in df["City Name"].values:
        maha_row = df[df["City Name"] == "Maharashtra"].iloc[0]
        population = maha_row.get("Population", 0)
        ghg_total = maha_row.get("GHG Emissions", 0)
        cap_status = maha_row.get("CAP Status", "—")
        cap_link = maha_row.get("CAP Link", "")
        vulnerability_score = maha_row.get("Vulnerability Score", 0)
        est_ghg = round(population * (ghg_total/population if population else 0), 2)

        st.subheader("Maharashtra Overview")

        # Row 1
        cols = st.columns(4)
        render_card(cols[0], "CAP Status", cap_status, is_input=True,
                    bg_color={"completed":"#28A745","in progress":"#FFA500","not started":"#FF3B3B"}.get(str(cap_status).lower(), "#34495E"))
        render_card(cols[1], "Link", f"<a href='{cap_link}' target='_blank' style='color:#ECEFF1;text-decoration:underline;'>View CAP</a>" if cap_link else "—")
        render_card(cols[2], "GHG Emissions (tCO2e)", format_indian_number(ghg_total), is_input=True)
        render_card(cols[3], "Estimated GHG by Population", format_indian_number(est_ghg), is_input=True)

        # Row 2
        cols = st.columns(2)
        render_card(cols[0], "Vulnerability Assessment Score", round(vulnerability_score,2), is_input=True)
        render_card(cols[1], "Population", format_indian_number(population), is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # =====================
        # Environmental Metrics
        # =====================
        st.subheader("Environmental Metrics")
        env_cols = ["Renewable Energy (MWh)", "Urban Green Area (ha)", "Municipal Solid Waste (tons)",
                    "Waste Landfilled (%)", "Waste Composted (%)", "Wastewater Treated (m3)"]
        for i in range(0, len(env_cols), 3):
            cols = st.columns(3)
            for col, name in zip(cols, env_cols[i:i+3]):
                val = maha_row.get(name, 0)
                display_val = f"{int(val)}%" if "%" in name else format_indian_number(val)
                render_card(col, name, display_val, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

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

        social_metrics = [
            ("Male Population", format_indian_number(males)),
            ("Female Population", format_indian_number(females)),
            ("Total Population", format_indian_number(total_pop)),
            ("Children (0–6 Male)", format_indian_number(children_m)),
            ("Children (0–6 Female)", format_indian_number(children_f)),
            ("Total Children (0–6)", format_indian_number(total_children)),
            ("Male Literacy (%)", f"{literacy_m}%"),
            ("Female Literacy (%)", f"{literacy_f}%"),
            ("Average Literacy (%)", f"{literacy_avg}%"),
            ("Migrant Population (%)", f"{maha_row.get('Migrant (%)',0)}%"),
            ("Slum Population (%)", f"{maha_row.get('Slum (%)',0)}%"),
            ("BPL Households (%)", f"{maha_row.get('BPL Households (%)',0)}%"),
            ("Urbanization Rate (%)", f"{maha_row.get('Urbanization Rate (%)',0)}%")
        ]

        for i in range(0, len(social_metrics), 3):
            cols = st.columns(3)
            for col, (label, val) in zip(cols, social_metrics[i:i+3]):
                render_card(col, label, val, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # =====================
        # Contact Information
        # =====================
        st.subheader("Contact Information")
        contacts = [
            ("Department Exist", maha_row.get("Department Exist","—")),
            ("Department Name", maha_row.get("Department Name","—")),
            ("Email", maha_row.get("Email","—")),
            ("Contact Number", maha_row.get("Contact Number","—")),
            ("Website", maha_row.get("Website","—"))
        ]
        for i in range(0, len(contacts), 2):
            cols = st.columns(2)
            for col, (label, val) in zip(cols, contacts[i:i+2]):
                render_card(col, label, val)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # =====================
        # Charts (Dark Mode)
        # =====================
        import plotly.express as px
        df["GHG Emissions"] = pd.to_numeric(df["GHG Emissions"], errors="coerce").fillna(0)
        df["Per Capita GHG"] = df.apply(lambda x: (x["GHG Emissions"]/x["Population"]) if x["Population"] else 0, axis=1)
        df["Estimated GHG"] = df["Population"] * df["Per Capita GHG"]

        # Chart 1
        fig_ghg = px.bar(df, x="City Name", y="GHG Emissions",
                         text=df["GHG Emissions"].apply(lambda x: format_indian_number(round(x,0))),
                         color="GHG Emissions", color_continuous_scale="Blues")
        fig_ghg.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(dark_layout(fig_ghg, "City-wise Total GHG Emissions"), use_container_width=True)

        # Chart 2
        fig_est = px.bar(df, x="City Name", y="Estimated GHG",
                         text=df["Estimated GHG"].apply(lambda x: format_indian_number(round(x,0))),
                         color="Estimated GHG", color_continuous_scale="Oranges")
        fig_est.update_traces(marker_line_width=0, textposition="outside")
        st.plotly_chart(dark_layout(fig_est, "Estimated GHG Emissions by Population"), use_container_width=True)

        # Chart 3
        evs_cols = ["GHG Emissions","Municipal Solid Waste (tons)","Wastewater Treated (m3)"]
        for c in evs_cols:
            if c not in df.columns: df[c] = 0
        max_env = {c: df[c].max() or 1 for c in evs_cols}
        df["EVS"] = (df["GHG Emissions"]/max_env["GHG Emissions"]*0.5 +
                     df["Municipal Solid Waste (tons)"]/max_env["Municipal Solid Waste (tons)"]*0.25 +
                     df["Wastewater Treated (m3)"]/max_env["Wastewater Treated (m3)"]*0.25) * 100
        social_factors = {"Population":0.3,"Households":0.2,"Urbanization Rate (%)":0.2,"Literacy Rate (%)":0.15,"Poverty Rate (%)":0.15}
        for c in social_factors:
            if c not in df.columns: df[c]=0
            else: df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
        max_social = {c: df[c].max() or 1 for c in social_factors}
        df["SVS"] = ((df["Population"]/max_social["Population"])*0.3 +
                     (df["Households"]/max_social["Households"])*0.2 +
                     (df["Urbanization Rate (%)"]/max_social["Urbanization Rate (%)"])*0.2 +
                     (1 - df["Literacy Rate (%)"]/max_social["Literacy Rate (%)"])*0.15 +
                     (df["Poverty Rate (%)"]/max_social["Poverty Rate (%)"])*0.15) * 100
        vuln_df = df[["City Name","EVS","SVS"]].melt(id_vars="City Name", var_name="Score Type", value_name="Score")
        fig_vuln = px.bar(vuln_df, x="City Name", y="Score", color="Score Type", barmode="group",
                          text=vuln_df["Score"].apply(lambda x: f"{round(x,1)}"),
                          color_discrete_map={"EVS":"#1f77b4","SVS":"#ff7f0e"})
        fig_vuln.update_traces(textposition="outside")
        st.plotly_chart(dark_layout(fig_vuln, "City Vulnerability Scores (Environmental vs Social)"), use_container_width=True)

        
# ---------------------------
# City Information Page
# ---------------------------
elif menu == "City Information":
    st.markdown("<h2 style='margin-bottom:15px;'>City Information Dashboard</h2>", unsafe_allow_html=True)

    # Always pull latest saved data
    df_meta = st.session_state.get("data", pd.DataFrame()).copy()

    # Dropdown list should reflect available data
    available_cities = sorted(set(df_meta["City Name"])) if not df_meta.empty else list(cities_districts.keys())
    city = st.selectbox("Select City", available_cities)

    if not df_meta.empty and city in df_meta["City Name"].values:
        row = df_meta[df_meta["City Name"] == city].iloc[0].fillna("—")  # fallback for NaN
        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- Card Rendering ----------
        def render_card(col, label, value, is_input=False, bg_color="#34495E"):
            value_html = f"<b style='font-size:18px;'>{value}</b>" if is_input else f"<span style='font-size:15px;'>{value}</span>"
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
            ' onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 6px 10px rgba(0,0,0,0.5)';"
              onmouseout="this.style.transform='translateY(0px)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.4)';">
                {label}<br>{value_html}
            </div>
            """
            col.markdown(card_html, unsafe_allow_html=True)

        # ---------- BASIC INFORMATION ----------
        st.markdown("<h4>Basic Information</h4>", unsafe_allow_html=True)
        population = int(row.get("Population", 0) or 0)
        area = float(row.get("Area (sq.km)", row.get("Geographical Area (sq. km)", 0)) or 0)
        density = int(round(population / area)) if area > 0 else "—"

        est_year = row.get("Est. Year", "—")
        try:
            est_year = int(float(est_year)) if est_year not in ("—", "") else "—"
        except:
            pass

        cap_status = row.get("CAP Status", "—")
        cap_link = row.get("CAP Link", "")
        cap_colors = {"completed": "#66BB6A", "in progress": "#FFA726", "not started": "#EF5350"}
        cap_color = cap_colors.get(str(cap_status).lower(), "#34495E")

        basic_metrics = [
            ("District", row.get("District", "—")),
            ("ULB Category", row.get("ULB Category", "—")),
            ("Population", format_indian_number(population)),
            ("Area (sq.km)", format_indian_number(area)),
            ("Density (/sq.km)", format_indian_number(density) if density != "—" else "—"),
            ("Est. Year", est_year),
            ("CAP Status", cap_status),
        ]

        non_input_labels = {"District", "ULB Category"}
        for i in range(0, len(basic_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, basic_metrics[i:i+3]):
                bg = cap_color if label == "CAP Status" else "#34495E"
                render_card(col, label, value, is_input=(label not in non_input_labels), bg_color=bg)

        if cap_link:
            st.markdown(
                f"""
                <div style='background-color:#34495E; color:#ECEFF1; padding:12px;
                border-radius:10px; font-size:14px; text-align:center; margin-top:6px;
                box-shadow:0 4px 6px rgba(0,0,0,0.4);'>
                <a href='{cap_link}' target='_blank' style='color:#ECEFF1; text-decoration:underline;'>
                View CAP Document</a></div>
                """, unsafe_allow_html=True
            )

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- ENVIRONMENTAL INFORMATION ----------
        st.markdown("<h4>Environmental Information</h4>", unsafe_allow_html=True)
        ghg_total = float(row.get("GHG Emissions", 0) or 0)
        per_capita_ghg = int(round(ghg_total / population)) if population > 0 else 0

        env_metrics = [
            ("GHG Emissions (tCO2e)", format_indian_number(ghg_total)),
            ("Per Capita Emissions (tCO2e)", format_indian_number(per_capita_ghg)),
            ("Renewable Energy (MWh)", format_indian_number(row.get("Renewable Energy (MWh)", 0) or 0)),
            ("Urban Green Area (ha)", format_indian_number(row.get("Urban Green Area (ha)", 0) or 0)),
            ("Solid Waste (tons)", format_indian_number(row.get("Municipal Solid Waste (tons)", 0) or 0)),
            ("Wastewater Treated (m³)", format_indian_number(row.get("Wastewater Treated (m3)", 0) or 0)),
            ("Waste Landfilled (%)", f"{int(round(row.get('Waste Landfilled (%)',0)))}%"),
            ("Waste Composted (%)", f"{int(round(row.get('Waste Composted (%)',0)))}%"),
        ]
        for i in range(0, len(env_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, env_metrics[i:i+3]):
                render_card(col, label, value, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- SOCIAL INFORMATION ----------
        st.markdown("<h4>Social Information</h4>", unsafe_allow_html=True)
        males = int(row.get("Males", 0) or 0)
        females = int(row.get("Females", 0) or 0)
        total_pop = males + females
        children_m = int(row.get("Children Male", 0) or 0)
        children_f = int(row.get("Children Female", 0) or 0)
        total_children = children_m + children_f
        literacy_m = float(row.get("Male Literacy (%)", 0) or 0)
        literacy_f = float(row.get("Female Literacy (%)", 0) or 0)
        literacy_total = int(round((literacy_m + literacy_f) / 2)) if (literacy_m or literacy_f) else 0

        social_metrics = [
            ("Male Population", format_indian_number(males)),
            ("Female Population", format_indian_number(females)),
            ("Total Population", format_indian_number(total_pop)),
            ("Children (0–6 Male)", format_indian_number(children_m)),
            ("Children (0–6 Female)", format_indian_number(children_f)),
            ("Total Children", format_indian_number(total_children)),
            ("Male Literacy (%)", f"{int(round(literacy_m))}%"),
            ("Female Literacy (%)", f"{int(round(literacy_f))}%"),
            ("Overall Literacy (%)", f"{int(round(literacy_total))}%"),
            ("Slum Population (%)", f"{int(round(row.get('Slum (%)',0)))}%"),
            ("Migrant Population (%)", f"{int(round(row.get('Migrant (%)',0)))}%"),
            ("BPL Households (%)", f"{int(round(row.get('BPL Households (%)',0)))}%"),
        ]
        for i in range(0, len(social_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, social_metrics[i:i+3]):
                render_card(col, label, value, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- CONTACT INFORMATION ----------
        st.markdown("<h4>Contact Information</h4>", unsafe_allow_html=True)
        contact_metrics = [
            ("Department Exist", row.get("Department Exist","—")),
            ("Department Name", row.get("Department Name","—")),
            ("Email", row.get("Email","—")),
            ("Contact Number", row.get("Contact Number","—")),
            ("Website", row.get("Website","—")),
        ]
        for i in range(0, len(contact_metrics), 2):
            cols = st.columns(2)
            for col, (label, value) in zip(cols, contact_metrics[i:i+2]):
                render_card(col, label, value, is_input=False)

# ---------------------------
# Admin Panel Page
# ---------------------------
elif menu == "Admin":
    st.header("Admin Board")

    if not st.session_state.get("authenticated", False):
        admin_login()
    else:
        st.subheader("Update City / Maharashtra State Data")

        # ---------- Load existing data ----------
        df_meta = st.session_state.data.copy()

        # ---------- Helper function to get safe default ----------
        def safe_default(val, dtype):
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return dtype(0) if dtype in [int, float] else ''
            return dtype(val)

        # ---------- City selection ----------
        city = st.selectbox(
            "Select City",
            ["Maharashtra"] + list(cities_districts.keys()),
            key="selected_city"
        )

        # Get existing city data or empty dict
        existing_row = df_meta[df_meta["City Name"] == city]
        existing_data = existing_row.iloc[0].to_dict() if not existing_row.empty else {}

        # ---------- Admin Form ----------
        with st.form("admin_form", clear_on_submit=False):
            tabs = st.tabs(["Basic", "Environmental", "Social", "Contact"])

            # ---------- Basic Info ----------
            with tabs[0]:
                st.markdown("### Basic Information")
                population = st.number_input("Population (2011 Census)", min_value=0, step=1000, value=safe_default(existing_data.get("Population"), int))
                area = st.number_input("Geographical Area (sq. km)", min_value=0.0, step=0.1, value=safe_default(existing_data.get("Area (sq.km)"), float))
                ulb_category = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council", "Nagar Panchayat", "State"], index=["Municipal Corporation", "Municipal Council", "Nagar Panchayat", "State"].index(existing_data.get("ULB Category", "Municipal Corporation")))
                est_year = st.number_input("Year of Establishment of ULB", min_value=1800, max_value=2100, step=1, value=safe_default(existing_data.get("Est. Year"), int))
                cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"], index=["Not Started", "In Progress", "Completed"].index(existing_data.get("CAP Status", "Not Started")))
                cap_link = st.text_input("CAP Link", value=safe_default(existing_data.get("CAP Link"), str))

            # ---------- Environmental Info ----------
            with tabs[1]:
                st.markdown("### Environmental Information")
                ghg_val = st.number_input("Total GHG Emissions (tCO2e)", min_value=0.0, step=100.0, value=safe_default(existing_data.get("GHG Emissions"), float))
                renewable_energy = st.number_input("Renewable Energy Generated (MWh/year)", min_value=0, step=10, value=safe_default(existing_data.get("Renewable Energy (MWh)"), int))
                green_area = st.number_input("Urban Green Area (ha)", min_value=0, step=1, value=safe_default(existing_data.get("Urban Green Area (ha)"), int))
                solid_waste = st.number_input("Municipal Solid Waste (tons/year)", min_value=0, step=10, value=safe_default(existing_data.get("Municipal Solid Waste (tons)"), int))
                waste_landfilled = st.number_input("Waste Landfilled (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Waste Landfilled (%)"), float))
                waste_composted = st.number_input("Waste Composted (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Waste Composted (%)"), float))
                wastewater = st.number_input("Wastewater Treated (m³/year)", min_value=0, step=1000, value=safe_default(existing_data.get("Wastewater Treated (m3)"), int))

            # ---------- Social Info ----------
            with tabs[2]:
                st.markdown("### Social Information")
                males = st.number_input("Male Population", min_value=0, step=100, value=safe_default(existing_data.get("Males"), int))
                females = st.number_input("Female Population", min_value=0, step=100, value=safe_default(existing_data.get("Females"), int))
                children_m = st.number_input("Children (0–6 Male)", min_value=0, step=10, value=safe_default(existing_data.get("Children Male"), int))
                children_f = st.number_input("Children (0–6 Female)", min_value=0, step=10, value=safe_default(existing_data.get("Children Female"), int))
                literacy = st.number_input("Overall Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Literacy (%)"), float))
                literacy_m = st.number_input("Male Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Male Literacy (%)"), float))
                literacy_f = st.number_input("Female Literacy Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Female Literacy (%)"), float))
                bpl = st.number_input("BPL Households (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("BPL Households (%)"), float))
                migrant = st.number_input("Migrant Population (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Migrant (%)"), float))
                slum = st.number_input("Slum Population (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Slum (%)"), float))
                urban_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, step=0.1, value=safe_default(existing_data.get("Urbanization Rate (%)"), float))
                households = st.number_input("Total Households", min_value=0, step=100, value=safe_default(existing_data.get("Households"), int))

            # ---------- Contact Info ----------
            with tabs[3]:
                st.markdown("### Contact Information")
                dept_exist = st.selectbox("Environment Department Exist?", ["Yes", "No"], index=["Yes", "No"].index(existing_data.get("Department Exist", "No")))
                dept_name = st.text_input("Department Name", value=safe_default(existing_data.get("Department Name"), str))
                dept_email = st.text_input("Department Email", value=safe_default(existing_data.get("Email"), str))
                contact_number = st.text_input("Contact Number", value=safe_default(existing_data.get("Contact Number"), str))
                official_website = st.text_input("Official Website", value=safe_default(existing_data.get("Website"), str))

            # ---------- Submit Button ----------
            submit_admin = st.form_submit_button("Save / Update")

            if submit_admin:
                import datetime
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
                    "Last Updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

                if not existing_data:
                    df_meta = pd.concat([df_meta, pd.DataFrame([new_row])], ignore_index=True)
                else:
                    df_meta.loc[df_meta["City Name"] == city, new_row.keys()] = pd.DataFrame([new_row]).values

                st.session_state.data = df_meta
                df_meta.to_csv(DATA_FILE, index=False)
                st.success(f"{city} data updated successfully!")
                

# ---------------------------
# CAP Generation Page
# ---------------------------
if menu == "Generate CAP":
    st.header("CAP Generation : Comprehensive Data Collection")

    # Admin check
    if not st.session_state.get("authenticated", False):
        admin_login()
    else:
        st.markdown("""
        Collect detailed city-level raw data for generating a comprehensive GHG inventory.
        Use each section to provide available activity data and sectoral priority/resilience inputs.
        Fields are optional — submit what you have. Data will be saved and used to generate the GHG inventory.
        """)

        # Unique form key to avoid duplicate form errors
        with st.form("cap_generation_form_v2", clear_on_submit=False):

            # -------------------
            # 1. BASIC CITY INFORMATION
            # -------------------
            with st.expander("1. Basic City Information", expanded=True):
                city = st.selectbox("City Name", list(cities_districts.keys()))
                population = st.number_input("Total Population", min_value=0, value=0, step=1000)
                households = st.number_input("Number of Households", min_value=0, value=0, step=100)
                area_km2 = st.number_input("Area (km²)", min_value=0.0, value=0.0, step=0.1)
                admin_type = st.selectbox("Administrative Type", ["Municipal Corporation", "Municipal Council", "Nagar Panchayat", "Other"])
                inventory_year = st.number_input("Year of Inventory", min_value=2000, max_value=2100, value=datetime.now().year)
                urbanization_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

                # Priority / resilience flags (basic)
                coastal_city = st.selectbox("Coastal City?", ["No", "Yes"])
                has_airport = st.selectbox("Has Airport within city boundary?", ["No", "Yes"])
                major_industrial_hub = st.selectbox("Major industrial zone inside city?", ["No", "Yes"])

            # -------------------
            # 2. ENERGY & GREEN BUILDING
            # -------------------
            with st.expander("2. Energy & Green Building"):
                st.subheader("Electricity & Heat (MWh or kWh)")
                municipal_electricity_mwh = st.number_input("Municipal buildings energy (MWh/year)", min_value=0, value=0, step=10)
                residential_electricity_mwh = st.number_input("Residential electricity (MWh/year)", min_value=0, value=0, step=10)
                commercial_electricity_mwh = st.number_input("Commercial electricity (MWh/year)", min_value=0, value=0, step=10)
                industrial_electricity_mwh = st.number_input("Industrial electricity (MWh/year)", min_value=0, value=0, step=10)
                purchased_heat_gj = st.number_input("Purchased heat/steam (GJ/year)", min_value=0, value=0, step=10)

                st.subheader("On-site generation & backup")
                diesel_gen_l = st.number_input("Diesel generator fuel (litres/year)", min_value=0, value=0, step=10)
                gas_turbine_m3 = st.number_input("Gas turbine fuel (m³/year)", min_value=0, value=0, step=10)

                st.subheader("Renewable energy & potential")
                rooftop_solar_mw_potential = st.number_input("Estimated rooftop solar potential (MW)", min_value=0.0, value=0.0, step=0.1)
                rooftop_solar_mwh = st.number_input("Rooftop solar generation (MWh/year)", min_value=0, value=0, step=10)
                utility_scale_solar_mwh = st.number_input("Utility-scale solar (MWh/year)", min_value=0, value=0, step=10)
                wind_mwh = st.number_input("Wind (MWh/year)", min_value=0, value=0, step=10)
                biomass_mwh = st.number_input("Biomass (MWh/year)", min_value=0, value=0, step=10)

                st.subheader("Green buildings & efficiency")
                percent_buildings_energy_audited = st.number_input("% of public/commercial buildings energy audited", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                retrofittable_building_area_m2 = st.number_input("Estimated retrofittable building area (m²)", min_value=0, value=0, step=100)
                planned_building_efficiency_program = st.selectbox("Planned building retrofit program?", ["No", "Yes"])

                # Priority / resilience (energy)
                critical_facilities_on_microgrid = st.selectbox("Critical facilities with backup renewables (hospitals, water)?", ["No", "Yes"])
                energy_security_risk_level = st.selectbox("Energy security risk (low/medium/high)", ["Low","Medium","High"])

            # -------------------
            # 3. URBAN GREEN COVER & BIODIVERSITY
            # -------------------
            with st.expander("3. Urban Green Cover & Biodiversity"):
                urban_green_area_ha = st.number_input("Urban green area (ha)", min_value=0, value=0, step=1)
                percent_tree_canopy = st.number_input("Tree canopy cover (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                number_parks = st.number_input("Number of parks/public gardens", min_value=0, value=0, step=1)
                community_gardens = st.selectbox("Community gardens / urban farms present?", ["No","Yes"])

                st.subheader("Biodiversity & land")
                protected_areas_ha = st.number_input("Protected natural area within city (ha)", min_value=0, value=0, step=1)
                urban_forest_program = st.selectbox("Active urban forestry program?", ["No","Yes"])

                # Resilience / priority items
                heat_vulnerability_index = st.number_input("Urban heat vulnerability index (0-100)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                priority_afforestation_ha = st.number_input("Planned afforestation area (ha)", min_value=0, value=0, step=1)

            # -------------------
            # 4. SUSTAINABLE MOBILITY
            # -------------------
            with st.expander("4. Sustainable Mobility"):
                st.subheader("Vehicle Fleet & Activity")
                cars = st.number_input("Number of cars", min_value=0, value=0, step=10)
                buses = st.number_input("Number of buses", min_value=0, value=0, step=1)
                trucks = st.number_input("Number of trucks", min_value=0, value=0, step=1)
                two_wheelers = st.number_input("Number of 2/3-wheelers", min_value=0, value=0, step=10)

                avg_km_cars = st.number_input("Average km/year per car", min_value=0, value=0, step=100)
                avg_km_buses = st.number_input("Average km/year per bus", min_value=0, value=0, step=100)
                avg_km_trucks = st.number_input("Average km/year per truck", min_value=0, value=0, step=100)
                avg_km_2w = st.number_input("Average km/year per 2/3-wheeler", min_value=0, value=0, step=100)

                st.subheader("Public transport & active travel")
                public_transport_ridership = st.number_input("Annual public transport ridership (passenger-km)", min_value=0, value=0, step=1000)
                public_transport_modes = st.multiselect("Public transport modes present", ["Bus","Metro","Suburban Rail","Tram","BRT"])
                km_cycle_tracks = st.number_input("Total dedicated cycle lane length (km)", min_value=0.0, value=0.0, step=0.1)
                pedestrian_zone_km = st.number_input("Pedestrian-only zone length (km)", min_value=0.0, value=0.0, step=0.1)

                st.subheader("Freight & logistics")
                freight_km = st.number_input("Annual goods vehicle km (estimated)", min_value=0, value=0, step=1000)
                freight_fuel_diesel_l = st.number_input("Freight diesel (L/year)", min_value=0, value=0, step=10)
                freight_electric_mwh = st.number_input("Freight electricity (MWh/year)", min_value=0, value=0, step=10)

                # Mobility priorities / resilience
                electric_vehicle_penetration_pct = st.number_input("EV penetration in fleet (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                congestion_hotspots_count = st.number_input("Number of major congestion hotspots", min_value=0, value=0, step=1)
                transport_emergency_routes_exist = st.selectbox("Designated emergency transport corridors?", ["No","Yes"])

            # -------------------
            # 5. WATER RESOURCE MANAGEMENT
            # -------------------
            with st.expander("5. Water Resource Management"):
                st.subheader("Water supply & treatment")
                water_supply_m3 = st.number_input("Total water supplied (m³/year)", min_value=0, value=0, step=1000)
                water_loss_fraction = st.number_input("Distribution loss / NRW (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                energy_for_water_kwh = st.number_input("Energy for water pumping & treatment (kWh/year)", min_value=0, value=0, step=100)
                wastewater_treated_m3 = st.number_input("Wastewater treated (m³/year)", min_value=0, value=0, step=1000)
                wastewater_treatment_level = st.selectbox("Wastewater treatment level", ["None","Primary","Secondary","Tertiary"])

                st.subheader("Flooding / drought & climate risk")
                percent_area_flood_prone = st.number_input("Percent of city area flood-prone (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                has_urban_flood_management_plan = st.selectbox("Urban flood management plan?", ["No","Yes"])
                drought_risk_level = st.selectbox("Drought risk (Low/Medium/High)", ["Low","Medium","High"])
                stormwater_infrastructure_capacity = st.selectbox("Stormwater infrastructure adequate?", ["No","Partially","Yes"])

                # Water priorities
                planned_reservoirs_m3 = st.number_input("Planned additional water storage (m³)", min_value=0, value=0, step=1000)
                groundwater_overdraft_pct = st.number_input("Estimated groundwater overdraft (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

            # -------------------
            # 6. WASTE MANAGEMENT
            # -------------------
            with st.expander("6. Waste Management"):
                st.subheader("Solid waste")
                msw_tons = st.number_input("Municipal solid waste generated (tons/year)", min_value=0, value=0, step=10)
                percent_landfilled = st.number_input("Fraction landfilled (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                percent_recycled = st.number_input("Fraction recycled (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                percent_composted = st.number_input("Fraction composted (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                landfill_methane_capture = st.number_input("Landfill methane capture rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)

                st.subheader("Wastewater & sludge")
                sludge_tons = st.number_input("Sludge generated (tons/year)", min_value=0, value=0, step=10)
                energy_wastewater_kwh = st.number_input("Energy use in wastewater treatment (kWh/year)", min_value=0, value=0, step=10)
                planned_waste_to_energy = st.selectbox("Planned waste-to-energy projects?", ["No","Yes"])

                # Waste priorities
                circular_economy_programs = st.selectbox("Circular economy programs active?", ["No","Yes"])
                commercial_waste_audit_done = st.selectbox("Commercial waste audits done?", ["No","Yes"])

            # -------------------
            # 7. UPLOAD & SUBMIT
            # -------------------
            with st.expander("7. Upload & Submit"):
                st.markdown("### Attach supporting documents (maps, reports, energy bills, surveys)")
                file_upload = st.file_uploader("Attach supporting documents (optional)", type=["pdf","xlsx","csv"])
                notes = st.text_area("Any additional notes / clarifications (optional)", value="", height=120)

                # Submit button
                submit_cap = st.form_submit_button("Generate GHG Inventory")

                if submit_cap:
                    # Basic validation: require minimal key fields (optional: make all optional if you prefer)
                    if not city or population <= 0 or inventory_year <= 0:
                        st.error("Please provide minimum required fields: City, Population and Year of Inventory.")
                    else:
                        # Build single standardized record (column names chosen to be consistent)
                        raw_data = {
                            "City Name": city,
                            "Population": population,
                            "Households": households,
                            "Area_km2": area_km2,
                            "Administrative Type": admin_type,
                            "Year of Inventory": inventory_year,
                            "Urbanization Rate (%)": urbanization_rate,
                            "Coastal City": coastal_city,
                            "Has Airport": has_airport,
                            "Major Industrial Hub": major_industrial_hub,

                            # Energy
                            "Municipal Electricity (MWh)": municipal_electricity_mwh,
                            "Residential Electricity (MWh)": residential_electricity_mwh,
                            "Commercial Electricity (MWh)": commercial_electricity_mwh,
                            "Industrial Electricity (MWh)": industrial_electricity_mwh,
                            "Purchased Heat (GJ)": purchased_heat_gj,
                            "Diesel Gen (L/year)": diesel_gen_l,
                            "Gas Turbine Fuel (m3/year)": gas_turbine_m3,
                            "Rooftop Solar Potential (MW)": rooftop_solar_mw_potential,
                            "Rooftop Solar (MWh)": rooftop_solar_mwh,
                            "Utility Solar (MWh)": utility_scale_solar_mwh,
                            "Wind (MWh)": wind_mwh,
                            "Biomass (MWh)": biomass_mwh,
                            "Percent Buildings Audited (%)": percent_buildings_energy_audited,
                            "Retrofittable Area (m2)": retrofittable_building_area_m2,
                            "Retrofitting Program Planned": planned_building_efficiency_program,
                            "Critical Facilities on Microgrid": critical_facilities_on_microgrid,
                            "Energy Security Risk": energy_security_risk_level,

                            # Green cover & biodiversity
                            "Urban Green Area (ha)": urban_green_area_ha,
                            "Tree Canopy (%)": percent_tree_canopy,
                            "Number of Parks": number_parks,
                            "Community Gardens": community_gardens,
                            "Protected Areas (ha)": protected_areas_ha,
                            "Urban Forest Program": urban_forest_program,
                            "Heat Vulnerability Index": heat_vulnerability_index,
                            "Planned Afforestation (ha)": priority_afforestation_ha,

                            # Transport
                            "Cars": cars,
                            "Buses": buses,
                            "Trucks": trucks,
                            "Two Wheelers": two_wheelers,
                            "Avg Km Cars": avg_km_cars,
                            "Avg Km Buses": avg_km_buses,
                            "Avg Km Trucks": avg_km_trucks,
                            "Avg Km 2W": avg_km_2w,
                            "Public Transport Ridership (pkm)": public_transport_ridership,
                            "Public Transport Modes": ",".join(public_transport_modes) if public_transport_modes else "",
                            "Cycle Lane km": km_cycle_tracks,
                            "Pedestrian Zone km": pedestrian_zone_km,
                            "Freight km": freight_km,
                            "Freight Diesel (L)": freight_fuel_diesel_l,
                            "Freight Electricity (MWh)": freight_electric_mwh,
                            "EV Penetration (%)": electric_vehicle_penetration_pct,
                            "Congestion Hotspots": congestion_hotspots_count,
                            "Emergency Transport Routes": transport_emergency_routes_exist,

                            # Water
                            "Water Supplied (m3)": water_supply_m3,
                            "Water Loss (%)": water_loss_fraction,
                            "Energy for Water (kWh)": energy_for_water_kwh,
                            "Wastewater Treated (m3)": wastewater_treated_m3,
                            "Wastewater Treatment Level": wastewater_treatment_level,
                            "Percent Flood Prone (%)": percent_area_flood_prone,
                            "Urban Flood Plan": has_urban_flood_management_plan,
                            "Drought Risk": drought_risk_level,
                            "Stormwater Capacity": stormwater_infrastructure_capacity,
                            "Planned Water Storage (m3)": planned_reservoirs_m3,
                            "Groundwater Overdraft (%)": groundwater_overdraft_pct,

                            # Waste
                            "MSW (tons/year)": msw_tons,
                            "Percent Landfilled (%)": percent_landfilled,
                            "Percent Recycled (%)": percent_recycled,
                            "Percent Composted (%)": percent_composted,
                            "Landfill Methane Capture (%)": landfill_methane_capture,
                            "Sludge (tons/year)": sludge_tons,
                            "Energy Wastewater (kWh)": energy_wastewater_kwh,
                            "Waste-to-Energy Planned": planned_waste_to_energy,
                            "Circular Economy Programs": circular_economy_programs,
                            "Commercial Waste Audit Done": commercial_waste_audit_done,

                            # Files & metadata
                            "Attachments": file_upload.name if file_upload else None,
                            "Notes": notes,
                            "Submission Date": datetime.now()
                        }

                        # Append to session-state dataframe and save
                        df_cap = st.session_state.get("cap_data", pd.DataFrame())
                        # Normalize columns if new DF is empty
                        if df_cap.empty:
                            df_cap = pd.DataFrame(columns=list(raw_data.keys()))
                        # Append
                        df_cap = pd.concat([df_cap, pd.DataFrame([raw_data])], ignore_index=True)
                        st.session_state.cap_data = df_cap
                        try:
                            df_cap.to_csv(CAP_DATA_FILE, index=False)
                        except Exception as e:
                            st.warning(f"Could not write CAP file: {e}")

                        st.success(f"Raw data for {city} submitted successfully. Redirecting to GHG Inventory...")
                        st.session_state.menu = "GHG Inventory"
                        st.experimental_rerun()

                

# ---------------------------
# GHG Inventory Page
# ---------------------------
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from io import BytesIO
from datetime import datetime
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# Page settings (if needed)
st.set_page_config(page_title="GHG Inventory", page_icon="🌍", layout="wide")

# Admin auth guard (reuse your admin check)
if not st.session_state.get("authenticated", False):
    admin_login()

# Ensure cap_data exists in session (we intentionally use session only as you requested)
cap_df = st.session_state.get("cap_data", pd.DataFrame()).copy()

# If empty, show warning and return user to CAP Generation
if cap_df.empty:
    st.warning("No CAP raw data available in session. Please submit raw data in 'CAP Generation'.")
    if st.button("Go to CAP Generation"):
        st.session_state.menu = "CAP Generation"
        st.experimental_rerun()
    st.stop()

# Normalize column access function
def col(dfrow, names, default=0):
    """Try multiple candidate column names (compatibility)"""
    for n in names:
        if n in dfrow and pd.notna(dfrow[n]):
            return dfrow[n]
    return default

# Emission factors (India / IPCC-aligned approximations)
# Units: electricity kgCO2/kWh, diesel & petrol kgCO2/litre, LPG kgCO2/kg (approx), natural gas kgCO2/m3, coal kgCO2/ton
EMISSION_FACTORS = {
    "grid_elec": 0.82,      # kgCO2 / kWh  (example value; replace with authoritative value per year / grid)
    "diesel_l": 2.68,       # kgCO2 / litre
    "petrol_l": 2.32,       # kgCO2 / litre
    "lpg_kg": 3.0,          # kgCO2 / kg (approx)
    "cng_kg": 2.75,         # kgCO2 / kg (approx; if using m3, convert externally)
    "natural_gas_m3": 2.0,  # kgCO2 / m3 (approx)
    "coal_t": 2500.0,       # kgCO2 / tonne (approx 2.5 tCO2/ton)
    "waste_t": 0.5,         # tCO2e per ton MSW (highly variable) -> we'll treat as tCO2e/ton (set conservatively)
    "wastewater_m3": 0.00034  # tCO2e per m3 treated ~ 0.34 kgCO2/m3 -> 0.00034 tCO2/m3
}

# Helper: format numbers in Indian style (no decimals)
def format_indian_number(num):
    try:
        num = int(round(float(num)))
        s = str(num)[::-1]
        parts = [s[:3]]
        s = s[3:]
        while s:
            parts.append(s[:2])
            s = s[2:]
        return ','.join(parts)[::-1]
    except:
        return str(num)

# UI header
st.markdown("<h2 style='color:#CFD8DC'>GHG Inventory</h2>", unsafe_allow_html=True)
st.markdown("Visual summary of emissions + sectoral priorities (derived from submitted CAP raw data).")

# Select city (only those present)
city_options = cap_df["City Name"].astype(str).tolist() if "City Name" in cap_df.columns else cap_df["City"].astype(str).tolist()
selected_city = st.selectbox("Select City", city_options)

# find selected record (use either "City Name" or "City")
if "City Name" in cap_df.columns:
    city_row = cap_df[cap_df["City Name"] == selected_city].iloc[0]
else:
    city_row = cap_df[cap_df["City"] == selected_city].iloc[0]

# ---------- Compute Emissions by Sector ----------
# Energy: Electricity (MWh -> kWh), stationary fuels (L or tons), on-site gen
elec_mwh = col(city_row, ["Municipal Electricity (MWh)", "Residential Electricity (MWh)", "Commercial Electricity (MWh)","Utility Solar (MWh)","Rooftop Solar (MWh)","Industrial Electricity (MWh)","Residential_electricity_mwh"], 0)
# Note: some CAP fields may be broken into multiple; we'll compute by reading likely columns
# We'll compute sector-level totals using commonly-named columns and fallbacks.

# Electricity breakdown (if fields exist separately)
res_elec = col(city_row, ["Residential Electricity (MWh)","residential_electricity_mwh"], 0)
com_elec = col(city_row, ["Commercial Electricity (MWh)","commercial_electricity_mwh"], 0)
ind_elec = col(city_row, ["Industrial Electricity (MWh)","industrial_electricity_mwh","Industrial Energy (MWh)"], 0)
mun_elec = col(city_row, ["Municipal Electricity (MWh)","municipal_electricity_mwh","Public Buildings Energy (MWh)"], 0)
street_elec = col(city_row, ["Street Lights Energy","Street Lights Energy (kWh/year)","Street_Lights_Energy","Streetlights Energy (MWh)"], 0)

# convert kWh/MWh consistently: our forms mostly used MWh for electricity; if user stored kWh variants, we try to detect by name
# We'll assume columns with "(MWh)" are in MWh. If someone provided kWh columns, they'd need to be named differently.
total_elec_mwh = sum([res_elec, com_elec, ind_elec, mun_elec, street_elec, elec_mwh])

# Stationary fuels
diesel_l = col(city_row, ["Diesel (L/year)","Diesel_L","Diesel (L/year)","Diesel Gen (L/year)","diesel_l","Diesel (litres)"], 0)
petrol_l = col(city_row, ["Petrol (L/year)","Petrol_L","Petrol (litres)","petrol_l"], 0)
lpg_l = col(city_row, ["LPG (L/year)","LPG_L","lpg_l"], 0)
natural_gas_m3 = col(city_row, ["Natural Gas (m3/year)","Natural_Gas_m3","Gas_Ind_m3","gas_ind"], 0)
coal_t = col(city_row, ["Coal (tons/year)","Coal_t","coal_t"], 0)

# Transport: if user provided fuels directly use that else estimate from vehicle counts + default economy
# Prefer freight_fuel and vehicle fuel cols for accuracy
transport_diesel_l = col(city_row, ["Freight Diesel (L)","Freight_Fuel_Diesel_L","freight_fuel_diesel_l"], 0)
transport_electric_mwh = col(city_row, ["Freight Electricity (MWh)","Freight_Fuel_Electric_MWh","freight_fuel_electric_mwh"], 0)
# If not present, try to estimate:
cars = col(city_row, ["Cars","cars"], 0)
avg_km_cars = col(city_row, ["Avg Km Cars","Avg Km Cars","Avg_Km_Cars","avg_km_cars"], 0)
two_wheelers = col(city_row, ["Two Wheelers","Two_Wheelers","two_wheelers"], 0)
avg_km_2w = col(city_row, ["Avg Km 2W","Avg_Km_2W","avg_km_2w"], 0)
buses = col(city_row, ["Buses","buses"], 0)
avg_km_buses = col(city_row, ["Avg Km Buses","Avg_Km_Buses","avg_km_buses"], 0)
trucks = col(city_row, ["Trucks","trucks"], 0)
avg_km_trucks = col(city_row, ["Avg Km Trucks","Avg_Km_Trucks","avg_km_trucks"], 0)

# Default fuel economies (India-typical approximations) -> litres per 100 km (converted to litres/km)
DEFAULT_ECONOMY = {
    "car_l_per_km": 0.08,    # 8 L/100km -> 0.08 L/km
    "two_wheeler_l_per_km": 0.03,  # 3 L/100km
    "bus_l_per_km": 0.5,     # 50 L/100km
    "truck_l_per_km": 0.6    # 60 L/100km
}

# Estimate transport diesel/petrol if not provided via fuel fields
est_transport_fuel_l = 0
try:
    est_transport_fuel_l += cars * avg_km_cars * DEFAULT_ECONOMY["car_l_per_km"]
    est_transport_fuel_l += two_wheelers * avg_km_2w * DEFAULT_ECONOMY["two_wheeler_l_per_km"]
    est_transport_fuel_l += buses * avg_km_buses * DEFAULT_ECONOMY["bus_l_per_km"]
    est_transport_fuel_l += trucks * avg_km_trucks * DEFAULT_ECONOMY["truck_l_per_km"]
except:
    est_transport_fuel_l = 0

# If explicit transport diesel exists, add it else use estimate
transport_diesel_l_total = transport_diesel_l if transport_diesel_l else est_transport_fuel_l

# Waste & wastewater
msw_tons = col(city_row, ["MSW (tons/year)","Municipal Solid Waste (tons)","MSW_tons","msw_tons"], 0)
wastewater_m3 = col(city_row, ["Wastewater Treated (m3)","Wastewater Treated (m3)","Wastewater Treated (m3)","Wastewater Treated (m3)","Wastewater Treated (m3)","Wastewater_treated_m3","wastewater_treated_m3"], 0)
# fallback to sewage or Sewage_m3
if not wastewater_m3:
    wastewater_m3 = col(city_row, ["Sewage_m3","sewage_m3","Sewage Generated (m³/year)"], 0)

# Water energy
energy_for_water_kwh = col(city_row, ["Energy for Water (kWh)","energy_for_water_kwh","Water Pumping Energy (kWh/year)","Water_Pumping_Energy"], 0)

# ---------- Calculate emissions (tCO2e) ----------
emissions = {}
# Electricity (MWh -> kWh then kgCO2 -> tCO2)
emissions["Electricity (tCO2e)"] = (total_elec_mwh * 1000) * EMISSION_FACTORS["grid_elec"] / 1000.0

# Stationary fuels
emissions["Diesel (tCO2e)"] = (diesel_l + transport_diesel_l_total) * EMISSION_FACTORS["diesel_l"] / 1000.0
emissions["Petrol (tCO2e)"] = petrol_l * EMISSION_FACTORS["petrol_l"] / 1000.0
# For LPG we converted L to kg approximately 1 L ~ 0.54 kg for LPG (liquid), but since forms used L we keep it conservative:
try:
    lpg_kg = lpg_l * 0.54
except:
    lpg_kg = 0
emissions["LPG (tCO2e)"] = lpg_kg * EMISSION_FACTORS["lpg_kg"] / 1000.0

# Natural gas & coal
emissions["Natural Gas (tCO2e)"] = natural_gas_m3 * EMISSION_FACTORS["natural_gas_m3"] / 1000.0
emissions["Coal (tCO2e)"] = coal_t * EMISSION_FACTORS["coal_t"] / 1000.0

# Waste (we store as tCO2e already; using waste factor as tCO2/ton)
emissions["Waste (tCO2e)"] = msw_tons * EMISSION_FACTORS["waste_t"]

# Wastewater (tCO2e)
emissions["Wastewater (tCO2e)"] = wastewater_m3 * EMISSION_FACTORS["wastewater_m3"]

# Aggregate total (sum)
total_emissions_t = sum([v for v in emissions.values() if isinstance(v, (int, float))])

# ---------- Top KPIs (dark cards) ----------
def card_html(label, value, is_input=True, size='18px'):
    color = "#2E7D32" if is_input else "#ECEFF1"  # forest green for input values
    return f"""
    <div style="
        background-color:#2B2B3B;
        padding:14px;
        border-radius:10px;
        text-align:center;
        min-height:80px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    ">
      <div style="color:#CFD8DC;font-weight:600;">{label}</div>
      <div style="color:{color}; font-weight:700; font-size:{size}; margin-top:6px;">{value}</div>
    </div>
    """

st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.markdown(card_html("City", selected_city, is_input=False, size="16px"), unsafe_allow_html=True)
k2.markdown(card_html("Total GHG (tCO₂e)", f"{int(round(total_emissions_t)):,}", is_input=True, size="20px"), unsafe_allow_html=True)
population = col(city_row, ["Population","Population"], 0)
k3.markdown(card_html("Population", format_indian_number(population), is_input=True, size="18px"), unsafe_allow_html=True)
k4.markdown(card_html("Inventory Year", col(city_row, ["Year of Inventory","Inventory_Year","Year of Inventory"], "—"), is_input=False, size="16px"), unsafe_allow_html=True)
st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

# ---------- Visualizations ----------
# 1) Sectoral emissions bar (matplotlib)
sectors = list(emissions.keys())
values = [emissions[s] for s in sectors]

fig1, ax1 = plt.subplots(figsize=(9,4), facecolor="#1E1E2F")
bars = ax1.bar(sectors, values, color=cm.Blues(np.linspace(0.4,0.8,len(sectors))))
ax1.set_facecolor("#1E1E2F")
ax1.tick_params(colors="white", labelsize=10)
plt.xticks(rotation=45, ha='right', color="white")
plt.yticks(color="white")
ax1.set_ylabel("tCO₂e", color="white")
ax1.set_title("Sectoral GHG Emissions (tCO₂e)", color="white")
for i, v in enumerate(values):
    ax1.text(i, v + max(values)*0.01 if max(values)>0 else v + 0.01, f"{round(v,1)}", color="white", ha="center")
st.pyplot(fig1)

# 2) Priority Radar (spider) - build from relevant priority indicators in CAP data
priority_items = {
    "Flood-prone %": col(city_row, ["Percent Flood Prone (%)","Percent Flood Prone (%)","Percent Flood Prone (%)"], 0),
    "Rooftop Solar (MW)": col(city_row, ["Rooftop Solar Potential (MW)","Rooftop Solar Potential (MW)"], 0),
    "Green Cover %": col(city_row, ["Tree Canopy (%)","Tree Canopy (%)","Tree Canopy"], 0),
    "Public Transport Share %": col(city_row, ["Public Transport Share (%)","EV Penetration (%)"], 0),
    "Waste Segregation %": col(city_row, ["Percent Recycled (%)","Percent Recycled (%)","Percent Recycled (%)"], 0),
    "Non-revenue Water %": col(city_row, ["Water Loss (%)","Water Loss (%)"], 0)
}

# Normalize radar scale: scale each metric to 0-100 for plotting (make Rooftop Solar normalized via a reasonable cap)
radar_labels = list(priority_items.keys())
radar_vals_raw = list(priority_items.values())

# normalization function (simple)
def normalize_for_radar(vals):
    norm = []
    # for rooftop solar, assume max potential 1000 MW for normalization (you can change)
    for lab, v in zip(radar_labels, vals):
        if "Rooftop Solar" in lab:
            norm.append(min(100, (v / 1000.0) * 100))  # cap at 100
        else:
            # percent-based items already 0-100; others scale
            try:
                norm.append(min(100, float(v)))
            except:
                norm.append(0)
    return norm

radar_vals = normalize_for_radar(radar_vals_raw)
# close loop
angles = np.linspace(0, 2 * np.pi, len(radar_labels), endpoint=False).tolist()
radar_vals_loop = radar_vals + radar_vals[:1]
angles_loop = angles + angles[:1]

fig2, ax2 = plt.subplots(figsize=(6,6), subplot_kw=dict(polar=True), facecolor="#1E1E2F")
ax2.plot(angles_loop, radar_vals_loop, color="#2E7D32", linewidth=2)
ax2.fill(angles_loop, radar_vals_loop, color="#2E7D32", alpha=0.25)
ax2.set_xticks(angles)
ax2.set_xticklabels(radar_labels, color="white", fontsize=10)
ax2.set_yticklabels([])
ax2.set_title("Sectoral Priorities & Resilience (normalized)", color="white")
st.pyplot(fig2)

# Save plots to in-memory PNGs for embedding in PDF
def fig_to_png_bytes(fig, facecolor="#1E1E2F"):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight", facecolor=facecolor)
    buf.seek(0)
    return buf

png1 = fig_to_png_bytes(fig1)
png2 = fig_to_png_bytes(fig2)

# ---------- PDF generator ----------
def make_pdf(city_row, emissions, png_buffers):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"City Climate Action Plan — GHG Inventory", styles["Title"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"City: <b>{selected_city}</b>", styles["Normal"]))
    population_text = format_indian_number(col(city_row, ["Population","Population"], 0))
    story.append(Paragraph(f"Population: {population_text}", styles["Normal"]))
    story.append(Paragraph(f"Inventory Year: {col(city_row,['Year of Inventory','Inventory_Year','Year of Inventory'], '')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Sectoral Emissions (tCO₂e)</b>", styles["Heading2"]))
    for k, v in emissions.items():
        story.append(Paragraph(f"{k}: {round(v,2)}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Add charts images (from BytesIO)
    for pb in png_buffers:
        # reportlab Image accepts a filename or a file-like object
        img = Image(pb, width=450, height=260)
        story.append(img)
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Generated on: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles["Normal"]))
    doc.build(story)
    buf.seek(0)
    return buf

pdf_buf = make_pdf(city_row, emissions, [png1, png2])

# Download PDF button (in a two-column row)
col_dl, col_nav = st.columns([2,1])
with col_dl:
    st.download_button(
        label="Download CAP Summary (PDF)",
        data=pdf_buf,
        file_name=f"CAP_Report_{selected_city.replace(' ','_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )

# Back & Actions buttons
with col_nav:
    if st.button("← Back to CAP Generation"):
        st.session_state.menu = "CAP Generation"
        st.experimental_rerun()
    if st.button("View Actions"):
        st.session_state.menu = "Actions"
        st.experimental_rerun()

# End of page


# ---------------------------
# Actions
# ---------------------------
elif menu == "Actions":
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
