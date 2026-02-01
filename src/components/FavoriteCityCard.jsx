import { useState, useEffect, memo } from 'react';
import { weatherAPI } from '../api/weather';
import { citiesAPI } from '../api/cities';
import {
  WiDaySunny, WiCloudy, WiRain, WiSnow, WiThunderstorm,
  WiFog, WiDayCloudy
} from 'react-icons/wi';
import './FavoriteCityCard.css';

const getWeatherIcon = (condition, size = 48) => {
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

function FavoriteCityCard({ city, onRemove, onSelect }) {
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
    try {
      await citiesAPI.removeFavorite(city.id);
      if (onRemove) onRemove();
    } catch (err) {
      console.error('Failed to remove favorite:', err);
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
