import { useState, useEffect } from 'react';
import { weatherAPI } from '../api/weather';
import { citiesAPI } from '../api/cities';
import Skeleton from './Skeleton';
import './WeatherWidget.css';

export default function WeatherWidget({ city, onRemove, isFavorite }) {
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
        <div className="temp-display">
          <span className="temp-value">{Math.round(weather.temperature)}°</span>
          <span className="temp-unit">C</span>
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
