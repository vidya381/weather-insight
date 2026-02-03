import { useState, useEffect, memo } from 'react';
import { weatherAPI } from '../api/weather';
import { citiesAPI } from '../api/cities';
import { removeGuestCity } from '../utils/guestCities';
import {
  IoSunny, IoPartlySunny, IoCloud, IoRainy, IoSnow,
  IoThunderstorm, IoCloudyNight
} from 'react-icons/io5';
import './FavoriteCityCard.css';

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

function FavoriteCityCard({ city, onRemove, onSelect, isAuthenticated = true }) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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
      setError('Failed to load');
      console.error('Weather load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (e) => {
    e.stopPropagation();

    // Optimistically update UI immediately
    if (onRemove) onRemove(city);

    try {
      if (isAuthenticated) {
        // Remove from API for authenticated users
        await citiesAPI.removeFavorite(city.id);
      } else {
        // Remove from localStorage for guests
        removeGuestCity(city.id);
      }
    } catch (err) {
      console.error('Failed to remove favorite:', err);
      // Could add error handling here to revert if needed
    }
  };

  const handleClick = () => {
    if (onSelect && weather) {
      onSelect(city);
    }
  };

  if (loading) {
    return (
      <div className="favorite-city-card loading">
        <div className="city-card-content">
          <div className="loading-spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="favorite-city-card error">
        <div className="city-card-content">
          <p className="error-text">{error}</p>
          <button onClick={loadWeather} className="retry-small">↻</button>
        </div>
      </div>
    );
  }

  if (!weather) return null;

  return (
    <div className="favorite-city-card" onClick={handleClick}>
      <button className="remove-btn" onClick={handleRemove} title="Remove from favorites">
        ×
      </button>

      <div className="city-card-content">
        <div className="city-icon">
          {getWeatherIcon(weather.weather.main, 40)}
        </div>

        <div className="city-info">
          <h3 className="city-card-name">{weather.city}</h3>
          <p className="city-card-country">{weather.country}</p>
        </div>

        <div className="city-temp">
          <span className="temp-main">{Math.round(weather.temperature)}°</span>
          <span className="temp-range">
            /{Math.round(weather.temp_max)}°
          </span>
        </div>
      </div>
    </div>
  );
}

export default memo(FavoriteCityCard);
