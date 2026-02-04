import { useState, useEffect, useRef, useCallback } from 'react';
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
import { IoCloud, IoAnalytics, IoSparkles, IoTrendingUp, IoLocationSharp, IoSunny, IoInformationCircle } from 'react-icons/io5';
import { getGuestCities, addGuestCity, removeGuestCity, checkAndClearExpiredGuestData, clearGuestCities } from '../utils/guestCities';
import './Dashboard.css';

export default function Dashboard() {
  const { user, isAuthenticated, logout, updateUser } = useAuth();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [showSearch, setShowSearch] = useState(false);
  const [showProfileEdit, setShowProfileEdit] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const searchSectionRef = useRef(null);

  useEffect(() => {
    // Check and clear expired guest data on mount
    checkAndClearExpiredGuestData();

    // Load favorites (guest or authenticated)
    loadFavorites();

    // Clear guest data when user logs in (existing account)
    // Migration only happens on signup via Register page
    if (isAuthenticated) {
      const guestCities = getGuestCities();
      if (guestCities.length > 0) {
        // User logged in with guest cities - clear them
        clearGuestCities();
      }
    }
  }, [isAuthenticated]);

  const loadFavorites = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      let data;

      if (isAuthenticated) {
        // Load from API for authenticated users
        data = await citiesAPI.getFavorites();
      } else {
        // Load from localStorage for guests
        data = getGuestCities();
      }

      setFavorites(data);
      // Set primary city as selected hero city, or first city if no primary
      if (data.length > 0 && !selectedCity) {
        const primaryCity = data.find(city => city.is_primary);
        setSelectedCity(primaryCity || data[0]);
      } else if (data.length === 0) {
        setSelectedCity(null);
      }
      return data;
    } catch (err) {
      console.error('Failed to load favorites:', err);
      if (isAuthenticated) {
        setError('Failed to load your favorite cities. Please try again.');
      } else {
        // For guests, just use empty array if there's an error
        setFavorites([]);
      }
      return [];
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, selectedCity]);

  const handleLogout = () => {
    logout();
    navigate('/dashboard');
  };

  const handleCitySelect = useCallback(async (city) => {
    try {
      if (isAuthenticated) {
        // Save to API for authenticated users
        await citiesAPI.addFavorite(city.id);
      } else {
        // Save to localStorage for guests
        addGuestCity(city);
      }
      await loadFavorites();
      setShowSearch(false);
    } catch (error) {
      console.error('Failed to add favorite:', error);
    }
  }, [isAuthenticated, loadFavorites]);

  const handleRemoveFavorite = useCallback(async (removedCity) => {
    // Check if removed city was primary
    const wasPrimary = removedCity.is_primary;

    // Optimistic update - remove immediately from UI
    let updatedFavorites = favorites.filter(city => city.id !== removedCity.id);

    // If removed city was primary and there are remaining cities, set the first one as primary
    if (wasPrimary && updatedFavorites.length > 0) {
      updatedFavorites = updatedFavorites.map((city, index) => ({
        ...city,
        is_primary: index === 0
      }));
    }

    setFavorites(updatedFavorites);

    // If the removed city was the selected one, select the first available
    if (selectedCity?.id === removedCity.id) {
      if (updatedFavorites.length > 0) {
        setSelectedCity(updatedFavorites[0]);
      } else {
        setSelectedCity(null);
      }
    }
  }, [favorites, selectedCity]);

  const handleCityCardSelect = useCallback((city) => {
    setSelectedCity(city);
  }, []);

  const handlePrimaryChange = useCallback(async (cityId) => {
    // Reload favorites to get updated order and is_primary flags
    await loadFavorites();
  }, [loadFavorites]);

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
          <div className="logo-section" onClick={() => navigate('/dashboard')}>
            <div className="logo-icon-wrapper">
              <IoCloud className="logo-icon logo-cloud" size={32} />
              <IoSparkles className="logo-icon logo-sparkle" size={16} />
            </div>
            <h1>WeatherInsight</h1>
          </div>
          <div className="header-actions">
            <button
              onClick={() => navigate('/ml-insights')}
              className="header-btn header-btn-ml"
            >
              <IoAnalytics size={20} />
              <span>ML Insights</span>
            </button>
            {isAuthenticated ? (
              <ProfileDropdown
                username={user?.username}
                onLogout={handleLogout}
                onEditProfile={handleEditProfile}
              />
            ) : (
              <button
                onClick={() => navigate('/login')}
                className="header-btn-signin"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Guest Mode Badge */}
      {!isAuthenticated && (
        <div className="guest-badge-container">
          <div className="guest-badge">
            Guest Mode •{' '}
            <button onClick={() => navigate('/register')} className="guest-badge-link">
              Sign up
            </button>{' '}
            to sync
          </div>
        </div>
      )}

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
                  <IoSunny className="empty-weather-icon" size={80} />
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
                    onPrimaryChange={handlePrimaryChange}
                    isAuthenticated={isAuthenticated}
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
