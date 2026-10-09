#!/usr/bin/env python3
"""Generate a synthetic data/metabase_report.csv for local testing.

Mimics the Metabase question "Monthly Hypertension Patient-Days by Drug Class
for top 5 UHC facilities": one row per month and facility, one
'Hypertension: <drug class>' column per drug class, values in patient-days.
The numbers are fake; use a real Metabase export for anything meaningful.
"""
import os
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))        # scripts/
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')              # data/
RAW_CSV  = os.path.join(DATA_DIR, 'metabase_report.csv')

MONTHS = 36                 # >= 2 years so Prophet fits yearly seasonality
END_MONTH = '2026-09-01'    # last full month of history

# facility: (patients on treatment at start, monthly growth rate)
FACILITIES = {
    'UHC Sreepur':    (1800, 0.025),
    'UHC Kaliganj':   (1400, 0.030),
    'UHC Shibganj':   (2200, 0.015),
    'UHC Mirsharai':  (1100, 0.040),
    'UHC Nabiganj':   (900,  0.035),
}

# drug class: share of patients on it
DRUG_CLASSES = {
    'CCB':      0.75,   # amlodipine, first-line
    'ARB':      0.40,   # losartan, step-up
    'Diuretic': 0.15,   # hydrochlorothiazide
}

DAYS_COVERED = 24           # average days per month a patient has medication


def main():
    rng = np.random.default_rng(42)
    months = pd.date_range(end=END_MONTH, periods=MONTHS, freq='MS')

    rows = []
    for facility, (start_patients, growth) in FACILITIES.items():
        for i, month in enumerate(months):
            patients = start_patients * (1 + growth) ** i
            # Mild yearly dip around the monsoon months (Jun-Sep)
            season = 1 - 0.08 * np.sin(np.pi * (month.month - 5) / 5) if 5 <= month.month <= 10 else 1
            row = {'month_date': month.strftime('%Y-%m-%d'), 'facility': facility}
            for drug, share in DRUG_CLASSES.items():
                noise = rng.normal(1, 0.05)
                row[f'Hypertension: {drug}'] = int(patients * share * DAYS_COVERED * season * noise)
            rows.append(row)

    os.makedirs(DATA_DIR, exist_ok=True)
    pd.DataFrame(rows).to_csv(RAW_CSV, index=False)
    print(f"Saved {len(rows)} rows ({len(FACILITIES)} facilities x {MONTHS} months) to {RAW_CSV}")


if __name__ == '__main__':
    main()
