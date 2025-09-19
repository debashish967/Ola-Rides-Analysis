# 🚖 Ola Rides Analysis Dashboard

## 📌 Project Overview
This project analyzes **Ola ride-sharing data** to uncover insights about ride performance, cancellations, customer/driver behavior, and revenue.  
The goal is to provide **business use cases** and **actionable recommendations** for operational improvement.

## 🎯 Business Use Cases
- Understand **ride success vs. cancellations** and reasons behind cancellations.
- Analyze **driver & customer ratings** to measure satisfaction.
- Track **revenue trends** and **top customers**.
- Identify **high-cancellation zones** and demand hotspots.
- Provide **recommendations for improving efficiency** and customer experience.

## 🛠️ Approach
1. **Data Cleaning** → Cleaned raw rides data → `rides_cleaned.csv`
2. **EDA (20 analyses)** → Key metrics, cancellations, revenue, hotspots, trends.
3. **SQL Queries (10 queries)** → Customer patterns, driver issues, payment modes.
4. **Visualization**  
   - 📊 **Power BI Dashboard** ([View here](https://app.powerbi.com/view?r=eyJrIjoiYjdiZmVhOWMtYjY3Zi00Nzc0LWFlZWItN2Q0N2M2NjYyNDIzIiwidCI6ImZlM2I0ZGI2LWYzOGUtNDQ4Ni1hZTkwLTU3OGFmM2E1YTM4OCJ9))  
   - 🌐 **Streamlit App** (interactive web app with KPIs, EDA, SQL, BI, and Insights)
5. **Insights & Recommendations** → Expanded with charts and crisp recommendations.

## 🚀 Streamlit App
Run locally:
```bash
pip install -r requirements.txt
streamlit run app.py