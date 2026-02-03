import { useState, useEffect, memo } from 'react';
import { weatherAPI } from '../api/weather';
import Skeleton from './Skeleton';
import {
  IoSunny, IoPartlySunny, IoCloud, IoRainy, IoSnow,
  IoThunderstorm, IoCloudyNight
} from 'react-icons/io5';
import './DailyForecast.css';

const getWeatherIcon = (condition, size = 48) => {
  const cond = condition?.toLowerCase() || '';

  if (cond.includes('clear')) return <IoSunny size={size} className="weather-icon weather-icon-clear" />;
  if (cond.includes('cloud')) return <IoCloud size={size} className="weather-icon weather-icon-cloudy" />;
  if (cond.includes('rain') || cond.includes('drizzle')) return <IoRainy size={size} className="weather-icon weather-icon-rain" />;
  if (cond.includes('snow')) return <IoSnow size={size} className="weather-icon weather-icon-snow" />;
  if (cond.includes('thunder') || cond.includes('storm')) return <IoThunderstorm size={size} className="weather-icon weather-icon-thunder" />;
  if (cond.includes('fog') || cond.includes('mist') || cond.includes('haze')) return <IoCloudyNight size={size} className="weather-icon weather-icon-fog" />;
  return <IoPartlySunny size={size} className="weather-icon weather-icon-cloudy" />;
};

function DailyForecast({ city }) {
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (city) {
      loadForecast();
    }
  }, [city]);

  const loadForecast = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await weatherAPI.getForecast(city.name, 5);

      // Group by day and get daily highs/lows
      const dailyData = processForecastData(data.forecast);
      setForecast(dailyData);
    } catch (err) {
      setError('Failed to load forecast');
      console.error('Forecast load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const processForecastData = (forecastList) => {
    const dailyMap = {};

    forecastList.forEach(item => {
      const date = new Date(item.datetime * 1000);
      const dateKey = date.toDateString();

      if (!dailyMap[dateKey]) {
        dailyMap[dateKey] = {
          date: date,
          temps: [],
          conditions: [],
          weather: item.weather
        };
      }

      dailyMap[dateKey].temps.push(item.temperature);
      dailyMap[dateKey].conditions.push(item.weather.main);
    });

    // Convert to array and calculate min/max
    return Object.values(dailyMap).slice(0, 7).map(day => ({
      date: day.date,
      tempMin: Math.round(Math.min(...day.temps)),
      tempMax: Math.round(Math.max(...day.temps)),
      weather: day.weather,
      // Get most common condition
      condition: day.conditions.sort((a, b) =>
        day.conditions.filter(v => v === a).length -
        day.conditions.filter(v => v === b).length
      ).pop()
    }));
  };

  const formatDate = (date) => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const tomorrowOnly = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate());

    if (dateOnly.getTime() === todayOnly.getTime()) {
      return 'Today';
    } else if (dateOnly.getTime() === tomorrowOnly.getTime()) {
      return 'Tomorrow';
    } else {
      return date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    }
  };

  const formatTemp = (temp) => {
    return temp > 0 ? `+${temp}°` : `${temp}°`;
  };

  if (loading) {
    return (
      <div className="daily-forecast-section">
        <h2>Daily Forecast</h2>
        <div className="daily-forecast-grid">
          {[1, 2, 3, 4, 5, 6, 7].map(i => (
            <div key={i} className="daily-card">
              <Skeleton width="100%" height="140px" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="daily-forecast-section">
        <h2>Daily Forecast</h2>
        <div className="error-message">
          <p>{error}</p>
          <button onClick={loadForecast} className="retry-btn">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!forecast.length) return null;

  return (
    <div className="daily-forecast-section">
      <h2 className="section-title section-title-forecast">Daily Forecast</h2>
      <div className="daily-forecast-grid">
        {forecast.map((day, index) => (
          <div key={index} className="daily-card">
            <span className="daily-date">{formatDate(day.date)}</span>
            <div className="daily-icon">
              {getWeatherIcon(day.condition, 52)}
            </div>
            <div className="daily-temps">
              <span className="temp-high">{formatTemp(day.tempMax)}</span>
              <span className="temp-divider">/</span>
              <span className="temp-low">{formatTemp(day.tempMin)}</span>
            </div>
            <span className="daily-condition">{day.weather.description}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default memo(DailyForecast);
