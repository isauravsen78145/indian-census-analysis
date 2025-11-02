import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.set_page_config(page_title="Uber Analytics Dashboard", layout="wide", initial_sidebar_state="expanded")

@st.cache_data
def load_data(path='uber.csv'):
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]
    try:
        df['datetime'] = pd.to_datetime(df['Date'].astype(str) + ' ' + df['Time'].astype(str))
    except Exception:
        df['datetime'] = pd.to_datetime(df['Date'], errors='coerce')
    df['date'] = df['datetime'].dt.date
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['weekday'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour
    if 'Avg VTAT' in df.columns:
        df['Avg VTAT'] = pd.to_numeric(df['Avg VTAT'], errors='coerce')
    return df

@st.cache_data
def agg_counts(df, groupby_cols, value_col=None, agg='count'):
    if agg == 'count':
        return df.groupby(groupby_cols).size().reset_index(name='count')
    else:
        return df.groupby(groupby_cols)[value_col].mean().reset_index(name=f'{value_col}_mean')

st.title("🚕 Uber — Interactive Analytics Dashboard")
st.markdown("A fully interactive dashboard built using **pandas**, **numpy**, **matplotlib**, **seaborn**, **plotly**, and **streamlit**.")

with st.spinner('Loading data...'):
    df = load_data()

st.sidebar.header("Filters & Settings")
min_date = pd.to_datetime(df['date'].min())
max_date = pd.to_datetime(df['date'].max())

date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
vehicle_types = st.sidebar.multiselect("Vehicle Type", options=df['Vehicle Type'].unique().tolist(), default=df['Vehicle Type'].unique().tolist())
booking_status = st.sidebar.multiselect("Booking Status", options=df['Booking Status'].unique().tolist(), default=df['Booking Status'].unique().tolist())

if len(date_range) == 2:
    start_date, end_date = date_range
    mask = (pd.to_datetime(df['date']) >= pd.to_datetime(start_date)) & (pd.to_datetime(df['date']) <= pd.to_datetime(end_date))
else:
    mask = pd.Series([True]*len(df))
mask &= df['Vehicle Type'].isin(vehicle_types)
mask &= df['Booking Status'].isin(booking_status)

filtered = df[mask].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Bookings", f"{filtered.shape[0]:,}")
col2.metric("Unique Customers", f"{filtered['Customer ID'].nunique():,}")
col3.metric("Avg VTAT (overall)", f"{filtered['Avg VTAT'].mean():.2f}" if 'Avg VTAT' in filtered.columns else "N/A")
col4.metric("Cancelled (%)", f"{(filtered['Booking Status']=='Cancelled').mean()*100:.2f}%")

st.header("📈 Booking Analysis")
by_date = agg_counts(filtered, 'date')
fig_time = px.line(by_date, x='date', y='count', title='Bookings Over Time', labels={'count':'Bookings','date':'Date'})
st.plotly_chart(fig_time, use_container_width=True)

status_counts = filtered['Booking Status'].value_counts().reset_index()
status_counts.columns = ['status', 'count']
fig_pie = px.pie(status_counts, names='status', values='count', title='Booking Status Breakdown')
st.plotly_chart(fig_pie, use_container_width=True)

st.header("🕒 Time Analysis")
colA, colB = st.columns([2,1])
with colA:
    hours = agg_counts(filtered, 'hour')
    fig_hours = px.bar(hours, x='hour', y='count', title='Bookings by Hour')
    st.plotly_chart(fig_hours, use_container_width=True)
with colB:
    pivot = filtered.pivot_table(index='weekday', columns='hour', values='Booking ID', aggfunc='count').fillna(0)
    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    pivot = pivot.reindex(weekdays)
    fig, ax = plt.subplots(figsize=(10,3))
    sns.heatmap(pivot, ax=ax, cmap='coolwarm', cbar_kws={'label':'Bookings'})
    ax.set_title('Bookings Heatmap (Weekday vs Hour)')
    st.pyplot(fig)

st.header("📍 Location Insights")
col1, col2 = st.columns(2)
with col1:
    top_pick = filtered['Pickup Location'].value_counts().nlargest(10).reset_index()
    top_pick.columns = ['Pickup Location','count']
    fig_pick = px.bar(top_pick, x='count', y='Pickup Location', orientation='h', title='Top Pickup Locations')
    st.plotly_chart(fig_pick, use_container_width=True)
with col2:
    top_drop = filtered['Drop Location'].value_counts().nlargest(10).reset_index()
    top_drop.columns = ['Drop Location','count']
    fig_drop = px.bar(top_drop, x='count', y='Drop Location', orientation='h', title='Top Drop Locations')
    st.plotly_chart(fig_drop, use_container_width=True)

st.header("🚘 Vehicle Performance")
if 'Avg VTAT' in filtered.columns:
    vtat = filtered.groupby('Vehicle Type')['Avg VTAT'].agg(['mean','median','count']).reset_index()
    fig_vtat = px.bar(vtat, x='Vehicle Type', y='mean', title='Average VTAT by Vehicle Type')
    st.plotly_chart(fig_vtat, use_container_width=True)

st.header("👥 Customer Behavior")
customers = filtered['Customer ID'].value_counts().nlargest(10).reset_index()
customers.columns = ['Customer ID','Bookings']
fig_cust = px.bar(customers, x='Customer ID', y='Bookings', title='Top 10 Customers')
st.plotly_chart(fig_cust, use_container_width=True)

bookings_per_cust = filtered.groupby('Customer ID').size()
fig_hist = px.histogram(bookings_per_cust, nbins=50, title='Bookings per Customer')
st.plotly_chart(fig_hist, use_container_width=True)

st.header("📂 Data & Export")
st.dataframe(filtered.head(200))
st.download_button(label='Download Filtered Data as CSV', data=filtered.to_csv(index=False), file_name='filtered_uber_data.csv', mime='text/csv')

st.markdown("---")
st.write("💡 Tips: Explore by adjusting filters and visualizing different sections of data.")