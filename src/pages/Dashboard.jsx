import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { citiesAPI } from '../api/cities';
import CitySearch from '../components/CitySearch';
import WeatherWidget from '../components/WeatherWidget';
import './Dashboard.css';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadFavorites();
  }, []);

  const loadFavorites = async () => {
    try {
      const data = await citiesAPI.getFavorites();
      setFavorites(data);
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

  const handleCitySelect = async (city) => {
    try {
      await citiesAPI.addFavorite(city.id);
      loadFavorites();
    } catch (error) {
      console.error('Failed to add favorite:', error);
    }
  };

  const handleRemoveFavorite = () => {
    loadFavorites();
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>WeatherInsight</h1>
          <div className="header-actions">
            <span className="user-name">{user?.username}</span>
            <button onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="search-section">
            <h2>Search for a city</h2>
            <CitySearch onCitySelect={handleCitySelect} />
          </div>

          <div className="favorites-section">
            <h2>Your Favorite Cities</h2>

            {loading && <div className="loading-message">Loading favorites...</div>}

            {!loading && favorites.length === 0 && (
              <div className="empty-message">
                <p>No favorite cities yet.</p>
                <p className="empty-hint">Search for a city above to add it to your favorites.</p>
              </div>
            )}

            {!loading && favorites.length > 0 && (
              <div className="weather-grid">
                {favorites.map((city) => (
                  <WeatherWidget
                    key={city.id}
                    city={city}
                    isFavorite={true}
                    onRemove={handleRemoveFavorite}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
