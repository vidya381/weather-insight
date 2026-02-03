/**
 * Guest Cities Management
 * Handles localStorage operations for guest users' favorite cities
 */

const GUEST_CITIES_KEY = 'guest_cities';
const GUEST_CITIES_TIMESTAMP_KEY = 'guest_cities_timestamp';
const EXPIRATION_DAYS = 30;

/**
 * Get all guest cities from localStorage
 */
export const getGuestCities = () => {
  try {
    const cities = localStorage.getItem(GUEST_CITIES_KEY);
    return cities ? JSON.parse(cities) : [];
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
    // Add guest prefix to ID if it doesn't have one
    const guestCity = {
      ...city,
      id: city.id?.toString().startsWith('guest-') ? city.id : `guest-${Date.now()}-${city.id}`,
      addedAt: new Date().toISOString()
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
  const filtered = cities.filter(c => c.id !== cityId);
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
