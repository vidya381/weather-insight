import { useState, useEffect, memo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { mlAPI } from '../api/ml';
import Spinner from './Spinner';
import './MLInsights.css';

function TrendAnalysis({ cityName }) {
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(90);

  useEffect(() => {
    if (cityName) {
      loadTrends();
    }
  }, [cityName, days]);

  const loadTrends = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await mlAPI.getTrends(cityName, 'temperature', days);
      setTrends(data);
    } catch (err) {
      setError(
        'Not enough data yet. Trend analysis requires at least 30 days of weather history. ' +
        'Weather is collected hourly - check back in a few days!'
      );
      console.error('Trend load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (direction) => {
    if (direction === 'increasing') return '↗';
    if (direction === 'decreasing') return '↘';
    return '→';
  };

  const getTrendColor = (direction) => {
    if (direction === 'increasing') return '#dc2626';
    if (direction === 'decreasing') return '#3b82f6';
    return '#6b7280';
  };

  // Prepare chart data
  const chartData = trends?.predictions_7_day
    ? Object.entries(trends.predictions_7_day).map(([day, value]) => ({
        day: `Day ${day}`,
        temperature: value,
      }))
    : [];

  return (
    <div className="ml-section">
      <div className="ml-header">
        <h3>Temperature Trend Analysis</h3>
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

      {loading && <Spinner text="Analyzing temperature trends..." />}

      {error && (
        <div className="ml-error">
          <p>{error}</p>
          <button onClick={loadTrends} className="retry-btn">
            Retry
          </button>
        </div>
      )}

      {!loading && !error && trends && (
        <>

      <div className="trend-summary">
        <div className="trend-stat">
          <span className="stat-label">Direction</span>
          <span
            className="stat-value"
            style={{ color: getTrendColor(trends.trend_direction) }}
          >
            {getTrendIcon(trends.trend_direction)} {trends.trend_direction}
          </span>
        </div>
        <div className="trend-stat">
          <span className="stat-label">Slope</span>
          <span className="stat-value">
            {trends.slope > 0 ? '+' : ''}
            {trends.slope?.toFixed(4)}°C/day
          </span>
        </div>
        <div className="trend-stat">
          <span className="stat-label">Confidence (R²)</span>
          <span className="stat-value">{(trends.r_squared * 100)?.toFixed(1)}%</span>
        </div>
      </div>

      <div className="trend-interpretation">
        <p>{trends.slope_interpretation}</p>
      </div>

      {chartData.length > 0 && (
        <div className="trend-chart">
          <h4>7-Day Prediction</h4>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#60A5FA" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#60A5FA" stopOpacity={0.1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.15} />
              <XAxis
                dataKey="day"
                stroke="currentColor"
                style={{ fontSize: '0.75rem', fill: 'var(--text-secondary)' }}
              />
              <YAxis
                stroke="currentColor"
                style={{ fontSize: '0.75rem', fill: 'var(--text-secondary)' }}
                unit="°C"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--tooltip-bg, #ffffff)',
                  border: '1px solid var(--tooltip-border, #e5e5e5)',
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                  color: 'var(--text-primary)',
                }}
              />
              <Area
                type="monotone"
                dataKey="temperature"
                stroke="#60A5FA"
                strokeWidth={3}
                fill="url(#tempGradient)"
                dot={{ fill: '#60A5FA', r: 5, strokeWidth: 2, stroke: '#ffffff' }}
                activeDot={{ r: 7, fill: '#3b82f6' }}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="trend-stats">
        <h4>Historical Statistics</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Average</span>
            <span className="stat-value">{trends.statistics?.mean?.toFixed(1)}°C</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Minimum</span>
            <span className="stat-value">{trends.statistics?.min?.toFixed(1)}°C</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Maximum</span>
            <span className="stat-value">{trends.statistics?.max?.toFixed(1)}°C</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Std Dev</span>
            <span className="stat-value">{trends.statistics?.std?.toFixed(1)}°C</span>
          </div>
        </div>
      </div>
      </>
      )}
    </div>
  );
}

export default memo(TrendAnalysis);
