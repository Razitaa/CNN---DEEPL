# Data Guide

## Overview

This document describes the datasets used in the weather forecasting project, their structure, sources, and preprocessing steps.

## Dataset Files

### 1. weather_data_indonesia.csv

**Description**: Historical weather data from Indonesian meteorological stations.

**Source**: Indonesian Meteorological Agency (BMKG)

**Columns**:

- `date`: Date of observation (YYYY-MM-DD)
- `station_id`: Weather station identifier
- `location`: Station location name
- `province`: Province name
- `longitude`: Station longitude
- `latitude`: Station latitude
- `Tavg`: Average temperature (°C)
- `Tx`: Maximum temperature (°C)
- `Tn`: Minimum temperature (°C)
- `RH_avg`: Average relative humidity (%)
- `ss`: Sunshine hours
- `RR`: Rainfall (mm)
- `ff_x`: Maximum wind speed (m/s)
- `ddd_x`: Wind direction (degrees)

**Size**: ~500,000 records

**Time Period**: 2010-2023

### 2. weather_data_2020_2025.csv

**Description**: Recent weather observations with enhanced quality control.

**Columns**: Same as weather_data_indonesia.csv

**Size**: ~150,000 records

**Time Period**: 2020-2025

**Notes**:

- Higher data quality
- More frequent observations
- Used for model validation and recent predictions

### 3. solar_irradiance_complete_dataset.csv

**Description**: Solar radiation measurements with derived features.

**Columns**:

- `date`: Date of observation
- `station_id`: Weather station identifier
- `longitude`, `latitude`: Station coordinates
- `Tavg`, `Tx`, `Tn`: Temperature metrics
- `ss`: Sunshine hours
- `RH_avg`: Relative humidity
- `solar_radiation_MJ`: Solar radiation (MJ/m²/day)
- `cloud_cover_pct`: Cloud cover percentage (%)
- `sunshine_hours`: Actual sunshine duration (hours)

**Size**: ~300,000 records

**Time Period**: 2015-2025

**Calculation**:

```python
# Solar radiation estimation
solar_radiation_MJ = (sunshine_hours / max_sunshine_hours) * theoretical_radiation
```

### 4. climate_data.csv

**Description**: Long-term climate statistics per station.

**Columns**:

- `station_id`: Weather station identifier
- `avg_temp_annual`: Annual average temperature
- `avg_rainfall_annual`: Annual average rainfall
- `temp_variance`: Temperature variance
- `climate_zone`: Köppen climate classification

### 5. station_detail.csv

**Description**: Metadata for weather stations.

**Columns**:

- `station_id`: Unique station identifier
- `station_name`: Full station name
- `longitude`, `latitude`: Coordinates
- `elevation`: Elevation above sea level (m)
- `province`: Province name
- `region`: Region (Western, Central, Eastern Indonesia)
- `operational_since`: Start date of operations

### 6. province_detail.csv

**Description**: Provincial-level information.

**Columns**:

- `province_id`: Province identifier
- `province_name`: Province name
- `region`: Geographic region
- `num_stations`: Number of weather stations
- `avg_longitude`, `avg_latitude`: Average coordinates

## Data Quality

### Missing Values

**Handling Strategy**:

1. **Forward Fill**: For short gaps (<3 days)

```python
df.fillna(method='ffill', limit=3)
```

2. **Interpolation**: For medium gaps (3-7 days)

```python
df.interpolate(method='linear')
```

3. **Station Average**: For longer gaps

```python
df['Tavg'].fillna(df.groupby('station_id')['Tavg'].transform('mean'))
```

4. **Drop**: If >30% of record is missing

```python
df.dropna(thresh=len(df.columns) * 0.7)
```

### Outlier Detection

**Method**: Quantile-based filtering

```python
# Remove extreme outliers (1%-99% quantile)
Q1 = df['Tavg'].quantile(0.01)
Q99 = df['Tavg'].quantile(0.99)
df = df[(df['Tavg'] >= Q1) & (df['Tavg'] <= Q99)]
```

**Physical Constraints**:

- Temperature: -5°C to 45°C (Indonesia range)
- Humidity: 0% to 100%
- Sunshine hours: 0 to 14 hours
- Solar radiation: 0 to 35 MJ/m²/day

### Data Validation

```python
# Check for duplicate records
duplicates = df.duplicated(subset=['date', 'station_id'])

# Check for chronological order
df = df.sort_values(['station_id', 'date'])

# Check for temporal gaps
df['date_diff'] = df.groupby('station_id')['date'].diff()
gaps = df[df['date_diff'] > pd.Timedelta(days=1)]
```

## Feature Engineering

### Temporal Features

```python
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day_of_year'] = df['date'].dt.dayofyear
df['week_of_year'] = df['date'].dt.isocalendar().week
df['day_of_week'] = df['date'].dt.dayofweek

# Seasonal encoding
df['season'] = df['month'].map({
    12: 1, 1: 1, 2: 1,  # Wet season
    3: 2, 4: 2, 5: 2,   # Transition
    6: 3, 7: 3, 8: 3,   # Dry season
    9: 4, 10: 4, 11: 4  # Transition
})

# Cyclic encoding for month
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
```

### Spatial Features

```python
# Regional clustering based on longitude
def assign_region(longitude):
    if longitude < 110:
        return 'Barat'  # Western Indonesia
    elif longitude < 125:
        return 'Tengah'  # Central Indonesia
    else:
        return 'Timur'  # Eastern Indonesia

df['region_cluster'] = df['longitude'].apply(assign_region)

# Distance from equator (affects solar radiation)
df['abs_latitude'] = df['latitude'].abs()
```

### Derived Meteorological Features

```python
# Temperature range (diurnal variation)
df['temp_range'] = df['Tx'] - df['Tn']

# Temperature anomaly (deviation from average)
df['temp_anomaly'] = df.groupby('station_id')['Tavg'].transform(
    lambda x: x - x.rolling(30, min_periods=1).mean()
)

# Humidity deficit
df['humidity_deficit'] = 100 - df['RH_avg']

# Heat index (apparent temperature)
def calculate_heat_index(T, RH):
    if T < 27:
        return T
    HI = -8.78 + 1.61*T + 2.34*RH - 0.14*T*RH - 0.01*T**2 - 0.002*RH**2
    return HI

df['heat_index'] = df.apply(
    lambda row: calculate_heat_index(row['Tavg'], row['RH_avg']),
    axis=1
)

# Cloud cover from sunshine hours
df['cloud_cover_pct'] = (1 - df['ss'] / 12) * 100

# Solar radiation estimation
df['estimated_solar_radiation'] = (
    df['ss'] * 0.75  # Angstrom coefficient
    * (1 - 0.75 * df['cloud_cover_pct'] / 100)
)
```

### Lag Features

```python
# Previous days' values (7 and 14 day lags)
for lag in [1, 3, 7, 14]:
    df[f'Tavg_lag_{lag}'] = df.groupby('station_id')['Tavg'].shift(lag)
    df[f'solar_lag_{lag}'] = df.groupby('station_id')['solar_radiation_MJ'].shift(lag)

# Rolling statistics
df['Tavg_rolling_mean_7d'] = df.groupby('station_id')['Tavg'].transform(
    lambda x: x.rolling(7, min_periods=1).mean()
)
df['Tavg_rolling_std_7d'] = df.groupby('station_id')['Tavg'].transform(
    lambda x: x.rolling(7, min_periods=1).std()
)
```

## Data Preprocessing Pipeline

### Step 1: Loading

```python
import pandas as pd

df = pd.read_csv('data/raw/weather_data_indonesia.csv')
df['date'] = pd.to_datetime(df['date'])
```

### Step 2: Cleaning

```python
# Remove duplicates
df = df.drop_duplicates(subset=['date', 'station_id'])

# Remove outliers
for col in ['Tavg', 'Tx', 'Tn', 'RH_avg']:
    Q1 = df[col].quantile(0.01)
    Q99 = df[col].quantile(0.99)
    df = df[(df[col] >= Q1) & (df[col] <= Q99)]

# Handle missing values
df = df.sort_values(['station_id', 'date'])
df = df.groupby('station_id', group_keys=False).apply(
    lambda x: x.fillna(method='ffill').fillna(method='bfill')
)
df = df.dropna()
```

### Step 3: Feature Engineering

```python
# Add temporal features
df['month'] = df['date'].dt.month
df['day_of_year'] = df['date'].dt.dayofyear

# Add spatial features
df['region_cluster'] = df['longitude'].apply(assign_region)

# Add derived features
df['temp_range'] = df['Tx'] - df['Tn']
df['cloud_cover_pct'] = (1 - df['ss'] / 12) * 100
```

### Step 4: Sequence Creation

```python
def create_sequences(data, lookback=14, forecast=7):
    X, y = [], []
    for i in range(lookback, len(data) - forecast + 1):
        X.append(data[i-lookback:i])
        y.append(data[i:i+forecast, target_col])
    return np.array(X), np.array(y)

# Create sequences per station
sequences = []
for station_id in df['station_id'].unique():
    station_data = df[df['station_id'] == station_id].sort_values('date')
    if len(station_data) >= 21:  # 14 + 7
        X, y = create_sequences(station_data[feature_cols].values)
        sequences.append((X, y))
```

### Step 5: Normalization

```python
from sklearn.preprocessing import RobustScaler

scaler_X = RobustScaler()
scaler_y = RobustScaler()

X_scaled = scaler_X.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
y_scaled = scaler_y.fit_transform(y)

# Save scalers
import pickle
with open('models/scalers/scalers.pkl', 'wb') as f:
    pickle.dump({
        'scaler_X': scaler_X,
        'scaler_y': scaler_y,
        'feature_cols': feature_cols
    }, f)
```

### Step 6: Train/Validation/Test Split

```python
from sklearn.model_selection import train_test_split

# Temporal split (70% train, 15% val, 15% test)
n = len(X_scaled)
train_size = int(0.7 * n)
val_size = int(0.15 * n)

X_train = X_scaled[:train_size]
y_train = y_scaled[:train_size]

X_val = X_scaled[train_size:train_size+val_size]
y_val = y_scaled[train_size:train_size+val_size]

X_test = X_scaled[train_size+val_size:]
y_test = y_scaled[train_size+val_size:]
```

## Data Statistics

### Temperature Distribution

| Metric  | Value  |
| ------- | ------ |
| Mean    | 26.8°C |
| Std Dev | 2.1°C  |
| Min     | 18.5°C |
| Max     | 34.2°C |
| Median  | 27.1°C |

### Regional Differences

| Region  | Avg Temp | Avg Humidity | Avg Solar Radiation |
| ------- | -------- | ------------ | ------------------- |
| Western | 27.2°C   | 78%          | 18.5 MJ/m²          |
| Central | 26.5°C   | 75%          | 19.2 MJ/m²          |
| Eastern | 27.8°C   | 72%          | 20.1 MJ/m²          |

### Seasonal Patterns

| Season        | Avg Temp | Avg Rainfall | Avg Sunshine |
| ------------- | -------- | ------------ | ------------ |
| Wet (Dec-Feb) | 26.2°C   | 285 mm       | 4.8 hrs      |
| Transition 1  | 27.1°C   | 165 mm       | 6.2 hrs      |
| Dry (Jun-Aug) | 27.5°C   | 45 mm        | 8.1 hrs      |
| Transition 2  | 27.0°C   | 125 mm       | 6.8 hrs      |

## Data Usage Examples

### Example 1: Load and Explore

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/raw/weather_data_indonesia.csv')
df['date'] = pd.to_datetime(df['date'])

# Plot temperature trends for Jakarta
jakarta = df[df['location'] == 'Jakarta']
plt.figure(figsize=(15, 5))
plt.plot(jakarta['date'], jakarta['Tavg'])
plt.title('Temperature in Jakarta')
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.show()
```

### Example 2: Station Analysis

```python
# Get statistics per station
station_stats = df.groupby('station_id').agg({
    'Tavg': ['mean', 'std', 'min', 'max'],
    'RH_avg': 'mean',
    'ss': 'mean',
    'date': ['min', 'max', 'count']
})
```

### Example 3: Seasonal Comparison

```python
# Compare seasons
df['season'] = df['month'].map({
    12:1, 1:1, 2:1, 3:2, 4:2, 5:2,
    6:3, 7:3, 8:3, 9:4, 10:4, 11:4
})

seasonal_avg = df.groupby('season')['Tavg'].mean()
```

## Data Updates

**Frequency**: Data should be updated monthly with new observations.

**Process**:

1. Download new data from BMKG
2. Run data validation checks
3. Append to existing datasets
4. Re-run feature engineering
5. Retrain models if significant drift detected

---

For preprocessing code, see `notebooks/processing.ipynb` and `notebooks/mergedata.ipynb`.
