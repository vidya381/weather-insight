# Weather Insight Frontend

React-based frontend with intelligent caching, ML insights visualization, and responsive design.

## Overview

The frontend is built with React 18.3 and Vite, featuring a modern component architecture with performance optimizations, custom hooks, and seamless API integration.

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

### Component Architecture

#### Smart Components (Stateful)
- **Dashboard** - Manages favorites, selected city, loading states
- **MLInsights** - Handles city selection for ML analysis
- **Login/Register** - Form state and validation

#### Presentational Components (Memoized)
- **HeroWeatherCard** - Uses `useCachedWeather` and `useCachedForecast`
- **FavoriteCityCard** - Memoized with React.memo
- **WeatherBackground** - Memoized, re-renders only on city change
- **DailyForecast** - Uses `useCachedForecast`

### Performance Optimizations

#### 1. Custom Caching Hooks
**useCachedWeather.js** - Prevents duplicate API calls
```javascript
const { weather, loading, error } = useCachedWeather(cityName);
```

**Features:**
- 10-minute TTL cache
- In-flight request deduplication
- Single API call even if 3+ components request same city
- Reduces API calls by 66%

**useCachedForecast.js** - Same pattern for forecast data
```javascript
const { forecast, loading, error } = useCachedForecast(cityName);
```

#### 2. React.memo
Prevents unnecessary re-renders for expensive components:
- `WeatherBackground` - Only re-renders when city changes
- `FavoriteCityCard` - Only re-renders when props change
- `AnomalyDetection`, `TrendAnalysis`, `PatternClustering`

#### 3. useMemo
Memoizes expensive calculations:
- Chart data preparation in `TrendAnalysis`
- Forecast processing in `DailyForecast`

#### 4. useCallback
Stabilizes function references in Dashboard:
```javascript
const handleCitySelect = useCallback(async (city) => {
  // Implementation
}, [isAuthenticated, loadFavorites]);
```

### Authentication System

**AuthContext.jsx** - Centralized auth state
```javascript
const { user, login, logout, register } = useAuth();
```

**Features:**
- JWT token management (localStorage)
- Automatic token injection (Axios interceptors)
- Protected routes (redirect to login if not authenticated)
- User profile state

**Guest Mode:**
- Try app without signup
- Store cities in localStorage (max 10)
- 30-day expiration
- Migrate to database on signup

### Data Visualization

**Recharts Integration** - `TrendAnalysis.jsx`
```jsx
<LineChart data={chartData}>
  <Line type="monotone" dataKey="temperature" stroke="#3b82f6" />
  <Line type="monotone" dataKey="upper" stroke="#10b981" strokeDasharray="3 3" />
  <Line type="monotone" dataKey="lower" stroke="#10b981" strokeDasharray="3 3" />
</LineChart>
```

**Features:**
- Temperature trends with confidence bands
- Responsive charts (mobile-friendly)
- Tooltips with detailed data
- Custom styling

### Responsive Design

**Breakpoints:**
- **320px** - Small mobile (iPhone SE)
- **375px** - Mobile (iPhone 12/13)
- **768px** - Tablet
- **1024px** - Desktop
- **1440px** - Large desktop

**Mobile Optimizations:**
- Touch-friendly buttons (44px min height)
- Scrollable favorite cities
- Collapsible forecast
- No hover states (always visible actions)

### Dynamic Backgrounds

**WeatherBackground.jsx** - Animated weather-themed backgrounds
```javascript
getBackgroundGradient(condition) {
  switch(condition) {
    case 'Clear': return 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    case 'Rain': return 'linear-gradient(135deg, #4b6cb7 0%, #182848 100%)';
    // ... more conditions
  }
}
```

**Features:**
- Particle animations (rain, snow, clear sky)
- Smooth gradient transitions
- Weather-specific color themes
- Performance-optimized with RAF

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

### Performance
- **Service Worker:** Cache API responses offline
- **Image Optimization:** WebP format, lazy loading
- **Bundle Analysis:** Code splitting by route

## Learning Resources

### React Patterns Used
- Custom Hooks (useCachedWeather, useCachedForecast)
- Context API (AuthContext)
- Compound Components (WeatherCard with subcomponents)
- Render Props (CitySearch modal)
- Higher-Order Components (coming soon: withAuth)

### Performance Patterns
- Memoization (React.memo, useMemo, useCallback)
- Code Splitting (React.lazy, Suspense)
- Caching (custom TTL cache)
- Optimistic Updates (instant UI feedback)

---

For backend documentation, see [../backend/README.md](../backend/README.md)

For architecture details, see [../ARCHITECTURE.md](../ARCHITECTURE.md)
