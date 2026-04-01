import os
from pathlib import Path

import fastf1
import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# CONFIG
# -----------------------------
YEAR = 2024
GRAND_PRIX = "Miami Grand Prix"   # change this later if you want
SESSION_TYPE = "R"                 # Race session

st.set_page_config(
    page_title="F1 Driver Performance Dashboard",
    page_icon="🏎️",
    layout="wide"
)

# -----------------------------
# FASTF1 CACHE
# -----------------------------
cache_dir = Path("./f1_cache")
cache_dir.mkdir(exist_ok=True)
fastf1.Cache.enable_cache(str(cache_dir))


# -----------------------------
# HELPERS
# -----------------------------
def td_to_seconds(value):
    if pd.isna(value):
        return None
    return value.total_seconds()


@st.cache_data(show_spinner=False)
def load_race_data(year: int, gp: str, session_type: str):
    session = fastf1.get_session(year, gp, session_type)

    # lighter load for a quick dashboard
    session.load(laps=True, telemetry=False, weather=False, messages=False)

    results = session.results.copy()
    laps = session.laps.copy()

    # clean results
    results = results.reset_index(drop=False)
    if "index" in results.columns and "DriverNumber" not in results.columns:
        results = results.rename(columns={"index": "DriverNumber"})

    # add seconds columns for plotting
    laps["LapTimeSeconds"] = laps["LapTime"].apply(td_to_seconds)
    laps["Sector1Seconds"] = laps["Sector1Time"].apply(td_to_seconds)
    laps["Sector2Seconds"] = laps["Sector2Time"].apply(td_to_seconds)
    laps["Sector3Seconds"] = laps["Sector3Time"].apply(td_to_seconds)

    # keep only useful laps with valid lap time
    valid_laps = laps[laps["LapTimeSeconds"].notna()].copy()

    return {
        "event_name": session.event["EventName"],
        "event_date": session.event["EventDate"],
        "results": results,
        "laps": valid_laps
    }


def get_driver_row(results_df: pd.DataFrame, driver_code: str):
    row = results_df[results_df["Abbreviation"] == driver_code]
    if row.empty:
        return None
    return row.iloc[0]


def format_pos(value):
    if pd.isna(value):
        return "N/A"
    try:
        return str(int(value))
    except Exception:
        return str(value)


# -----------------------------
# LOAD DATA
# -----------------------------
st.title("🏎️ F1 Driver Performance Dashboard")

data = load_race_data(YEAR, GRAND_PRIX, SESSION_TYPE)
results_df = data["results"]
laps_df = data["laps"]

st.subheader(f"{data['event_name']} ({YEAR})")
st.write(f"Session: {SESSION_TYPE}")
st.write(f"Date: {data['event_date'].strftime('%Y-%m-%d')}")

# -----------------------------
# SIDEBAR
# -----------------------------
driver_options = sorted(results_df["Abbreviation"].dropna().unique().tolist())
selected_driver = st.sidebar.selectbox("Select a driver", driver_options)

driver_row = get_driver_row(results_df, selected_driver)
driver_laps = laps_df[laps_df["Driver"] == selected_driver].copy()

# driver_laps = driver_laps[driver_laps["LapNumber"] > 1]   

if driver_row is None or driver_laps.empty:
    st.error("No data found for the selected driver.")
    st.stop()

# -----------------------------
# DRIVER INFO
# -----------------------------
driver_name = driver_row["FullName"]
team_name = driver_row["TeamName"]
finish_pos = driver_row.get("Position", None)
grid_pos = driver_row.get("GridPosition", None)
points = driver_row.get("Points", None)
status = driver_row.get("Status", "N/A")
laps_completed = driver_row.get("Laps", None)

position_change = None
if pd.notna(finish_pos) and pd.notna(grid_pos):
    position_change = int(grid_pos - finish_pos)

fastest_lap = driver_laps.loc[driver_laps["LapTimeSeconds"].idxmin()]
avg_lap = driver_laps["LapTimeSeconds"].mean()

# -----------------------------
# HEADER
# -----------------------------
st.markdown(f"## {driver_name}")

# -----------------------------
# KPIs
# -----------------------------
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Finish Position", format_pos(finish_pos))
c2.metric("Grid Position", format_pos(grid_pos))
c3.metric("Position Change", "N/A" if position_change is None else f"{position_change:+d}")
c4.metric("Points", "N/A" if pd.isna(points) else f"{points:.0f}")
c5.metric("Laps Completed", "N/A" if pd.isna(laps_completed) else f"{int(laps_completed)}")

c6, c7, c8 = st.columns(3)
c6.metric("Fastest Lap", f"{fastest_lap['LapTimeSeconds']:.3f}s")
c7.metric("Average Lap", f"{avg_lap:.3f}s")
c8.metric("Status", str(status))

st.divider()

# -----------------------------
# CHART 1: LAP TIMES
# -----------------------------
lap_fig = px.line(
    driver_laps,
    x="LapNumber",
    y="LapTimeSeconds",
    markers=True,
    title=f"{selected_driver} Lap Times by Lap"
)
lap_fig.update_layout(
    xaxis_title="Lap Number",
    yaxis_title="Lap Time (seconds)"
)
st.plotly_chart(lap_fig, use_container_width=True)

# -----------------------------
# CHART 2: FASTEST LAP SECTORS
# -----------------------------
fastest_sector_df = pd.DataFrame({
    "Sector": ["Sector 1", "Sector 2", "Sector 3"],
    "Seconds": [
        fastest_lap["Sector1Seconds"],
        fastest_lap["Sector2Seconds"],
        fastest_lap["Sector3Seconds"]
    ]
})

sector_fig = px.bar(
    fastest_sector_df,
    x="Sector",
    y="Seconds",
    title=f"{selected_driver} Fastest Lap Sector Breakdown (Lap {int(fastest_lap['LapNumber'])})"
)
sector_fig.update_layout(yaxis_title="Seconds")
st.plotly_chart(sector_fig, use_container_width=True)

# -----------------------------
# CHART 3: TIRE / STINT VIEW
# -----------------------------
tire_cols = ["LapNumber", "Compound", "TyreLife"]
available_tire_cols = [col for col in tire_cols if col in driver_laps.columns]

if "Compound" in driver_laps.columns:
    tire_df = driver_laps[available_tire_cols].copy()

    tire_fig = px.scatter(
        tire_df,
        x="LapNumber",
        y="TyreLife" if "TyreLife" in tire_df.columns else "LapNumber",
        color="Compound",
        title=f"{selected_driver} Tire Usage by Lap"
    )
    tire_fig.update_layout(
        xaxis_title="Lap Number",
        yaxis_title="Tyre Life" if "TyreLife" in tire_df.columns else "Lap Number"
    )
    st.plotly_chart(tire_fig, use_container_width=True)

# -----------------------------
# CHART 4: DRIVER VS FIELD AVG
# -----------------------------
field_avg = laps_df.groupby("LapNumber", as_index=False)["LapTimeSeconds"].mean()
field_avg = field_avg.rename(columns={"LapTimeSeconds": "FieldAverageSeconds"})

compare_df = driver_laps[["LapNumber", "LapTimeSeconds"]].merge(
    field_avg, on="LapNumber", how="left"
)

compare_long = compare_df.melt(
    id_vars="LapNumber",
    value_vars=["LapTimeSeconds", "FieldAverageSeconds"],
    var_name="Series",
    value_name="Seconds"
)

compare_long["Series"] = compare_long["Series"].replace({
    "LapTimeSeconds": selected_driver,
    "FieldAverageSeconds": "Field Average"
})

compare_fig = px.line(
    compare_long,
    x="LapNumber",
    y="Seconds",
    color="Series",
    title=f"{selected_driver} vs Field Average Lap Time"
)
compare_fig.update_layout(
    xaxis_title="Lap Number",
    yaxis_title="Lap Time (seconds)"
)
st.plotly_chart(compare_fig, use_container_width=True)

# -----------------------------
# SUMMARY TABLE
# -----------------------------
st.subheader("Driver Race Summary")

summary_df = pd.DataFrame({
    "Metric": [
        "Full Name",
        "Team",
        "Grid Position",
        "Finish Position",
        "Position Change",
        "Points",
        "Status",
        "Fastest Lap Number",
        "Fastest Lap Time",
        "Average Lap Time"
    ],
    "Value": [
        driver_name,
        team_name,
        format_pos(grid_pos),
        format_pos(finish_pos),
        "N/A" if position_change is None else f"{position_change:+d}",
        "N/A" if pd.isna(points) else f"{points:.0f}",
        str(status),
        int(fastest_lap["LapNumber"]),
        f"{fastest_lap['LapTimeSeconds']:.3f}s",
        f"{avg_lap:.3f}s"
    ]
})

st.dataframe(summary_df, use_container_width=True, hide_index=True)