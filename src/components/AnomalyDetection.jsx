import { useState, useEffect } from 'react';
import { mlAPI } from '../api/ml';
import './MLInsights.css';

export default function AnomalyDetection({ cityName }) {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(30);

  useEffect(() => {
    if (cityName) {
      loadAnomalies();
    }
  }, [cityName, days]);

  const loadAnomalies = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await mlAPI.getAnomalies(cityName, days);
      setAnomalies(data.anomalies);
    } catch (err) {
      setError(
        'Not enough data yet. Anomaly detection requires at least 10 days of weather history. ' +
        'Weather is collected hourly - check back soon!'
      );
      console.error('Anomaly load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return '#dc2626';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  if (loading) {
    return <div className="ml-loading">Loading anomalies...</div>;
  }

  if (error) {
    return <div className="ml-error">{error}</div>;
  }

  return (
    <div className="ml-section">
      <div className="ml-header">
        <h3>Temperature Anomalies</h3>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="ml-select"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {anomalies.length === 0 ? (
        <div className="ml-empty">
          <p>✓ No unusual weather patterns detected</p>
          <p className="ml-empty-hint">
            Temperature has been consistent with historical averages.
            Anomalies are flagged when values deviate more than 2 standard deviations from normal.
          </p>
        </div>
      ) : (
        <div className="anomaly-list">
          {anomalies.map((anomaly, index) => (
            <div key={index} className="anomaly-item">
              <div className="anomaly-header">
                <span
                  className="anomaly-severity"
                  style={{ backgroundColor: getSeverityColor(anomaly.severity) }}
                >
                  {anomaly.severity}
                </span>
                <span className="anomaly-date">
                  {new Date(anomaly.timestamp).toLocaleDateString()}
                </span>
              </div>
              <div className="anomaly-details">
                <div className="anomaly-value">
                  <span className="value-label">Current</span>
                  <span className="value-number">{anomaly.current_value?.toFixed(1)}°C</span>
                </div>
                <div className="anomaly-value">
                  <span className="value-label">Expected</span>
                  <span className="value-number">{anomaly.expected_value?.toFixed(1)}°C</span>
                </div>
                <div className="anomaly-value">
                  <span className="value-label">Z-Score</span>
                  <span className="value-number deviation">
                    {anomaly.deviation > 0 ? '+' : ''}
                    {anomaly.deviation?.toFixed(1)}σ
                  </span>
                </div>
              </div>
              {anomaly.description && (
                <p className="anomaly-description">{anomaly.description}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
