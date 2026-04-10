import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="HousingPulse Dashboard", layout="wide")

st.title("HousingPulse Dashboard")
st.write("Compare rent and housing prices across U.S. states.")

# Load data
@st.cache_data
def load_data():
    fmr = pd.read_excel("FY26_FMRs.xlsx")
    hpi = pd.read_excel("hpi_po_state.xlsx")
    return fmr, hpi

fmr, hpi = load_data()

# Clean column names
fmr.columns = fmr.columns.str.strip()
hpi.columns = hpi.columns.str.strip()

# Clean columns
fmr["stusps"] = fmr["stusps"].astype(str).str.strip().str.upper()
hpi["state"] = hpi["state"].astype(str).str.strip().str.upper()

fmr["fmr_2"] = pd.to_numeric(fmr["fmr_2"], errors="coerce")
hpi["index_nsa"] = pd.to_numeric(hpi["index_nsa"], errors="coerce")

# Keep needed columns
rent_data = fmr[["stusps", "fmr_2"]].dropna()
price_data = hpi[["state", "index_nsa"]].dropna()

# Group
rent_by_state = rent_data.groupby("stusps", as_index=False)["fmr_2"].mean()
rent_by_state.rename(columns={"stusps": "state", "fmr_2": "avg_rent_2br"}, inplace=True)

price_by_state = price_data.groupby("state", as_index=False)["index_nsa"].mean()
price_by_state.rename(columns={"index_nsa": "avg_hpi"}, inplace=True)

# Merge
merged = pd.merge(rent_by_state, price_by_state, on="state", how="inner")

if merged.empty:
    st.error("Merged dataset is empty. Check state names.")
    st.stop()

# Sidebar filter
st.sidebar.header("Filters")
selected_states = st.sidebar.multiselect(
    "Select States",
    options=sorted(merged["state"].unique()),
    default=sorted(merged["state"].unique())
)

filtered = merged[merged["state"].isin(selected_states)]

if filtered.empty:
    st.warning("Select at least one state.")
    st.stop()

# Summary
st.subheader("Summary Metrics")
col1, col2 = st.columns(2)

with col1:
    st.metric("Average Rent", f"${filtered['avg_rent_2br'].mean():,.2f}")

with col2:
    st.metric("Average Housing Index", f"{filtered['avg_hpi'].mean():.2f}")

# Data
st.subheader("Data Preview")
st.dataframe(filtered)

# Chart
st.subheader("Rent vs Housing Price Index")

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(filtered["avg_hpi"], filtered["avg_rent_2br"])

for _, row in filtered.iterrows():
    ax.text(row["avg_hpi"], row["avg_rent_2br"], row["state"], fontsize=8)

ax.set_xlabel("Housing Price Index")
ax.set_ylabel("Average 2BR Rent")
ax.set_title("Housing Price vs Rent by State")
ax.grid(True)

st.pyplot(fig)

# Insights
st.subheader("Insights")
st.write("This dashboard compares average 2-bedroom rent and housing prices across states.")
st.write("Users can identify which states have higher housing costs.")
st.write("The chart shows the relationship between rent and housing prices.")
