import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# -----------------------
# File Paths
# -----------------------
DB_PATH = "ola_rides.db"
CSV_PATH = "rides_cleaned.csv"
LOGO_PATH = "images/ola-logo.png"

# -----------------------
# Load Data
# -----------------------
df = pd.read_csv(CSV_PATH, parse_dates=["Date"])
min_date, max_date = df["Date"].min(), df["Date"].max()

st.set_page_config(page_title="Ola Rides Analysis", layout="wide")

# -----------------------
# Sidebar / Navigation
# -----------------------
st.sidebar.image(LOGO_PATH, width=150)
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Home", "Exploratory Data Analysis", "SQL Queries", "Power BI Dashboard", "Insights & Recommendations"]
)

# Global Date Filter
st.sidebar.markdown("### Date Filter")
date_range = st.sidebar.date_input(
    "Select Date Range",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)
df_filtered = df[(df["Date"] >= pd.to_datetime(date_range[0])) &
                 (df["Date"] <= pd.to_datetime(date_range[1]))]

# -----------------------
# HOME PAGE
# -----------------------
if page == "Home":
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(LOGO_PATH, width=100)
    with col2:
        st.title("🚖 Ola Rides Analysis Dashboard")

    # KPIs
    total_rides = len(df_filtered)
    success_rate = (df_filtered["Booking_Status"].eq("Success").mean()) * 100
    avg_fare = df_filtered.loc[df_filtered["Booking_Status"] == "Success", "Booking_Value"].mean()
    cancel_rate = df_filtered["Booking_Status"].str.contains("Canceled").mean() * 100

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Rides", f"{total_rides:,}")
    kpi2.metric("Success Rate", f"{success_rate:.2f}%")
    kpi3.metric("Avg Fare (₹)", f"{avg_fare:.0f}")
    kpi4.metric("Cancellation Rate", f"{cancel_rate:.2f}%")


# -----------------------
# EXPLORATORY DATA ANALYSIS PAGE
# -----------------------
elif page == "Exploratory Data Analysis":
    st.header("📊 Exploratory Data Analysis")

    # 1. Rides by Vehicle Type
    vc1 = df_filtered["Vehicle_Type"].value_counts().reset_index()
    vc1.columns = ["Vehicle_Type", "count"]
    fig1 = px.bar(vc1, x="Vehicle_Type", y="count", title="Rides by Vehicle Type",
                  labels={"Vehicle_Type": "Vehicle Type", "count": "Number of Rides"})
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("🔎 Insight: Autos and Bikes dominate total rides.")

    # 2. Daily Booking Trend
    daily_booking = df_filtered.groupby("Date")["Booking_ID"].count().reset_index()
    daily_booking.columns = ["Date", "count"]
    fig2 = px.line(daily_booking, x="Date", y="count", title="Daily Booking Trend",
                   labels={"count": "Number of Rides"})
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("🔎 Insight: Ride demand fluctuates with clear weekday peaks.")

    # 3. Payment Method Distribution
    pm = df_filtered["Payment_Method"].value_counts().reset_index()
    pm.columns = ["Payment_Method", "count"]
    fig3 = px.pie(pm, names="Payment_Method", values="count", title="Payment Method Distribution")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("🔎 Insight: UPI and Cash dominate payment preferences.")

    # 4. Booking Value by Vehicle Type
    fig4 = px.box(df_filtered, x="Vehicle_Type", y="Booking_Value", title="Booking Value by Vehicle Type")
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("🔎 Insight: Prime Sedan and SUVs have higher fare distribution.")

    # 5. Customer Rating Distribution
    fig5 = px.histogram(df_filtered, x="Customer_Rating", nbins=20, title="Distribution of Customer Ratings")
    st.plotly_chart(fig5, use_container_width=True)
    st.caption("🔎 Insight: Most customers give ratings between 3.5 and 4.5.")

    # 6. Driver Ratings Distribution
    fig6 = px.histogram(df_filtered, x="Driver_Ratings", nbins=20, title="Distribution of Driver Ratings")
    st.plotly_chart(fig6, use_container_width=True)
    st.caption("🔎 Insight: Driver ratings are skewed towards positive values.")

    # 7. Rides by Day of Week
    vc2 = df_filtered["Day_of_Week"].value_counts().reset_index()
    vc2.columns = ["Day_of_Week", "count"]
    fig7 = px.bar(vc2, x="Day_of_Week", y="count", title="Rides by Day of Week")
    st.plotly_chart(fig7, use_container_width=True)
    st.caption("🔎 Insight: Weekdays have higher ride demand compared to weekends.")

    # 8. Rides by Hour
    vc3 = df_filtered["Ride_Hour"].value_counts().reset_index()
    vc3.columns = ["Ride_Hour", "count"]
    fig8 = px.bar(vc3.sort_values("Ride_Hour"), x="Ride_Hour", y="count", title="Rides by Hour of Day")
    st.plotly_chart(fig8, use_container_width=True)
    st.caption("🔎 Insight: Ride demand peaks during morning and evening commute hours.")

    # 9. Ride Distance Distribution
    fig9 = px.histogram(df_filtered, x="Ride_Distance", nbins=50, title="Ride Distance Distribution")
    st.plotly_chart(fig9, use_container_width=True)
    st.caption("🔎 Insight: Majority of rides are short distance trips.")

    # 10. Cancellations Over Time
    cancel_trend = df_filtered[df_filtered["Booking_Status"].str.contains("Canceled")]
    cancel_daily = cancel_trend.groupby("Date")["Booking_ID"].count().reset_index()
    cancel_daily.columns = ["Date", "count"]
    fig10 = px.line(cancel_daily, x="Date", y="count", title="Daily Cancellations Trend")
    st.plotly_chart(fig10, use_container_width=True)
    st.caption("🔎 Insight: Cancellations follow overall demand trends.")

    # 11. Top Pickup Locations
    vc4 = df_filtered["Pickup_Location"].value_counts().head(10).reset_index()
    vc4.columns = ["Pickup_Location", "count"]
    fig11 = px.bar(vc4, x="Pickup_Location", y="count", title="Top 10 Pickup Locations")
    st.plotly_chart(fig11, use_container_width=True)
    st.caption("🔎 Insight: Few hotspots account for bulk of ride pickups.")

    # 12. Top Drop Locations
    vc5 = df_filtered["Drop_Location"].value_counts().head(10).reset_index()
    vc5.columns = ["Drop_Location", "count"]
    fig12 = px.bar(vc5, x="Drop_Location", y="count", title="Top 10 Drop Locations")
    st.plotly_chart(fig12, use_container_width=True)
    st.caption("🔎 Insight: Drop locations overlap with key pickup hotspots.")

    # 13. Booking Value Trend
    daily_value = df_filtered.groupby("Date")["Booking_Value"].sum().reset_index()
    daily_value.columns = ["Date", "total_value"]
    fig13 = px.line(daily_value, x="Date", y="total_value", title="Daily Booking Value Trend")
    st.plotly_chart(fig13, use_container_width=True)
    st.caption("🔎 Insight: Revenue follows demand cycles with weekday peaks.")

    # 14. Average Ride Distance per Vehicle Type
    avg_dist = df_filtered.groupby("Vehicle_Type")["Ride_Distance"].mean().reset_index()
    fig14 = px.bar(avg_dist, x="Vehicle_Type", y="Ride_Distance", title="Average Ride Distance by Vehicle Type")
    st.plotly_chart(fig14, use_container_width=True)
    st.caption("🔎 Insight: Cars (Mini, Sedan, SUV) have longer average rides than Autos.")

    # 15. Average Customer Rating by Vehicle Type
    avg_rating = df_filtered.groupby("Vehicle_Type")["Customer_Rating"].mean().reset_index()
    fig15 = px.bar(avg_rating, x="Vehicle_Type", y="Customer_Rating", title="Avg Customer Rating by Vehicle Type")
    st.plotly_chart(fig15, use_container_width=True)
    st.caption("🔎 Insight: Prime Plus and Prime Sedan achieve slightly better ratings.")

    # 16. Customer Cancellations by Location
    cust_cancel = df_filtered[df_filtered["Booking_Status"]=="Canceled by Customer"]["Pickup_Location"].value_counts().head(10).reset_index()
    cust_cancel.columns = ["Pickup_Location", "count"]
    fig16 = px.bar(cust_cancel, x="Pickup_Location", y="count", title="Top Customer Cancellation Locations")
    st.plotly_chart(fig16, use_container_width=True)
    st.caption("🔎 Insight: Cancellations cluster around high-demand pickup zones.")

    # 17. Booking Value vs Distance
    fig17 = px.scatter(df_filtered, x="Ride_Distance", y="Booking_Value", title="Booking Value vs Ride Distance", opacity=0.5)
    st.plotly_chart(fig17, use_container_width=True)
    st.caption("🔎 Insight: Fare generally increases with distance but with variability.")

    # 18. Incomplete Rides by Reason
    incomplete = df_filtered[df_filtered["Incomplete_Rides"]=="Yes"]["Incomplete_Rides_Reason"].value_counts().reset_index()
    incomplete.columns = ["Reason", "count"]
    fig18 = px.bar(incomplete, x="Reason", y="count", title="Reasons for Incomplete Rides")
    st.plotly_chart(fig18, use_container_width=True)
    st.caption("🔎 Insight: Vehicle breakdowns and customer demand are leading causes.")

    # 19. Top Customers by Ride Count
    top_cust = df_filtered["Customer_ID"].value_counts().head(10).reset_index()
    top_cust.columns = ["Customer_ID", "count"]
    fig19 = px.bar(top_cust, x="Customer_ID", y="count", title="Top 10 Customers by Ride Count")
    st.plotly_chart(fig19, use_container_width=True)
    st.caption("🔎 Insight: Very few customers are repeat riders.")

    # 20. Avg Booking Value by Payment Method
    avg_payment = df_filtered.groupby("Payment_Method")["Booking_Value"].mean().reset_index()
    fig20 = px.bar(avg_payment, x="Payment_Method", y="Booking_Value", title="Avg Booking Value by Payment Method")
    st.plotly_chart(fig20, use_container_width=True)
    st.caption("🔎 Insight: UPI and Credit Card transactions have higher booking values.")



# -----------------------
# SQL QUERIES PAGE
# -----------------------
elif page == "SQL Queries":
    st.header("🗄 SQL Queries Explorer")

    queries = {
        "1. Retrieve all successful bookings": """
            SELECT * FROM rides WHERE "Booking_Status" = 'Success' LIMIT 10;
        """,
        "2. Average ride distance by vehicle type": """
            SELECT "Vehicle_Type", AVG("Ride_Distance") AS avg_distance
            FROM rides GROUP BY "Vehicle_Type";
        """,
        "3. Total cancelled rides by customers": """
            SELECT COUNT(*) AS total_customer_cancellations
            FROM rides WHERE "Booking_Status" = 'Canceled by Customer';
        """,
        "4. Top 5 customers by rides": """
            SELECT "Customer_ID", COUNT(*) AS total_rides
            FROM rides GROUP BY "Customer_ID"
            ORDER BY total_rides DESC LIMIT 5;
        """,
        "5. Driver cancellations (personal & car issues)": """
            SELECT COUNT(*) AS driver_cancellations_personal
            FROM rides WHERE "Booking_Status" = 'Canceled by Driver'
            AND "Canceled_Rides_by_Driver" = 'Personal & Car related issue';
        """,
        "6. Max & Min driver ratings for Prime Sedan": """
            SELECT MAX("Driver_Ratings") AS max_rating, MIN("Driver_Ratings") AS min_rating
            FROM rides WHERE "Vehicle_Type" = 'Prime Sedan' AND "Driver_Ratings" IS NOT NULL;
        """,
        "7. All rides paid with UPI": """
            SELECT * FROM rides WHERE "Payment_Method" = 'UPI' LIMIT 10;
        """,
        "8. Average customer rating per vehicle type": """
            SELECT "Vehicle_Type", AVG("Customer_Rating") AS avg_rating
            FROM rides WHERE "Customer_Rating" IS NOT NULL
            GROUP BY "Vehicle_Type";
        """,
        "9. Total booking value of successful rides": """
            SELECT SUM("Booking_Value") AS total_success_value
            FROM rides WHERE "Booking_Status" = 'Success';
        """,
        "10. Incomplete rides with reasons": """
            SELECT Booking_ID, Incomplete_Rides, Incomplete_Rides_Reason
            FROM rides WHERE Incomplete_Rides = 'Yes' LIMIT 10;
        """
    }

    choice = st.selectbox("Select a query to run:", list(queries.keys()))
    conn = sqlite3.connect(DB_PATH)
    df_sql = pd.read_sql(queries[choice], conn)
    conn.close()

    st.code(queries[choice], language="sql")
    st.dataframe(df_sql, use_container_width=True)


# -----------------------
# POWER BI DASHBOARD PAGE
# -----------------------
elif page == "Power BI Dashboard":
    st.header("📊 Power BI Dashboard")
    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiYjdiZmVhOWMtYjY3Zi00Nzc0LWFlZWItN2Q0N2M2NjYyNDIzIiwidCI6ImZlM2I0ZGI2LWYzOGUtNDQ4Ni1hZTkwLTU3OGFmM2E1YTM4OCJ9"
    st.markdown(
        f'<iframe title="Ola Rides PowerBI" width="100%" height="800" src="{powerbi_url}" frameborder="0" allowFullScreen="true"></iframe>',
        unsafe_allow_html=True
    )


# ==============================
# 📊 INSIGHTS & RECOMMENDATIONS
# ==============================
elif page == "Insights & Recommendations":
    st.title("📊 Insights & Recommendations")
    st.image("images/ola-logo.png", width=120)

    st.markdown("Here we combine **EDA findings + Power BI dashboard** into actionable insights.")

    # ---- Layout: 10 Visuals with Insights ----
    # 1. Booking Status Breakdown
    fig1 = px.pie(df, names="Booking_Status", title="Booking Status Breakdown")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Out of **103,024 rides**, only **62% were successful**.
        - **38% cancellations** (Driver: 18k, Customer: 10k, Driver Not Found: 10k).
        - High cancellation rate is a **critical operational issue**.
        """)

    # 2. Cancellation Reasons by Driver
    driver_reasons = df["Canceled_Rides_by_Driver"].value_counts().head(5).reset_index()
    driver_reasons.columns = ["Reason", "Count"]
    fig2 = px.bar(driver_reasons, x="Reason", y="Count", title="Driver Cancellation Reasons")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Top reasons: **Personal/Car issues (6.5k)**, **Customer issues (5.4k)**, **Health-related (3.6k)**.
        - Indicates gaps in **driver support & backup fleet availability**.
        """)

    # 3. Cancellation Reasons by Customer
    cust_reasons = df["Canceled_Rides_by_Customer"].value_counts().head(5).reset_index()
    cust_reasons.columns = ["Reason", "Count"]
    fig3 = px.bar(cust_reasons, x="Reason", y="Count", title="Customer Cancellation Reasons")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig3, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Main reasons: **Driver not moving (3.1k)**, **Driver asked to cancel (2.6k)**, **Change of plans (2k)**.
        - These highlight **driver behavior issues** and need for **better route compliance**.
        """)

    # 4. Revenue by Vehicle Type
    revenue_vehicle = df.groupby("Vehicle_Type")["Booking_Value"].sum().reset_index()
    fig4 = px.bar(revenue_vehicle, x="Vehicle_Type", y="Booking_Value", title="Revenue by Vehicle Type")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig4, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - **Prime Sedan, eBike, Auto, Prime Plus** dominate total revenue.
        - Premium vehicles bring **higher ticket sizes**, while 2/3-wheelers bring **high frequency**.
        """)

    # 5. Weekly Revenue Trends
    weekly_rev = df.groupby("Ride_Week")["Booking_Value"].sum().reset_index()
    fig5 = px.line(weekly_rev, x="Ride_Week", y="Booking_Value", title="Weekly Revenue Trends")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig5, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Revenue is **consistent across weeks** (~12.7M per week).
        - Week 31 shows a dip (**seasonality/holidays**).
        - Indicates **stable demand with periodic dips**.
        """)

    # 6. Distance vs Fare Scatter
    fig6 = px.scatter(df, x="Ride_Distance", y="Booking_Value", title="Distance vs Fare")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig6, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Correlation is almost **zero (0.0005)**.
        - Suggests **pricing is not distance-driven** but **dynamic surge/vehicle-based**.
        """)

    # 7. Top Pickup Locations (Cancellations)
    cancel_pickups = df[df["Booking_Status"].str.contains("Canceled", na=False)]["Pickup_Location"].value_counts().head(10).reset_index()
    cancel_pickups.columns = ["Pickup_Location", "Count"]
    fig7 = px.bar(cancel_pickups, x="Pickup_Location", y="Count", title="Top Cancellation Hotspots")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig7, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - **Vijayanagar, Whitefield, Tumkur Road** are top cancellation hotspots.
        - Indicates **mismatch of supply-demand** in these areas.
        """)

    # 8. Driver Ratings Distribution
    fig8 = px.histogram(df, x="Driver_Ratings", nbins=20, title="Driver Ratings Distribution")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig8, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Ratings are **centered around 4.0**.
        - Indicates **service quality is consistent but not exceptional**.
        """)

    # 9. Customer Ratings Distribution
    fig9 = px.histogram(df, x="Customer_Rating", nbins=20, title="Customer Ratings Distribution")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig9, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Customers also average around **4.0**.
        - Balanced ratings → indicates **both driver & customer expectations need work**.
        """)

    # 10. High Value Customers
    high_value = df.groupby("Customer_ID")["Booking_Value"].sum().sort_values(ascending=False).head(10).reset_index()
    fig10 = px.bar(high_value, x="Customer_ID", y="Booking_Value", title="Top 10 High-Value Customers")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig10, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - A handful of **loyal customers contribute disproportionately** to revenue.
        - Opportunity to **launch loyalty programs**.
        """)

    # ---- Embed Power BI Dashboard ----
    st.subheader("Interactive Power BI Dashboard")
    st.components.v1.iframe(
        "https://app.powerbi.com/view?r=eyJrIjoiYjdiZmVhOWMtYjY3Zi00Nzc0LWFlZWItN2Q0N2M2NjYyNDIzIiwidCI6ImZlM2I0ZGI2LWYzOGUtNDQ4Ni1hZTkwLTU3OGFmM2E1YTM4OCJ9",
        height=600,
        width=1000
    )

    # ---- Recommendations Section ----
    st.header("✅ Recommendations")
    st.markdown("""
    - **Reduce Driver Cancellations**: Incentives, vehicle support, backup fleet.
    - **Curb Customer Cancellations**: Improve ETA accuracy, penalize frequent cancellations.
    - **Optimize Hotspots**: More driver allocation in **Vijayanagar, Whitefield, Tumkur Road**.
    - **Pricing Strategy**: Consider **distance + dynamic** pricing to make fares fairer.
    - **Customer Loyalty**: Special offers for top customers (retention strategy).
    - **Service Quality**: Training for drivers, feedback loop to lift average ratings.
    """)
