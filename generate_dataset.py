"""
generate_dataset.py
Generates an authentic agronomic dataset for CROPWISE AI based on ICAR, TNAU and FAO benchmark standards.
Features: Soil_Type, pH, Temperature, Humidity, Rainfall -> Crop
"""

# =============================================================================
# CROPWISE AI - Agricultural Dataset Generation Pipeline
# =============================================================================
# Generates realistic synthetic soil and weather training data based on ICAR,
# TNAU, and FAO benchmark guidelines for major Indian and Tamil Nadu crops:
# - Models soil distribution weights (Clayey, Loamy, Sandy, Alluvial, Red, Black).
# - Synthesizes realistic Gaussian distributions for pH, Temperature, Humidity, and Rainfall.
# - Outputs clean, balanced crop_data.csv for training the Decision Tree Classifier.
# =============================================================================

import numpy as np
import pandas as pd

import numpy as np
import pandas as pd

# Distinctive agronomic profiles based on ICAR / TNAU agro-climatic zones
crop_profiles = {
    "Paddy": {
        "soils": ["Clayey", "Alluvial", "Clayey"],
        "soil_weights": [0.60, 0.35, 0.05],
        "ph_mean": 6.4, "ph_std": 0.30, "ph_min": 5.5, "ph_max": 7.4,
        "temp_mean": 27.5, "temp_std": 2.0, "temp_min": 22.0, "temp_max": 34.0,
        "hum_mean": 82.0, "hum_std": 3.5, "hum_min": 72.0, "hum_max": 95.0,
        "rain_mean": 1650.0, "rain_std": 140.0, "rain_min": 1300.0, "rain_max": 2200.0,
        "samples": 220
    },
    "Wheat": {
        "soils": ["Loamy", "Alluvial", "Clayey"],
        "soil_weights": [0.55, 0.35, 0.10],
        "ph_mean": 6.8, "ph_std": 0.30, "ph_min": 6.0, "ph_max": 7.8,
        "temp_mean": 17.5, "temp_std": 1.8, "temp_min": 11.0, "temp_max": 22.5,
        "hum_mean": 48.0, "hum_std": 4.0, "hum_min": 35.0, "hum_max": 60.0,
        "rain_mean": 520.0, "rain_std": 60.0, "rain_min": 350.0, "rain_max": 700.0,
        "samples": 200
    },
    "Maize": {
        "soils": ["Loamy", "Red", "Alluvial"],
        "soil_weights": [0.50, 0.35, 0.15],
        "ph_mean": 6.5, "ph_std": 0.30, "ph_min": 5.8, "ph_max": 7.3,
        "temp_mean": 25.0, "temp_std": 2.0, "temp_min": 20.0, "temp_max": 31.0,
        "hum_mean": 65.0, "hum_std": 4.0, "hum_min": 52.0, "hum_max": 76.0,
        "rain_mean": 750.0, "rain_std": 70.0, "rain_min": 550.0, "rain_max": 950.0,
        "samples": 210
    },
    "Cotton": {
        "soils": ["Black", "Alluvial"],
        "soil_weights": [0.80, 0.20],
        "ph_mean": 7.5, "ph_std": 0.30, "ph_min": 6.8, "ph_max": 8.3,
        "temp_mean": 29.0, "temp_std": 2.0, "temp_min": 23.0, "temp_max": 36.0,
        "hum_mean": 58.0, "hum_std": 4.5, "hum_min": 45.0, "hum_max": 70.0,
        "rain_mean": 820.0, "rain_std": 80.0, "rain_min": 600.0, "rain_max": 1050.0,
        "samples": 210
    },
    "Sugarcane": {
        "soils": ["Clayey", "Loamy", "Alluvial"],
        "soil_weights": [0.45, 0.35, 0.20],
        "ph_mean": 7.1, "ph_std": 0.35, "ph_min": 6.2, "ph_max": 8.0,
        "temp_mean": 31.5, "temp_std": 2.2, "temp_min": 25.0, "temp_max": 38.0,
        "hum_mean": 74.0, "hum_std": 4.0, "hum_min": 62.0, "hum_max": 86.0,
        "rain_mean": 1350.0, "rain_std": 120.0, "rain_min": 1050.0, "rain_max": 1750.0,
        "samples": 210
    },
    "Groundnut": {
        "soils": ["Sandy", "Red"],
        "soil_weights": [0.65, 0.35],
        "ph_mean": 6.4, "ph_std": 0.30, "ph_min": 5.6, "ph_max": 7.4,
        "temp_mean": 26.5, "temp_std": 2.0, "temp_min": 21.0, "temp_max": 32.0,
        "hum_mean": 55.0, "hum_std": 4.0, "hum_min": 42.0, "hum_max": 68.0,
        "rain_mean": 580.0, "rain_std": 60.0, "rain_min": 420.0, "rain_max": 750.0,
        "samples": 210
    },
    "Black Gram": {
        "soils": ["Loamy", "Clayey", "Black"],
        "soil_weights": [0.45, 0.35, 0.20],
        "ph_mean": 7.0, "ph_std": 0.30, "ph_min": 6.2, "ph_max": 7.8,
        "temp_mean": 29.5, "temp_std": 2.0, "temp_min": 24.0, "temp_max": 35.0,
        "hum_mean": 52.0, "hum_std": 4.5, "hum_min": 40.0, "hum_max": 65.0,
        "rain_mean": 480.0, "rain_std": 50.0, "rain_min": 350.0, "rain_max": 640.0,
        "samples": 200
    },
    "Chickpea": {
        "soils": ["Black", "Loamy"],
        "soil_weights": [0.70, 0.30],
        "ph_mean": 7.3, "ph_std": 0.30, "ph_min": 6.5, "ph_max": 8.1,
        "temp_mean": 19.5, "temp_std": 1.8, "temp_min": 14.0, "temp_max": 24.5,
        "hum_mean": 42.0, "hum_std": 4.0, "hum_min": 30.0, "hum_max": 54.0,
        "rain_mean": 380.0, "rain_std": 45.0, "rain_min": 260.0, "rain_max": 500.0,
        "samples": 200
    },
    "Millets": {
        "soils": ["Red", "Sandy", "Laterite"],
        "soil_weights": [0.60, 0.30, 0.10],
        "ph_mean": 6.0, "ph_std": 0.35, "ph_min": 5.1, "ph_max": 7.2,
        "temp_mean": 27.5, "temp_std": 2.2, "temp_min": 21.0, "temp_max": 35.0,
        "hum_mean": 44.0, "hum_std": 4.5, "hum_min": 32.0, "hum_max": 58.0,
        "rain_mean": 420.0, "rain_std": 50.0, "rain_min": 280.0, "rain_max": 600.0,
        "samples": 200
    },
    "Banana": {
        "soils": ["Loamy", "Alluvial", "Clayey"],
        "soil_weights": [0.50, 0.35, 0.15],
        "ph_mean": 6.6, "ph_std": 0.28, "ph_min": 5.9, "ph_max": 7.5,
        "temp_mean": 29.0, "temp_std": 2.0, "temp_min": 23.0, "temp_max": 35.0,
        "hum_mean": 80.0, "hum_std": 3.5, "hum_min": 70.0, "hum_max": 92.0,
        "rain_mean": 1420.0, "rain_std": 100.0, "rain_min": 1150.0, "rain_max": 1800.0,
        "samples": 200
    },
    "Coconut": {
        "soils": ["Sandy", "Alluvial", "Red"],
        "soil_weights": [0.55, 0.30, 0.15],
        "ph_mean": 6.5, "ph_std": 0.35, "ph_min": 5.6, "ph_max": 7.8,
        "temp_mean": 28.5, "temp_std": 2.0, "temp_min": 23.0, "temp_max": 34.5,
        "hum_mean": 75.0, "hum_std": 4.0, "hum_min": 65.0, "hum_max": 88.0,
        "rain_mean": 1780.0, "rain_std": 130.0, "rain_min": 1400.0, "rain_max": 2300.0,
        "samples": 200
    },
    "Coffee": {
        "soils": ["Laterite", "Red", "Loamy"],
        "soil_weights": [0.65, 0.25, 0.10],
        "ph_mean": 5.7, "ph_std": 0.25, "ph_min": 5.0, "ph_max": 6.4,
        "temp_mean": 21.0, "temp_std": 1.8, "temp_min": 16.0, "temp_max": 26.0,
        "hum_mean": 76.0, "hum_std": 3.8, "hum_min": 66.0, "hum_max": 88.0,
        "rain_mean": 1750.0, "rain_std": 120.0, "rain_min": 1400.0, "rain_max": 2250.0,
        "samples": 190
    },
    "Tea": {
        "soils": ["Laterite", "Loamy"],
        "soil_weights": [0.80, 0.20],
        "ph_mean": 5.0, "ph_std": 0.22, "ph_min": 4.4, "ph_max": 5.6,
        "temp_mean": 18.0, "temp_std": 1.8, "temp_min": 13.0, "temp_max": 23.0,
        "hum_mean": 88.0, "hum_std": 3.0, "hum_min": 78.0, "hum_max": 96.0,
        "rain_mean": 2350.0, "rain_std": 150.0, "rain_min": 1850.0, "rain_max": 2900.0,
        "samples": 190
    },
    "Jute": {
        "soils": ["Alluvial", "Clayey"],
        "soil_weights": [0.70, 0.30],
        "ph_mean": 6.9, "ph_std": 0.28, "ph_min": 6.1, "ph_max": 7.6,
        "temp_mean": 32.0, "temp_std": 2.0, "temp_min": 26.0, "temp_max": 38.0,
        "hum_mean": 86.0, "hum_std": 3.2, "hum_min": 76.0, "hum_max": 95.0,
        "rain_mean": 1850.0, "rain_std": 120.0, "rain_min": 1500.0, "rain_max": 2300.0,
        "samples": 190
    }
}

np.random.seed(42)

rows = []
for crop, prof in crop_profiles.items():
    n = prof["samples"]
    soils = np.random.choice(prof["soils"], size=n, p=prof["soil_weights"])
    
    phs = np.clip(np.random.normal(prof["ph_mean"], prof["ph_std"], n), prof["ph_min"], prof["ph_max"])
    temps = np.clip(np.random.normal(prof["temp_mean"], prof["temp_std"], n), prof["temp_min"], prof["temp_max"])
    hums = np.clip(np.random.normal(prof["hum_mean"], prof["hum_std"], n), prof["hum_min"], prof["hum_max"])
    rains = np.clip(np.random.normal(prof["rain_mean"], prof["rain_std"], n), prof["rain_min"], prof["rain_max"])
    
    for i in range(n):
        rows.append({
            "Soil_Type": soils[i],
            "pH": round(float(phs[i]), 2),
            "Temperature": round(float(temps[i]), 1),
            "Humidity": round(float(hums[i]), 1),
            "Rainfall": round(float(rains[i]), 1),
            "Crop": crop
        })

df = pd.DataFrame(rows)
df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)
df.to_csv("crop_data.csv", index=False)
print(f"Generated crop_data.csv with {len(df)} samples across {df['Crop'].nunique()} crops and {df['Soil_Type'].nunique()} soil types.")
print(df.head(10))
