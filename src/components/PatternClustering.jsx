import { useState, useEffect, memo } from 'react';
import { mlAPI } from '../api/ml';
import Spinner from './Spinner';
import './MLInsights.css';

function PatternClustering({ cityName }) {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(90);
  const [totalDays, setTotalDays] = useState(0);

  useEffect(() => {
    if (cityName) {
      loadPatterns();
    }
  }, [cityName, days]);

  const loadPatterns = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await mlAPI.getPatterns(cityName, days);
      setPatterns(data.patterns);
      // Calculate total days across all patterns
      const total = data.patterns.reduce((sum, p) => sum + p.count, 0);
      setTotalDays(total);
    } catch (err) {
      setError(
        'Not enough data yet. Pattern clustering requires at least 30 days of weather history. ' +
        'Weather is collected hourly - check back in a few days!'
      );
      // Only log unexpected errors (404 is expected when no data available)
      if (err.response?.status !== 404) {
        console.error('Pattern load error:', err);
      }
    } finally {
      setLoading(false);
    }
  };

  const getClusterColor = (clusterId) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];
    return colors[clusterId % colors.length];
  };

  return (
    <div className="ml-section">
      <div className="ml-header">
        <h3>Weather Patterns (K-Means Clustering)</h3>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="ml-select"
        >
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
          <option value={180}>Last 180 days</option>
        </select>
      </div>

      {loading && <Spinner text="Clustering weather patterns..." />}

      {error && (
        <div className="ml-error">
          <p>{error}</p>
          <button onClick={loadPatterns} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      {!loading && !error && (
        <>

      {patterns.length === 0 ? (
        <div className="ml-empty">
          <p>Collecting weather patterns...</p>
          <p className="ml-empty-hint">
            K-means clustering groups similar weather days together.
            This feature becomes available after 30 days of data collection.
          </p>
        </div>
      ) : (
        <div className="pattern-list">
          {patterns.map((pattern, index) => (
            <div key={index} className="pattern-item">
              <div className="pattern-header">
                <span
                  className="pattern-cluster"
                  style={{ backgroundColor: getClusterColor(pattern.cluster_id) }}
                >
                  Cluster {pattern.cluster_id}
                </span>
                <span className="pattern-count">
                  {pattern.count} days ({Math.round((pattern.count / totalDays) * 100)}%)
                </span>
              </div>

              {pattern.characteristics && (
                <div className="pattern-characteristics">
                  <div className="char-item">
                    <span className="char-label">Avg Temp</span>
                    <span className="char-value">
                      {pattern.characteristics.avg_temperature?.toFixed(1)}°C
                    </span>
                  </div>
                  <div className="char-item">
                    <span className="char-label">Avg Humidity</span>
                    <span className="char-value">
                      {pattern.characteristics.avg_humidity?.toFixed(0)}%
                    </span>
                  </div>
                  <div className="char-item">
                    <span className="char-label">Avg Pressure</span>
                    <span className="char-value">
                      {pattern.characteristics.avg_pressure?.toFixed(0)} hPa
                    </span>
                  </div>
                  <div className="char-item">
                    <span className="char-label">Avg Wind</span>
                    <span className="char-value">
                      {pattern.characteristics.avg_wind_speed?.toFixed(1)} m/s
                    </span>
                  </div>
                </div>
              )}

              {pattern.similar_dates && pattern.similar_dates.length > 0 && (() => {
                // Deduplicate dates by date-only (ignore time)
                const uniqueDates = [...new Set(
                  pattern.similar_dates.map(date =>
                    new Date(date).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })
                  )
                )];

                return (
                  <div className="similar-dates">
                    <span className="similar-label">Similar days:</span>
                    <div className="similar-list">
                      {uniqueDates.slice(0, 5).map((dateStr, idx) => (
                        <span key={idx} className="similar-date">
                          {dateStr}
                        </span>
                      ))}
                      {uniqueDates.length > 5 && (
                        <span className="similar-more">
                          +{uniqueDates.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                );
              })()}
            </div>
          ))}
        </div>
      )}

      <div className="pattern-info">
        <p className="info-text">
          K-means clustering groups similar weather days together based on temperature, humidity,
          and pressure patterns. This helps identify recurring weather conditions.
        </p>
      </div>
      </>
      )}
    </div>
  );
}

export default memo(PatternClustering);
