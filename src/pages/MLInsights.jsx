import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { citiesAPI } from '../api/cities';
import AnomalyDetection from '../components/AnomalyDetection';
import TrendAnalysis from '../components/TrendAnalysis';
import PatternClustering from '../components/PatternClustering';
import ProfileDropdown from '../components/ProfileDropdown';
import ProfileEditModal from '../components/ProfileEditModal';
import Spinner from '../components/Spinner';
import { IoCloud, IoSparkles, IoHome } from 'react-icons/io5';
import './Dashboard.css';
import './MLInsights.css';

export default function MLInsights() {
  const { user, logout, updateUser } = useAuth();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showProfileEdit, setShowProfileEdit] = useState(false);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const data = await citiesAPI.getFavorites();
      setFavorites(data);
      if (data.length > 0 && !selectedCity) {
        setSelectedCity(data[0]);
      }
    } catch (error) {
      console.error('Failed to load favorites:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleEditProfile = () => {
    setShowProfileEdit(true);
  };

  const handleProfileUpdateSuccess = (updatedUser) => {
    updateUser(updatedUser);
  };

  return (
    <div className="dashboard">
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
              <IoHome size={18} />
              <span>Dashboard</span>
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
          <div className="ml-insights-header">
            <h2>ML Insights</h2>
            {!loading && favorites.length > 0 && (
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
            )}
          </div>

          {loading && <Spinner text="Loading ML insights..." />}

          {!loading && favorites.length === 0 && (
            <div className="empty-message">
              <p>No favorite cities yet.</p>
              <p className="empty-hint">
                Add cities to your favorites from the dashboard to see ML insights.
              </p>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-primary"
                style={{ marginTop: '1rem' }}
              >
                Go to Dashboard
              </button>
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
