import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="HousingPulse Dashboard", layout="wide")

st.title("HousingPulse Dashboard")
st.write("Compare 2-bedroom rent and housing price index across U.S. states.")

@st.cache_data
def load_data():
    fmr = pd.read_excel("FY26_FMRs.xlsx")
    hpi = pd.read_excel("hpi_po_state.xlsx")
    return fmr, hpi

fmr, hpi = load_data()

fmr.columns = fmr.columns.str.strip()
hpi.columns = hpi.columns.str.strip()

fmr["stusps"] = fmr["stusps"].astype(str).str.strip().str.upper()
hpi["state"] = hpi["state"].astype(str).str.strip().str.upper()

fmr["fmr_2"] = pd.to_numeric(fmr["fmr_2"], errors="coerce")
hpi["index_nsa"] = pd.to_numeric(hpi["index_nsa"], errors="coerce")

rent_data = fmr[["stusps", "fmr_2"]].dropna()
price_data = hpi[["state", "index_nsa"]].dropna()

rent_by_state = rent_data.groupby("stusps", as_index=False)["fmr_2"].mean()
rent_by_state.rename(columns={"stusps": "state", "fmr_2": "avg_rent_2br"}, inplace=True)

price_by_state = price_data.groupby("state", as_index=False)["index_nsa"].mean()
price_by_state.rename(columns={"index_nsa": "avg_hpi"}, inplace=True)

merged = pd.merge(rent_by_state, price_by_state, on="state", how="inner")

if merged.empty:
    st.error("Merged dataset is empty. Check state names.")
    st.stop()

# New professor-feedback feature: affordability ratio
merged["affordability_ratio"] = merged["avg_rent_2br"] / merged["avg_hpi"]

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

st.subheader("Summary Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average 2BR Rent", f"${filtered['avg_rent_2br'].mean():,.2f}")

with col2:
    st.metric("Average HPI", f"{filtered['avg_hpi'].mean():.2f}")

with col3:
    correlation = filtered["avg_rent_2br"].corr(filtered["avg_hpi"])
    st.metric("Rent vs HPI Correlation", f"{correlation:.2f}")

st.subheader("Data Preview")
st.dataframe(filtered)

st.subheader("Rent vs Housing Price Index")

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(filtered["avg_hpi"], filtered["avg_rent_2br"])

for _, row in filtered.iterrows():
    ax.text(row["avg_hpi"], row["avg_rent_2br"], row["state"], fontsize=8)

ax.set_xlabel("Housing Price Index")
ax.set_ylabel("Average 2BR Rent")
ax.set_title("Housing Price Index vs 2BR Rent by State")
ax.grid(True)

st.pyplot(fig)

st.subheader("Affordability Measure")
st.write("Affordability ratio = Average 2BR Rent / Housing Price Index")

affordability_sorted = filtered.sort_values("affordability_ratio", ascending=False)

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.bar(affordability_sorted["state"], affordability_sorted["affordability_ratio"])
ax2.set_xlabel("State")
ax2.set_ylabel("Affordability Ratio")
ax2.set_title("Affordability Ratio by State")
ax2.tick_params(axis="x", rotation=90)

st.pyplot(fig2)

st.subheader("Insights")

highest_rent = filtered.loc[filtered["avg_rent_2br"].idxmax()]
highest_hpi = filtered.loc[filtered["avg_hpi"].idxmax()]
highest_affordability = filtered.loc[filtered["affordability_ratio"].idxmax()]

st.write(f"Highest average 2BR rent: {highest_rent['state']} (${highest_rent['avg_rent_2br']:,.2f})")
st.write(f"Highest housing price index: {highest_hpi['state']} ({highest_hpi['avg_hpi']:.2f})")
st.write(f"Highest affordability ratio: {highest_affordability['state']} ({highest_affordability['affordability_ratio']:.2f})")

st.write(
    "This dashboard compares average 2-bedroom rent and housing price index across states. "
    "The scatter plot shows the relationship between rent and HPI, while the affordability ratio gives another way to compare housing pressure by state."
)
