import { useState, useEffect } from 'react';
import { mlAPI } from '../api/ml';
import './MLInsights.css';

export default function PatternClustering({ cityName }) {
  const [patterns, setPatterns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(90);

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
    } catch (err) {
      setError('Failed to load patterns');
      console.error('Pattern load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getClusterColor = (clusterId) => {
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];
    return colors[clusterId % colors.length];
  };

  if (loading) {
    return <div className="ml-loading">Loading patterns...</div>;
  }

  if (error) {
    return <div className="ml-error">{error}</div>;
  }

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

      {patterns.length === 0 ? (
        <div className="ml-empty">
          <p>No patterns detected yet.</p>
          <p className="ml-empty-hint">More historical data is needed to identify weather patterns.</p>
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
                <span className="pattern-date">
                  {new Date(pattern.pattern_date).toLocaleDateString()}
                </span>
              </div>

              {pattern.characteristics && (
                <div className="pattern-characteristics">
                  <div className="char-item">
                    <span className="char-label">Avg Temp</span>
                    <span className="char-value">
                      {pattern.characteristics.avg_temp?.toFixed(1)}°C
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
                </div>
              )}

              {pattern.similar_dates && pattern.similar_dates.length > 0 && (
                <div className="similar-dates">
                  <span className="similar-label">Similar days:</span>
                  <div className="similar-list">
                    {pattern.similar_dates.slice(0, 5).map((date, idx) => (
                      <span key={idx} className="similar-date">
                        {new Date(date).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                        })}
                      </span>
                    ))}
                    {pattern.similar_dates.length > 5 && (
                      <span className="similar-more">
                        +{pattern.similar_dates.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              )}
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
    </div>
  );
}
