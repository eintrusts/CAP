# mahacap.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin Password
# ---------------------------
ADMIN_PASSWORD = "eintrust2025"

# ---------------------------
# Data File for Persistence
# ---------------------------
DATA_FILE = "cities_data.csv"

# ---------------------------
# Cities and Districts
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
    "Udgir Coucil": "Latur",
    "Akola": "Akola",
    "Parbhani Council": "Parbhani",
    "Amravati": "Amravati",
    "Achalpur Council": "Amravati",
    "Wardha Coumcil": "Wardha",
    "Hinganghat Ciuncil": "Wardha",
    "Nagpur": "Nagpur",
    "Chandrapur": "Chandrapur",
    "Gondia Council": "Gondia"
}

# ---------------------------
# Session State Initialization
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "menu" not in st.session_state:
    st.session_state.menu = "Home"
if os.path.exists(DATA_FILE):
    st.session_state.data = pd.read_csv(DATA_FILE)
else:
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Department Email"
    ])

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
# Sidebar - Professional Style
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

# Custom CSS for forest green buttons
st.sidebar.markdown(
    """
    <style>
    .css-1d391kg button { 
        background-color: #228B22 !important; 
        color: white !important; 
        width: 100%;
        margin-bottom: 5px;
        height: 40px;
        font-size: 16px;
        border-radius: 5px;
    }
    .css-1d391kg button:hover { 
        background-color: #196619 !important; 
        color: white !important; 
    }
    </style>
    """, unsafe_allow_html=True
)

# Sidebar navigation buttons
if st.sidebar.button("Home"):
    st.session_state.menu = "Home"
if st.sidebar.button("City Dashboard"):
    st.session_state.menu = "City Dashboard"
if st.sidebar.button("Admin Panel"):
    st.session_state.menu = "Admin Panel"

st.sidebar.markdown("---")
st.sidebar.markdown("EinTrust | © 2025")

menu = st.session_state.menu

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
# Home Page
# ---------------------------
if menu == "Home":
    st.header("Maharashtra CAP Dashboard")
    st.markdown("Maharashtra's Net Zero Journey")

    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        total_cities = df.shape[0]
        cities_done = df[df["CAP Status"] == "Completed"].shape[0]
        st.metric("Total Cities", total_cities)
        st.metric("Cities with CAP Completed", cities_done)

        if "GHG Emissions" in df.columns:
            fig2 = px.bar(df, x="City Name", y="GHG Emissions", title="GHG Emissions by City", text="GHG Emissions")
            st.plotly_chart(fig2, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        st.header("City Dashboard")
        st.markdown("View detailed information for each city.")

        # Select city dropdown
        city_col = "City Name"
        city = st.selectbox("Select City", df[city_col].dropna().unique())
        city_row = df[df[city_col] == city].iloc[0]

        st.subheader(f"{city} Details")

        # Basic Info
        with st.expander("Basic Info", expanded=True):
            st.write(f"**District:** {get_val(city_row, 'District')}")
            st.write(f"**Population:** {format_population(get_val(city_row, 'Population'))}")
            st.write(f"**ULB Category:** {get_val(city_row, 'ULB Category')}")
            st.write(f"**CAP Status:** {get_val(city_row, 'CAP Status')}")

        # Environment Department
        with st.expander("Environment Department"):
            st.write(f"**Exists:** {get_val(city_row, 'Environment Department Exist')}")
            st.write(f"**Dept Name:** {get_val(city_row, 'Department Name')}")
            st.write(f"**Head Name:** {get_val(city_row, 'Head Name')}")
            st.write(f"**Email:** {get_val(city_row, 'Department Email')}")


        # Display last updated info
        if "last_updated" in st.session_state:
            last_updated = st.session_state.last_updated
        else:
            last_updated = pd.to_datetime(os.path.getmtime(DATA_FILE), unit='s')
        st.markdown(f"*Last Updated: {last_updated.strftime('%B %Y')}*")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("Admin Panel")
        st.write("Add or update city data below. Changes will reflect on the dashboard immediately.")

        df = st.session_state.data
        cities_list = list(cities_districts.keys())

        with st.form("admin_form"):
            city_name = st.selectbox("Select City", cities_list)
            district = st.text_input("District", value=cities_districts[city_name], disabled=True)

            population_val = df[df["City Name"]==city_name]["Population"].values[0] if city_name in df.get("City Name", []) else 0
            population = st.number_input("Population(as per 2011 census)", min_value=0, value=int(population_val), step=1000, format="%d")
            
            ulb_cat = st.selectbox("ULB Category", ["Municipal Corporation", "Municipal Council"])
            cap_status = st.selectbox("CAP Status", ["Not Started", "In Progress", "Completed"])
            
            ghg = st.text_input("GHG Emissions (MTCO2e)", df[df["City Name"]==city_name]["GHG Emissions"].values[0] if city_name in df.get("City Name", []) else "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"], index=0)
            dept_name = st.text_input("Department Name", df[df["City Name"]==city_name]["Department Name"].values[0] if city_name in df.get("City Name", []) else "")
            head_name = st.text_input("Head Name", df[df["City Name"]==city_name]["Head Name"].values[0] if city_name in df.get("City Name", []) else "")
            dept_email = st.text_input("Department Email", df[df["City Name"]==city_name]["Department Email"].values[0] if city_name in df.get("City Name", []) else "")

            submit = st.form_submit_button("Add/Update City")
            if submit:
                new_row = {
                    "City Name": city_name,
                    "District": district,
                    "Population": population,
                    "ULB Category": ulb_cat,
                    "CAP Status": cap_status,
                    "GHG Emissions": ghg,
                    "Environment Department Exist": env_exist,
                    "Department Name": dept_name,
                    "Head Name": head_name,
                    "Department Email": dept_email
                }

                if city_name in df.get("City Name", []):
                    idx = df[df["City Name"] == city_name].index[0]
                    df.loc[idx] = new_row
                    st.success(f"{city_name} updated successfully.")
                else:
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"{city_name} added successfully.")
         
                
                # Save data to CSV for lifetime persistence
                st.session_state.data = df
                df.to_csv(DATA_FILE, index=False)

                # Update last updated timestamp
                st.session_state.last_updated = pd.Timestamp.now()



