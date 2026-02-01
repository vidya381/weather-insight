import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { citiesAPI } from '../api/cities';
import CitySearch from '../components/CitySearch';
import HeroWeatherCard from '../components/HeroWeatherCard';
import DailyForecast from '../components/DailyForecast';
import FavoriteCityCard from '../components/FavoriteCityCard';
import AddCityCard from '../components/AddCityCard';
import ThemeToggle from '../components/ThemeToggle';
import Spinner from '../components/Spinner';
import './Dashboard.css';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [showSearch, setShowSearch] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const searchSectionRef = useRef(null);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await citiesAPI.getFavorites();
      setFavorites(data);
      // Set first city as selected hero city
      if (data.length > 0 && !selectedCity) {
        setSelectedCity(data[0]);
      }
    } catch (err) {
      console.error('Failed to load favorites:', err);
      setError('Failed to load your favorite cities. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleCitySelect = async (city) => {
    try {
      await citiesAPI.addFavorite(city.id);
      await loadFavorites();
      setShowSearch(false);
    } catch (error) {
      console.error('Failed to add favorite:', error);
    }
  };

  const handleRemoveFavorite = async () => {
    await loadFavorites();
    // If the removed city was the selected one, select the first available
    if (favorites.length > 0) {
      setSelectedCity(favorites[0]);
    } else {
      setSelectedCity(null);
    }
  };

  const handleCityCardSelect = (city) => {
    setSelectedCity(city);
  };

  const handleAddCityClick = () => {
    setShowSearch(true);
    // Scroll to search section
    setTimeout(() => {
      searchSectionRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>WeatherInsight</h1>
          <div className="header-actions">
            <button
              onClick={() => navigate('/ml-insights')}
              className="btn-secondary"
            >
              ML Insights
            </button>
            <span className="user-name">{user?.username}</span>
            <ThemeToggle />
            <button onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          {/* Search Section - conditionally shown */}
          {showSearch && (
            <div className="search-section" ref={searchSectionRef}>
              <div className="search-header">
                <h2>Search for a city</h2>
                <button
                  className="close-search-btn"
                  onClick={() => setShowSearch(false)}
                  title="Close search"
                >
                  ×
                </button>
              </div>
              <CitySearch onCitySelect={handleCitySelect} />
            </div>
          )}

          {/* Hero Section */}
          {loading && (
            <div className="hero-section">
              <Spinner text="Loading weather data..." />
            </div>
          )}

          {!loading && error && (
            <div className="hero-section">
              <div className="error-message">
                <p>{error}</p>
                <button onClick={loadFavorites} className="retry-btn">
                  Retry
                </button>
              </div>
            </div>
          )}

          {!loading && !error && favorites.length === 0 && (
            <div className="hero-section">
              <div className="empty-message">
                <h3>Welcome to WeatherInsight</h3>
                <p>No favorite cities yet.</p>
                <p className="empty-hint">Click the button below to add your first city.</p>
                <button
                  className="btn-primary"
                  onClick={handleAddCityClick}
                  style={{ marginTop: '1rem' }}
                >
                  Add Your First City
                </button>
              </div>
            </div>
          )}

          {!loading && !error && selectedCity && (
            <div className="hero-section">
              <HeroWeatherCard city={selectedCity} />
            </div>
          )}

          {/* Daily Forecast Section */}
          {!loading && !error && selectedCity && (
            <DailyForecast city={selectedCity} />
          )}

          {/* Favorites Section - Horizontal Scroll */}
          {!loading && !error && favorites.length > 0 && (
            <div className="favorites-section">
              <h2>Favorite Cities</h2>
              <div className="favorites-scroll">
                {favorites.map((city) => (
                  <FavoriteCityCard
                    key={city.id}
                    city={city}
                    onRemove={handleRemoveFavorite}
                    onSelect={handleCityCardSelect}
                  />
                ))}
                <AddCityCard onClick={handleAddCityClick} />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
