# district_dashboard.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# Load data
df = pd.read_csv("asd.csv")

# Sidebar filters
st.sidebar.title("🔍 Filter Options")
state = st.sidebar.selectbox("Select State", sorted(df["State_name"].unique()))
districts = df[df["State_name"] == state]["District_name"].unique()
district = st.sidebar.selectbox("Select District", sorted(districts))

# Filtered data
data = df[(df["State_name"] == state) & (df["District_name"] == district)].iloc[0]

# Title
st.title("📊 District Insights Explorer")
st.markdown(f"### {district}, {state}")

# Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("🧍 Population", f"{data['Population']:,}")
col2.metric("📚 Literacy Rate", f"{(data['Literate'] / data['Population'] * 100):.2f}%")
col3.metric("👨‍👩‍👧‍👦 Gender Ratio", f"{data['Female'] / data['Male']:.2f}")

# Age Distribution
st.subheader("📈 Age Group Distribution")
age_labels = ["0–29", "30–49", "50+"]
age_values = [data["Age_Group_0_29"], data["Age_Group_30_49"], data["Age_Group_50"]]
fig1 = px.pie(names=age_labels, values=age_values, title="Age Group Breakdown")
st.plotly_chart(fig1)

# Education Levels
st.subheader("🎓 Education Levels")
edu_labels = ["Secondary", "Higher", "Graduate"]
edu_values = [data["Secondary_Education"], data["Higher_Education"], data["Graduate_Education"]]
fig2, ax2 = plt.subplots()
ax2.bar(edu_labels, edu_values, color=["#6A5ACD", "#20B2AA", "#FF6347"])
ax2.set_ylabel("Number of People")
st.pyplot(fig2)

# Worker Composition
st.subheader("💼 Worker Composition")
worker_labels = ["Cultivators", "Agricultural", "Household"]
worker_values = [data["Cultivator_Workers"], data["Agricultural_Workers"], data["Household_Workers"]]
fig3 = px.bar(x=worker_labels, y=worker_values, color=worker_labels, title="Worker Types")
st.plotly_chart(fig3)

# Religion Distribution
st.subheader("🕊️ Religion Distribution")
religions = {
    "Hindus": data["Hindus"],
    "Muslims": data["Muslims"],
    "Christians": data["Christians"],
    "Sikhs": data["Sikhs"],
    "Buddhists": data["Buddhists"],
    "Jains": data["Jains"]
}
fig4 = px.pie(names=list(religions.keys()), values=list(religions.values()), title="Religious Composition")
st.plotly_chart(fig4)

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit, pandas, numpy, matplotlib, and plotly")
