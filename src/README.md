# Weather Insight Frontend

React + Vite frontend with custom caching hooks and ML visualizations.

## Overview

Built with React 18.3 and Vite. Uses Context API for auth, custom hooks for caching weather data, and Recharts for trend visualizations.

## Tech Stack

- **Framework:** React 18.3
- **Build Tool:** Vite 6.0
- **Routing:** React Router v7
- **State Management:** React Context API + Custom Hooks
- **Styling:** CSS Modules with responsive design
- **Charts:** Recharts 3.7
- **HTTP Client:** Axios 1.13 with interceptors
- **Icons:** React Icons 5.5

## Project Structure

```
src/
├── components/                 # Reusable UI components
│   ├── HeroWeatherCard.jsx     # Main city weather display
│   ├── FavoriteCityCard.jsx    # Favorite city cards
│   ├── DailyForecast.jsx       # 5-day forecast
│   ├── CitySearch.jsx          # City search modal
│   ├── AddCityCard.jsx         # Add city button
│   ├── WeatherBackground.jsx   # Animated weather background
│   ├── ProfileDropdown.jsx     # User profile menu
│   ├── Spinner.jsx             # Loading spinner
│   │
│   ├── AnomalyDetection.jsx    # ML: Anomaly detection UI
│   ├── TrendAnalysis.jsx       # ML: Trend analysis with charts
│   ├── PatternClustering.jsx   # ML: Pattern clustering UI
│   └── MLInsights.css          # ML components styling
│
├── pages/                      # Route pages
│   ├── Dashboard.jsx           # Main dashboard (/dashboard)
│   ├── MLInsights.jsx          # ML insights page (/ml-insights)
│   ├── Login.jsx               # Login page (/login)
│   └── Register.jsx            # Register page (/register)
│
├── context/                    # React Context
│   └── AuthContext.jsx         # Authentication state & methods
│
├── hooks/                      # Custom React hooks
│   ├── useCachedWeather.js     # Weather caching hook (10-min TTL)
│   └── useCachedForecast.js    # Forecast caching hook (10-min TTL)
│
├── api/                        # API client modules
│   ├── auth.js                 # Auth endpoints (login, register, profile)
│   ├── weather.js              # Weather endpoints (current, forecast)
│   ├── cities.js               # City endpoints (search, favorites)
│   └── ml.js                   # ML endpoints (anomalies, trends, patterns)
│
├── utils/                      # Utility functions
│   ├── guestCities.js          # Guest mode localStorage helpers
│   └── localStorage.js         # localStorage wrapper
│
├── App.jsx                     # Root component with routing
├── App.css                     # Global styles
├── main.jsx                    # React DOM entry point
└── index.css                   # Base CSS reset
```

## Key Features

### Component Structure

**Pages (stateful)**
- Dashboard - Manages favorites and selected city
- MLInsights - City selection for ML analysis
- Login/Register - Form handling

**Components (memoized)**
- HeroWeatherCard - Uses cached weather/forecast
- FavoriteCityCard - Memoized with React.memo
- WeatherBackground - Only re-renders on city change
- DailyForecast - Uses cached forecast data

### Performance

**Custom Caching Hooks**
```javascript
const { weather, loading, error } = useCachedWeather(cityName);
const { forecast, loading, error } = useCachedForecast(cityName);
```
- Caches for 10 minutes
- Deduplicates simultaneous requests (3 components requesting same city = 1 API call)
- Reduces API calls by ~66%

**React.memo** - Prevents re-renders
- WeatherBackground, FavoriteCityCard, ML components
- Only re-renders when props actually change

**useMemo** - Memoizes calculations
- Chart data prep in TrendAnalysis
- Forecast processing in DailyForecast

**useCallback** - Stabilizes functions
- Event handlers in Dashboard
- Prevents child components from re-rendering

### Authentication

```javascript
const { user, login, logout, register } = useAuth();
```

- JWT tokens stored in localStorage
- Auto-injects token in Axios requests
- Protected routes redirect to login
- Guest mode: stores up to 10 cities in localStorage (30-day expiration)
- Guest data migrates to DB on signup

### Charts

Uses Recharts for trend visualization in TrendAnalysis component:
- Temperature line chart with confidence bands
- Responsive and mobile-friendly
- Custom tooltips

### Responsive

Breakpoints: 320px (mobile), 375px, 768px (tablet), 1024px (desktop), 1440px

Mobile optimizations:
- Touch-friendly 44px buttons
- Scrollable city cards
- No hover states (actions always visible)

### Animated Backgrounds

WeatherBackground component changes gradient and particles based on weather:
- Clear: purple gradient with particles
- Rain: dark blue with rain animation
- Snow: light blue with snow particles
- Smooth transitions between conditions

## Getting Started

### Installation
```bash
npm install
```

### Development
```bash
npm run dev  # Starts on http://localhost:5173
```

### Build
```bash
npm run build  # Outputs to /dist
```

### Preview Production Build
```bash
npm run preview
```

## Configuration

### Environment Variables
Create `.env` in project root:
```env
VITE_API_URL=http://localhost:8000
```

**Usage in code:**
```javascript
const API_URL = import.meta.env.VITE_API_URL;
```

### Vite Config
```javascript
// vite.config.js
export default {
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000'  // Optional: proxy API requests
    }
  }
}
```

## API Integration

### Axios Setup
**Interceptors** - Automatic token injection
```javascript
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Error Handling:**
- 401 → Redirect to login (token expired)
- 404 → Show friendly error (data not available yet)
- 500 → Show retry option

### API Modules
Each API module exports typed functions:
```javascript
// api/weather.js
export const weatherAPI = {
  getCurrentWeather: (cityName) => axios.get(`/api/weather/current/${cityName}`),
  getForecast: (cityName, days) => axios.get(`/api/weather/forecast/${cityName}?days=${days}`)
};
```

## Styling Approach

### CSS Modules
Component-scoped styles prevent conflicts:
```jsx
import styles from './HeroWeatherCard.module.css';

<div className={styles.card}>...</div>
```

### Global Styles
- **index.css** - CSS reset, base typography
- **App.css** - Layout, common utilities
- **MLInsights.css** - Shared ML component styles

### Color Palette
```css
:root {
  --primary: #3b82f6;      /* Blue */
  --success: #10b981;      /* Green */
  --warning: #f59e0b;      /* Orange */
  --danger: #dc2626;       /* Red */
  --dark: #1e293b;         /* Dark gray */
}
```

## React Patterns Used

- Custom hooks (useCachedWeather, useCachedForecast)
- Context API (AuthContext)
- Memoization (React.memo, useMemo, useCallback)
- Code splitting (React.lazy for pages)
- Optimistic updates

---

For backend documentation, see [../backend/README.md](../backend/README.md)

For architecture details, see [../ARCHITECTURE.md](../ARCHITECTURE.md)
