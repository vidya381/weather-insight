import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // State management
  const [temperature, setTemperature] = useState('')
  const [fromScale, setFromScale] = useState('Celsius')
  const [toScale, setToScale] = useState('Fahrenheit')
  const [result, setResult] = useState('')
  const [darkMode, setDarkMode] = useState(false)

  // Temperature scales
  const scales = ['Celsius', 'Fahrenheit', 'Kelvin', 'Rankine', 'Réaumur']

  // Load dark mode preference from localStorage
  useEffect(() => {
    const savedTheme = localStorage.getItem('darkMode')
    if (savedTheme) {
      setDarkMode(savedTheme === 'true')
    }
  }, [])

  // Apply dark mode class to body
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode')
    } else {
      document.body.classList.remove('dark-mode')
    }
    localStorage.setItem('darkMode', darkMode)
  }, [darkMode])

  // Conversion functions
  const convertToCelsius = (value, scale) => {
    switch (scale) {
      case 'Celsius': return value
      case 'Fahrenheit': return (value - 32) * 5 / 9
      case 'Kelvin': return value - 273.15
      case 'Rankine': return (value - 491.67) * 5 / 9
      case 'Réaumur': return value * 5 / 4
      default: return value
    }
  }

  const convertFromCelsius = (celsius, scale) => {
    switch (scale) {
      case 'Celsius': return celsius
      case 'Fahrenheit': return celsius * 9 / 5 + 32
      case 'Kelvin': return celsius + 273.15
      case 'Rankine': return celsius * 9 / 5 + 491.67
      case 'Réaumur': return celsius * 4 / 5
      default: return celsius
    }
  }

  const handleConvert = () => {
    const temp = parseFloat(temperature)
    if (isNaN(temp)) {
      setResult('Please enter a valid number')
      return
    }

    const celsius = convertToCelsius(temp, fromScale)
    const converted = convertFromCelsius(celsius, toScale)
    setResult(`${temp}° ${fromScale} = ${converted.toFixed(2)}° ${toScale}`)
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
  }

  return (
    <div className={`app ${darkMode ? 'dark' : ''}`}>
      <div className="container">
        <button className="theme-toggle" onClick={toggleDarkMode}>
          {darkMode ? '☀️' : '🌙'}
        </button>

        <h1>Temperature Converter</h1>

        <div className="converter-form">
          <div className="input-group">
            <label>Temperature</label>
            <input
              type="number"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              placeholder="Enter temperature"
              onKeyPress={(e) => e.key === 'Enter' && handleConvert()}
            />
          </div>

          <div className="scale-selectors">
            <div className="input-group">
              <label>From</label>
              <select value={fromScale} onChange={(e) => setFromScale(e.target.value)}>
                {scales.map(scale => (
                  <option key={scale} value={scale}>{scale}</option>
                ))}
              </select>
            </div>

            <div className="arrow">→</div>

            <div className="input-group">
              <label>To</label>
              <select value={toScale} onChange={(e) => setToScale(e.target.value)}>
                {scales.map(scale => (
                  <option key={scale} value={scale}>{scale}</option>
                ))}
              </select>
            </div>
          </div>

          <button className="convert-btn" onClick={handleConvert}>
            Convert
          </button>

          {result && (
            <div className="result">
              {result}
            </div>
          )}
        </div>

        <div className="thermometer">
          <div className="mercury"></div>
        </div>
      </div>
    </div>
  )
}

export default App
