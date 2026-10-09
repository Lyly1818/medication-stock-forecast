#!/usr/bin/env python3
import os
import numpy as np
import pandas as pd
from prophet import Prophet

# 1. Define project paths
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))          # scripts/
OUTPUT_DIR  = os.path.abspath(os.path.join(BASE_DIR, '..', 'outputs'))
INPUT_CSV   = os.path.join(OUTPUT_DIR, 'prophet_input.csv')    # adjust name if needed
FORECAST_CSV = os.path.join(OUTPUT_DIR, 'forecast_results_12mo.csv')

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 2. Load the prepared input data
df = pd.read_csv(INPUT_CSV, parse_dates=['ds'])

results = []

# 3. Loop over each facility + drug_class and forecast
for (facility, drug), group in df.groupby(['facility', 'drug_class']):
    # Fit in log space: Prophet's linear trend then models compound (%) growth,
    # and seasonality becomes multiplicative. log1p keeps zero months valid.
    # A stiffer trend (default 0.05) stops a few noisy recent months from being
    # extrapolated, which log space would compound over the 12-month horizon.
    model = Prophet(changepoint_prior_scale=0.01)
    model.fit(group[['ds','y']].assign(y=np.log1p(group['y'])))
    
    # Forecast 12 months ahead
    future = model.make_future_dataframe(periods=12, freq='MS')
    forecast = model.predict(future)
    
    last_date = group['ds'].max()
    future_preds = forecast[forecast['ds'] > last_date]
    
    for _, row in future_preds.iterrows():
        results.append({
            'ds':         row['ds'],
            'facility':   facility,
            'drug_class': drug,
            'yhat':       int(round(np.expm1(row['yhat'])))
        })

# 4. Assemble, sort, and write out
out_df = pd.DataFrame(results)
out_df = out_df.sort_values(['ds','facility'])
out_df.to_csv(FORECAST_CSV, index=False)

print(f"Saved integer-only 12-month forecasts to {FORECAST_CSV}")

long_df = pd.read_csv(FORECAST_CSV, parse_dates=['ds'])
pivot_df = (
    long_df
    .pivot(index=['ds', 'facility'], columns='drug_class', values='yhat')
    .reset_index()
)

PIVOT_CSV = os.path.join(OUTPUT_DIR, 'forecast_results_pivot.csv')
pivot_df.to_csv(PIVOT_CSV, index=False)
print(f"Saved pivoted forecasts to {PIVOT_CSV}")
