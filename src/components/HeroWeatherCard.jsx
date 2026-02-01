import { useState, useEffect, memo } from 'react';
import { weatherAPI } from '../api/weather';
import Skeleton from './Skeleton';
import {
  WiDaySunny, WiCloudy, WiRain, WiSnow, WiThunderstorm,
  WiFog, WiDayCloudy
} from 'react-icons/wi';
import './HeroWeatherCard.css';

const getWeatherIcon = (condition, size = 120) => {
  const iconProps = { size, className: 'weather-icon' };
  const cond = condition?.toLowerCase() || '';

  if (cond.includes('clear')) return <WiDaySunny {...iconProps} />;
  if (cond.includes('cloud')) return <WiCloudy {...iconProps} />;
  if (cond.includes('rain') || cond.includes('drizzle')) return <WiRain {...iconProps} />;
  if (cond.includes('snow')) return <WiSnow {...iconProps} />;
  if (cond.includes('thunder') || cond.includes('storm')) return <WiThunderstorm {...iconProps} />;
  if (cond.includes('fog') || cond.includes('mist') || cond.includes('haze')) return <WiFog {...iconProps} />;
  return <WiDayCloudy {...iconProps} />;
};

const getSmallWeatherIcon = (condition, size = 32) => {
  return getWeatherIcon(condition, size);
};

function HeroWeatherCard({ city }) {
  const [weather, setWeather] = useState(null);
  const [forecast, setForecast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (city) {
      loadWeatherData();
    }
  }, [city]);

  const loadWeatherData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [currentData, forecastData] = await Promise.all([
        weatherAPI.getCurrentWeather(city.name),
        weatherAPI.getForecast(city.name, 5)
      ]);

      setWeather(currentData);
      // Get first 12 forecast items (next 36 hours in 3-hour intervals)
      setForecast(forecastData.forecast.slice(0, 12));
    } catch (err) {
      setError('Failed to load weather data');
      console.error('Weather load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp * 1000);
    const hours = date.getHours();
    const ampm = hours >= 12 ? 'pm' : 'am';
    const displayHours = hours % 12 || 12;
    return `${displayHours < 10 ? '0' : ''}${displayHours} ${ampm}`;
  };

  const getDayLabel = (timestamp) => {
    const date = new Date(timestamp * 1000);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    // Reset time to midnight for comparison
    const dateOnly = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const todayOnly = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const tomorrowOnly = new Date(tomorrow.getFullYear(), tomorrow.getMonth(), tomorrow.getDate());

    if (dateOnly.getTime() === todayOnly.getTime()) {
      return 'Today';
    } else if (dateOnly.getTime() === tomorrowOnly.getTime()) {
      return 'Tomorrow';
    } else {
      // Return day name for days after tomorrow
      return date.toLocaleDateString('en-US', { weekday: 'short' });
    }
  };

  if (loading) {
    return (
      <div className="hero-weather-card">
        <div className="hero-main">
          <div className="hero-left">
            <Skeleton width="180px" height="8rem" />
            <Skeleton width="120px" height="1.5rem" style={{ marginTop: '1rem' }} />
          </div>
          <div className="hero-stats">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="stat-item">
                <Skeleton width="100%" height="3rem" />
              </div>
            ))}
          </div>
        </div>
        <div className="hourly-forecast">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
            <Skeleton key={i} width="90px" height="110px" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="hero-weather-card error">
        <div className="error-text">{error}</div>
        <button onClick={loadWeatherData} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  if (!weather) return null;

  // Format temperature with proper sign
  const formatTemp = (temp) => {
    const rounded = Math.round(temp);
    return rounded > 0 ? `+${rounded}°` : `${rounded}°`;
  };

  return (
    <div className="hero-weather-card">
      <div className="hero-main">
        <div className="hero-left-group">
          <div className="hero-icon-wrapper">
            {getWeatherIcon(weather.weather.main, 90)}
          </div>

          <div className="hero-info">
            <h2 className="hero-city-name">{weather.city}</h2>
            <p className="hero-country">{weather.country}</p>
          </div>
        </div>

        <div className="hero-temp-section">
          <span className="hero-temperature">{formatTemp(weather.temperature)}</span>
          <div className="hero-temp-info">
            <span className="hero-temp-label">Temperature</span>
            <span className="hero-weather-desc">{weather.weather.description}</span>
          </div>
        </div>

        <div className="hero-stats">
          <div className="stat-item">
            <div className="stat-badge">
              <span className="stat-value">{weather.humidity}</span>
              <span className="stat-unit">%</span>
            </div>
            <span className="stat-label">Humidity</span>
          </div>
          <div className="stat-item">
            <div className="stat-badge">
              <span className="stat-value">{Math.round(weather.wind.speed)}</span>
              <span className="stat-unit">km/h</span>
            </div>
            <span className="stat-label">Wind speed</span>
          </div>
          <div className="stat-item">
            <div className="stat-badge">
              <span className="stat-value">{Math.round(weather.feels_like)}°</span>
            </div>
            <span className="stat-label">Feels like</span>
          </div>
        </div>
      </div>

      {forecast.length > 0 && (
        <div className="hourly-forecast">
          {forecast.map((item, index) => {
            const currentDay = getDayLabel(item.datetime);
            const previousDay = index > 0 ? getDayLabel(forecast[index - 1].datetime) : null;
            const showDayLabel = index === 0 || currentDay !== previousDay;

            return (
              <div key={index} className="hourly-item">
                <span className="hourly-day">{showDayLabel ? currentDay : '\u00A0'}</span>
                <span className="hourly-time">{formatTime(item.datetime)}</span>
                <div className="hourly-icon">
                  {getSmallWeatherIcon(item.weather.main, 32)}
                </div>
                <span className="hourly-temp">{formatTemp(item.temperature)}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default memo(HeroWeatherCard);
