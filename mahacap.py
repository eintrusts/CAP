import streamlit as st
import pandas as pd
import plotly.express as px
import io

# ---------------------------
# Config
# ---------------------------
st.set_page_config(page_title="Maharashtra CAP Dashboard", page_icon="🌍", layout="wide")

# ---------------------------
# Admin Password
# ---------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False

ADMIN_PASSWORD = "eintrust123"  # can also be st.secrets["ADMIN_PASSWORD"] for production

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
# Load Data
# ---------------------------
@st.cache_data
def load_data():
    return pd.read_excel("data/cities_data.xlsx")

if "data" not in st.session_state:
    st.session_state.data = load_data()

df = st.session_state.data

# ---------------------------
# UI Layout
# ---------------------------
st.title("🌍 Maharashtra Climate Action Dashboard")
st.markdown("### Engage • Enlighten • Empower")

st.sidebar.image("https://raw.githubusercontent.com/eintrusts/CAP/main/EinTrust%20%20(2).png", use_container_width=True)
menu = st.sidebar.radio("Navigate", ["Home", "City Dashboard", "Admin Login"])

# ---------------------------
# Home Page
# ---------------------------
if menu == "Home":
    st.header("📊 State-Level Overview")

    st.subheader("CAP Status Overview")
    cap_status_count = df["CAP Status"].value_counts()
    fig1 = px.pie(values=cap_status_count.values, names=cap_status_count.index, title="CAP Status of 43 Cities")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("District-Wise CAP Count")
    district_cap = df.groupby(["District", "CAP Status"]).size().reset_index(name="Count")
    fig2 = px.bar(district_cap, x="District", y="Count", color="CAP Status", title="District Wise CAP Status")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("GHG Emissions by City")
    fig3 = px.bar(df, x="City Name", y="GHG Emissions (tCO2e)", title="City-Wise GHG Emissions (tCO2e)")
    st.plotly_chart(fig3, use_container_width=True)

# ---------------------------
# City Dashboard
# ---------------------------
elif menu == "City Dashboard":
    st.header("🏙️ City Dashboard")
    city = st.selectbox("Select City", df["City Name"].unique())
    city_row = df[df["City Name"] == city].iloc[0]

    st.subheader(f"📌 Details for {city}")
    st.write(f"**District:** {city_row['District']}")
    st.write(f"**Population (2011):** {city_row['Population (2011)']}")
    st.write(f"**ULB Category:** {city_row['ULB Category']}")
    st.write(f"**CAP Status:** {city_row['CAP Status']}")
    st.write(f"**Total Budget:** {city_row['Total Budget']}")
    st.write(f"**Environment Budget:** {city_row['Environment Budget']}")
    st.write(f"**GHG Emissions (tCO2e):** {city_row['GHG Emissions (tCO2e)']}")
    st.write(f"**ESR Prepared:** {city_row['ESR Prepared']}")
    st.write(f"**Latest ESR Year:** {city_row['Latest ESR Year']}")
    st.write(f"**Remarks:** {city_row['Remarks']}")
    st.write(f"**Data Source:** {city_row['Data Source']}")

    # Download CAP report
    with st.form("download_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Work Email")
        download = st.form_submit_button("Download City Report")
        if download:
            if name and email:
                output = io.BytesIO()
                city_df = pd.DataFrame(city_row).reset_index()
                city_df.columns = ["Parameter", "Value"]
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    city_df.to_excel(writer, index=False, sheet_name="Report")
                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name=f"{city}_CAP_Report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.success("Report ready for download!")
            else:
                st.error("Please provide your name and work email.")

# ---------------------------
# Admin Panel
# ---------------------------
elif menu == "Admin Login":
    if not st.session_state.authenticated:
        login()
    else:
        st.header("🔑 Admin Panel")
        st.write("Upload or update the dataset for all 43 cities.")

        uploaded = st.file_uploader("Upload Excel (with city data)", type=["xlsx"])
        if uploaded:
            df_up = pd.read_excel(uploaded)
            st.session_state.data = df_up
            df = st.session_state.data
            st.success("Data updated successfully!")
