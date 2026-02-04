import React, { useState, useEffect } from 'react';
import { useCachedWeather } from '../hooks/useCachedWeather';
import './WeatherBackground.css';

const WeatherBackground = ({ city }) => {
  // Use cached weather to prevent duplicate API calls
  const { weather } = useCachedWeather(city?.name);
  const [particles, setParticles] = useState([]);

  // Get background gradient based on weather and time
  const getBackgroundGradient = () => {
    if (!weather) {
      return 'linear-gradient(135deg, #1e2029 0%, #252937 100%)';
    }

    const condition = weather.weather?.main?.toLowerCase() || 'clear';
    const hour = new Date().getHours();
    const isNight = hour < 6 || hour > 20;

    // Base gradients for different weather conditions
    const gradients = {
      clear: isNight
        ? 'linear-gradient(135deg, #1a1d2e 0%, #2a2d3f 100%)'
        : 'linear-gradient(135deg, #2a3142 0%, #3a4152 100%)',
      clouds: 'linear-gradient(135deg, #1e2029 0%, #2d3340 100%)',
      rain: 'linear-gradient(135deg, #1a1f2e 0%, #242938 100%)',
      drizzle: 'linear-gradient(135deg, #1c212e 0%, #262b38 100%)',
      thunderstorm: 'linear-gradient(135deg, #14161f 0%, #1e2029 100%)',
      snow: 'linear-gradient(135deg, #1e2433 0%, #2a2f3f 100%)',
      mist: 'linear-gradient(135deg, #1e2029 0%, #2a2f3c 100%)',
      fog: 'linear-gradient(135deg, #1e2029 0%, #2a2f3c 100%)',
      haze: 'linear-gradient(135deg, #1e2029 0%, #2a2f3c 100%)',
    };

    return gradients[condition] || gradients.clear;
  };

  // Generate particles for weather effects
  useEffect(() => {
    if (!weather) return;

    const condition = weather.weather?.main?.toLowerCase() || '';
    let particleCount = 0;
    let particleType = '';

    // Determine particle type and count
    if (condition === 'rain' || condition === 'drizzle') {
      particleCount = condition === 'rain' ? 100 : 60;
      particleType = 'rain';
    } else if (condition === 'snow') {
      particleCount = 80;
      particleType = 'snow';
    } else if (condition === 'thunderstorm') {
      particleCount = 120;
      particleType = 'rain';
    }

    // Generate particles
    if (particleCount > 0) {
      const newParticles = Array.from({ length: particleCount }, (_, i) => ({
        id: i,
        type: particleType,
        left: Math.random() * 100,
        animationDuration: particleType === 'rain'
          ? 0.5 + Math.random() * 0.5
          : 2 + Math.random() * 3,
        animationDelay: Math.random() * 2,
        opacity: 0.3 + Math.random() * 0.4,
        size: particleType === 'rain'
          ? 1 + Math.random() * 2
          : 2 + Math.random() * 4,
      }));
      setParticles(newParticles);
    } else {
      setParticles([]);
    }
  }, [weather]);

  return (
    <div
      className="weather-background"
      style={{ background: getBackgroundGradient() }}
    >
      {/* Particle effects */}
      <div className="particles-container">
        {particles.map((particle) => (
          <div
            key={particle.id}
            className={`particle particle-${particle.type}`}
            style={{
              left: `${particle.left}%`,
              animationDuration: `${particle.animationDuration}s`,
              animationDelay: `${particle.animationDelay}s`,
              opacity: particle.opacity,
              width: `${particle.size}px`,
              height: particle.type === 'rain'
                ? `${particle.size * 10}px`
                : `${particle.size}px`,
            }}
          />
        ))}
      </div>

      {/* Lightning effect for thunderstorms */}
      {weather?.weather?.main?.toLowerCase() === 'thunderstorm' && (
        <div className="lightning-overlay" />
      )}

      {/* Fog overlay for misty conditions */}
      {['mist', 'fog', 'haze'].includes(weather?.weather?.main?.toLowerCase()) && (
        <div className="fog-overlay" />
      )}
    </div>
  );
};

export default WeatherBackground;
