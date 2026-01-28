# Temperature Converter

A simple, modern temperature converter built with React and Vite. This is a **learning project** focused on understanding React fundamentals, state management, and modern frontend development practices.

## 🎯 Learning Objectives

This project was built to practice:
- React hooks (`useState`, `useEffect`)
- Component state management
- Event handling in React
- localStorage for persisting user preferences
- Responsive design with CSS
- Dark mode implementation

## ✨ Features

- **5 Temperature Scales**: Convert between Celsius, Fahrenheit, Kelvin, Rankine, and Réaumur
- **Dark Mode**: Toggle between light and dark themes (preference saved to localStorage)
- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop
- **Visual Thermometer**: Animated mercury display
- **Keyboard Support**: Press Enter to convert
- **Clean UI**: Modern gradient design with smooth animations

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone https://github.com/vidya381/temperature-converter.git
cd temperature-converter
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

## 🏗️ Building for Production

```bash
npm run build
```

The production-ready files will be in the `dist` folder.

## 🛠️ Technologies Used

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **CSS3** - Styling with gradients, animations, and flexbox
- **localStorage API** - Persisting theme preference

## 📚 Project Structure

```
temperature-converter/
├── src/
│   ├── App.jsx          # Main component with conversion logic
│   ├── App.css          # Component-specific styles
│   ├── main.jsx         # React entry point
│   └── index.css        # Global styles
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
└── vite.config.js       # Vite configuration
```

## 🧮 How It Works

### Conversion Logic

All temperatures are first converted to Celsius as an intermediate step, then converted to the target scale:

```
Input Temperature → Celsius → Output Temperature
```

**Example conversions:**
- Celsius to Fahrenheit: `(°C × 9/5) + 32`
- Fahrenheit to Celsius: `(°F - 32) × 5/9`
- Kelvin to Celsius: `K - 273.15`

## 🎨 Features Breakdown

### Temperature Conversion
- Supports 5 different temperature scales
- Real-time conversion on button click
- Input validation to ensure numeric values

### Dark Mode
- Toggle between light and dark themes
- Preference saved to browser localStorage
- Smooth transitions between themes
- Different gradient backgrounds for each theme

### Responsive Design
- Mobile-first approach
- Breakpoint at 600px for mobile devices
- Flexible layout that adapts to screen size

## 🌱 What I Learned

Building this project helped me understand:

1. **React State Management**: Using `useState` to manage multiple pieces of state
2. **Side Effects**: Using `useEffect` for localStorage operations and DOM manipulation
3. **Event Handling**: onClick, onChange, onKeyPress events
4. **Controlled Components**: Inputs controlled by React state
5. **CSS Animations**: Creating smooth transitions and animations
6. **Responsive Design**: Media queries and flexible layouts

## 🔮 Future Enhancements

Potential features to add for further learning:
- [ ] Unit conversion history
- [ ] Voice input (Web Speech API)
- [ ] Temperature comparison chart
- [ ] More temperature scales
- [ ] Export results
- [ ] PWA support

## 📝 Notes

This is a learning project to strengthen frontend development skills, particularly React. It's intentionally kept simple to focus on core concepts rather than complex features.

## 📄 License

MIT License - Feel free to use this project for learning purposes.

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are welcome! Feel free to open an issue.

## 👤 Author

**Vidya Sagar Reddy Desu**

---

*Built with React + Vite as part of my frontend learning journey* 🚀
