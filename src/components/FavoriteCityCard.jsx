import { useState, useEffect, memo } from 'react';
import { weatherAPI } from '../api/weather';
import { citiesAPI } from '../api/cities';
import { removeGuestCity, setPrimaryGuestCity } from '../utils/guestCities';
import {
  IoSunny, IoPartlySunny, IoCloud, IoRainy, IoSnow,
  IoThunderstorm, IoCloudyNight, IoStar, IoStarOutline
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

function FavoriteCityCard({ city, onRemove, onSelect, onPrimaryChange, isAuthenticated = true }) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [settingPrimary, setSettingPrimary] = useState(false);
  const [removing, setRemoving] = useState(false);

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

    if (removing) return;

    setRemoving(true);

    try {
      if (isAuthenticated) {
        // Remove from API for authenticated users
        await citiesAPI.removeFavorite(city.id);
      } else {
        // Remove from localStorage for guests
        removeGuestCity(city.id);
      }

      // Only update UI after successful removal
      if (onRemove) onRemove(city);
    } catch (err) {
      console.error('Failed to remove favorite:', err);
      alert('Failed to remove city. Please try again.');
      setRemoving(false);
    }
  };

  const handleSetPrimary = async (e) => {
    e.stopPropagation();

    if (city.is_primary || settingPrimary) return;

    setSettingPrimary(true);

    try {
      if (isAuthenticated) {
        await citiesAPI.setPrimaryCity(city.id);
      } else {
        setPrimaryGuestCity(city.id);
      }

      if (onPrimaryChange) {
        onPrimaryChange(city.id);
      }
    } catch (err) {
      console.error('Failed to set primary city:', err);
    } finally {
      setSettingPrimary(false);
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
      <button
        className={`star-btn ${city.is_primary ? 'is-primary' : ''}`}
        onClick={handleSetPrimary}
        title={city.is_primary ? 'Primary city' : 'Set as primary city'}
        disabled={settingPrimary}
      >
        {city.is_primary ? <IoStar size={18} /> : <IoStarOutline size={18} />}
      </button>

      <button
        className="remove-btn"
        onClick={handleRemove}
        title="Remove from favorites"
        disabled={removing}
      >
        {removing ? '...' : '×'}
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
