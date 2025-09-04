import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin/City Passwords
# ---------------------------
ADMIN_PASSWORD = "eintrust123"
CITY_PASSWORD = "cityaccess123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "access_level" not in st.session_state:
    st.session_state.access_level = "public"

# ---------------------------
# Load Data Function
# ---------------------------
@st.cache_data
def load_data(file_path="cities_data.xlsx"):
    if not os.path.exists(file_path):
        return None
    return pd.read_excel(file_path)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# ---------------------------
# Helper: Generate CAP Actions
# ---------------------------
def generate_cap_actions(city_row):
    ghg = city_row.get("GHG Emissions (tCO2e)", 0)
    actions = []
    if ghg > 100000:
        actions += [
            "Accelerate renewable energy adoption",
            "Implement EV and public transport incentives",
            "Waste-to-energy projects"
        ]
    elif ghg > 50000:
        actions += [
            "Increase solar rooftop installations",
            "Energy efficiency in buildings",
            "Smart traffic management"
        ]
    else:
        actions += [
            "Promote green buildings",
            "Urban forestry initiatives"
        ]
    return actions

# ---------------------------
# Login Functions
# ---------------------------
def login(level="admin"):
    with st.form(f"login_form_{level}"):
        password = st.text_input(f"Enter {level.capitalize()} Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            if (level=="admin" and password==ADMIN_PASSWORD) or (level=="city" and password==CITY_PASSWORD):
                st.session_state.authenticated = True
                st.session_state.access_level = level
                st.success(f"{level.capitalize()} login successful")
            else:
                st.error("Incorrect password")

# ---------------------------
# Sidebar Navigation
# ---------------------------
st.sidebar.image("https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png", use_container_width=True)
menu = st.sidebar.radio("Navigate", ["Home", "City Dashboard", "CAP Generation", "Admin Login", "City Login"])

# ---------------------------
# Admin Upload if Data Missing
# ---------------------------
if st.session_state.data is None:
    st.warning("City data file not found. Admin needs to upload.")
    uploaded_file = st.file_uploader("Upload cities_data.xlsx", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.session_state.data = df
        st.success("Data loaded successfully!")
else:
    df = st.session_state.data

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.title("🌍 Maharashtra CAP Dashboard - State Overview")
    st.markdown("### Engage • Enlighten • Empower")

    if df is not None:
        st.subheader("CAP Status Across 43 Cities")
        cap_status = df["CAP Status"].value_counts()
        st.bar_chart(cap_status)

        st.subheader("District-wise CAP Summary")
        district_cap = df.groupby("District")["CAP Status"].value_counts().unstack(fill_value=0)
        st.dataframe(district_cap)

        st.subheader("City-wise GHG Emissions (tCO2e)")
        if "GHG Emissions (tCO2e)" in df.columns:
            fig = px.bar(df, x="City Name", y="GHG Emissions (tCO2e)", text="GHG Emissions (tCO2e)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No city data available. Admin upload required.")

# ---------------------------
# City Dashboard (Public)
# ---------------------------
elif menu == "City Dashboard":
    st.title("🏙️ City Dashboard")
    if df is not None:
        city = st.selectbox("Select City", df["City Name"])
        city_row = df[df["City Name"] == city].iloc[0]

        st.subheader(f"📌 {city} Details")
        st.write(f"**District:** {city_row['District']}")
        st.write(f"**Population (2011):** {city_row['Population (2011)']}")
        st.write(f"**ULB Category:** {city_row['ULB Category']}")
        st.write(f"**CAP Status:** {city_row['CAP Status']}")
        st.write(f"**Total Budget:** {city_row['Total Budget']}")
        st.write(f"**Environment Budget:** {city_row['Environment Budget']}")
        st.write(f"**GHG Emissions (tCO2e):** {city_row['GHG Emissions (tCO2e)']}")
        st.write(f"**Remarks:** {city_row['Remarks']}")
        st.write(f"**Data Source:** {city_row['Data Source']}")
    else:
        st.info("No city data available. Admin upload required.")

# ---------------------------
# CAP Generation (Closed Access)
# ---------------------------
elif menu == "CAP Generation":
    if not st.session_state.authenticated or st.session_state.access_level != "city":
        st.info("🔒 City login required to access CAP generation.")
        login("city")
    else:
        st.title("⚡ Automatic CAP Generation")
        city = st.selectbox("Select Your City", df["City Name"])
        city_row = df[df["City Name"] == city].iloc[0]

        st.subheader(f"📊 Sectoral GHG Emissions for {city}")
        sectors = ["Energy", "Transport", "Waste", "Industrial", "Buildings", "AFOLU"]
        ghg_values = [city_row.get(f"{s} Emissions (tCO2e)", 0) for s in sectors]
        sector_df = pd.DataFrame({"Sector": sectors, "Emissions (tCO2e)": ghg_values})
        st.dataframe(sector_df)
        fig = px.bar(sector_df, x="Sector", y="Emissions (tCO2e)", title="Sectoral GHG Emissions")
        st.plotly_chart(fig)

        st.subheader("📝 Recommended Actions to Reach Net Zero by 2050")
        actions = generate_cap_actions(city_row)
        for a in actions:
            st.write(f"- {a}")

        st.subheader("📥 Download CAP Report")
        with st.form("download_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Work Email")
            download = st.form_submit_button("Generate & Download Report")
            if download:
                if name and email:
                    output = io.BytesIO()
                    report_df = pd.DataFrame({
                        "Parameter": ["City", "District", "Population (2011)", "CAP Status", "Total Budget", "Environment Budget", "GHG Emissions (tCO2e)"],
                        "Value": [city_row["City Name"], city_row["District"], city_row["Population (2011)"], city_row["CAP Status"], city_row["Total Budget"], city_row["Environment Budget"], city_row["GHG Emissions (tCO2e)"]]
                    })
                    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                        report_df.to_excel(writer, index=False, sheet_name="CAP Report")
                        actions_df = pd.DataFrame({"Recommended Actions": actions})
                        actions_df.to_excel(writer, index=False, sheet_name="Recommended Actions")
                        sector_df.to_excel(writer, index=False, sheet_name="Sectoral Emissions")
                    st.download_button(
                        "📥 Download CAP Report",
                        data=output.getvalue(),
                        file_name=f"{city}_CAP_Report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("Report generated successfully!")
                else:
                    st.error("Please provide your name and email.")

# ---------------------------
# Admin Login & Update
# ---------------------------
elif menu == "Admin Login":
    if not st.session_state.authenticated or st.session_state.access_level != "admin":
        login("admin")
    else:
        st.title("🔑 Admin Panel")
        st.write("Upload new data for all 43 cities")
        uploaded = st.file_uploader("Upload Excel", type=["xlsx"])
        if uploaded:
            new_df = pd.read_excel(uploaded)
            st.session_state.data = new_df
            st.success("Data updated successfully!")
