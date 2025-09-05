import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ---------------------------
# App Config
# ---------------------------
st.set_page_config(page_title="MahaCAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Session State Init
# ---------------------------
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=[
        "City", "District", "Population", "ULB Category", "CAP Status", "Last Updated"
    ])
if "emissions" not in st.session_state:
    st.session_state.emissions = {}

# ---------------------------
# Sidebar & Logo
# ---------------------------
st.sidebar.image(
    "https://github.com/eintrusts/CAP/blob/main/EinTrust%20%20(2).png?raw=true",
    use_column_width=True
)

menu = st.sidebar.radio("Navigation", ["Home", "City Dashboard"])

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.title("🌍 Maharashtra Climate Action Dashboard")
    st.markdown("### Welcome to MahaCAP — Unified Climate Action Planning for Cities")

    if not st.session_state.df.empty:
        # Take first city as reference for demo
        latest_data = st.session_state.df.iloc[-1]
        population = latest_data["Population"]

        try:
            population_num = int(str(population).replace(",", ""))
        except:
            population_num = 0

        # Approximate GHG = Population × 1.5 tCO₂e per capita → converted to MtCO₂e
        approx_emissions = round(population_num * 1.5 / 1e6, 2)

        st.metric("Approximate GHG Emissions (based on population)", f"{approx_emissions} MtCO₂e")
        st.metric("Per Capita Emissions (approx)", "1.5 tCO₂e/person")

    else:
        st.info("Admin has not yet added any city data.")

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    st.header("🏙️ City Dashboard")

    if st.session_state.df.empty:
        st.warning("No city data available. Please wait until admin adds data.")
    else:
        city_choice = st.selectbox("Select City", st.session_state.df["City"].unique())
        city_data = st.session_state.df[st.session_state.df["City"] == city_choice].iloc[0]

        st.subheader(f"📊 {city_choice} - Dashboard")
        st.write(f"**District:** {city_data['District']}")
        st.write(f"**Population:** {city_data['Population']}")
        st.write(f"**ULB Category:** {city_data['ULB Category']}")
        st.write(f"**CAP Status:** {city_data['CAP Status']}")

        if "Last Updated" in city_data and pd.notna(city_data["Last Updated"]):
            st.markdown(f"🕒 Last Updated: **{city_data['Last Updated']}**")

        # Emissions data available → show sector-wise chart
        if city_choice in st.session_state.emissions:
            emissions = st.session_state.emissions[city_choice]
            total_emissions = sum(emissions.values())

            st.subheader("GHG Emissions by Sector")

            # Pie chart
            fig, ax = plt.subplots()
            ax.pie(emissions.values(), labels=emissions.keys(), autopct='%1.1f%%', startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

            st.write("**Emissions Data (tCO₂e):**")
            st.write(emissions)

            # Per capita emissions
            try:
                population_num = int(str(city_data["Population"]).replace(",", ""))
            except:
                population_num = 0

            if population_num > 0:
                per_capita = round(total_emissions / population_num, 2)
                st.metric("Per Capita Emissions (actual)", f"{per_capita} tCO₂e/person")

        else:
            # No emissions inventory available → fallback to population-based estimate
            try:
                population_num = int(str(city_data["Population"]).replace(",", ""))
            except:
                population_num = 0

            approx_emissions = round(population_num * 1.5 / 1e6, 2)
            st.info(f"No detailed GHG inventory available. Approximate emissions: {approx_emissions} MtCO₂e")
            st.metric("Per Capita Emissions (approx)", "1.5 tCO₂e/person")
