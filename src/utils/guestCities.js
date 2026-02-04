/**
 * Guest Cities Management
 * Handles localStorage operations for guest users' favorite cities
 */

const GUEST_CITIES_KEY = 'guest_cities';
const GUEST_CITIES_TIMESTAMP_KEY = 'guest_cities_timestamp';
const EXPIRATION_DAYS = 30;

/**
 * Get all guest cities from localStorage
 * Returns cities sorted by is_primary (primary first), then by addedAt
 */
export const getGuestCities = () => {
  try {
    const cities = localStorage.getItem(GUEST_CITIES_KEY);
    const parsed = cities ? JSON.parse(cities) : [];

    // Sort by is_primary (true first), then by addedAt (newest first)
    return parsed.sort((a, b) => {
      if (a.is_primary && !b.is_primary) return -1;
      if (!a.is_primary && b.is_primary) return 1;
      return new Date(b.addedAt) - new Date(a.addedAt);
    });
  } catch (error) {
    console.error('Error reading guest cities:', error);
    return [];
  }
};

/**
 * Save guest cities to localStorage
 */
export const saveGuestCities = (cities) => {
  try {
    localStorage.setItem(GUEST_CITIES_KEY, JSON.stringify(cities));
    localStorage.setItem(GUEST_CITIES_TIMESTAMP_KEY, Date.now().toString());
  } catch (error) {
    console.error('Error saving guest cities:', error);
  }
};

/**
 * Add a city to guest favorites
 */
export const addGuestCity = (city) => {
  const cities = getGuestCities();

  // Check if city already exists (by id or by name+country)
  const exists = cities.some(
    c => c.id === city.id || (c.name === city.name && c.country === city.country)
  );

  if (!exists) {
    // Check if this is the first city
    const isFirstCity = cities.length === 0;

    // Add guest prefix to ID if it doesn't have one
    const guestCity = {
      ...city,
      id: city.id?.toString().startsWith('guest-') ? city.id : `guest-${Date.now()}-${city.id}`,
      addedAt: new Date().toISOString(),
      is_primary: isFirstCity  // First city is automatically primary
    };

    cities.push(guestCity);
    saveGuestCities(cities);
  }

  return cities;
};

/**
 * Remove a city from guest favorites
 */
export const removeGuestCity = (cityId) => {
  const cities = getGuestCities();

  // Check if the city being removed is primary
  const removedCity = cities.find(c => c.id === cityId);
  const wasPrimary = removedCity?.is_primary;

  const filtered = cities.filter(c => c.id !== cityId);

  // If removed city was primary and there are remaining cities, set the first one as primary
  if (wasPrimary && filtered.length > 0) {
    filtered[0].is_primary = true;
  }

  saveGuestCities(filtered);
  return filtered;
};

/**
 * Clear all guest cities
 */
export const clearGuestCities = () => {
  try {
    localStorage.removeItem(GUEST_CITIES_KEY);
    localStorage.removeItem(GUEST_CITIES_TIMESTAMP_KEY);
  } catch (error) {
    console.error('Error clearing guest cities:', error);
  }
};

/**
 * Check if guest data has expired and clear if needed
 */
export const checkAndClearExpiredGuestData = () => {
  try {
    const timestamp = localStorage.getItem(GUEST_CITIES_TIMESTAMP_KEY);

    if (timestamp) {
      const age = Date.now() - parseInt(timestamp);
      const expirationMs = EXPIRATION_DAYS * 24 * 60 * 60 * 1000;

      if (age > expirationMs) {
        clearGuestCities();
        return true; // Data was expired and cleared
      }
    }

    return false; // Data is still valid or doesn't exist
  } catch (error) {
    console.error('Error checking guest data expiration:', error);
    return false;
  }
};

/**
 * Get count of guest cities
 */
export const getGuestCitiesCount = () => {
  return getGuestCities().length;
};

/**
 * Check if a city is in guest favorites
 */
export const isGuestFavorite = (cityId) => {
  const cities = getGuestCities();
  return cities.some(c => c.id === cityId);
};

/**
 * Set a city as primary favorite for guest
 * Unsets all other primary cities
 */
export const setPrimaryGuestCity = (cityId) => {
  const cities = getGuestCities();

  // Unset all primary flags
  const updatedCities = cities.map(city => ({
    ...city,
    is_primary: city.id === cityId
  }));

  saveGuestCities(updatedCities);
  return updatedCities;
};
