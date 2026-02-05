# Testing

## Frontend Tests

Using Vitest + React Testing Library.

### Running Tests

```bash
npm test                  # Run all tests
npm test -- --watch       # Watch mode
npm run test:ui          # UI mode
npm run test:coverage    # Coverage report
```

### Files

```
src/
├── contexts/
│   └── AuthContext.test.jsx      # Auth context tests
├── hooks/
│   └── useCachedWeather.test.js  # Caching hook tests
└── test/
    └── setup.js                   # Test configuration
```

### Writing Tests

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import MyComponent from './MyComponent';

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### What's Covered

- AuthContext (login, logout, registration)
- useCachedWeather hook (caching, API calls)
- useCachedForecast hook
- TODO: Component tests (Dashboard, MLInsights, WeatherCard)

## Backend Tests

Using pytest with in-memory SQLite.

### Running Tests

```bash
cd backend
source venv/bin/activate

pytest                   # All tests
pytest -v               # Verbose
pytest --cov=app tests/ # Coverage
pytest tests/test_password.py::TestPasswordHashing::test_hash_password  # Specific test
```

### Files

```
backend/tests/
├── conftest.py                  # Fixtures
├── test_password.py             # Password hashing
├── test_ml_algorithms.py        # ML algorithms
├── test_repositories.py         # Repository layer
└── test_weather_storage.py      # Weather storage
```

### Fixtures (conftest.py)

- `db_session` - Fresh database for each test
- `client` - FastAPI test client
- `auth_headers` - Authenticated user with JWT token

```python
def test_protected_endpoint(client, auth_headers):
    response = client.get("/api/protected", headers=auth_headers)
    assert response.status_code == 200
```

### What's Covered

**Password Hashing:**
- Hash generation and verification
- Salt uniqueness
- Bcrypt implementation

**ML Algorithms:**
- Z-score anomaly detection
- Linear regression trend analysis
- K-Means pattern clustering
- Normalization and predictions

**Repositories:**
- City creation and lookup
- Weather data storage
- History queries and aggregates

**Weather Storage:**
- API endpoint integration
- Data retrieval
- Error handling

## Coverage Reports

```bash
# Frontend
npm run test:coverage

# Backend
cd backend
pytest --cov=app --cov-report=html tests/
# Open htmlcov/index.html
```

## Mocking

**Frontend** (Vitest):

```javascript
import { vi } from 'vitest';

vi.mock('../api/auth', () => ({
  authAPI: {
    login: vi.fn(),
  }
}));

authAPI.login.mockResolvedValue({ access_token: 'fake-token' });
```

**Backend** (unittest.mock):

```python
from unittest.mock import patch, MagicMock

@patch('app.services.weather_service.requests.get')
def test_api_call(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"temp": 20}
    mock_get.return_value = mock_response
```

## CI/CD (TODO)

GitHub Actions example (`.github/workflows/test.yml`):

```yaml
name: Tests
on: [push, pull_request]

jobs:
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm test

  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.14'
      - run: pip install -r backend/requirements.txt
      - run: cd backend && pytest
```

## Writing Tests

**Frontend:**
- Mock API calls
- Test happy path + errors
- Check loading states
- Cleanup is automatic (setup.js)

**Backend:**
- Use fixtures (db_session, client, auth_headers)
- Test success + error cases (400, 401, 404, 422)
- Check database state
- Cleanup is automatic

## Common Issues

**Frontend:**

`ReferenceError: localStorage is not defined`
```javascript
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
};
global.localStorage = localStorageMock;
```

`Cannot find module` errors
```bash
npm install  # Reinstall dependencies
```

**Backend:**

`No module named 'app'`
```bash
cd backend && pytest  # Run from backend directory
```

`Import errors`
```bash
touch backend/tests/__init__.py
```

## Tips

**Frontend:**
- Mock API calls, not internal logic
- Use `screen.getByRole()` over `getByTestId()`
- Keep tests fast

**Backend:**
- Use fixtures for setup
- Mock external APIs (OpenWeather)
- Test success + error paths
- Each test should be independent

## TODO

**Frontend:**
- Dashboard, MLInsights, WeatherCard component tests
- Full user flow tests

**Backend:**
- Cities endpoint tests
- Favorite cities tests
- Background job tests
- Edge cases

**E2E:**
- Playwright for end-to-end testing
