# Machine Learning Models - Weather Insight

This document explains the three machine learning algorithms used in Weather Insight to provide intelligent weather analytics.

---

## Overview

Weather Insight implements three distinct ML features:

1. **Anomaly Detection** - Identifies unusual weather patterns
2. **Trend Analysis** - Predicts future temperature trends
3. **Pattern Clustering** - Groups similar weather conditions

All models run on historical weather data collected hourly from the OpenWeather API.

---

## 1. Anomaly Detection

### Purpose
Identify unusual temperature readings that deviate significantly from normal patterns.

### Algorithm: Z-Score Method

**Statistical Foundation:**
```
Z-Score = (X - μ) / σ

Where:
- X = observed temperature value
- μ = mean temperature (average)
- σ = standard deviation
```

### Implementation

**File:** `backend/app/ml/anomaly_detection.py`

```python
def detect_anomalies(city_name, days=30):
    # 1. Get historical temperature data
    temperatures = get_last_n_days(city_name, days)

    # 2. Calculate statistics
    mean = np.mean(temperatures)
    std_dev = np.std(temperatures)

    # 3. Calculate z-scores for each value
    z_scores = (temperatures - mean) / std_dev

    # 4. Flag anomalies based on threshold
    anomalies = []
    for value, z in zip(temperatures, z_scores):
        if abs(z) > 1.5:  # Threshold
            severity = classify_severity(z)
            anomalies.append({
                'value': value,
                'z_score': z,
                'severity': severity
            })

    return anomalies
```

### Severity Classification

| Z-Score Range | Severity | Meaning |
|--------------|----------|---------|
| \|z\| > 3.0 | **High** | Extremely unusual (>99.7% deviation) |
| 2.0 < \|z\| ≤ 3.0 | **Medium** | Very unusual (>95% deviation) |
| 1.5 < \|z\| ≤ 2.0 | **Low** | Moderately unusual (>87% deviation) |
| \|z\| ≤ 1.5 | Normal | Within expected range |

### Data Requirements
- **Minimum:** 10 days of historical data
- **Optimal:** 30+ days for accurate statistics
- **Collection:** Hourly temperature readings

### Example Output

**High Severity Anomaly:**
```json
{
  "date": "2024-01-15",
  "temperature": 28.5,     // Actual temperature
  "expected": 15.2,        // Mean temperature
  "deviation": 13.3,       // Difference
  "z_score": 3.4,          // Statistical measure
  "severity": "High",
  "description": "Unusually high temperature"
}
```

### Use Cases
- Identify record-breaking temperatures
- Detect sensor malfunctions (if values are impossible)
- Alert users to extreme weather events
- Track climate anomalies over time

### Limitations
- Assumes normal distribution (Gaussian)
- Sensitive to outliers in small datasets
- Doesn't account for seasonal trends
- Requires consistent data quality

---

## 2. Trend Analysis

### Purpose
Analyze historical temperature trends and predict future temperatures using linear regression.

### Algorithm: Linear Regression

**Mathematical Model:**
```
y = mx + b

Where:
- y = predicted temperature
- m = slope (trend direction and magnitude)
- x = day index (0, 1, 2, ...)
- b = intercept (starting point)
```

### Implementation

**File:** `backend/app/ml/trend_analysis.py`

```python
def analyze_trends(city_name, days=90):
    # 1. Get historical data
    data = get_historical_temperatures(city_name, days)

    # 2. Prepare data for regression
    X = np.array(range(len(data))).reshape(-1, 1)  # Day indices
    y = np.array([d['temperature'] for d in data])  # Temperatures

    # 3. Fit linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # 4. Extract trend parameters
    slope = model.coef_[0]
    intercept = model.intercept_
    r_squared = model.score(X, y)

    # 5. Generate predictions (7 days ahead)
    future_X = np.array(range(len(data), len(data) + 7)).reshape(-1, 1)
    predictions = model.predict(future_X)

    # 6. Calculate confidence intervals (95%)
    residuals = y - model.predict(X)
    std_error = np.std(residuals)
    margin = 1.96 * std_error  # 95% confidence

    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_squared,
        'predictions': predictions,
        'confidence_intervals': {
            'upper': predictions + margin,
            'lower': predictions - margin
        }
    }
```

### Trend Direction Classification

**Based on Slope (m):**
```python
if slope > 0.01:
    direction = "increasing"   # Warming trend
elif slope < -0.01:
    direction = "decreasing"   # Cooling trend
else:
    direction = "stable"       # No significant trend
```

**Slope Interpretation:**
- `slope = 0.05` → Temperature increasing by 0.05°C per day
- `slope = -0.03` → Temperature decreasing by 0.03°C per day

### Confidence Level (R² Score)

**R² (R-squared) measures prediction accuracy:**

| R² Range | Confidence | Interpretation |
|----------|-----------|----------------|
| > 0.7 | **High** | Strong linear trend, reliable predictions |
| 0.4 - 0.7 | **Medium** | Moderate trend, predictions somewhat reliable |
| < 0.4 | **Low** | Weak trend, high variability |

**Formula:**
```
R² = 1 - (SS_residual / SS_total)

Where:
- SS_residual = Sum of squared residuals (errors)
- SS_total = Total sum of squares (variance)
```

### Data Requirements
- **Minimum:** 30 days of data
- **Recommended:** 90 days for reliable trends
- **Optimal:** 365 days for seasonal patterns
- **Collection:** Daily average temperatures

### Prediction Intervals

**95% Confidence Interval:**
```
Upper Bound = prediction + (1.96 × standard_error)
Lower Bound = prediction - (1.96 × standard_error)
```

**Interpretation:**
- 95% chance actual temperature falls within this range
- Wider intervals = more uncertainty
- Intervals widen further into the future

### Example Output

```json
{
  "city": "London",
  "metric": "temperature",
  "analysis_period": 90,
  "trend": {
    "direction": "increasing",
    "slope": 0.05,           // +0.05°C per day
    "intercept": 14.2,       // Starting temperature
    "r_squared": 0.78,       // 78% of variance explained
    "confidence": "high"
  },
  "predictions_7_day": {
    "2024-01-16": 18.5,
    "2024-01-17": 18.6,
    "2024-01-18": 18.7,
    "2024-01-19": 18.8,
    "2024-01-20": 18.9,
    "2024-01-21": 19.0,
    "2024-01-22": 19.1
  },
  "prediction_intervals": {
    "2024-01-16": {
      "lower": 16.5,         // 95% confidence lower bound
      "upper": 20.5          // 95% confidence upper bound
    }
  }
}
```

### Use Cases
- Long-term temperature forecasting
- Climate change trend identification
- Seasonal pattern analysis
- Agricultural planning
- Energy demand prediction

### Limitations
- Assumes linear relationship (not always true for weather)
- Doesn't account for sudden weather changes
- Long-term predictions less accurate
- Sensitive to data quality
- Ignores cyclical/seasonal patterns (in current implementation)

---

## 3. Pattern Clustering

### Purpose
Group similar weather conditions into clusters to identify recurring weather patterns.

### Algorithm: K-Means Clustering

**Concept:**
- Group data points into K clusters
- Each cluster represents a "weather pattern"
- Points in same cluster have similar characteristics

**Mathematical Objective:**
```
Minimize: Σ Σ ||x - μ_k||²

Where:
- x = data point (weather reading)
- μ_k = cluster centroid (mean of cluster)
- ||·|| = Euclidean distance
```

### Implementation

**File:** `backend/app/ml/pattern_clustering.py`

```python
def cluster_patterns(city_name, days=90, n_clusters=3):
    # 1. Get historical weather data
    data = get_historical_data(city_name, days)

    # 2. Extract features
    features = np.array([
        [d['temperature'], d['humidity'], d['pressure']]
        for d in data
    ])

    # 3. Normalize features (StandardScaler)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # 4. Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(features_scaled)

    # 5. Analyze each cluster
    patterns = []
    for i in range(n_clusters):
        cluster_data = [data[j] for j in range(len(data)) if labels[j] == i]

        pattern = {
            'cluster_id': i,
            'pattern_type': classify_pattern(cluster_data),
            'avg_temperature': np.mean([d['temperature'] for d in cluster_data]),
            'avg_humidity': np.mean([d['humidity'] for d in cluster_data]),
            'avg_pressure': np.mean([d['pressure'] for d in cluster_data]),
            'count': len(cluster_data),
            'percentage': len(cluster_data) / len(data) * 100
        }
        patterns.append(pattern)

    return patterns
```

### Feature Engineering

**Input Features (3 dimensions):**
1. **Temperature (°C)** - Primary weather indicator
2. **Humidity (%)** - Moisture content
3. **Pressure (hPa)** - Atmospheric pressure

**Feature Normalization:**
```python
StandardScaler:
  scaled_value = (value - mean) / std_deviation
```

**Why normalize?**
- Different units (°C, %, hPa) have different scales
- Prevents features with larger values from dominating
- Ensures fair clustering

### Cluster Count Selection

**Current:** Fixed at 3-5 clusters

**Methods to determine optimal K:**
1. **Elbow Method:** Plot within-cluster variance vs. K
2. **Silhouette Score:** Measure cluster separation
3. **Domain Knowledge:** 3-5 patterns typically sufficient for weather

**Typical Patterns:**
- **3 clusters:** Cold, Moderate, Warm
- **4 clusters:** Cold & Dry, Cold & Humid, Warm & Dry, Warm & Humid
- **5 clusters:** Very Cold, Cold, Moderate, Warm, Hot

### Pattern Classification

**Based on cluster centroid values:**

```python
def classify_pattern(cluster_data):
    avg_temp = mean(temperatures)
    avg_humidity = mean(humidity)

    if avg_temp < 10 and avg_humidity < 60:
        return "Cold & Dry"
    elif avg_temp < 10 and avg_humidity >= 60:
        return "Cold & Humid"
    elif 10 <= avg_temp < 20 and avg_humidity < 70:
        return "Moderate"
    elif avg_temp >= 20 and avg_humidity >= 70:
        return "Hot & Humid"
    # ... more classifications
```

### Data Requirements
- **Minimum:** 30 days of data
- **Recommended:** 90 days for stable patterns
- **Optimal:** 365 days for seasonal patterns
- **Collection:** Hourly weather readings (temp, humidity, pressure)

### Example Output

```json
{
  "city": "London",
  "analysis_period": 90,
  "patterns": [
    {
      "cluster_id": 0,
      "pattern_type": "Cold & Dry",
      "avg_temperature": 8.5,
      "avg_humidity": 65,
      "avg_pressure": 1020,
      "count": 25,
      "percentage": 27.8,
      "similar_dates": [
        "2024-01-05",
        "2024-01-12",
        "2024-01-18"
      ]
    },
    {
      "cluster_id": 1,
      "pattern_type": "Moderate",
      "avg_temperature": 15.2,
      "avg_humidity": 72,
      "avg_pressure": 1013,
      "count": 45,
      "percentage": 50.0,
      "similar_dates": [
        "2024-01-03",
        "2024-01-07"
      ]
    },
    {
      "cluster_id": 2,
      "pattern_type": "Warm & Humid",
      "avg_temperature": 22.1,
      "avg_humidity": 82,
      "avg_pressure": 1008,
      "count": 20,
      "percentage": 22.2,
      "similar_dates": [
        "2024-01-09"
      ]
    }
  ],
  "total_days_analyzed": 90
}
```

### Use Cases
- Identify typical weather patterns for a city
- Compare current weather to historical patterns
- Predict likely weather pattern transitions
- Tourism and event planning
- Understand seasonal weather variations

### Limitations
- K must be chosen beforehand (not automatically optimal)
- Assumes spherical clusters (Euclidean distance)
- Sensitive to initialization (uses random_state=42 for reproducibility)
- Doesn't capture temporal sequences
- Hard boundaries (each point belongs to exactly one cluster)

---

## Data Collection Pipeline

### Weather Data Collection

**Job:** `backend/app/jobs/weather_collection.py`

**Schedule:** Every hour (via APScheduler)

**Process:**
```
1. Get all cities from favorite_cities table
2. For each unique city:
   a. Call OpenWeather API
   b. Extract: temperature, humidity, pressure, conditions
   c. Store in weather_data table with timestamp
3. Log results (success/failures)
```

**Data Stored:**
```sql
INSERT INTO weather_data (
  city_id,
  timestamp,
  temperature,
  humidity,
  pressure,
  weather_main,
  description
) VALUES (...)
```

### Data Retention

**Job:** `backend/app/jobs/data_retention.py`

**Schedule:** Daily at 2:00 AM

**Cleanup Rules:**
- `weather_data`: Delete > 180 days old
- `ml_anomalies`: Delete > 90 days old
- `ml_patterns`: Delete > 90 days old
- `ml_trends`: Delete > 90 days old

---

## Model Performance

### Computational Complexity

| Model | Time Complexity | Space Complexity | Avg Runtime |
|-------|----------------|------------------|-------------|
| Anomaly Detection | O(n) | O(n) | ~50ms |
| Trend Analysis | O(n²) | O(n) | ~200ms |
| Pattern Clustering | O(n·k·i) | O(n·k) | ~500ms |

**Where:**
- n = number of data points
- k = number of clusters
- i = iterations (typically 10-100)

### Accuracy Considerations

**Anomaly Detection:**
- Accuracy depends on data distribution
- False positives if data is not normally distributed
- Works best with stable baseline

**Trend Analysis:**
- R² score indicates prediction quality
- Confidence intervals provide uncertainty estimates
- Accuracy decreases for long-term predictions

**Pattern Clustering:**
- Silhouette score can measure cluster quality
- Interpretability depends on clear cluster separation
- Best with distinct weather patterns

---

## References

### Libraries Used
- **NumPy:** Numerical computations
- **Pandas:** Data manipulation
- **Scikit-learn:** ML algorithms (LinearRegression, KMeans, StandardScaler)
- **SQLAlchemy:** Database queries

### Academic References
1. Z-Score Anomaly Detection: Standard statistical method
2. Linear Regression: Ordinary Least Squares (OLS)
3. K-Means Clustering: MacQueen, J. (1967)

### Documentation
- Scikit-learn: https://scikit-learn.org/
- NumPy: https://numpy.org/
- Pandas: https://pandas.pydata.org/

---