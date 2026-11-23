import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import date
from sklearn.ensemble import IsolationForest

# -----------------------------
# WATERWISE AI - FIRST VERSION
# -----------------------------
st.set_page_config(
    page_title="WATERWISE AI",
    page_icon="💧",
    layout="wide"
)

st.title("💧 WATERWISE AI")
st.subheader("Intelligent Water Conservation and Usage Monitoring System")
st.write(
    "Monitor water consumption, identify unusual usage "
    "and discover ways to conserve water."
)

# DATABASE
conn = sqlite3.connect("waterwise.db", check_same_thread=False)
conn.execute("""
CREATE TABLE IF NOT EXISTS water_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    usage_date TEXT,
    litres REAL
)
""")
conn.commit()

# USER CATEGORY
st.sidebar.header("User Settings")
category = st.sidebar.selectbox(
    "Select your category",
    ["Household", "College", "Office / Industry"]
)

# NAVIGATION
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Water Usage", "AI Analysis", "Water Saving Advisor"]
)

# READ DATABASE
def load_data():
    return pd.read_sql_query(
        "SELECT * FROM water_usage WHERE category = ?",
        conn,
        params=(category,)
    )

# ADD WATER USAGE
if page == "Add Water Usage":
    st.header("📝 Enter Water Consumption")
    with st.form("usage_form"):
        usage_date = st.date_input(
            "Select date",
            value=date.today()
        )
        litres = st.number_input(
            "Water consumed (litres)",
            min_value=1.0,
            max_value=10000000.0,
            value=1000.0
        )
        submitted = st.form_submit_button("Save Water Usage")

    if submitted:
        conn.execute(
            """
            INSERT INTO water_usage
            (category, usage_date, litres)
            VALUES (?, ?, ?)
            """,
            (category, str(usage_date), litres)
        )
        conn.commit()
        st.success("Water consumption saved successfully!")

# DASHBOARD
elif page == "Dashboard":
    st.header("📊 Water Consumption Dashboard")
    df = load_data()

    if df.empty:
        st.info("No records found. Add water consumption data first.")
    else:
        total = df["litres"].sum()
        average = df["litres"].mean()
        records = len(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Consumption", f"{total:,.0f} L")
        col2.metric("Average Consumption", f"{average:,.0f} L")
        col3.metric("Total Records", records)

        df["usage_date"] = pd.to_datetime(df["usage_date"])
        daily = (
            df.groupby("usage_date", as_index=False)["litres"]
            .sum()
            .sort_values("usage_date")
        )

        st.subheader("Water Consumption Over Time")
        fig = px.line(
            daily,
            x="usage_date",
            y="litres",
            markers=True,
            title="Daily Water Consumption"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Consumption History")
        st.dataframe(df, use_container_width=True)

# AI ANALYSIS
elif page == "AI Analysis":
    st.header("🤖 AI Water Usage Analysis")
    df = load_data()

    if len(df) < 5:
        st.warning(
            "Please enter at least 5 records to perform "
            "a basic consumption analysis."
        )
    else:
        daily = (
            df.groupby("usage_date", as_index=False)["litres"]
            .sum()
            .sort_values("usage_date")
        )
        values = daily[["litres"]]

        model = IsolationForest(
            contamination=0.15,
            random_state=42
        )
        daily["result"] = model.fit_predict(values)
        anomalies = daily[daily["result"] == -1]

        st.write(
            f"Average daily consumption: "
            f"{daily['litres'].mean():,.0f} litres"
        )

        if anomalies.empty:
            st.success("No unusual consumption detected.")
        else:
            st.warning("Unusual consumption patterns detected!")
            st.dataframe(
                anomalies[["usage_date", "litres"]],
                use_container_width=True
            )

        st.info(
            "Consider checking water usage activities, "
            "taps and storage systems. This alert does "
            "not confirm an actual leak."
        )

# WATER SAVING ADVISOR
elif page == "Water Saving Advisor":
    st.header("🌱 AI Water Conservation Advisor")
    df = load_data()

    if df.empty:
        st.info("Add water consumption records to receive suggestions.")
    else:
        average = df.groupby("usage_date")["litres"].sum().mean()
        st.metric(
            "Average Daily Consumption",
            f"{average:,.0f} litres"
        )

        st.subheader("Your Water Saving Suggestions")
        if average > 5000:
            st.write("💧 Review areas with high water consumption.")
            st.write("🚿 Check taps and pipelines for possible wastage.")
            st.write("🌱 Consider reusing suitable water for gardening.")
        else:
            st.write("👏 Continue monitoring your water consumption.")
            st.write("💧 Turn off taps when not in use.")
            st.write("🌱 Consider collecting rainwater where practical.")

        st.caption(
            "Suggestions are general guidance based on "
            "recorded consumption, not verified savings."
        )

st.sidebar.markdown("---")
st.sidebar.caption("WATERWISE AI | Sustainable Development")
