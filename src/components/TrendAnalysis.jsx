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
      console.log(`🔄 Loading trends for ${cityName}, ${days} days...`);
      const data = await mlAPI.getTrends(cityName, 'temperature', days);
      console.log('✅ API Response received:', data);
      console.log('📊 historical_data length:', data.historical_data?.length || 0);
      console.log('📊 First historical point:', data.historical_data?.[0]);
      console.log('📊 Slope:', data.slope, 'Intercept:', data.intercept);
      setTrends(data);
    } catch (err) {
      setError(
        'Not enough data yet. Trend analysis requires at least 30 days of weather history. ' +
        'Weather is collected hourly - check back in a few days!'
      );
      console.error('❌ Trend load error:', err);
      console.error('❌ Error details:', err.response?.data || err.message);
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

  // Prepare combined chart data: historical + trend line + predictions
  const prepareChartData = () => {
    if (!trends) {
      console.log('No trends data');
      return [];
    }

    console.log('Trends data:', trends);

    const data = [];

    // Add historical data with trend line
    if (trends.historical_data && trends.historical_data.length > 0) {
      console.log('Processing historical data:', trends.historical_data.length, 'points');

      trends.historical_data.forEach((point, idx) => {
        // Validate data
        if (!point || point.temperature == null || point.x == null) {
          console.warn('Invalid historical point at index', idx, point);
          return;
        }

        // Calculate trend line value: y = slope * x + intercept
        const trendValue = (trends.slope || 0) * point.x + (trends.intercept || 0);

        data.push({
          date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          actual: Number(point.temperature),
          trend: Number(trendValue.toFixed(2)),
          type: 'historical'
        });
      });
    } else {
      console.log('No historical data available');
    }

    // Add predictions
    if (trends.predictions_7_day) {
      const lastHistoricalX = trends.historical_data?.length > 0
        ? trends.historical_data[trends.historical_data.length - 1].x
        : 0;

      console.log('Last historical X:', lastHistoricalX);

      Object.entries(trends.predictions_7_day).forEach(([date, value], index) => {
        const predictionX = lastHistoricalX + (index + 1);
        const trendValue = (trends.slope || 0) * predictionX + (trends.intercept || 0);

        data.push({
          date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          prediction: Number(value),
          trend: Number(trendValue.toFixed(2)),
          type: 'prediction'
        });
      });
    }

    console.log('Final chart data:', data.length, 'points', data.slice(0, 3), '...');
    return data;
  };

  const chartData = prepareChartData();

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
          <h4>Temperature Trend Analysis & 7-Day Forecast</h4>
          <ResponsiveContainer width="100%" height={320}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="predictionGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.15} />
              <XAxis
                dataKey="date"
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
                formatter={(value) => {
                  if (value == null || isNaN(value)) return 'N/A';
                  return `${Number(value).toFixed(1)}°C`;
                }}
              />
              {/* Historical actual temperatures */}
              <Area
                type="monotone"
                dataKey="actual"
                stroke="#3b82f6"
                strokeWidth={2}
                fill="none"
                dot={{ fill: '#3b82f6', r: 3, strokeWidth: 1, stroke: '#ffffff' }}
                connectNulls
              />
              {/* Trend line (dashed) */}
              <Area
                type="monotone"
                dataKey="trend"
                stroke="#A78BFA"
                strokeWidth={2}
                strokeDasharray="5 5"
                fill="none"
                dot={false}
                connectNulls
              />
              {/* Future predictions */}
              <Area
                type="monotone"
                dataKey="prediction"
                stroke="#f97316"
                strokeWidth={3}
                fill="url(#predictionGradient)"
                dot={{ fill: '#f97316', r: 5, strokeWidth: 2, stroke: '#ffffff' }}
                activeDot={{ r: 7, fill: '#ea580c' }}
                connectNulls
              />
            </AreaChart>
          </ResponsiveContainer>
          <div className="chart-legend">
            <div className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: '#3b82f6' }}></span>
              <span>Actual Temperature</span>
            </div>
            <div className="legend-item">
              <span className="legend-line" style={{ borderColor: '#A78BFA' }}></span>
              <span>Trend Line</span>
            </div>
            <div className="legend-item">
              <span className="legend-dot" style={{ backgroundColor: '#f97316' }}></span>
              <span>7-Day Forecast</span>
            </div>
          </div>
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
            <span className="stat-value">{trends.statistics?.std_dev?.toFixed(1)}°C</span>
          </div>
        </div>
      </div>
      </>
      )}
    </div>
  );
}

export default memo(TrendAnalysis);
