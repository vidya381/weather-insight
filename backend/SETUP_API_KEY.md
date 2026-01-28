# OpenWeather API Key Setup

## Quick Setup (5 minutes)

### 1. Get Free API Key

1. Go to: https://openweathermap.org/api
2. Click "Sign Up" (top right)
3. Create free account
4. Verify email
5. Go to: https://home.openweathermap.org/api_keys
6. Copy your API key (starts with a long string of letters/numbers)

### 2. Add to .env File

```bash
# Edit backend/.env
OPENWEATHER_API_KEY=your_api_key_here
```

### 3. Restart Server

```bash
# Stop server (Ctrl+C)
# Start again
python -m app.main
```

### 4. Test Endpoints

Visit: http://localhost:8000/docs

Try:
- `GET /api/weather/current/London`
- `GET /api/weather/forecast/Tokyo`

---

**Note:** Free tier limits:
- 1,000 API calls/day
- 60 calls/minute
- Current weather + 5-day forecast
