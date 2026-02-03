import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { citiesAPI } from '../api/cities';
import { getGuestCities, clearGuestCities } from '../utils/guestCities';
import { IoCloud, IoSparkles } from 'react-icons/io5';
import './Auth.css';

export default function Register() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!username || !email || !password || !confirmPassword) {
      setError('Please fill in all fields');
      return;
    }

    if (username.length < 3) {
      setError('Username must be at least 3 characters');
      return;
    }

    if (username.length > 50) {
      setError('Username must be 50 characters or less');
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    const result = await register(username, email, password);

    if (result.success) {
      // Migrate guest cities for new accounts
      const guestCities = result.guestCities || [];
      if (guestCities.length > 0) {
        try {
          // Process all cities in parallel
          const migrationPromises = guestCities.map(async (city) => {
            try {
              const searchResults = await citiesAPI.searchCities(city.name, 5);
              const matchedCity = searchResults.find(
                c => c.name === city.name && c.country === city.country
              );
              if (matchedCity) {
                await citiesAPI.addFavorite(matchedCity.id);
              }
            } catch (err) {
              console.error('Failed to migrate city:', city.name, err);
            }
          });

          await Promise.all(migrationPromises);
          clearGuestCities();
        } catch (err) {
          console.error('Migration error:', err);
        }
      }

      setLoading(false);
      navigate('/dashboard');
    } else {
      setLoading(false);
      setError(result.error);
    }
  };

  return (
    <div className="auth-container">
      <header className="auth-header">
        <div className="auth-header-content">
          <div className="logo-section" onClick={() => navigate('/dashboard')}>
            <div className="logo-icon-wrapper">
              <IoCloud className="logo-icon logo-cloud" size={28} />
              <IoSparkles className="logo-icon logo-sparkle" size={14} />
            </div>
            <h1 className="logo-text">WeatherInsight</h1>
          </div>
        </div>
      </header>

      <div className="auth-box">
        <h2>Create Account</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={loading}
              autoComplete="new-password"
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
