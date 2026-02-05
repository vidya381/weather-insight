"""
Tests for ML Algorithm Implementations
"""

import pytest
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class TestAnomalyDetection:
    """Test anomaly detection algorithm"""

    def test_z_score_calculation(self):
        """Test Z-score calculation for anomaly detection"""
        # Normal temperatures around 20°C
        temps = np.array([19, 20, 21, 20, 19, 21, 20, 22, 40])  # 40 is anomaly

        mean = np.mean(temps)
        std = np.std(temps)

        # Calculate z-score for the anomaly (40)
        z_score = (40 - mean) / std

        # Z-score should be high for anomaly
        assert abs(z_score) > 2.0, "Anomaly should have high z-score"

    def test_z_score_normal_values(self):
        """Test that normal values have low z-scores"""
        temps = np.array([19, 20, 21, 20, 19, 20, 21, 19, 20])

        mean = np.mean(temps)
        std = np.std(temps)

        # Calculate z-scores for all values
        z_scores = (temps - mean) / std

        # All should be within normal range (|z| < 2.0)
        assert all(abs(z) < 2.0 for z in z_scores)

    def test_severity_classification(self):
        """Test severity classification based on z-score"""
        def classify_severity(z_score):
            abs_z = abs(z_score)
            if abs_z > 3.0:
                return "High"
            elif abs_z > 2.0:
                return "Medium"
            elif abs_z > 1.5:
                return "Low"
            return "Normal"

        assert classify_severity(3.5) == "High"
        assert classify_severity(2.5) == "Medium"
        assert classify_severity(1.7) == "Low"
        assert classify_severity(1.0) == "Normal"


class TestTrendAnalysis:
    """Test trend analysis algorithm"""

    def test_linear_regression_upward_trend(self):
        """Test linear regression detects upward trend"""
        # Create increasing temperature data (warming trend)
        days = np.array(range(30)).reshape(-1, 1)
        temps = np.array([15 + (i * 0.1) for i in range(30)])  # +0.1°C per day

        model = LinearRegression()
        model.fit(days, temps)

        # Slope should be positive (warming)
        assert model.coef_[0] > 0, "Should detect warming trend"
        assert 0.08 < model.coef_[0] < 0.12, "Slope should be ~0.1"

    def test_linear_regression_downward_trend(self):
        """Test linear regression detects downward trend"""
        # Create decreasing temperature data (cooling trend)
        days = np.array(range(30)).reshape(-1, 1)
        temps = np.array([25 - (i * 0.15) for i in range(30)])  # -0.15°C per day

        model = LinearRegression()
        model.fit(days, temps)

        # Slope should be negative (cooling)
        assert model.coef_[0] < 0, "Should detect cooling trend"

    def test_linear_regression_r_squared(self):
        """Test R² score calculation"""
        # Perfect linear data (R² should be ~1.0)
        days = np.array(range(20)).reshape(-1, 1)
        temps = np.array([10 + (i * 0.5) for i in range(20)])

        model = LinearRegression()
        model.fit(days, temps)
        r2 = model.score(days, temps)

        # Should have very high R² for perfect linear data
        assert r2 > 0.99, "R² should be close to 1.0 for linear data"

    def test_prediction_generation(self):
        """Test generating future predictions"""
        # Train on 30 days
        days = np.array(range(30)).reshape(-1, 1)
        temps = np.array([20 + (i * 0.1) for i in range(30)])

        model = LinearRegression()
        model.fit(days, temps)

        # Predict next 7 days
        future_days = np.array(range(30, 37)).reshape(-1, 1)
        predictions = model.predict(future_days)

        # Should have 7 predictions
        assert len(predictions) == 7

        # Predictions should continue the trend (higher than training data)
        assert predictions[0] > temps[-1]


class TestPatternClustering:
    """Test pattern clustering algorithm"""

    def test_kmeans_basic_clustering(self):
        """Test K-Means creates distinct clusters"""
        # Create two distinct weather patterns
        # Pattern 1: Hot & Humid (temp=30, humidity=80)
        # Pattern 2: Cold & Dry (temp=5, humidity=40)
        data = np.array([
            [30, 80],  # Hot & Humid
            [31, 82],
            [29, 78],
            [5, 40],   # Cold & Dry
            [6, 42],
            [4, 38]
        ])

        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        labels = kmeans.fit_predict(data)

        # Should create 2 clusters
        unique_labels = set(labels)
        assert len(unique_labels) == 2

        # First 3 should be in same cluster
        assert labels[0] == labels[1] == labels[2]

        # Last 3 should be in same cluster (different from first)
        assert labels[3] == labels[4] == labels[5]
        assert labels[0] != labels[3]

    def test_kmeans_with_normalization(self):
        """Test K-Means with StandardScaler normalization"""
        # Weather data with different scales
        data = np.array([
            [30, 1000],  # Temperature, Pressure
            [31, 1010],
            [5, 980],
            [6, 990]
        ])

        # Normalize data
        scaler = StandardScaler()
        normalized = scaler.fit_transform(data)

        # Check normalization worked (mean ~0, std ~1)
        assert abs(normalized.mean()) < 0.1
        assert 0.9 < normalized.std() < 1.1

    def test_cluster_center_calculation(self):
        """Test that cluster centers are calculated correctly"""
        # Simple data
        data = np.array([
            [10, 50],
            [11, 51],
            [20, 80],
            [21, 81]
        ])

        kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
        kmeans.fit(data)

        # Should have 2 cluster centers
        assert len(kmeans.cluster_centers_) == 2

        # Centers should be between the data points
        for center in kmeans.cluster_centers_:
            assert 9 < center[0] < 22
            assert 49 < center[1] < 82
