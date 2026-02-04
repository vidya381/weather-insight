/**
 * Custom hook for cached weather data
 * Prevents duplicate API calls when multiple components request the same city's weather
 */

import { useState, useEffect, useRef } from 'react';
import { weatherAPI } from '../api/weather';

// Global cache shared across all hook instances
const weatherCache = new Map();
const forecastCache = new Map();
const inflightRequests = new Map();

const CACHE_TTL = 10 * 60 * 1000; // 10 minutes

function isCacheValid(cacheEntry) {
  if (!cacheEntry) return false;
  return Date.now() - cacheEntry.timestamp < CACHE_TTL;
}

export function useCachedWeather(cityName) {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    if (!cityName) {
      setWeather(null);
      setError(null);
      setLoading(false);
      return;
    }

    const loadWeather = async () => {
      setLoading(true);
      setError(null);

      try {
        // Check cache first
        const cached = weatherCache.get(cityName);
        if (isCacheValid(cached)) {
          if (mountedRef.current) {
            setWeather(cached.data);
            setLoading(false);
          }
          return;
        }

        // Check if request is already in-flight
        let weatherPromise = inflightRequests.get(cityName);

        if (!weatherPromise) {
          // Create new request
          weatherPromise = weatherAPI.getCurrentWeather(cityName);
          inflightRequests.set(cityName, weatherPromise);
        }

        // Wait for the request (either new or existing)
        const data = await weatherPromise;

        // Cache the result
        weatherCache.set(cityName, {
          data,
          timestamp: Date.now()
        });

        // Clear in-flight request
        inflightRequests.delete(cityName);

        if (mountedRef.current) {
          setWeather(data);
          setLoading(false);
        }
      } catch (err) {
        inflightRequests.delete(cityName);
        if (mountedRef.current) {
          setError(err?.message || 'Failed to load weather data');
          setLoading(false);
        }
      }
    };

    loadWeather();

    return () => {
      mountedRef.current = false;
    };
  }, [cityName]);

  return { weather, loading, error };
}

export function useCachedForecast(cityName) {
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    if (!cityName) {
      setForecast(null);
      setError(null);
      setLoading(false);
      return;
    }

    const loadForecast = async () => {
      setLoading(true);
      setError(null);

      try {
        // Check cache first
        const cached = forecastCache.get(cityName);
        if (isCacheValid(cached)) {
          if (mountedRef.current) {
            setForecast(cached.data);
            setLoading(false);
          }
          return;
        }

        // Check if request is already in-flight
        const cacheKey = `forecast_${cityName}`;
        let forecastPromise = inflightRequests.get(cacheKey);

        if (!forecastPromise) {
          // Create new request
          forecastPromise = weatherAPI.getForecast(cityName);
          inflightRequests.set(cacheKey, forecastPromise);
        }

        // Wait for the request (either new or existing)
        const data = await forecastPromise;

        // Cache the result
        forecastCache.set(cityName, {
          data,
          timestamp: Date.now()
        });

        // Clear in-flight request
        inflightRequests.delete(cacheKey);

        if (mountedRef.current) {
          setForecast(data);
          setLoading(false);
        }
      } catch (err) {
        inflightRequests.delete(`forecast_${cityName}`);
        if (mountedRef.current) {
          setError(err?.message || 'Failed to load forecast data');
          setLoading(false);
        }
      }
    };

    loadForecast();

    return () => {
      mountedRef.current = false;
    };
  }, [cityName]);

  return { forecast, loading, error };
}

// Utility to clear cache (useful for testing or force refresh)
export function clearWeatherCache() {
  weatherCache.clear();
  forecastCache.clear();
  inflightRequests.clear();
}
