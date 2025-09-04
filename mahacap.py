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

# ---------------------------
# Session State Initialization
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "data" not in st.session_state:
    # Initialize with empty DataFrame with required columns
    st.session_state.data = pd.DataFrame(columns=[
        "City Name", "District", "Population", "ULB Category", "CAP Status",
        "GHG Emissions", "Environment Department Exist", "Department Name",
        "Head Name", "Head Designantion", "Head Qualification", "Department Email",
        "Dedicated Climate Officer"
    ])

# ---------------------------
# Helpers
# ---------------------------
def canon(s: str) -> str:
    s = str(s).lower().strip()
    s = s.replace("\n", " ")
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"[’'`\"()%/\.]", "", s)
    return s

def get_val(row: pd.Series, target: str, default="—"):
    if target in row:
        val = row[target]
        if pd.isna(val):
            return default
        return val
    return default

# ---------------------------
# Sidebar Logo
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_container_width=True
)

# ---------------------------
# Navigation
# ---------------------------
menu = st.sidebar.radio("Navigate", ["Home", "City Dashboard", "Admin Panel"])

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
    st.header("📊 Maharashtra CAP Dashboard")
    st.markdown("### Engage • Enlighten • Empower")

    df = st.session_state.data
    if df.empty:
        st.info("No city data available. Admin must add data.")
    else:
        total_cities = df.shape[0]
        cities_done = df[df.get("CAP Status") == "Approved"].shape[0]
        st.metric("Total Cities", total_cities)
        st.metric("Cities with CAP Completed", cities_done)

        if "District" in df.columns:
            district_summary = df.groupby("District")["CAP Status"].apply(lambda x: (x=="Approved").sum()).reset_index()
            district_summary.columns = ["District", "CAPs Done"]
            fig = px.bar(district_summary, x="District", y="CAPs Done", text="CAPs Done",
                         title="District-wise CAP Completion")
            st.plotly_chart(fig, use_container_width=True)

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
        city_col = "City Name"
        city = st.selectbox("Select City", df[city_col].dropna().unique())
        city_row = df[df[city_col] == city].iloc[0]

        st.subheader(f"🏙️ {city} Details")

        with st.expander("🏠 Basic Info", expanded=True):
            st.write(f"**District:** {get_val(city_row, 'District')}")
            st.write(f"**Population:** {get_val(city_row, 'Population')}")
            st.write(f"**ULB Category:** {get_val(city_row, 'ULB Category')}")

        with st.expander("🏢 Environment Dept"):
            st.write(f"**Exists:** {get_val(city_row, 'Environment Department Exist')}")
            st.write(f"**Dept Name:** {get_val(city_row, 'Department Name')}")
            st.write(f"**Head Name:** {get_val(city_row, 'Head Name')}")
            st.write(f"**Head Designation:** {get_val(city_row, 'Head Designantion')}")
            st.write(f"**Head Qualification:** {get_val(city_row, 'Head Qualification')}")
            st.write(f"**Email:** {get_val(city_row, 'Department Email')}")
            st.write(f"**Dedicated Climate Officer:** {get_val(city_row, 'Dedicated Climate Officer')}")

        with st.expander("🌡️ GHG & CAP Actions"):
            st.write(f"**Total GHG Emissions:** {get_val(city_row, 'GHG Emissions')} MTCO2e")
            st.write("**Suggested CAP Actions:**")
            st.write("- Renewable energy increase")
            st.write("- Public transport & EV promotion")
            st.write("- Waste to energy initiatives")
            st.write("- Energy efficiency programs")
            st.write("- Urban forestry & green cover")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Panel":
    if not st.session_state.authenticated:
        admin_login()
    else:
        st.header("🔑 Admin Panel")
        st.write("Add or update city data below. Changes will reflect on the dashboard immediately.")

        with st.form("admin_form"):
            city_name = st.text_input("City Name", "")
            district = st.text_input("District", "")
            population = st.text_input("Population", "")
            ulb_cat = st.text_input("ULB Category", "")
            cap_status = st.selectbox("CAP Status", ["Pending", "Approved", "In Progress"])
            ghg = st.text_input("GHG Emissions (MTCO2e)", "")
            env_exist = st.selectbox("Environment Dept Exists?", ["Yes", "No"])
            dept_name = st.text_input("Department Name", "")
            head_name = st.text_input("Head Name", "")
            head_design = st.text_input("Head Designation", "")
            head_qual = st.text_input("Head Qualification", "")
            dept_email = st.text_input("Department Email", "")
            climate_officer = st.text_input("Dedicated Climate Officer", "")

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
                    "Head Designantion": head_design,
                    "Head Qualification": head_qual,
                    "Department Email": dept_email,
                    "Dedicated Climate Officer": climate_officer
                }
                df = st.session_state.data
                if city_name in df.get("City Name", []):
                    idx = df[df["City Name"] == city_name].index[0]
                    df.loc[idx] = new_row
                    st.success(f"{city_name} updated successfully.")
                else:
                    st.session_state.data = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    st.success(f"{city_name} added successfully.")
