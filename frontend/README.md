# Galaxy Chatbot Frontend 🌌

A beautiful React-based animated galaxy-themed chatbot interface for the News Intelligence Agent.

## Features ✨

- **Animated Galaxy Background**: 150-200 randomly positioned animated stars with upward drift
- **Glassmorphism Chat Container**: Semi-transparent overlay with backdrop blur effect
- **Cloud-Shaped Chat Bubbles**: User messages (white) and bot messages (gradient purple/blue)
- **Responsive Design**: Mobile-friendly with proper breakpoints
- **Smooth Animations**: Message fade-in effects and star animations
- **Real-time Chat**: Interactive messaging with typing indicators
- **Backend Integration**: Ready to connect with the Flask backend API

## Visual Design 🎨

### Galaxy Background
- Dark gradient background transitioning from deep navy (#0a0e27) to black (#000000)
- 150-200 randomly positioned white stars (2-4px circles with varying opacity 0.3-1.0)
- Continuous upward star animation using CSS keyframes (15-25 seconds at varying speeds)
- Stars respawn at the bottom when they exit the top for infinite effect
- Subtle white glow/blur using CSS box-shadow

### Chat Container
- Semi-transparent overlay (background: rgba(255, 255, 255, 0.05))
- Backdrop-filter: blur(10px) for glassmorphism effect
- Rounded corners (border-radius: 24px)
- Soft shadow: box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3)
- Max-width: 800px, centered on screen
- Height: 80vh with proper padding (32px)

### Chat Bubbles (Cloud-Shaped)
- **User Messages**: White background, left-aligned, border-radius: 20px 20px 20px 4px
- **Bot Messages**: Gradient purple/blue background, right-aligned, border-radius: 20px 20px 4px 20px
- Both have max-width: 70%, padding: 16px 20px, margin-bottom: 16px

## Technical Implementation 🔧

### Component Structure
```
App
├── GalaxyBackground (stars animation layer)
├── ChatContainer
│   ├── ChatHeader (optional title)
│   ├── MessagesWindow (scrollable)
│   │   └── MessageBubble components
│   └── InputArea
│       ├── TextInput
│       └── SendButton
```

### State Management
- `useState` for messages array
- `useState` for input value
- `useRef` for auto-scrolling to latest message
- `useEffect` to scroll chat window when new messages arrive

### Key Features
- Auto-scroll to bottom when new message added
- Enter key support for message submission
- Empty message prevention
- Smooth animations with CSS transitions
- Responsive design for mobile and desktop

## Setup & Installation 🚀

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

   Or manually install dependencies:
   ```bash
   npm install
   npm start
   ```

3. The application will open at `http://localhost:3000`

## Development 🛠️

### Available Scripts
- `npm start` - Runs the app in development mode
- `npm build` - Builds the app for production
- `npm test` - Launches the test runner

### Backend Integration
The frontend is configured to proxy API requests to the Flask backend running on `http://localhost:8000`. Make sure the backend server is running before testing the chat functionality.

### API Endpoints
- `POST /api/chat` - Send message to chatbot
- Expected response format: `{ response: "bot message" }`

## Browser Support 🌐

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Accessibility ♿

- High contrast mode support
- Reduced motion support
- Keyboard navigation
- Screen reader friendly
- Proper ARIA labels

## Performance ⚡

- GPU-accelerated animations using CSS transforms
- Optimized re-renders with React best practices
- Lazy loading of components
- Efficient star generation and animation

## Customization 🎨

You can easily customize:
- Star count and animation speed in `GalaxyBackground.js`
- Color schemes in CSS files
- Animation durations and easing
- Chat bubble styling
- Responsive breakpoints

## License 📄

This project is part of the News Intelligence Agent system.