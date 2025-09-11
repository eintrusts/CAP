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

# ghg_inventory.py
# Modular GHG Inventory Streamlit page (Plotly visuals, PDF export, Indian number format)
# Drop this file into your app directory and import + call render_ghg_inventory() from your main app.

import io
import os
import math
from datetime import datetime

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Optional libs for PDF export
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ---------------------------
# Indian Number Formatter (no decimals)
# ---------------------------
def format_indian_number(num):
    """
    Format number in Indian style without decimals (e.g., 12,34,567).
    Works for int, float and numeric strings. Returns string.
    """
    try:
        if pd.isna(num):
            return "0"
        n = int(round(float(num)))
        s = str(n)[::-1]
        parts = [s[:3]]
        s = s[3:]
        while s:
            parts.append(s[:2])
            s = s[2:]
        return ",".join(parts)[::-1]
    except Exception:
        return str(num)

# ---------------------------
# Default emission factors (example, configurable)
# Values are kg CO2e per unit input (documented inline).
# These are illustrative and should be replaced with official IPCC/NPC India factors for audit.
# ---------------------------
DEFAULT_EF = {
    # Electricity grid (kgCO2e / kWh) - example for India ~0.7-0.9; set to 0.82 as default here
    "grid_electricity_kgCO2e_per_kWh": 0.82,
    # Diesel (kgCO2e / litre)
    "diesel_kgCO2e_per_l": 2.68,
    # Petrol (kgCO2e / litre)
    "petrol_kgCO2e_per_l": 2.31,
    # LPG (kgCO2e / litre)
    "lpg_kgCO2e_per_l": 1.51,
    # Natural gas (kgCO2e / m3) approximate
    "ng_kgCO2e_per_m3": 2.0,
    # Coal (kgCO2e / ton)
    "coal_kgCO2e_per_ton": 2450.0 / 1000.0,  # if 2450 kgCO2e/ton -> 2450
    # Biomass assumed carbon-neutral for combustion (set 0 by default)
    "biomass_kgCO2e_per_ton": 0.0,
    # Electricity for freight / MWh -> convert MWh->kWh
    # other sector-specific EFs can be added and preserved for auditing
}

# ---------------------------
# Helper: Safely get latest CAP record (most recent Submission Date)
# ---------------------------
def _get_latest_cap_record():
    # Priority: st.session_state.cap_data (in-memory), otherwise CSV file CAP_DATA_FILE
    df = st.session_state.get("cap_data")
    if df is None or df.empty:
        CAP_DATA_FILE = "cap_raw_data.csv"
        if os.path.exists(CAP_DATA_FILE):
            try:
                df = pd.read_csv(CAP_DATA_FILE)
            except Exception:
                df = pd.DataFrame()
    # Normalize column names if necessary (some CAP code used "City" vs "City Name")
    if not df.empty:
        if "City Name" not in df.columns and "City" in df.columns:
            df = df.rename(columns={"City": "City Name"})
    if df is None:
        df = pd.DataFrame()
    if df.empty:
        return None, df
    # choose the most recent by Submission Date
    date_cols = [c for c in df.columns if "Submission" in c or "Date" in c]
    try:
        if "Submission Date" in df.columns:
            df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")
            latest = df.sort_values("Submission Date", ascending=False).iloc[0]
            return latest.to_dict(), df
    except Exception:
        pass
    # fallback: last row
    latest = df.iloc[-1]
    return latest.to_dict(), df

# ---------------------------
# Emission calculation functions (simple, auditable)
# All outputs in metric tons CO2e (tCO2e)
# ---------------------------
def calc_energy_emissions(record, ef=DEFAULT_EF):
    """
    Calculate emissions from electricity and stationary fuels.
    record: dict-like with keys (MWh values or L/m3/ton where indicated)
    Returns float: tCO2e and breakdown dict by sub-sector
    """
    # Electricity fields in MWh in CAP form (many fields named e.g. 'Residential Electricity (MWh)')
    # Convert MWh -> kWh by *1000
    factor = ef.get("grid_electricity_kgCO2e_per_kWh", 0.82)
    sub = {}
    total_kg = 0.0

    # Electricity sub-sectors
    for k_label, friendly in [
        ("Municipal Electricity (MWh)", "Municipal"),
        ("Residential Electricity (MWh)", "Residential"),
        ("Commercial Electricity (MWh)", "Commercial"),
        ("Industrial Electricity (MWh)", "Industrial"),
        ("Rooftop Solar (MWh)", "Rooftop Solar (assumed zero-grid)"),
        ("Utility Solar (MWh)", "Utility Solar (assumed zero-grid)"),
        ("Wind (MWh)", "Wind (assumed zero-grid)"),
        ("Biomass (MWh)", "Biomass (assumed zero-grid)"),
    ]:
        val = float(record.get(k_label, 0) or 0)
        if any(src in k_label for src in ["Solar", "Wind", "Biomass"]):
            # Renewables treated as zero scope-2 grid emissions here (user can later include life-cycle EFs)
            kg = 0.0
        else:
            # MWh -> kWh
            kg = val * 1000.0 * factor
        sub[friendly] = kg / 1000.0  # convert to tCO2e
        total_kg += kg

    # Stationary fuels (litres/tons/m3)
    diesel_l = float(record.get("Diesel_L", record.get("Diesel (L/year)", 0) or 0))
    petrol_l = float(record.get("Petrol_L", record.get("Petrol (L/year)", 0) or 0))
    lpg_l = float(record.get("LPG_L", record.get("LPG (L/year)", 0) or 0))
    ng_m3 = float(record.get("Natural_Gas_m3", record.get("Gas Ind m3", 0) or 0))
    coal_t = float(record.get("Coal_t", record.get("Coal (tons/year)", 0) or 0))

    kg_diesel = diesel_l * ef.get("diesel_kgCO2e_per_l", 2.68)
    kg_petrol = petrol_l * ef.get("petrol_kgCO2e_per_l", 2.31)
    kg_lpg = lpg_l * ef.get("lpg_kgCO2e_per_l", 1.51)
    kg_ng = ng_m3 * ef.get("ng_kgCO2e_per_m3", 2.0)
    kg_coal = coal_t * ef.get("coal_kgCO2e_per_ton", 1000.0)  # default might be 2450; ensure consistent

    sub["Diesel (stationary)"] = kg_diesel / 1000.0
    sub["Petrol (stationary)"] = kg_petrol / 1000.0
    sub["LPG (stationary)"] = kg_lpg / 1000.0
    sub["Natural Gas (stationary)"] = kg_ng / 1000.0
    sub["Coal (stationary)"] = kg_coal / 1000.0

    total_kg += (kg_diesel + kg_petrol + kg_lpg + kg_ng + kg_coal)

    total_t = total_kg / 1000.0
    return total_t, sub

def calc_transport_emissions(record, ef=DEFAULT_EF):
    """
    Estimate transport emissions by vehicle counts * avg km * EF.
    This function uses very simple per-km emission approximations:
      - Diesel vehicles (cars/trucks/buses): kgCO2e per km
      - Petrol vehicles: kgCO2e per km
      - CNG: lower per km
      - Electric vehicles: counted at grid emissions via electricity used (simple proxy)
    For audit, these EFs should be replaced with official per-vehicle/per-fuel EFs.
    Returns tCO2e and breakdown dict.
    """
    # Basic per-km EFs (kgCO2e/km) - example placeholders
    EF_PER_KM = {
        "car_diesel": 0.21,
        "car_petrol": 0.18,
        "two_wheeler_petrol": 0.08,
        "bus_diesel": 0.9,
        "truck_diesel": 0.8,
        "cng_per_km": 0.12,
        "ev_grid_per_km": 0.12  # proxy (should be computed via kWh/km * grid factor)
    }

    cars = float(record.get("Cars", 0) or 0)
    buses = float(record.get("Buses", 0) or 0)
    trucks = float(record.get("Trucks", 0) or 0)
    two_wheelers = float(record.get("Two Wheelers", 0) or record.get("Two_Wheelers", 0) or 0)

    avg_km_cars = float(record.get("Avg Km Cars", record.get("Avg_Km_Cars", 0) or 0))
    avg_km_buses = float(record.get("Avg Km Buses", record.get("Avg_Km_Buses", 0) or 0))
    avg_km_trucks = float(record.get("Avg Km Trucks", record.get("Avg_Km_Trucks", 0) or 0))
    avg_km_2w = float(record.get("Avg Km 2W", record.get("Avg_Km_2W", 0) or 0))

    kg_total = 0.0
    breakdown = {}

    kg_cars = cars * avg_km_cars * EF_PER_KM["car_petrol"]  # assume petrol cars by default
    kg_buses = buses * avg_km_buses * EF_PER_KM["bus_diesel"]
    kg_trucks = trucks * avg_km_trucks * EF_PER_KM["truck_diesel"]
    kg_2w = two_wheelers * avg_km_2w * EF_PER_KM["two_wheeler_petrol"]

    kg_total += (kg_cars + kg_buses + kg_trucks + kg_2w)
    breakdown["Cars (tCO2e)"] = kg_cars / 1000.0
    breakdown["Buses (tCO2e)"] = kg_buses / 1000.0
    breakdown["Trucks (tCO2e)"] = kg_trucks / 1000.0
    breakdown["2/3-Wheelers (tCO2e)"] = kg_2w / 1000.0

    # Freight diesel if specific volume provided
    freight_diesel_l = float(record.get("Freight Diesel (L)", record.get("Freight_Fuel_Diesel_L", 0) or 0))
    if freight_diesel_l > 0:
        kg_freight = freight_diesel_l * ef.get("diesel_kgCO2e_per_l", 2.68)
        kg_total += kg_freight
        breakdown["Freight diesel (tCO2e)"] = kg_freight / 1000.0

    return (kg_total / 1000.0), breakdown

def calc_waste_emissions(record, ef=DEFAULT_EF):
    """
    Estimate waste sector emissions (landfill methane approximated using MSW and landfill fraction).
    This is a simplified approach — for audit use IPCC decay-model or CH4 collection data.
    Returns tCO2e and breakdown dict.
    """
    msw_tons = float(record.get("MSW (tons/year)", record.get("Municipal Solid Waste (tons)", 0) or 0))
    percent_landfilled = float(record.get("Percent Landfilled (%)", record.get("Landfill_Frac", 0) or 0))
    landfill_capture_pct = float(record.get("Landfill Methane Capture (%)", record.get("Landfill_Methane_Capture", 0) or 0))

    # Rough emission factor (kgCO2e per ton MSW landfilled) placeholder
    EF_MSW_LANDFILL = 200.0  # kgCO2e per ton (example)
    landfill_tons = msw_tons * (percent_landfilled / 100.0)
    kg = landfill_tons * EF_MSW_LANDFILL * (1.0 - landfill_capture_pct / 100.0)
    breakdown = {
        "Landfilled (tCO2e)": kg / 1000.0,
        "Recycled (tCO2e avoided approx)": 0.0
    }
    return (kg / 1000.0), breakdown

def calc_water_emissions(record, ef=DEFAULT_EF):
    """
    Estimate energy-related emissions from water pumping and wastewater treatment.
    record keys: 'Energy for Water (kWh)' or 'Energy for Water (MWh)'
    """
    energy_kwh = float(record.get("Energy for Water (kWh)", record.get("Energy for Water (MWh)", 0) or 0))
    # if "Energy for Water (MWh)" provided, convert
    if energy_kwh == 0 and record.get("Energy for Water (MWh)", None):
        energy_kwh = float(record.get("Energy for Water (MWh)", 0)) * 1000.0

    grid_factor = ef.get("grid_electricity_kgCO2e_per_kWh", 0.82)
    kg = energy_kwh * grid_factor
    return (kg / 1000.0), {"Water energy (tCO2e)": kg / 1000.0}

# ---------------------------
# Plot styling helpers (dark theme)
# ---------------------------
PLOTLY_TEMPLATE = "plotly_dark"

def _plot_sector_bar(sector_values):
    """sector_values: dict {sector: value_tCO2e}"""
    labels = list(sector_values.keys())
    vals = [v for v in sector_values.values()]
    fig = px.bar(x=labels, y=vals, text=[format_indian_number(round(v)) for v in vals],
                 labels={'x':"", 'y':'tCO2e'}, title="Sector-wise Emissions (tCO2e)",
                 template=PLOTLY_TEMPLATE, color=vals, color_continuous_scale="Viridis")
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_layout(yaxis=dict(title="tCO2e"))
    return fig

def _plot_sector_pie(sector_values):
    labels = list(sector_values.keys())
    vals = [v for v in sector_values.values()]
    fig = px.pie(values=vals, names=labels, title="Emissions Share by Sector", template=PLOTLY_TEMPLATE,
                 hole=0.35)
    return fig

def _plot_radar(priorities_scores):
    """
    priorities_scores: dict {sector: normalized_score (0..100)}
    """
    categories = list(priorities_scores.keys())
    values = [priorities_scores[c] for c in categories]
    # radar requires repetition of first point
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]],
                                  theta=categories + [categories[0]],
                                  mode='lines+markers',
                                  name='Priority score',
                                  fill='toself'))
    fig.update_layout(template=PLOTLY_TEMPLATE,
                      polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                      showlegend=False,
                      title="Sectoral Priority / Resilience Radar (0-100)")
    return fig

# ---------------------------
# Build PDF (ReportLab) embedding PNG images created from plotly
# ---------------------------
def build_pdf_report(city_name, summary_table_df, plotly_figs, notes=""):
    """
    plotly_figs: list of (title, fig) where fig is a plotly figure.
    Returns: bytes of the generated PDF or raises if reportlab/kaleido not available.
    """
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab not available on server. Install reportlab to enable PDF export.")

    # Create images from plotly figures using kaleido -> fig.to_image
    images = []
    for title, fig in plotly_figs:
        try:
            img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
            images.append((title, io.BytesIO(img_bytes)))
        except Exception as e:
            # skip figure if image generation fails
            images.append((title, None))

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title page
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 60, f"Climate Action Plan Report: {city_name}")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 80, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.line(40, height - 90, width - 40, height - 90)

    # Summary table
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, height - 120, "Summary (sector emissions in tCO2e)")
    y = height - 140
    c.setFont("Helvetica", 10)
    for idx, row in summary_table_df.iterrows():
        c.drawString(45, y, f"{row['Sector']}: {format_indian_number(row['Emissions_tCO2e'])}")
        y -= 16
        if y < 120:
            c.showPage()
            y = height - 60

    # Insert plots
    for title, img_io in images:
        if img_io is None:
            continue
        img_io.seek(0)
        img_reader = ImageReader(img_io)
        # Fit into A4 with margins
        img_w = width - 80
        img_h = img_w * 9.0 / 16.0
        if y - img_h < 60:
            c.showPage()
            y = height - 60
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, title)
        y -= 20
        c.drawImage(img_reader, 40, y - img_h, width=img_w, height=img_h)
        y -= (img_h + 30)
        if y < 120:
            c.showPage()
            y = height - 60

    # Notes (if any)
    if notes:
        c.showPage()
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, height - 60, "Notes")
        c.setFont("Helvetica", 10)
        text = c.beginText(40, height - 80)
        for line in notes.split("\n"):
            text.textLine(line)
        c.drawText(text)

    c.save()
    buffer.seek(0)
    return buffer.read()

# ---------------------------
# Main render function for the page
# ---------------------------
def render_ghg_inventory():
    """
    Call this from your main app when menu == "GHG Inventory".
    """

    st.header("GHG Inventory & Sectoral Priorities")
    # Admin check - assume main app handles authentication; still check session_state
    if not st.session_state.get("authenticated", False):
        st.warning("Admin login required to view GHG Inventory.")
        return

    # Pull latest CAP record
    record, cap_df = _get_latest_cap_record()
    if record is None:
        st.info("No CAP raw data found in session. Please submit data on CAP Generation page.")
        return

    city_name = record.get("City Name", record.get("City", "Unnamed City"))

    # --- Calculations per sector ---
    energy_t, energy_breakdown = calc_energy_emissions(record)
    transport_t, transport_breakdown = calc_transport_emissions(record)
    waste_t, waste_breakdown = calc_waste_emissions(record)
    water_t, water_breakdown = calc_water_emissions(record)

    # For green cover, set small proxy emissions (usually a sink, but for summary keep 0)
    green_t = 0.0

    # total
    sector_totals = {
        "Energy": energy_t,
        "Mobility": transport_t,
        "Waste": waste_t,
        "Water": water_t,
        "Green Cover": green_t
    }
    total_emissions = sum(sector_totals.values())

    # --- Top summary blocks ---
    st.markdown("### City: " + str(city_name))
    cols = st.columns(5)
    for col, (label, val) in zip(cols, sector_totals.items()):
        display_val = format_indian_number(val)
        col.markdown(f"""
            <div style="
                background-color:#2B2B3B;
                padding:12px;
                border-radius:10px;
                text-align:center;
                color:#FFFFFF;
            ">
                <div style='font-size:12px'>{label}</div>
                <div style='font-size:20px; font-weight:700; color:#54c750'>{display_val} tCO2e</div>
            </div>
        """, unsafe_allow_html=True)
    # Total block (full width)
    st.markdown("---")
    st.markdown(f"""
        <div style="
            background: linear-gradient(90deg,#1f8a1f,#2ecc71);
            padding:14px;
            border-radius:10px;
        ">
            <h3 style="margin:0; color:white">Total Emissions (city)</h3>
            <h1 style="margin:0; color:white">{format_indian_number(total_emissions)} tCO2e</h1>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # --- Charts: Sector bar + pie + radar ---
    st.subheader("Emissions Visuals")
    bar_fig = _plot_sector_bar(sector_totals)
    pie_fig = _plot_sector_pie(sector_totals)

    # Radar: priorities/resilience normalized from record inputs (simple heuristic)
    # Compose scores from selected resilience indicators into 0..100 per sector
    def _norm(x, cap=100): return float(min(max(x, 0), cap))

    radar_scores = {
        "Energy": _norm(record.get("Rooftop Solar Potential (MW)", record.get("Rooftop Solar Potential (MW)", 0)) / (record.get("Population",1)/1000000) * 20 if record.get("Population") else 0),
        "Green Cover": _norm(record.get("Tree Canopy (%)", 0)),
        "Mobility": _norm(min(record.get("EV Penetration (%)", record.get("EV Penetration (%)", 0)), 100)),
        "Water": _norm(100 - record.get("Percent Flood Prone (%)", 0)),  # higher flood-prone -> lower score
        "Waste": _norm(record.get("Percent Recycled (%)", 0))
    }
    # Scale to 0..100
    for k in list(radar_scores.keys()):
        v = radar_scores[k] or 0
        radar_scores[k] = float(max(0.0, min(100.0, v)))

    radar_fig = _plot_radar(radar_scores)

    # Display charts side-by-side
    c1, c2 = st.columns([1.2, 1])
    c1.plotly_chart(bar_fig, use_container_width=True)
    c2.plotly_chart(pie_fig, use_container_width=True)
    st.plotly_chart(radar_fig, use_container_width=True)

    # --- Sector-specific visualizations (compact) ---
    st.subheader("Sector Breakdown Visuals")

    # Energy breakdown stacked bar (grid vs renewables vs stationary fuels)
    eb_labels = []
    eb_vals = []
    # grid electricity total (sum municipal/residential/commercial/industrial)
    grid_kwh = (
        (record.get("Municipal Electricity (MWh)", 0) or 0) * 1000.0 +
        (record.get("Residential Electricity (MWh)", 0) or 0) * 1000.0 +
        (record.get("Commercial Electricity (MWh)", 0) or 0) * 1000.0 +
        (record.get("Industrial Electricity (MWh)", 0) or 0) * 1000.0
    )
    rooftop_kwh = (record.get("Rooftop Solar (MWh)", record.get("Rooftop Solar (MWh)", 0)) or 0) * 1000.0
    utility_kwh = (record.get("Utility Solar (MWh)", 0) or 0) * 1000.0
    wind_kwh = (record.get("Wind (MWh)", 0) or 0) * 1000.0
    biomass_kwh = (record.get("Biomass (MWh)", 0) or 0) * 1000.0
    stationary_diesel_l = float(record.get("Diesel_L", 0) or 0)

    energy_breakdown = {
        "Grid (kWh)": grid_kwh,
        "Rooftop Solar (kWh)": rooftop_kwh,
        "Utility Solar (kWh)": utility_kwh,
        "Wind (kWh)": wind_kwh,
        "Biomass (kWh)": biomass_kwh,
        "Diesel backup (L)": stationary_diesel_l
    }
    # Convert kWh -> MWh for display convenience
    eb_df = pd.DataFrame({
        "Source": list(energy_breakdown.keys()),
        "Value": [energy_breakdown[k] for k in energy_breakdown]
    })
    # show stacked bar for top 5 (skip Diesel linear unit difference)
    fig_energy = px.bar(eb_df[eb_df["Value"]>0], x="Source", y="Value", text=eb_df["Value"].apply(lambda x: format_indian_number(x) if x>0 else "0"),
                       title="Energy Breakdown (kWh / litres)", template=PLOTLY_TEMPLATE)
    fig_energy.update_traces(textposition="outside")
    st.plotly_chart(fig_energy, use_container_width=True)

    # Mobility pie: fleet composition
    mob_comp = {
        "Cars": float(record.get("Cars", 0) or 0),
        "Buses": float(record.get("Buses", 0) or 0),
        "Trucks": float(record.get("Trucks", 0) or 0),
        "2/3-Wheelers": float(record.get("Two Wheelers", record.get("Two_Wheelers", 0)) or 0)
    }
    mob_df = pd.DataFrame({"Type": list(mob_comp.keys()), "Count": list(mob_comp.values())})
    if mob_df["Count"].sum() > 0:
        fig_mob = px.pie(mob_df, names="Type", values="Count", title="Vehicle Fleet Composition", template=PLOTLY_TEMPLATE)
        st.plotly_chart(fig_mob, use_container_width=True)
    else:
        st.info("No mobility fleet data entered to visualise.")

    # Water risks chart: flood-prone, drought risk, wastewater treated
    water_scores = {
        "Flood-prone (%)": float(record.get("Percent Flood Prone (%)", 0) or 0),
        "Wastewater Treated (m3)": float(record.get("Wastewater Treated (m3)", record.get("Wastewater Treated (m3)", 0) or 0)),
        "Water Loss (%)": float(record.get("Water Loss (%)", 0) or 0)
    }
    # Convert wastewater to a normalized 0-100 for plotting
    max_waste = max(1.0, water_scores["Wastewater Treated (m3)"])
    water_plot_vals = [water_scores["Flood-prone (%)"], (water_scores["Wastewater Treated (m3)"] / max_waste) * 100.0, water_scores["Water Loss (%)"]]
    fig_water = go.Figure(data=[go.Bar(x=["Flood-prone (%)", "Wastewater Treated (norm%)", "Water Loss (%)"], y=water_plot_vals)])
    fig_water.update_layout(template=PLOTLY_TEMPLATE, title="Water Risks & Capacity (normalized)")
    st.plotly_chart(fig_water, use_container_width=True)

    # Waste segregation donut
    waste_breakdown_vals = {
        "Landfilled (%)": float(record.get("Percent Landfilled (%)", 0) or 0),
        "Recycled (%)": float(record.get("Percent Recycled (%)", 0) or 0),
        "Composted (%)": float(record.get("Percent Composted (%)", 0) or 0),
        "Incinerated (%)": 100.0 - sum([
            float(record.get("Percent Landfilled (%)", 0) or 0),
            float(record.get("Percent Recycled (%)", 0) or 0),
            float(record.get("Percent Composted (%)", 0) or 0),
        ])
    }
    wd_df = pd.DataFrame({"Method": list(waste_breakdown_vals.keys()), "Share": list(waste_breakdown_vals.values())})
    fig_waste = px.pie(wd_df, names="Method", values="Share", title="Waste Treatment Share (%)", template=PLOTLY_TEMPLATE, hole=0.4)
    st.plotly_chart(fig_waste, use_container_width=True)

    # --- Data table (summary)
    st.subheader("Emissions Summary Table (tCO2e)")
    summary_rows = []
    for s, v in sector_totals.items():
        summary_rows.append({"Sector": s, "Emissions_tCO2e": round(v, 2)})
    summary_df = pd.DataFrame(summary_rows)
    # Format numbers for display in HTML table
    summary_df_display = summary_df.copy()
    summary_df_display["Emissions_tCO2e"] = summary_df_display["Emissions_tCO2e"].apply(lambda x: format_indian_number(x))
    st.table(summary_df_display)

    # --- PDF Export ---
    st.subheader("Export / Report")
    pdf_notes = st.text_area("Notes to include in PDF (optional)", "")
    cols_pdf = st.columns([2, 2, 1])
    # Generate PDF button
    if REPORTLAB_AVAILABLE:
        # Build PDF bytes on demand
        if cols_pdf[0].button("Generate Printable PDF Report"):
            # Prepare plotly figs for embedding
            figs_for_pdf = [
                ("Sector emissions (bar)", bar_fig),
                ("Emissions share (pie)", pie_fig),
                ("Priority radar", radar_fig),
                ("Energy breakdown", fig_energy),
            ]
            try:
                pdf_bytes = build_pdf_report(city_name, summary_df, figs_for_pdf, notes=pdf_notes)
                st.success("PDF generated.")
                st.download_button("Download PDF CAP Report", data=pdf_bytes,
                                   file_name=f"CAP_Report_{city_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                                   mime="application/pdf")
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}. Ensure 'kaleido' + 'reportlab' are installed on server.")
    else:
        st.info("PDF export unavailable (reportlab not installed on server).")

    # --- View Actions button (redirect to Actions / Goals) ---
    st.markdown("---")
    if st.button("View Actions / Goals"):
        st.session_state.menu = "Actions / Goals"
        st.experimental_rerun()

# When imported, render_ghg_inventory is available. Call from your main file:
# from ghg_inventory import render_ghg_inventory
# if menu == "GHG Inventory": render_ghg_inventory()


    # -------------------------
    # View Actions Button
    # -------------------------
    if st.button("➡️ View Actions"):
        st.session_state["menu"] = "Actions"
        st.experimental_rerun()



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
