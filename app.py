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
CSV_PATH = "rides_no_outliers.csv"
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

    # KPI Summary
    st.subheader("📌 KPI Summary")
    st.write("""
    - **Total Rides:** 99,109  
    - **Successful Rides:** 61,515  
    - **Success Rate:** 62.07%  
    - **Total Cancellations:** 37,594 (37.93%)  
    - **Avg Fare (Success):** ₹467.37  
    - **Median Fare (Success):** ₹374.0  
    - **Avg Distance (Success):** 22.86 km  
    - **Avg Driver Rating:** 4.0  
    - **Avg Customer Rating:** 4.0
    """)


    # 1. Rides by Vehicle Type
    vc1 = df_filtered["Vehicle_Type"].value_counts().reset_index()
    vc1.columns = ["Vehicle_Type", "count"]
    fig1 = px.bar(vc1, x="Vehicle_Type", y="count", title="Rides by Vehicle Type",
                  labels={"Vehicle_Type": "Vehicle Type", "count": "Number of Rides"})
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("🔎 Insight: eBikes, Autos, and Prime vehicles account for most rides; Mini and Bike have slightly lower usage.")


    # 2. Daily Booking Trend
    daily_booking = df_filtered.groupby("Date")["Booking_ID"].count().reset_index()
    daily_booking.columns = ["Date", "count"]
    fig2 = px.line(daily_booking, x="Date", y="count", title="Daily Booking Trend",
                   labels={"count": "Number of Rides"})
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("🔎 Insight: Ride demand peaks mid-week and drops slightly on weekends, showing weekday dominance.")


    # 3. Payment Method Distribution
    pm = df_filtered["Payment_Method"].value_counts().reset_index()
    pm.columns = ["Payment_Method", "count"]
    fig3 = px.pie(pm, names="Payment_Method", values="count", title="Payment Method Distribution")
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("🔎 Insight: UPI and Cash are the most popular payment methods; Credit Card usage is moderate and Not Applicable occurs for canceled/incomplete rides.")


    # 4. Booking Value by Vehicle Type
    fig4 = px.box(df_filtered, x="Vehicle_Type", y="Booking_Value", title="Booking Value by Vehicle Type")
    st.plotly_chart(fig4, use_container_width=True)
    st.caption("🔎 Insight: Prime Sedan, Prime SUV, and Mini vehicles generate higher fares compared to Bikes and Autos.")


    # 5. Customer Rating Distribution
    fig5 = px.histogram(df_filtered, x="Customer_Rating", nbins=20, title="Distribution of Customer Ratings")
    st.plotly_chart(fig5, use_container_width=True)
    st.caption("🔎 Insight: Majority of customers rate rides around 4.0, with fewer extreme low/high ratings.")


    # 6. Driver Ratings Distribution
    fig6 = px.histogram(df_filtered, x="Driver_Ratings", nbins=20, title="Distribution of Driver Ratings")
    st.plotly_chart(fig6, use_container_width=True)
    st.caption("🔎 Insight: Most drivers have ratings around 4.0, indicating consistent positive feedback from customers.")



    # 7. Rides by Day of Week
    vc2 = df_filtered["Day_of_Week"].value_counts().reset_index()
    vc2.columns = ["Day_of_Week", "count"]
    fig7 = px.bar(vc2, x="Day_of_Week", y="count", title="Rides by Day of Week")
    st.plotly_chart(fig7, use_container_width=True)
    st.caption("🔎 Insight: Fridays and weekdays see the highest ride demand, while weekends are slightly lower.")


    # 8. Rides by Hour
    vc3 = df_filtered["Ride_Hour"].value_counts().reset_index()
    vc3.columns = ["Ride_Hour", "count"]
    fig8 = px.bar(vc3.sort_values("Ride_Hour"), x="Ride_Hour", y="count", title="Rides by Hour of Day")
    st.plotly_chart(fig8, use_container_width=True)
    st.caption("🔎 Insight: Peak ride demand occurs during morning (8–10 AM) and evening (5–8 PM) commute hours.")


    # 9. Ride Distance Distribution
    fig9 = px.histogram(df_filtered, x="Ride_Distance", nbins=50, title="Ride Distance Distribution")
    st.plotly_chart(fig9, use_container_width=True)
    st.caption("🔎 Insight: Most rides are short to medium distance; long-distance trips are rare.")


    # 10. Cancellations Over Time
    cancel_trend = df_filtered[df_filtered["Booking_Status"].str.contains("Canceled")]
    cancel_daily = cancel_trend.groupby("Date")["Booking_ID"].count().reset_index()
    cancel_daily.columns = ["Date", "count"]
    fig10 = px.line(cancel_daily, x="Date", y="count", title="Daily Cancellations Trend")
    st.plotly_chart(fig10, use_container_width=True)
    st.caption("🔎 Insight: Cancellations correlate with ride volume; more rides result in more cancellations, with driver and customer contributions visible.")


    # 11. Top Pickup Locations
    vc4 = df_filtered["Pickup_Location"].value_counts().head(10).reset_index()
    vc4.columns = ["Pickup_Location", "count"]
    fig11 = px.bar(vc4, x="Pickup_Location", y="count", title="Top 10 Pickup Locations")
    st.plotly_chart(fig11, use_container_width=True)
    st.caption("🔎 Insight: Vijayanagar, Tumkur Road, Whitefield, and Banashankari are the busiest pickup locations.")


    # 12. Top Drop Locations
    vc5 = df_filtered["Drop_Location"].value_counts().head(10).reset_index()
    vc5.columns = ["Drop_Location", "count"]
    fig12 = px.bar(vc5, x="Drop_Location", y="count", title="Top 10 Drop Locations")
    st.plotly_chart(fig12, use_container_width=True)
    st.caption("🔎 Insight: Key drop locations mirror pickup hotspots, indicating concentrated ride demand in main city areas.")


    # 13. Booking Value Trend
    daily_value = df_filtered.groupby("Date")["Booking_Value"].sum().reset_index()
    daily_value.columns = ["Date", "total_value"]
    fig13 = px.line(daily_value, x="Date", y="total_value", title="Daily Booking Value Trend")
    st.plotly_chart(fig13, use_container_width=True)
    st.caption("🔎 Insight: Revenue peaks mid-week, dips on certain days, following ride volume trends.")


    # 14. Average Ride Distance per Vehicle Type
    avg_dist = df_filtered.groupby("Vehicle_Type")["Ride_Distance"].mean().reset_index()
    fig14 = px.bar(avg_dist, x="Vehicle_Type", y="Ride_Distance", title="Average Ride Distance by Vehicle Type")
    st.plotly_chart(fig14, use_container_width=True)
    st.caption("🔎 Insight: Mini, Prime Sedan, and SUVs cover longer average distances compared to Bikes and eBikes.")


    # 15. Average Customer Rating by Vehicle Type
    avg_rating = df_filtered.groupby("Vehicle_Type")["Customer_Rating"].mean().reset_index()
    fig15 = px.bar(avg_rating, x="Vehicle_Type", y="Customer_Rating", title="Avg Customer Rating by Vehicle Type")
    st.plotly_chart(fig15, use_container_width=True)
    st.caption("🔎 Insight: Prime Plus, Prime Sedan, and SUVs receive slightly higher average customer ratings than other vehicle types.")


    # 16. Customer Cancellations by Location
    cust_cancel = df_filtered[df_filtered["Booking_Status"]=="Canceled by Customer"]["Pickup_Location"].value_counts().head(10).reset_index()
    cust_cancel.columns = ["Pickup_Location", "count"]
    fig16 = px.bar(cust_cancel, x="Pickup_Location", y="count", title="Top Customer Cancellation Locations")
    st.plotly_chart(fig16, use_container_width=True)
    st.caption("🔎 Insight: Customers mostly cancel rides from busy pickup areas such as Vijayanagar, Tumkur Road, and Whitefield.")


    # 17. Booking Value vs Distance
    fig17 = px.scatter(df_filtered, x="Ride_Distance", y="Booking_Value", title="Booking Value vs Ride Distance", opacity=0.5)
    st.plotly_chart(fig17, use_container_width=True)
    st.caption("🔎 Insight: Booking value generally rises with ride distance, but short-distance rides can also have high fares due to vehicle type or surge pricing.")


    # 18. Incomplete Rides by Reason
    incomplete = df_filtered[df_filtered["Incomplete_Rides"]=="Yes"]["Incomplete_Rides_Reason"].value_counts().reset_index()
    incomplete.columns = ["Reason", "count"]
    fig18 = px.bar(incomplete, x="Reason", y="count", title="Reasons for Incomplete Rides")
    st.plotly_chart(fig18, use_container_width=True)
    st.caption("🔎 Insight: Incomplete rides mainly occur due to vehicle issues or ride cancellations by driver/customer.")



    # 19. Top Customers by Ride Count
    top_cust = df_filtered["Customer_ID"].value_counts().head(10).reset_index()
    top_cust.columns = ["Customer_ID", "count"]
    fig19 = px.bar(top_cust, x="Customer_ID", y="count", title="Top 10 Customers by Ride Count")
    st.plotly_chart(fig19, use_container_width=True)
    st.caption("🔎 Insight: Most customers take few rides, while a small set of customers account for multiple bookings.")


    # 20. Avg Booking Value by Payment Method
    avg_payment = df_filtered.groupby("Payment_Method")["Booking_Value"].mean().reset_index()
    fig20 = px.bar(avg_payment, x="Payment_Method", y="Booking_Value", title="Avg Booking Value by Payment Method")
    st.plotly_chart(fig20, use_container_width=True)
    st.caption("🔎 Insight: UPI and Credit Card payments tend to have higher average booking values; Cash is common but lower value on average.")




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
        - Out of **99,109 rides**, **62% were successful**; cancellations are **38%**.
        - Cancellations: Driver ~17.7k, Customer ~10k, Driver Not Found ~9.7k.
        - **High cancellation rate** indicates operational and demand-supply challenges.
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
        - Top reasons: **Personal/Car issues (6.2k)**, **Customer issues (5.2k)**, **Health (3.5k)**.
        - Highlights need for **better driver support, backup fleet, and training**.
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
        - Main reasons: **Driver not moving (3k)**, **Driver asked to cancel (2.5k)**, **Change of plans (2k)**.
        - Suggests **driver punctuality and communication** improvements are required.
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
        - **Prime Sedan, eBike, Auto, Prime Plus** generate majority revenue.
        - Premium vehicles have **higher fares**, while 2/3-wheelers contribute **high frequency rides**.
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
        - Revenue is **stable across weeks (~12–13M/week)**.
        - Week 31 shows a dip (**seasonality/holidays**).
        - Indicates **stable demand with occasional fluctuations**.
        """)


    # 6. Distance vs Fare Scatter
    fig6 = px.scatter(df, x="Ride_Distance", y="Booking_Value", title="Distance vs Fare")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig6, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Correlation between distance and fare is **almost zero (0.0005)**.
        - Pricing depends more on **vehicle type, surge pricing, and demand**, not distance alone.
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
        - Indicates **supply-demand mismatch** in these areas during peak hours.
        """)


    # 8. Driver Ratings Distribution
    fig8 = px.histogram(df, x="Driver_Ratings", nbins=20, title="Driver Ratings Distribution")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig8, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Driver ratings are mostly around **4.0**.
        - Service is **consistent**, but some drivers may require **performance support**.
        """)


    # 9. Customer Ratings Distribution
    fig9 = px.histogram(df, x="Customer_Rating", nbins=20, title="Customer Ratings Distribution")
    col1, col2 = st.columns([2, 3])
    with col1:
        st.plotly_chart(fig9, use_container_width=True)
    with col2:
        st.subheader("Insights")
        st.write("""
        - Customer ratings also center around **4.0**.
        - Balanced ratings suggest **both driver and customer experience** can be improved.
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
        - A few **loyal customers contribute disproportionately** to revenue.
        - Opportunity for **loyalty programs, personalized offers, and retention campaigns**.
        """)


    # ---- Embed Power BI Dashboard ----
    st.subheader("Interactive Power BI Dashboard")
    st.components.v1.iframe(
        "https://app.powerbi.com/view?r=eyJrIjoiYjdiZmVhOWMtYjY3Zi00Nzc0LWFlZWItN2Q0N2M2NjYyNDIzIiwidCI6ImZlM2I0ZGI2LWYzOGUtNDQ4Ni1hZTkwLTU3OGFmM2E1YTM4OCJ9",
        height=600,
        width=1000
    )

    # ---- Recommendations Section ----
    st.subheader("💡 Actionable Recommendations")
    st.write("""
    - **Reduce cancellations**:
      - Improve driver availability and route compliance.
      - Implement backup fleet support in high-demand zones.
    - **Optimize vehicle allocation**:
      - Focus premium vehicles on longer-distance rides to increase revenue.
      - Assign frequent 2/3-wheelers to short-distance, high-demand zones.
    - **Promote digital payments**:
      - Encourage UPI/Credit Card usage to increase average booking value.
    - **Customer retention**:
      - Launch loyalty programs targeting high-value and repeat customers.
      - Offer personalized promotions to top riders.
    - **Driver performance & quality**:
      - Conduct training and performance monitoring for low-rated drivers.
      - Incentivize top drivers to maintain high service standards.
    - **Demand forecasting & operational planning**:
      - Monitor peak hours and high-demand locations for better supply planning.
      - Adjust dynamic pricing or incentives based on ride volume patterns.
    """)

