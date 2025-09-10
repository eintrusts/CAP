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

    # ensure meta data is present
    df_meta = st.session_state.get("data", pd.DataFrame()).copy()
    city = st.selectbox("Select City", list(cities_districts.keys()))

    if not df_meta.empty and city in df_meta["City Name"].values:
        row = df_meta[df_meta["City Name"] == city].iloc[0]
        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- Card Rendering Function ----------
        def render_card(col, label, value, is_input=False, bg_color="#34495E"):
            """
            Render a metric card.
            - is_input: if True, value is shown bold and larger (inputted data)
            - bg_color: card background
            """
            # keep text color uniform, make inputted values bold + larger
            if is_input:
                value_html = f"<b style='font-size:18px;'>{value}</b>"
            else:
                value_html = f"<span style='font-size:15px;'>{value}</span>"

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

        # safe retrieval and conversions
        population = row.get("Population", 0) or 0
        area = row.get("Area (sq.km)", row.get("Geographical Area (sq. km)", 0)) or 0
        # density as integer, no decimals
        try:
            density = int(round(float(population) / float(area))) if float(area) > 0 else "—"
        except:
            density = "—"

        # Est. year - show as integer without .0
        est_raw = row.get("Est. Year", row.get("Est. Year", ""))
        try:
            est_year = int(float(est_raw)) if (est_raw is not None and str(est_raw) != "") else "—"
        except:
            est_year = est_raw or "—"

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
            ("CAP Status", cap_status)
        ]

        non_input_labels = {"District", "ULB Category"}  # these are not treated as "inputted" for styling

        for i in range(0, len(basic_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, basic_metrics[i:i+3]):
                bg = cap_color if label == "CAP Status" else "#34495E"
                is_input = False if label in non_input_labels else True
                render_card(col, label, value, is_input=is_input, bg_color=bg)

        # CAP Link as clickable (keeps text color same as app)
        if cap_link:
            link_html = f"""
            <div style='
                background-color:#34495E;
                color:#ECEFF1;
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
                <a href='{cap_link}' target='_blank' style='color:#ECEFF1; text-decoration:underline;'>View CAP Document</a>
            </div>
            """
            st.markdown(link_html, unsafe_allow_html=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- ENVIRONMENTAL INFORMATION ----------
        st.markdown("<h4>Environmental Information</h4>", unsafe_allow_html=True)
        ghg_total = row.get("GHG Emissions", 0) or 0
        try:
            per_capita_ghg = int(round(float(ghg_total) / float(population))) if float(population) > 0 else 0
        except:
            per_capita_ghg = 0

        renewable_energy = row.get("Renewable Energy (MWh)", 0) or 0
        urban_green = row.get("Urban Green Area (ha)", 0) or 0
        solid_waste = row.get("Municipal Solid Waste (tons)", 0) or 0
        wastewater = row.get("Wastewater Treated (m3)", 0) or 0
        waste_landfilled = row.get("Waste Landfilled (%)", 0)
        waste_composted = row.get("Waste Composted (%)", 0)

        env_metrics = [
            ("GHG Emissions (tCO2e)", format_indian_number(ghg_total)),
            ("Per Capita Emissions (tCO2e)", format_indian_number(per_capita_ghg)),
            ("Renewable Energy (MWh)", format_indian_number(renewable_energy)),
            ("Urban Green Area (ha)", format_indian_number(urban_green)),
            ("Solid Waste (tons)", format_indian_number(solid_waste)),
            ("Wastewater Treated (m³)", format_indian_number(wastewater)),
            ("Waste Landfilled (%)", f"{int(round(waste_landfilled))}%"),
            ("Waste Composted (%)", f"{int(round(waste_composted))}%")
        ]

        for i in range(0, len(env_metrics), 3):
            cols = st.columns(3)
            for col, (label, value) in zip(cols, env_metrics[i:i+3]):
                render_card(col, label, value, is_input=True)

        st.markdown("<hr style='border:0.5px solid #546E7A;'>", unsafe_allow_html=True)

        # ---------- SOCIAL INFORMATION ----------
        st.markdown("<h4>Social Information</h4>", unsafe_allow_html=True)
        males = row.get("Males", 0) or 0
        females = row.get("Females", 0) or 0
        total_pop = (males or 0) + (females or 0)
        children_m = row.get("Children Male", 0) or 0
        children_f = row.get("Children Female", 0) or 0
        total_children = children_m + children_f
        literacy_m = row.get("Male Literacy (%)", 0) or 0
        literacy_f = row.get("Female Literacy (%)", 0) or 0
        literacy_total = int(round((float(literacy_m) + float(literacy_f)) / 2)) if (literacy_m or literacy_f) else 0

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
            ("BPL Households (%)", f"{int(round(row.get('BPL Households (%)',0)))}%")
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
            ("Website", row.get("Website","—"))
        ]

        for i in range(0, len(contact_metrics), 2):
            cols = st.columns(2)
            for col, (label, value) in zip(cols, contact_metrics[i:i+2]):
                render_card(col, label, value, is_input=False)

# ---------------------------
# Admin Panel Page (Safe City Switching & Auto-Fill)
# ---------------------------
elif menu == "Admin":
    st.header("Admin Dashboard")

    if not st.session_state.get("authenticated", False):
        admin_login()
    else:
        st.subheader("Add / Update City / Maharashtra Data")

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
import streamlit as st
import pandas as pd
import os
from datetime import datetime

CAP_DATA_FILE = "cap_raw_data.csv"   # ensure this matches your app-wide constant

if menu == "CAP Generation":
    st.header("CAP Generation : Comprehensive Data Collection")

    # Require admin
    if not st.session_state.get("authenticated", False):
        admin_login()
    else:
        st.markdown(
            "Collect detailed city-level raw data for generating a comprehensive GHG inventory. "
            "Sectoral priority / vulnerability questions are embedded in each sector."
        )

        # Load existing CAP data (if any)
        if os.path.exists(CAP_DATA_FILE):
            try:
                cap_df = pd.read_csv(CAP_DATA_FILE)
            except Exception:
                cap_df = pd.DataFrame()
        else:
            cap_df = pd.DataFrame()

        # Unique form key to avoid duplicate form error
        with st.form("cap_comprehensive_form_v3", clear_on_submit=False):

            # -------------------
            # 1. General City Info
            # -------------------
            with st.expander("1. General City Info", expanded=True):
                city_name = st.selectbox("City Name", [""] + list(cities_districts.keys()))
                state = st.text_input("State / Province")
                population = st.number_input("Total Population", min_value=0, value=0, step=1000)
                households = st.number_input("Total Households (optional)", min_value=0, value=0, step=100)
                area_km2 = st.number_input("Area (sq.km)", min_value=0.0, value=0.0, step=0.1)
                admin_type = st.selectbox("Administrative Type", ["Municipal Corporation", "Municipal Council", "Nagar Panchayat", "Other"])
                inventory_year = st.number_input("Year of Inventory", min_value=2000, max_value=2100, value=datetime.now().year)
                climate_zone = st.selectbox("Climate Zone (for priority analysis)", ["Tropical", "Arid", "Temperate", "Coastal", "Mountain", "Other"])
                urbanization_rate = st.number_input("Urbanization Rate (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                notes_general = st.text_area("Notes / Local context (optional)", value="", height=80)

            # -------------------
            # 2. Energy Sector
            # -------------------
            with st.expander("2. Energy Sector (Electricity, Heat, Stationary Fuels)", expanded=False):
                st.subheader("Electricity & Heat Consumption")
                municipal_electricity_mwh = st.number_input("Municipal buildings (MWh/year)", min_value=0, value=0, step=10)
                residential_electricity_mwh = st.number_input("Residential (MWh/year)", min_value=0, value=0, step=10)
                commercial_electricity_mwh = st.number_input("Commercial (MWh/year)", min_value=0, value=0, step=10)
                industrial_electricity_mwh = st.number_input("Industrial (MWh/year)", min_value=0, value=0, step=10)
                purchased_heat_gj = st.number_input("Purchased heat/steam (GJ/year)", min_value=0, value=0, step=10)

                st.subheader("On-site generation & stationary fuels")
                diesel_gen_l = st.number_input("Diesel generators (litres/year or specify units)", min_value=0, value=0, step=10)
                gas_turbine_fuel_m3 = st.number_input("Gas turbine fuel (m³/year)", min_value=0, value=0, step=10)
                stationary_diesel_l = st.number_input("Stationary diesel (L/year)", min_value=0, value=0, step=10)
                stationary_petrol_l = st.number_input("Stationary petrol (L/year)", min_value=0, value=0, step=10)
                stationary_lpg_l = st.number_input("LPG (L/year)", min_value=0, value=0, step=10)
                stationary_natgas_m3 = st.number_input("Natural gas (m³/year)", min_value=0, value=0, step=10)
                stationary_coal_t = st.number_input("Coal (tons/year)", min_value=0, value=0, step=1)

                st.subheader("Renewable energy")
                solar_rooftop_mwh = st.number_input("Solar rooftops (MWh/year)", min_value=0, value=0, step=10)
                utility_scale_solar_mwh = st.number_input("Utility-scale solar (MWh/year)", min_value=0, value=0, step=10)
                wind_mwh = st.number_input("Wind (MWh/year)", min_value=0, value=0, step=10)
                biomass_mwh = st.number_input("Biomass (MWh/year)", min_value=0, value=0, step=10)

                # --- Energy Sector: Sectoral priorities / contextual questions
                st.markdown("**Priorities & context — Energy**")
                grid_reliability = st.selectbox("Grid reliability (priority)", ["Low", "Medium", "High"])
                rooftop_potential_pct = st.number_input("Estimated rooftop solar potential (%) (approx.)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                critical_infra_backup = st.selectbox("Critical municipal infrastructure backup available?", ["None", "Partial", "Full"])
                diesel_dependency_priority = st.selectbox("Is diesel backup a priority to replace?", ["No", "Low", "Medium", "High"])
                energy_efficiency_programs = st.selectbox("Existing energy efficiency programs?", ["None", "Pilot", "Established"])
                notes_energy_priorities = st.text_area("Energy priorities notes (optional)", value="", height=80)

            # -------------------
            # 3. Transport Sector
            # -------------------
            with st.expander("3. Transport Sector", expanded=False):
                st.subheader("Vehicle fleet & activity")
                vehicles_cars = st.number_input("Cars (number)", min_value=0, value=0, step=1)
                vehicles_buses = st.number_input("Buses (number)", min_value=0, value=0, step=1)
                vehicles_trucks = st.number_input("Trucks (number)", min_value=0, value=0, step=1)
                vehicles_2w = st.number_input("2/3-wheelers (number)", min_value=0, value=0, step=1)
                avg_km_per_car = st.number_input("Avg km per car / year", min_value=0, value=0, step=100)
                avg_km_per_bus = st.number_input("Avg km per bus / year", min_value=0, value=0, step=100)
                avg_km_per_truck = st.number_input("Avg km per truck / year", min_value=0, value=0, step=100)
                avg_km_per_2w = st.number_input("Avg km per 2/3-wheeler / year", min_value=0, value=0, step=100)

                st.subheader("Public transport & freight")
                public_transport_mode_share_pct = st.number_input("Public transport modal share (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                public_transport_energy_mwh = st.number_input("Public transport energy (MWh/year)", min_value=0, value=0, step=10)
                freight_km_year = st.number_input("Freight activity (vehicle-km/year)", min_value=0, value=0, step=1000)

                # --- Transport priorities
                st.markdown("**Priorities & context — Transport**")
                congestion_level = st.selectbox("Traffic congestion level", ["Low", "Medium", "High"])
                ev_charging_infrastructure = st.selectbox("EV charging network readiness", ["None", "Sparse", "Moderate", "Extensive"])
                last_mile_connectivity_priority = st.selectbox("Last-mile connectivity (priority)", ["Low", "Medium", "High"])
                freight_hub_presence = st.selectbox("Freight consolidation / logistics hubs present?", ["None", "Partial", "Yes"])
                non_motorized_infrastructure = st.selectbox("Bicycle / pedestrian infrastructure (quality)", ["Poor", "Fair", "Good", "Excellent"])
                notes_transport_priorities = st.text_area("Transport priorities notes (optional)", value="", height=80)

            # -------------------
            # 4. Waste Sector
            # -------------------
            with st.expander("4. Waste Sector", expanded=False):
                st.subheader("Solid waste")
                municipal_solid_waste_tons = st.number_input("Municipal solid waste generated (tons/year)", min_value=0, value=0, step=10)
                waste_collection_coverage_pct = st.number_input("Collection coverage (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                fraction_landfilled_pct = st.number_input("Fraction landfilled (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                fraction_recycled_pct = st.number_input("Fraction recycled (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                fraction_composted_pct = st.number_input("Fraction composted (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                landfill_capacity_years = st.number_input("Remaining landfill capacity (years, est.)", min_value=0.0, value=0.0, step=0.1)

                st.subheader("Wastewater")
                wastewater_treated_m3 = st.number_input("Wastewater treated (m³/year)", min_value=0, value=0, step=1000)
                wastewater_treatment_level = st.selectbox("Treatment level", ["None", "Primary", "Secondary", "Tertiary"])
                sludge_generated_tons = st.number_input("Sludge generated (tons/year)", min_value=0, value=0, step=1)
                wastewater_energy_kwh = st.number_input("Energy used in wastewater treatment (kWh/year)", min_value=0, value=0, step=10)

                # --- Waste priorities
                st.markdown("**Priorities & context — Waste**")
                segregation_at_source_status = st.selectbox("Source segregation status", ["Poor", "Partial", "Good"])
                informal_sector_dependency = st.selectbox("Informal recycling/scavenging dependency", ["None", "Low", "Medium", "High"])
                methane_capture_pct = st.number_input("Existing landfill methane capture (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                composting_infrastructure = st.selectbox("Composting infrastructure availability", ["None", "Pilot", "City-wide"])
                notes_waste_priorities = st.text_area("Waste priorities notes (optional)", value="", height=80)

            # -------------------
            # 5. Industrial Sector
            # -------------------
            with st.expander("5. Industrial Sector", expanded=False):
                coal_ind_t = st.number_input("Industrial coal consumption (tons/year)", min_value=0, value=0, step=1)
                industrial_gas_m3 = st.number_input("Industrial natural gas (m³/year)", min_value=0, value=0, step=10)
                industrial_electricity_kwh = st.number_input("Industrial electricity (kWh/year)", min_value=0, value=0, step=100)
                industrial_biomass_t = st.number_input("Industrial biomass (tons/year)", min_value=0, value=0, step=1)
                industrial_process_emissions_notes = st.text_area("Industrial process emissions (details)", value="", height=80)
                fugitive_emissions_notes = st.text_area("Fugitive emissions (refrigerants, leaks)", value="", height=80)

                # --- Industrial priorities
                st.markdown("**Priorities & context — Industry**")
                presence_of_heavy_industry = st.selectbox("Presence of heavy industry / clusters", ["None", "Light", "Moderate", "Heavy"])
                process_emissions_high_priority = st.selectbox("Process emissions monitoring needed?", ["No", "Low", "Medium", "High"])
                energy_intensity_reduction_priority = st.selectbox("Energy intensity / efficiency priority", ["Low", "Medium", "High"])
                notes_industry_priorities = st.text_area("Industry priorities notes (optional)", value="", height=80)

            # -------------------
            # 6. Agriculture & Land Use
            # -------------------
            with st.expander("6. Agriculture & Land Use", expanded=False):
                cropland_ha = st.number_input("Cropland (ha)", min_value=0, value=0, step=1)
                livestock_count = st.number_input("Livestock (number)", min_value=0, value=0, step=1)
                fertilizer_use_tons = st.number_input("Fertilizer use (tons/year)", min_value=0, value=0, step=1)
                crop_residue_burning_prevalence = st.selectbox("Crop residue burning prevalence", ["None", "Occasional", "Frequent"])
                manure_management_practice = st.selectbox("Manure management", ["Field applied", "Stored & treated", "Biogas", "Other"])

                # --- Agriculture & land use priorities
                st.markdown("**Priorities & context — Agriculture & LULUCF**")
                afforestation_opportunities_ha = st.number_input("Afforestation potential (ha)", min_value=0, value=0, step=1)
                deforestation_risk_level = st.selectbox("Deforestation risk", ["Low", "Medium", "High"])
                soil_carbon_sequestration_potential = st.number_input("Soil carbon sequestration (tons/yr estimate)", min_value=0, value=0, step=1)
                notes_agri_priorities = st.text_area("Agri & LULUCF priority notes (optional)", value="", height=80)

            # -------------------
            # 7. City Infrastructure
            # -------------------
            with st.expander("7. City Infrastructure", expanded=False):
                streetlights_count = st.number_input("Streetlights count", min_value=0, value=0, step=10)
                streetlights_energy_kwh = st.number_input("Streetlights energy (kWh/year)", min_value=0, value=0, step=10)
                municipal_fleet_fuel = st.text_input("Municipal fleet fuel / composition (text)")
                water_pumping_energy_kwh = st.number_input("Water pumping & treatment energy (kWh/year)", min_value=0, value=0, step=10)
                municipal_buildings_cooling_heating_kwh = st.number_input("Cooling/heating in municipal buildings (kWh/year)", min_value=0, value=0, step=10)

                # --- Infrastructure priorities
                st.markdown("**Priorities & context — Infrastructure**")
                drainage_capacity_status = st.selectbox("Stormwater drainage capacity", ["Inadequate", "Partial", "Adequate"])
                critical_facilities_backup = st.selectbox("Backup power for hospitals/critical facilities", ["No", "Partial", "Yes"])
                streetlight_led_pct = st.number_input("Share of LED streetlights (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                notes_infra_priorities = st.text_area("Infrastructure priorities notes (optional)", value="", height=80)

            # -------------------
            # 8. Hazard, Climate Risks & Vulnerability
            # -------------------
            with st.expander("8. Hazard / Climate Risks & Vulnerability", expanded=False):
                st.subheader("Flood, Drought, Heat & Related Risks")
                flood_risk_level = st.selectbox("Urban flood risk", ["Low", "Medium", "High"])
                stormwater_infra_status = st.selectbox("Stormwater infrastructure status", ["Poor", "Fair", "Good"])
                drought_vulnerability = st.selectbox("Drought vulnerability", ["Low", "Medium", "High"])
                heatwave_vulnerability = st.selectbox("Heatwave vulnerability", ["Low", "Medium", "High"])
                coastal_erosion_risk = st.selectbox("Coastal erosion / sea-level risk (if applicable)", ["None", "Low", "Medium", "High"])
                emergency_response_capacity = st.selectbox("Emergency response capacity", ["Weak", "Moderate", "Strong"])
                notes_hazard_vuln = st.text_area("Hazards / Vulnerability notes (optional)", value="", height=80)

            # -------------------
            # 9. Optional Co-benefit Indicators & Policy context
            # -------------------
            with st.expander("9. Optional Co-benefit Indicators & Policy Context", expanded=False):
                renewable_energy_share_pct = st.number_input("Renewable energy share (city electricity, %)", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
                air_quality_index = st.number_input("Typical annual AQI (approx.)", min_value=0, value=0, step=1)
                water_usage_m3 = st.number_input("Total water use (m³/year)", min_value=0, value=0, step=100)
                climate_policy_documents = st.selectbox("Existing climate policy / CAP document?", ["None", "Draft", "Adopted"])
                notes_cobenefits = st.text_area("Co-benefits / policy notes (optional)", value="", height=80)

            # -------------------
            # 10. Upload Supporting Documents
            # -------------------
            with st.expander("10. Upload Supporting Documents", expanded=False):
                support_files = st.file_uploader("Attach supporting documents (PDF / XLSX / CSV). You can upload multiple - upload them one by one.", type=["pdf", "xlsx", "csv"], accept_multiple_files=True)

            # -------------------
            # Submit Button
            # -------------------
            submit_cap = st.form_submit_button("Save CAP Raw Data & Proceed")

            if submit_cap:
                # Minimal validation (city name required)
                if not city_name:
                    st.error("Please select a City Name before submitting.")
                else:
                    # Build raw_data row (keys are column names saved to CSV)
                    raw_data = {
                        "City Name": city_name,
                        "State": state,
                        "Population": population,
                        "Households": households,
                        "Area (sq.km)": area_km2,
                        "Administrative Type": admin_type,
                        "Year of Inventory": inventory_year,
                        "Climate Zone": climate_zone,
                        "Urbanization Rate (%)": urbanization_rate,
                        "Notes_General": notes_general,

                        # Energy
                        "Municipal Electricity (MWh)": municipal_electricity_mwh,
                        "Residential Electricity (MWh)": residential_electricity_mwh,
                        "Commercial Electricity (MWh)": commercial_electricity_mwh,
                        "Industrial Electricity (MWh)": industrial_electricity_mwh,
                        "Purchased Heat (GJ)": purchased_heat_gj,
                        "Diesel Gen (L)": diesel_gen_l,
                        "Gas Turbine Fuel (m3)": gas_turbine_fuel_m3,
                        "Stationary Diesel (L)": stationary_diesel_l,
                        "Stationary Petrol (L)": stationary_petrol_l,
                        "Stationary LPG (L)": stationary_lpg_l,
                        "Stationary NatGas (m3)": stationary_natgas_m3,
                        "Stationary Coal (t)": stationary_coal_t,
                        "Solar Rooftop (MWh)": solar_rooftop_mwh,
                        "Utility Solar (MWh)": utility_scale_solar_mwh,
                        "Wind (MWh)": wind_mwh,
                        "Biomass (MWh)": biomass_mwh,
                        "Grid Reliability": grid_reliability,
                        "Rooftop Potential (%)": rooftop_potential_pct,
                        "Critical Infra Backup": critical_infra_backup,
                        "Diesel Dependency Priority": diesel_dependency_priority,
                        "Energy Efficiency Programs": energy_efficiency_programs,
                        "Notes_Energy": notes_energy_priorities,

                        # Transport
                        "Vehicles_Cars": vehicles_cars,
                        "Vehicles_Buses": vehicles_buses,
                        "Vehicles_Trucks": vehicles_trucks,
                        "Vehicles_2W": vehicles_2w,
                        "Avg_km_per_Car": avg_km_per_car,
                        "Avg_km_per_Bus": avg_km_per_bus,
                        "Avg_km_per_Truck": avg_km_per_truck,
                        "Avg_km_per_2W": avg_km_per_2w,
                        "Public Transport Share (%)": public_transport_mode_share_pct,
                        "Public Transport Energy (MWh)": public_transport_energy_mwh,
                        "Freight Vehicle-km": freight_km_year,
                        "Congestion Level": congestion_level,
                        "EV Charging Readiness": ev_charging_infrastructure,
                        "Last Mile Priority": last_mile_connectivity_priority,
                        "Freight Hub Present": freight_hub_presence,
                        "NMT Infrastructure Quality": non_motorized_infrastructure,
                        "Notes_Transport": notes_transport_priorities,

                        # Waste
                        "MSW (tons/year)": municipal_solid_waste_tons,
                        "Collection Coverage (%)": waste_collection_coverage_pct,
                        "Fraction Landfilled (%)": fraction_landfilled_pct,
                        "Fraction Recycled (%)": fraction_recycled_pct,
                        "Fraction Composted (%)": fraction_composted_pct,
                        "Landfill Capacity (years)": landfill_capacity_years,
                        "Wastewater Treated (m3)": wastewater_treated_m3,
                        "Wastewater Treatment Level": wastewater_treatment_level,
                        "Sludge (tons/year)": sludge_generated_tons,
                        "Wastewater Energy (kWh)": wastewater_energy_kwh,
                        "Segregation Status": segregation_at_source_status,
                        "Informal Sector Dependency": informal_sector_dependency,
                        "Methane Capture (%)": methane_capture_pct,
                        "Composting Infrastructure": composting_infrastructure,
                        "Notes_Waste": notes_waste_priorities,

                        # Industry
                        "Industrial Coal (t/yr)": coal_ind_t,
                        "Industrial Gas (m3/yr)": industrial_gas_m3,
                        "Industrial Electricity (kWh/yr)": industrial_electricity_kwh,
                        "Industrial Biomass (t/yr)": industrial_biomass_t,
                        "Industrial Process Emissions Notes": industrial_process_emissions_notes,
                        "Fugitive Emissions Notes": fugitive_emissions_notes,
                        "Presence Heavy Industry": presence_of_heavy_industry,
                        "Process Emissions Priority": process_emissions_high_priority,
                        "Industry Efficiency Priority": energy_intensity_reduction_priority,
                        "Notes_Industry": notes_industry_priorities,

                        # Agriculture & LULUCF
                        "Cropland (ha)": cropland_ha,
                        "Livestock_Count": livestock_count,
                        "Fertilizer (t/yr)": fertilizer_use_tons,
                        "Crop Residue Burning": crop_residue_burning_prevalence,
                        "Manure Management": manure_management_practice,
                        "Afforestation Potential (ha)": afforestation_opportunities_ha,
                        "Deforestation Risk": deforestation_risk_level,
                        "Soil Carbon Potential (t/yr)": soil_carbon_sequestration_potential,
                        "Notes_Agri": notes_agri_priorities,

                        # Infrastructure
                        "Streetlights Count": streetlights_count,
                        "Streetlights Energy (kWh/yr)": streetlights_energy_kwh,
                        "Municipal Fleet Fuel": municipal_fleet_fuel,
                        "Water Pumping Energy (kWh/yr)": water_pumping_energy_kwh,
                        "Municipal Cooling/Heating (kWh/yr)": municipal_buildings_cooling_heating_kwh,
                        "Drainage Capacity": drainage_capacity_status,
                        "Critical Facilities Backup": critical_facilities_backup,
                        "Streetlight LED (%)": streetlight_led_pct,
                        "Notes_Infrastructure": notes_infra_priorities,

                        # Hazards & Vulnerability
                        "Flood Risk": flood_risk_level,
                        "Stormwater Infrastructure": stormwater_infra_status,
                        "Drought Vulnerability": drought_vulnerability,
                        "Heatwave Vulnerability": heatwave_vulnerability,
                        "Coastal Risk": coastal_erosion_risk,
                        "Emergency Response Capacity": emergency_response_capacity,
                        "Notes_Hazards": notes_hazard_vuln,

                        # Co-benefits & policy
                        "Renewable Share (%)": renewable_energy_share_pct,
                        "AQI (approx)": air_quality_index,
                        "Total Water Usage (m3/yr)": water_usage_m3,
                        "Climate Policy Status": climate_policy_documents,
                        "Notes_CoBenefits": notes_cobenefits,

                        # Uploads & metadata
                        "File_Names": ";".join([f.name for f in support_files]) if support_files else None,
                        "Submission Date": datetime.now().isoformat()
                    }

                    # Update existing row for city OR append
                    if not cap_df.empty and "City Name" in cap_df.columns and city_name in cap_df["City Name"].astype(str).values:
                        # Update - replace existing row
                        cap_df.loc[cap_df["City Name"].astype(str) == city_name, list(raw_data.keys())] = list(raw_data.values())
                        saved_df = cap_df
                    else:
                        saved_df = pd.concat([cap_df, pd.DataFrame([raw_data])], ignore_index=True)

                    # Save to CSV and session state
                    try:
                        saved_df.to_csv(CAP_DATA_FILE, index=False)
                        st.session_state.cap_data = saved_df
                        st.success(f"Raw data for **{city_name}** saved successfully.")
                    except Exception as e:
                        st.error(f"Failed to save CAP data: {e}")
                        st.session_state.cap_data = saved_df  # still set in session

                    # Attempt to redirect to GHG Inventory (safe-guarded)
                    st.info("You can now go to the **GHG Inventory** page to generate the inventory using this raw data.")
                    st.session_state.menu = "GHG Inventory"
                    try:
                        st.experimental_rerun()
                    except Exception:
                        # Some hosting environments disallow experimental_rerun in this context.
                        st.write("Data saved. Please click `GHG Inventory` in the sidebar/menu to continue.")
                

# ---------------------------
# GHG Inventory Page
# ---------------------------
elif menu == "GHG Inventory":
    st.header("GHG Inventory")

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
