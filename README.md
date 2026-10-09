
# medication-stock-forecast

**End-to-end pipeline for forecasting medication stock needs at healthcare facilities using time-series AI.**

Initially focused on hypertension; easily extendable to diabetes and other therapies.

## Repository Structure

```
medication-stock-forecast/
├── data/
│   └── metabase_report.csv         # Raw Metabase export (git-ignored)
├── scripts/
│   ├── generate_sample_data.py     # Writes a synthetic metabase_report.csv for testing
│   ├── prepare_prophet_input.py    # Transforms raw CSV → prophet_input.csv
│   ├── run_forecasts.py            # Fits Prophet and writes forecast CSVs
│   └── evaluate_forecasts.py       # Scores forecasts against outputs/actuals.csv
├── outputs/                        
│   ├── prophet_input.csv           # Model-ready data (git-ignored)
│   ├── forecast_results_12mo.csv   # Raw forecasts (git-ignored)
│   └── forecast_results_pivot.csv  # Pivoted forecasts (git-ignored)
├── .gitignore                      
├── requirements.txt                # Python dependencies
└── README.md                       # Project overview and instructions
```

## Setup

1. **Clone the repository**  
   ```bash
   git clone <repo-url>
   cd medication-stock-forecast
   ```

2. **Create and activate a virtual environment** (tested with Python 3.11)  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Usage

1. **Export data from Metabase**  
   - Open this question in Metabase:  
     [Monthly Hypertension Patient-Days by Drug Class for top 5 uhc facilities](https://metabase.bd.simple.org/question/1049-monthly-hypertension-patient-days-by-drug-class-for-top-5-uhc-facilities-24-12-months-ago)  
   - Click **Export → CSV** → save as `data/metabase_report.csv`

   **No Metabase access?** Generate synthetic data instead:
   ```bash
   python3 scripts/generate_sample_data.py
   ```
   - Writes `data/metabase_report.csv` with 36 months of fake patient-days for 5 facilities and 3 drug classes (fixed seed, so results are repeatable)
   - Use it to test the pipeline, not for real stock decisions

2. **Prepare data for Prophet**  
   ```bash
   python3 scripts/prepare_prophet_input.py
   ```
   - Reads `data/metabase_report.csv`  
   - Writes `outputs/prophet_input.csv`.

3. **Run forecasts**  
   ```bash
   python3 scripts/run_forecasts.py
   ```
   - Reads `outputs/prophet_input.csv`  
   - Fits one Prophet model per facility and drug class on `log(1 + y)`, so the trend models percentage growth  
   - Writes `outputs/forecast_results_12mo.csv` (long)  
   - Writes `outputs/forecast_results_pivot.csv` (wide)

4. **Inspect outputs**  
   - `outputs/forecast_results_pivot.csv` has one row per month & facility, columns for each drug class forecast.

## Extending

- To support diabetes or other conditions, update the Metabase query and adjust the `class_cols` pattern in `prepare_prophet_input.py`.
