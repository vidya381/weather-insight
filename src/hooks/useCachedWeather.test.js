import { describe, it, expect, beforeEach, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useCachedWeather, clearWeatherCache } from './useCachedWeather';
import * as weatherAPI from '../api/weather';

// Mock the weather API
vi.mock('../api/weather', () => ({
  weatherAPI: {
    getCurrentWeather: vi.fn(),
  },
}));

describe('useCachedWeather', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    clearWeatherCache(); // Clear cache between tests
  });

  it('should fetch weather data on first call', async () => {
    const mockWeatherData = {
      city: 'New York',
      temperature: 22.5,
      humidity: 65,
      weather_main: 'Clear',
    };

    weatherAPI.weatherAPI.getCurrentWeather.mockResolvedValue(mockWeatherData);

    const { result } = renderHook(() => useCachedWeather('New York'));

    // Initially loading
    expect(result.current.loading).toBe(true);
    expect(result.current.weather).toBeNull();

    // Wait for data to load
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.weather).toEqual(mockWeatherData);
    expect(result.current.error).toBeNull();
    expect(weatherAPI.weatherAPI.getCurrentWeather).toHaveBeenCalledWith('New York');
  });

  it('should return cached data on subsequent calls within TTL', async () => {
    const mockWeatherData = {
      city: 'London',
      temperature: 15.0,
      humidity: 70,
    };

    weatherAPI.weatherAPI.getCurrentWeather.mockResolvedValue(mockWeatherData);

    // First call
    const { result: result1 } = renderHook(() => useCachedWeather('London'));
    await waitFor(() => expect(result1.current.loading).toBe(false));

    // Second call (should use cache)
    const { result: result2 } = renderHook(() => useCachedWeather('London'));
    await waitFor(() => expect(result2.current.loading).toBe(false));

    // API should only be called once (cache hit on second call)
    expect(weatherAPI.weatherAPI.getCurrentWeather).toHaveBeenCalledTimes(1);
    expect(result2.current.weather).toEqual(mockWeatherData);
  });

  it('should handle API errors', async () => {
    const mockError = new Error('Network error');
    weatherAPI.weatherAPI.getCurrentWeather.mockRejectedValue(mockError);

    const { result } = renderHook(() => useCachedWeather('InvalidCity'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.weather).toBeNull();
    expect(result.current.error).toBeTruthy();
  });

  it('should fetch different data for different cities', async () => {
    const nyData = { city: 'New York', temperature: 22 };
    const laData = { city: 'Los Angeles', temperature: 28 };

    weatherAPI.weatherAPI.getCurrentWeather
      .mockResolvedValueOnce(nyData)
      .mockResolvedValueOnce(laData);

    const { result: result1 } = renderHook(() => useCachedWeather('New York'));
    const { result: result2 } = renderHook(() => useCachedWeather('Los Angeles'));

    await waitFor(() => {
      expect(result1.current.loading).toBe(false);
      expect(result2.current.loading).toBe(false);
    });

    expect(result1.current.weather).toEqual(nyData);
    expect(result2.current.weather).toEqual(laData);
    expect(weatherAPI.weatherAPI.getCurrentWeather).toHaveBeenCalledTimes(2);
  });
});
