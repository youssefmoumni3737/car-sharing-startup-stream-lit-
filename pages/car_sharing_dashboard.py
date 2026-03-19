import streamlit as st
import pandas as pd

st.title("🚗 Car Sharing Dashboard")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    trips = pd.read_csv("datasets/trips.csv")
    cars = pd.read_csv("datasets/cars.csv")
    cities = pd.read_csv("datasets/cities.csv")
    return trips, cars, cities

trips, cars, cities = load_data()

# ---- MERGE DATAFRAMES ----
trips_merged = trips.merge(cars, left_on="car_id", right_on="id")
trips_merged = trips_merged.merge(cities, on="city_id")

# ---- DROP USELESS COLUMNS ----
cols_to_drop = [col for col in ["id_car", "city_id", "id_customer", "id"] if col in trips_merged.columns]
trips_merged = trips_merged.drop(columns=cols_to_drop)

# ---- FIX DATE FORMAT ----
trips_merged['pickup_date'] = pd.to_datetime(trips_merged['pickup_time']).dt.date

# ---- SIDEBAR FILTER ----
st.sidebar.header("Filters")
brands = trips_merged["brand"].unique()
cars_brand = st.sidebar.multiselect("Select Car Brand", brands, default=brands)
trips_merged = trips_merged[trips_merged["brand"].isin(cars_brand)]

# ---- METRICS ----
total_trips = len(trips_merged)
total_distance = trips_merged["distance"].sum()
top_car = trips_merged.groupby("model")["revenue"].sum().idxmax()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Trips", total_trips)
with col2:
    st.metric("Top Car Model by Revenue", top_car)
with col3:
    st.metric("Total Distance (km)", f"{total_distance:,.2f}")

# ---- PREVIEW DATA ----
st.subheader("Data Preview")
st.write(trips_merged.head())

# ---- VISUALIZATIONS ----
st.subheader("📈 Trips Over Time")
trips_over_time = trips_merged.groupby("pickup_date").size().reset_index(name="trips")
st.line_chart(trips_over_time.set_index("pickup_date"))

st.subheader("💰 Revenue Per Car Model")
revenue_by_model = trips_merged.groupby("model")["revenue"].sum()
st.bar_chart(revenue_by_model)

st.subheader("🌍 Revenue by City")
revenue_by_city = trips_merged.groupby("city_name")["revenue"].sum()
st.bar_chart(revenue_by_city)