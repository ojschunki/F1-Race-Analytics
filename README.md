# F1 Driver Dashboard 🏎️📊
> As part of the ***2026 Monthly Personal Projects**  /  March 3 of 12*

Interactive dashboard for exploring Formula 1 driver performance within a single race. This project focuses on transforming raw race data into clear, visual insights using an interactive web application.

---

## Project Objective

The goal of this project is to:
- Load and process Formula 1 race data using a Python-based data pipeline
- Analyze driver performance within a single race context
- Visualize lap times, sector performance, and race outcomes
- Build an interactive dashboard for dynamic exploration of driver statistics

This project emphasizes **data processing, visualization, and interactivity**, rather than predictive modeling.

---

## Dataset

**Source:**  
Race session data retrieved using the :contentReference[oaicite:0]{index=0} library  

**Race:**  
Miami Grand Prix (2024 Season)

**Notes**
- Data includes lap times, sector times, tire compounds, and race results
- Some laps (e.g., opening laps, pit laps) may contain outliers and are filtered for visualization clarity
- Data is cached locally for faster repeated access

---

## Approach

### 1) Data Loading
- Retrieved race session data using FastF1
- Enabled local caching to improve performance
- Loaded lap-level and race result data

### 2) Data Cleaning
- Converted lap times and sector times into numeric format (seconds)
- Filtered out invalid or extreme lap times for visualization
- Handled missing values and ensured consistency across datasets

### 3) Feature Engineering
- Computed:
  - Average lap time
  - Fastest lap time
  - Sector-level performance
  - Position change (grid → finish)
- Created derived metrics for comparison against field averages

### 4) Visualization & Dashboard
Built an interactive dashboard using :contentReference[oaicite:1]{index=1} with:
- Driver selection dropdown
- KPI summary cards (position, points, lap stats)
- Lap time trends across the race
- Fastest lap sector breakdown
- Tire usage visualization
- Driver vs field average comparison

---

## Key Insights

- Lap time consistency provides a clearer indicator of performance than a single fastest lap
- Position changes highlight racecraft beyond qualifying performance
- Sector-level breakdowns reveal where time is gained or lost
- Tire strategy and stint length impact lap time variability

---

## How to Run

1. Clone the repository:
```bash
git clone <your-repo-link>
cd F1-Driver-Dashboard
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Run the application:
```bash
python -m streamlit run app.py
```
4. Open the provided local URL in your browser

## Summary

This project demonstrates how raw motorsport data can be transformed into an interactive analytical tool. By combining data processing with intuitive visualizations, the dashboard enables quick exploration of driver performance and race dynamics.