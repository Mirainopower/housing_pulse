import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.title("Housing Data App")
# -------------------------
# Load data
# -------------------------
fmr = pd.read_excel("FY26_FMRs.xlsx")
hpi = pd.read_excel("hpi_po_state.xlsx")

# -------------------------
# Clean column names
# -------------------------
fmr.columns = fmr.columns.str.strip()
hpi.columns = hpi.columns.str.strip()

# -------------------------
# Clean needed columns
# -------------------------
fmr["stusps"] = fmr["stusps"].astype(str).str.strip()
hpi["state"] = hpi["state"].astype(str).str.strip()

fmr["fmr_2"] = pd.to_numeric(fmr["fmr_2"], errors="coerce")
hpi["index_nsa"] = pd.to_numeric(hpi["index_nsa"], errors="coerce")

# -------------------------
# Keep only needed columns
# -------------------------
rent_data = fmr[["stusps", "fmr_2"]].dropna()
price_data = hpi[["state", "index_nsa"]].dropna()

# -------------------------
# Average by state
# -------------------------
rent_by_state = (
    rent_data.groupby("stusps", as_index=False)["fmr_2"]
    .mean()
    .rename(columns={"stusps": "state", "fmr_2": "avg_rent_2br"})
)

price_by_state = (
    price_data.groupby("state", as_index=False)["index_nsa"]
    .mean()
    .rename(columns={"index_nsa": "avg_hpi"})
)

# -------------------------
# Merge data
# -------------------------
merged = pd.merge(rent_by_state, price_by_state, on="state", how="inner")

# -------------------------
# Show merged table
# -------------------------
st.write("Merged Data:")
st.dataframe(merged.head(20))

# -------------------------
# Scatter plot
# -------------------------
plt.figure(figsize=(10, 6))
plt.scatter(merged["avg_hpi"], merged["avg_rent_2br"])

for i, row in merged.iterrows():
    plt.text(row["avg_hpi"], row["avg_rent_2br"], row["state"], fontsize=8)

plt.xlabel("Average Housing Price Index (index_nsa)")
plt.ylabel("Average 2-Bedroom Rent (fmr_2)")
plt.title("Relationship Between Housing Prices and Rent by State")
plt.grid(True)
st.pyplot(plt)
