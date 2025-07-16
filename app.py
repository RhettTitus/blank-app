import streamlit as st
import pandas as pd
from scipy.stats import binom_test
import numpy as np
import subprocess

def bin_feature(series, bins, labels=None):
    return pd.cut(series, bins=bins, labels=labels)

def discover_trends(df, feature_cols, min_samples=20, significance_level=0.05):
    overall_rate = df['nrfi_occurred'].mean()
    trends = []

    for feature in feature_cols:
        if pd.api.types.is_numeric_dtype(df[feature]):
            bins = np.quantile(df[feature].dropna(), [0, 0.25, 0.5, 0.75, 1.0])
            df[f"{feature}_binned"] = bin_feature(df[feature], bins)
            categories = df[f"{feature}_binned"].dropna().unique()
            col_to_scan = f"{feature}_binned"
        else:
            categories = df[feature].dropna().unique()
            col_to_scan = feature

        for cat in categories:
            subset = df[df[col_to_scan] == cat]
            n = len(subset)
            k = subset['nrfi_occurred'].sum()
            if n < min_samples:
                continue
            rate = k / n
            p_val = binom_test(k, n, overall_rate, alternative='greater')

            if rate > overall_rate and p_val < significance_level:
                trends.append({
                    "Feature": feature,
                    "Category": str(cat),
                    "Sample Size": n,
                    "NRFI Rate": rate,
                    "Overall Rate": overall_rate,
                    "p-value": p_val
                })

    return pd.DataFrame(trends)

st.title("⚾ NRFI Trend Discovery + Model")

if st.button("🔄 Refresh Today's Data"):
    subprocess.run(["python", "main.py"])

try:
    df_history = pd.read_csv("output/historical_nrfi.csv")
except FileNotFoundError:
    st.warning("No historical data found.")
    st.stop()

features_to_scan = [
    "team", "opponent_team", "whip", "xba", "lineup_status", "home_or_away",
    "market_odds", "temp", "wind_speed", "top4_avg_vs_pitcher", "top4_obp_vs_pitcher"
]

for col in features_to_scan:
    if col not in df_history.columns:
        df_history[col] = np.nan

trends_df = discover_trends(df_history, features_to_scan)

if not trends_df.empty:
    st.subheader("📊 Discovered NRFI Trends")
    sort_col = st.selectbox("Sort by:", trends_df.columns, index=4)
    ascending = st.checkbox("Ascending?", value=True)
    feature_filter = st.multiselect("Filter by Feature:", options=trends_df['Feature'].unique(), default=trends_df['Feature'].unique())
    filtered_df = trends_df.sort_values(by=sort_col, ascending=ascending)
    if feature_filter:
        filtered_df = filtered_df[filtered_df['Feature'].isin(feature_filter)]
    st.dataframe(filtered_df.style.format({"NRFI Rate": "{:.1%}", "Overall Rate": "{:.1%}", "p-value": "{:.4f}"}))
else:
    st.info("No significant trends yet.")
