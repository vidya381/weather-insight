import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { citiesAPI } from '../api/cities';
import { getGuestCities } from '../utils/guestCities';
import AnomalyDetection from '../components/AnomalyDetection';
import TrendAnalysis from '../components/TrendAnalysis';
import PatternClustering from '../components/PatternClustering';
import ProfileDropdown from '../components/ProfileDropdown';
import ProfileEditModal from '../components/ProfileEditModal';
import WeatherBackground from '../components/WeatherBackground';
import Spinner from '../components/Spinner';
import { IoCloud, IoSparkles, IoHome, IoAnalytics, IoTrendingUp, IoBulb, IoGitNetwork } from 'react-icons/io5';
import './Dashboard.css';
import './MLInsights.css';

export default function MLInsights() {
  const { user, isAuthenticated, logout, updateUser } = useAuth();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showProfileEdit, setShowProfileEdit] = useState(false);

  useEffect(() => {
    loadFavorites();
  }, [isAuthenticated]);

  const loadFavorites = async () => {
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
      if (data.length > 0 && !selectedCity) {
        setSelectedCity(data[0]);
      }
    } catch (error) {
      console.error('Failed to load favorites:', error);
      // For guests, just use empty array on error
      if (!isAuthenticated) {
        setFavorites([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/dashboard');
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
              onClick={() => navigate('/dashboard')}
              className="header-btn header-btn-home"
            >
              <IoHome size={20} />
              <span>Dashboard</span>
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

      <main className="dashboard-main">
        <div className="dashboard-content">
          {!loading && favorites.length > 0 && (
            <div className="ml-insights-header">
              <div className="ml-title-section">
                <h2>ML Insights</h2>
              </div>
              <div className="city-selector">
                <label htmlFor="city-select">Select City:</label>
                <select
                  id="city-select"
                  value={selectedCity?.id || ''}
                  onChange={(e) => {
                    const city = favorites.find(c => c.id === Number(e.target.value));
                    setSelectedCity(city);
                  }}
                  className="ml-select"
                >
                  {favorites.map((city) => (
                    <option key={city.id} value={city.id}>
                      {city.name}, {city.country}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}

          {loading && <Spinner text="Loading ML insights..." />}

          {!loading && favorites.length === 0 && (
            <div className="hero-section">
              <div className="empty-state">
                <div className="empty-icon-wrapper">
                  <IoAnalytics className="empty-ml-icon" size={80} />
                </div>
                <h2 className="empty-title">Unlock Weather Insights</h2>
                <p className="empty-subtitle">
                  Add favorite cities to unlock powerful ML-driven weather analytics and predictions
                </p>

                <div className="empty-features">
                  <div className="empty-feature">
                    <IoBulb size={24} />
                    <span>Anomaly Detection</span>
                  </div>
                  <div className="empty-feature">
                    <IoTrendingUp size={24} />
                    <span>Trend Analysis</span>
                  </div>
                  <div className="empty-feature">
                    <IoGitNetwork size={24} />
                    <span>Pattern Clustering</span>
                  </div>
                </div>

                <button
                  className="btn-primary btn-cta"
                  onClick={() => navigate('/dashboard')}
                >
                  Add Your First City
                </button>
              </div>
            </div>
          )}

          {!loading && selectedCity && (
            <div className="ml-insights-content">
              <AnomalyDetection cityName={selectedCity.name} />
              <TrendAnalysis cityName={selectedCity.name} />
              <PatternClustering cityName={selectedCity.name} />
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
