import { useState, useEffect } from 'react';
import { useDebounce } from '../hooks/useDebounce';
import { citiesAPI } from '../api/cities';
import './CitySearch.css';

export default function CitySearch({ onCitySelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const debouncedQuery = useDebounce(query, 400);

  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    handleSearch(debouncedQuery);
  }, [debouncedQuery]);

  const handleSearch = async (searchQuery) => {
    setLoading(true);
    setError(null);
    try {
      const cities = await citiesAPI.searchCities(searchQuery);
      setResults(cities);
      setShowResults(true);
    } catch (err) {
      console.error('Search failed:', err);
      setError('Failed to search cities. Please try again.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (city) => {
    setQuery('');
    setResults([]);
    setShowResults(false);
    onCitySelect(city);
  };

  return (
    <div className="city-search">
      <input
        type="text"
        placeholder="Search for a city..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onBlur={() => setTimeout(() => setShowResults(false), 200)}
        onFocus={() => query.length >= 2 && setShowResults(true)}
        className="search-input"
      />

      {showResults && (
        <div className="search-results">
          {loading && <div className="search-loading">Searching...</div>}

          {!loading && error && (
            <div className="search-error">{error}</div>
          )}

          {!loading && !error && results.length === 0 && (
            <div className="search-empty">No cities found for "{query}"</div>
          )}

          {!loading && !error &&
            results.map((city) => (
              <div
                key={city.id}
                className="search-result-item"
                onClick={() => handleSelect(city)}
              >
                <span className="city-name">{city.name}</span>
                <span className="city-country">{city.country}</span>
              </div>
            ))}
        </div>
      )}
    </div>
  );
}
