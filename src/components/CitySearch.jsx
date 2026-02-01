import { useState } from 'react';
import { citiesAPI } from '../api/cities';
import './CitySearch.css';

export default function CitySearch({ onCitySelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);

  const handleSearch = async (searchQuery) => {
    setQuery(searchQuery);

    if (searchQuery.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    setLoading(true);
    try {
      const cities = await citiesAPI.searchCities(searchQuery);
      setResults(cities);
      setShowResults(true);
    } catch (error) {
      console.error('Search failed:', error);
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
        onChange={(e) => handleSearch(e.target.value)}
        onBlur={() => setTimeout(() => setShowResults(false), 200)}
        onFocus={() => query.length >= 2 && setShowResults(true)}
        className="search-input"
      />

      {showResults && (
        <div className="search-results">
          {loading && <div className="search-loading">Searching...</div>}

          {!loading && results.length === 0 && (
            <div className="search-empty">No cities found</div>
          )}

          {!loading &&
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
