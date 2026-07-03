import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

DATA_PATH = "powerconsumption.csv"

st.set_page_config(
    page_title="Smart Energy Consumption Insights",
    page_icon="⚡",
    layout="wide",
)

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["Datetime"])
    df.sort_values("Datetime", inplace=True)
    df["Date"] = df["Datetime"].dt.date
    df["Hour"] = df["Datetime"].dt.hour
    df["DayOfWeek"] = df["Datetime"].dt.day_name()
    df["Month"] = df["Datetime"].dt.month_name()
    df["TotalPower"] = df[
        ["PowerConsumption_Zone1", "PowerConsumption_Zone2", "PowerConsumption_Zone3"]
    ].sum(axis=1)
    return df

@st.cache_data
def aggregate_data(df: pd.DataFrame, period: str) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if period == "Hourly":
        freq = "h"
    elif period == "Daily":
        freq = "d"
    elif period == "Weekly":
        freq = "w"
    elif period == "Monthly":
        freq = "ME"
    else:
        return df

    grouped = (
        df.resample(freq, on="Datetime")[numeric_cols]
        .mean()
        .reset_index()
    )
    return grouped

@st.cache_data
def to_long(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    return df.melt(
        id_vars=["Datetime"],
        value_vars=columns,
        var_name="Series",
        value_name="Value",
    )

st.title("Smart Energy Consumption Insights")
st.write(
    "Explore power consumption, weather patterns, and energy demand trends in the dataset. "
    "Use the filters to compare zones, time ranges, and aggregated trends."
)

try:
    data = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find {DATA_PATH}. Please place the `powerconsumption.csv` file in the same folder as this app."
    )
    st.stop()

min_date = data["Date"].min()
max_date = data["Date"].max()

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input("Date range", [min_date, max_date], min_value=min_date, max_value=max_date)
    available_zones = ["PowerConsumption_Zone1", "PowerConsumption_Zone2", "PowerConsumption_Zone3", "TotalPower"]
    selected_zones = st.multiselect("Power zones", available_zones, default=["PowerConsumption_Zone1", "PowerConsumption_Zone2", "PowerConsumption_Zone3"])
    aggregation = st.selectbox("Aggregation", ["None", "Hourly", "Daily", "Weekly", "Monthly"], index=1)
    show_correlations = st.checkbox("Show correlation matrix", value=True)
    show_table = st.checkbox("Show raw sample table", value=False)
    st.markdown("---")
    st.markdown("#### Quick view settings")
    hour_filter = st.slider("Hour of day", 0, 23, (0, 23))
    dayofweek_filter = st.multiselect("Day of week", data["DayOfWeek"].unique(), default=list(data["DayOfWeek"].unique()))

start_date, end_date = date_range if len(date_range) == 2 else (date_range[0], date_range[0])

filtered = data[
    (data["Date"] >= start_date)
    & (data["Date"] <= end_date)
    & (data["Hour"] >= hour_filter[0])
    & (data["Hour"] <= hour_filter[1])
    & (data["DayOfWeek"].isin(dayofweek_filter))
].copy()

if filtered.empty:
    st.warning("No data matches the selected filters. Please widen the date range or remove a filter.")
    st.stop()

aggregated = aggregate_data(filtered, aggregation)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Temperature (°C)", f"{filtered['Temperature'].mean():.2f}")
col2.metric("Average Humidity (%)", f"{filtered['Humidity'].mean():.2f}")
col3.metric("Average Total Consumption", f"{filtered['TotalPower'].mean():,.0f}")
peak_time = filtered.loc[filtered["TotalPower"].idxmax(), "Datetime"]
col4.metric("Peak Total Consumption", f"{filtered['TotalPower'].max():,.0f}", f"at {peak_time:%Y-%m-%d %H:%M}")

st.subheader("Power Consumption Over Time")
selected = [col for col in selected_zones if col in filtered.columns]
if not selected:
    st.warning("Select at least one zone to show the time series chart.")
else:
    long_df = to_long(aggregated if aggregation != "None" else filtered, selected)
    if long_df["Datetime"].nunique() <= 1:
        chart = (
            alt.Chart(long_df)
            .mark_point(size=120, filled=True)
            .encode(
                x="Datetime:T",
                y="Value:Q",
                color="Series:N",
                tooltip=["Datetime:T", "Series:N", "Value:Q"],
            )
            .interactive()
        )
    else:
        chart = (
            alt.Chart(long_df)
            .mark_line(point=True)
            .encode(
                x="Datetime:T",
                y="Value:Q",
                color="Series:N",
                tooltip=["Datetime:T", "Series:N", "Value:Q"],
            )
            .interactive()
        )
    st.altair_chart(chart, use_container_width=True)

with st.expander("Weather and Energy Distributions"):
    hist_cols = ["Temperature", "Humidity", "WindSpeed", "TotalPower"]
    for feature in hist_cols:
        chart = alt.Chart(filtered).mark_area(opacity=0.35).encode(
            alt.X(f"{feature}:Q", bin=alt.Bin(maxbins=40)),
            y="count():Q",
        )
        st.write(f"**{feature} distribution**")
        st.altair_chart(chart, use_container_width=True)

if show_correlations:
    st.subheader("Correlation Matrix")
    corr = filtered[["Temperature", "Humidity", "WindSpeed", "PowerConsumption_Zone1", "PowerConsumption_Zone2", "PowerConsumption_Zone3", "TotalPower"]].corr()
    st.dataframe(corr.style.background_gradient(cmap="RdYlGn", axis=None), use_container_width=True)

if show_table:
    st.subheader("Sample Data")
    st.dataframe(filtered.head(200), use_container_width=True)

st.markdown("---")
st.write("### Summary Insights")
st.write(
    "- The dataset includes energy consumption from three power zones plus temperature, humidity, and wind speed. "
    "- Use the date and hour filters to isolate high-demand periods or compare weather effects across time."
)

st.write(
    "- Aggregating by day or week reveals longer trends, while hourly aggregation highlights daily demand cycles. "
    "- The correlation matrix helps spot whether temperature or humidity is associated with higher zone consumption."
)
