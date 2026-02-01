import { useState, useEffect, memo } from 'react';
import { weatherAPI } from '../api/weather';
import { citiesAPI } from '../api/cities';
import Skeleton from './Skeleton';
import {
  WiDaySunny, WiCloudy, WiRain, WiSnow, WiThunderstorm,
  WiFog, WiDayCloudy, WiNightClear, WiNightCloudy
} from 'react-icons/wi';
import './WeatherWidget.css';

const getWeatherIcon = (condition, size = 80) => {
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

function WeatherWidget({ city, onRemove, isFavorite }) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [favLoading, setFavLoading] = useState(false);

  useEffect(() => {
    loadWeather();
  }, [city]);

  const loadWeather = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await weatherAPI.getCurrentWeather(city.name);
      setWeather(data);
    } catch (err) {
      setError('Failed to load weather');
      console.error('Weather load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFavoriteToggle = async () => {
    setFavLoading(true);
    try {
      if (isFavorite) {
        await citiesAPI.removeFavorite(city.id);
      } else {
        await citiesAPI.addFavorite(city.id);
      }
      // Reload or notify parent component
      if (onRemove && isFavorite) {
        onRemove(city.id);
      }
    } catch (err) {
      console.error('Favorite toggle error:', err);
    } finally {
      setFavLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="weather-widget">
        <div className="widget-header">
          <div style={{ flex: 1 }}>
            <Skeleton width="60%" height="1.5rem" />
            <Skeleton width="40%" height="0.875rem" style={{ marginTop: '0.5rem' }} />
          </div>
        </div>
        <div className="widget-content">
          <div className="temp-display">
            <Skeleton width="120px" height="4rem" />
          </div>
          <div className="weather-details">
            <Skeleton variant="rect" height="3rem" />
            <Skeleton variant="rect" height="3rem" />
            <Skeleton variant="rect" height="3rem" />
            <Skeleton variant="rect" height="3rem" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weather-widget error">
        <div className="error-text">{error}</div>
        <button onClick={loadWeather} className="retry-btn">
          Retry
        </button>
      </div>
    );
  }

  if (!weather) return null;

  // Color-code temperature
  const getTemperatureClass = (temp) => {
    if (temp >= 30) return 'hot';
    if (temp >= 20) return 'warm';
    if (temp >= 10) return 'cool';
    return 'cold';
  };

  const tempClass = getTemperatureClass(weather.temperature);

  return (
    <div className="weather-widget">
      <div className="widget-header">
        <div>
          <h3 className="city-title">
            {weather.city}, {weather.country}
          </h3>
          <p className="weather-desc">{weather.weather.description}</p>
        </div>
        <button
          onClick={handleFavoriteToggle}
          className={`fav-btn ${isFavorite ? 'active' : ''}`}
          disabled={favLoading}
          title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          {isFavorite ? '★' : '☆'}
        </button>
      </div>

      <div className="widget-content">
        <div className="temp-main">
          <div className="weather-icon-wrapper">
            {getWeatherIcon(weather.weather.main)}
          </div>
          <div className="temp-display">
            <span className={`temp-value ${tempClass}`}>{Math.round(weather.temperature)}°</span>
          </div>
        </div>

        <div className="weather-details">
          <div className="detail-item">
            <span className="detail-label">Feels like</span>
            <span className="detail-value">{Math.round(weather.feels_like)}°C</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Humidity</span>
            <span className="detail-value">{weather.humidity}%</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Wind</span>
            <span className="detail-value">{weather.wind.speed} m/s</span>
          </div>
          <div className="detail-item">
            <span className="detail-label">Pressure</span>
            <span className="detail-value">{weather.pressure} hPa</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default memo(WeatherWidget);
