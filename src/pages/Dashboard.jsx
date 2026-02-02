import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { citiesAPI } from '../api/cities';
import CitySearch from '../components/CitySearch';
import HeroWeatherCard from '../components/HeroWeatherCard';
import DailyForecast from '../components/DailyForecast';
import FavoriteCityCard from '../components/FavoriteCityCard';
import AddCityCard from '../components/AddCityCard';
import WeatherBackground from '../components/WeatherBackground';
import ProfileDropdown from '../components/ProfileDropdown';
import ProfileEditModal from '../components/ProfileEditModal';
import Spinner from '../components/Spinner';
import { IoCloudyNight, IoAnalytics, IoSparkles, IoTrendingUp, IoLocationSharp } from 'react-icons/io5';
import './Dashboard.css';

export default function Dashboard() {
  const { user, logout, updateUser } = useAuth();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [showSearch, setShowSearch] = useState(false);
  const [showProfileEdit, setShowProfileEdit] = useState(false);
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
      } else if (data.length === 0) {
        setSelectedCity(null);
      }
      return data;
    } catch (err) {
      console.error('Failed to load favorites:', err);
      setError('Failed to load your favorite cities. Please try again.');
      return [];
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
    const updatedFavorites = await loadFavorites();
    // If the removed city was the selected one, select the first available
    if (updatedFavorites.length > 0) {
      setSelectedCity(updatedFavorites[0]);
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

  const handleEditProfile = () => {
    setShowProfileEdit(true);
  };

  const handleProfileUpdateSuccess = (updatedUser) => {
    updateUser(updatedUser);
  };

  return (
    <div className="dashboard">
      {/* Dynamic weather background */}
      <WeatherBackground city={selectedCity} />

      <header className="dashboard-header">
        <div className="header-content">
          <div className="logo-section">
            <IoCloudyNight className="logo-icon" size={32} />
            <h1>WeatherInsight</h1>
          </div>
          <div className="header-actions">
            <button
              onClick={() => navigate('/ml-insights')}
              className="header-btn header-btn-ml"
            >
              <IoAnalytics size={18} />
              <span>ML Insights</span>
            </button>
            <ProfileDropdown
              username={user?.username}
              onLogout={handleLogout}
              onEditProfile={handleEditProfile}
            />
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
              <div className="empty-state">
                <div className="empty-icon-wrapper">
                  <IoCloudyNight className="empty-weather-icon" size={80} />
                </div>
                <h2 className="empty-title">Welcome to WeatherInsight</h2>
                <p className="empty-subtitle">
                  Track weather for your favorite cities in one beautiful dashboard
                </p>

                <div className="empty-features">
                  <div className="empty-feature">
                    <IoSparkles size={24} />
                    <span>Real-time Updates</span>
                  </div>
                  <div className="empty-feature">
                    <IoTrendingUp size={24} />
                    <span>7-Day Forecasts</span>
                  </div>
                  <div className="empty-feature">
                    <IoLocationSharp size={24} />
                    <span>Multiple Cities</span>
                  </div>
                </div>

                <button
                  className="btn-primary btn-cta"
                  onClick={handleAddCityClick}
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

      {/* Profile Edit Modal */}
      {showProfileEdit && (
        <ProfileEditModal
          user={user}
          onClose={() => setShowProfileEdit(false)}
          onSuccess={handleProfileUpdateSuccess}
        />
      )}
    </div>
  );
}
