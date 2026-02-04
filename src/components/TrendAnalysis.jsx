import { useState, useEffect, memo, useMemo } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { mlAPI } from '../api/ml';
import Spinner from './Spinner';
import './MLInsights.css';

function TrendAnalysis({ cityName }) {
  const [trends, setTrends] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [days, setDays] = useState(90);
  const [chartHeight, setChartHeight] = useState(320);

  useEffect(() => {
    if (cityName) {
      loadTrends();
    }
  }, [cityName, days]);

  // Handle responsive chart height
  useEffect(() => {
    const updateChartHeight = () => {
      if (window.innerWidth <= 320) {
        setChartHeight(220);
      } else if (window.innerWidth <= 375) {
        setChartHeight(240);
      } else if (window.innerWidth <= 640) {
        setChartHeight(260);
      } else if (window.innerWidth <= 768) {
        setChartHeight(280);
      } else {
        setChartHeight(320);
      }
    };

    updateChartHeight();
    window.addEventListener('resize', updateChartHeight);
    return () => window.removeEventListener('resize', updateChartHeight);
  }, []);

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
      // Only log unexpected errors (404 is expected when no data available)
      if (err.response?.status !== 404) {
        console.error('Trend load error:', err);
      }
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

  // Custom tooltip to show only relevant data
  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;

    return (
      <div style={{
        backgroundColor: 'var(--tooltip-bg, #ffffff)',
        border: '1px solid var(--tooltip-border, #e5e5e5)',
        borderRadius: '8px',
        padding: '8px 12px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        color: 'var(--text-primary)',
        fontSize: '0.875rem',
      }}>
        <div style={{ fontWeight: '600', marginBottom: '4px' }}>{data.date}</div>
        {data.actual != null && (
          <div style={{ color: '#3b82f6' }}>
            Actual: {data.actual.toFixed(1)}°C
          </div>
        )}
        {data.prediction != null && (
          <div style={{ color: '#f97316' }}>
            Forecast: {data.prediction.toFixed(1)}°C
          </div>
        )}
        {data.trend != null && (
          <div style={{ color: '#A78BFA', fontSize: '0.8125rem', marginTop: '2px' }}>
            Trend: {data.trend.toFixed(1)}°C
          </div>
        )}
      </div>
    );
  };

  // Prepare combined chart data: historical + trend line + predictions
  const prepareChartData = () => {
    if (!trends) {
      return [];
    }

    const data = [];

    // Add historical data with trend line and confidence bands
    if (trends.historical_data && trends.historical_data.length > 0) {
      trends.historical_data.forEach((point) => {
        // Validate data
        if (!point || point.temperature == null || point.x == null) {
          return;
        }

        // Calculate trend line value: y = slope * x + intercept
        const trendValue = (trends.slope || 0) * point.x + (trends.intercept || 0);

        const upper = point.trend_upper ? Number(point.trend_upper) : null;
        const lower = point.trend_lower ? Number(point.trend_lower) : null;
        const bandWidth = (upper !== null && lower !== null) ? upper - lower : null;

        data.push({
          date: new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          actual: Number(point.temperature),
          trend: Number(trendValue.toFixed(2)),
          confidenceLower: lower,
          confidenceBand: bandWidth,
          type: 'historical'
        });
      });
    }

    // Add predictions with confidence intervals
    if (trends.predictions_7_day && trends.prediction_intervals) {
      const lastHistoricalX = trends.historical_data?.length > 0
        ? trends.historical_data[trends.historical_data.length - 1].x
        : 0;

      Object.entries(trends.predictions_7_day).forEach(([date, value], index) => {
        const predictionX = lastHistoricalX + (index + 1);
        const trendValue = (trends.slope || 0) * predictionX + (trends.intercept || 0);
        const intervals = trends.prediction_intervals[date];

        const upper = intervals?.upper ? Number(intervals.upper) : null;
        const lower = intervals?.lower ? Number(intervals.lower) : null;
        const bandWidth = (upper !== null && lower !== null) ? upper - lower : null;

        data.push({
          date: new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          prediction: Number(value),
          trend: Number(trendValue.toFixed(2)),
          confidenceLower: lower,
          confidenceBand: bandWidth,
          type: 'prediction'
        });
      });
    }

    return data;
  };

  // Memoize chart data to prevent unnecessary recalculations
  const chartData = useMemo(() => prepareChartData(), [trends]);

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
          <ResponsiveContainer width="100%" height={chartHeight}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="predictionGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f97316" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#f97316" stopOpacity={0.05}/>
                </linearGradient>
                <linearGradient id="confidenceBandGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#A78BFA" stopOpacity={0.15}/>
                  <stop offset="95%" stopColor="#A78BFA" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.15} />
              <XAxis
                dataKey="date"
                stroke="currentColor"
                style={{ fontSize: '0.75rem', fill: 'var(--text-secondary)' }}
                interval={Math.floor(chartData.length / 6)}
                tick={{ dy: 10 }}
              />
              <YAxis
                stroke="currentColor"
                style={{ fontSize: '0.75rem', fill: 'var(--text-secondary)' }}
                unit="°C"
              />
              <Tooltip content={<CustomTooltip />} />
              {/* Confidence band - stacked areas to show uncertainty range */}
              <Area
                type="monotone"
                dataKey="confidenceLower"
                stroke="none"
                fill="transparent"
                stackId="confidence"
                dot={false}
                connectNulls
                isAnimationActive={false}
              />
              <Area
                type="monotone"
                dataKey="confidenceBand"
                stroke="none"
                fill="url(#confidenceBandGradient)"
                stackId="confidence"
                dot={false}
                connectNulls
                isAnimationActive={false}
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
              <span className="legend-band" style={{ backgroundColor: '#A78BFA', opacity: 0.2 }}></span>
              <span>95% Confidence Band</span>
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
          <div className="ml-stat-item">
            <span className="stat-label">Average</span>
            <span className="stat-value">{trends.statistics?.mean?.toFixed(1)}°C</span>
          </div>
          <div className="ml-stat-item">
            <span className="stat-label">Minimum</span>
            <span className="stat-value">{trends.statistics?.min?.toFixed(1)}°C</span>
          </div>
          <div className="ml-stat-item">
            <span className="stat-label">Maximum</span>
            <span className="stat-value">{trends.statistics?.max?.toFixed(1)}°C</span>
          </div>
          <div className="ml-stat-item">
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
