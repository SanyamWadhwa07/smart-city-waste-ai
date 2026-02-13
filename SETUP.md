# CogniRecycle - Setup & Professional UI Guide

## 🚀 Quick Start

### Prerequisites

- **Node.js** (v16 or higher) - [Install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)
- **npm** (comes with Node.js)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/SanyamWadhwa07/smart-city-waste-ai.git
   cd smart-city-waste-ai
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   
   Navigate to [http://localhost:8080](http://localhost:8080)

## 📦 Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run build:dev` - Build in development mode
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint for code quality
- `npm run test` - Run tests once
- `npm run test:watch` - Run tests in watch mode

## 🎨 Professional UI Enhancements

The UI has been professionally enhanced with modern design patterns:

### Visual Design Improvements

#### 1. Enhanced Color System
- **Dynamic Gradients** - Smooth, animated gradients throughout the app
- **Professional Color Palette** - Balanced primary (green), secondary (blue), and accent (orange) colors
- **Improved Contrast** - Better text readability and visual hierarchy

#### 2. Modern Effects
- **Glass Morphism** - Backdrop blur effects on cards and navigation
- **Shine Effects** - Subtle shine animations on key elements
- **Hover Animations** - Lift, scale, and shadow effects on interactive elements
- **Floating Particles** - Animated background particles for visual interest

#### 3. Typography & Spacing
- **Larger Headlines** - More impactful hero text (5xl-7xl)
- **Better Line Heights** - Improved readability with proper leading
- **Professional Font Weights** - Balanced bold, semibold, and medium weights
- **Generous Spacing** - Increased padding and margins (space-8, space-10)

#### 4. Component Styling
- **Pro Cards** - Enhanced card components with hover effects
- **Rounded Corners** - Consistent border-radius (xl, 2xl)
- **Shadow System** - Layered shadows for depth (shadow-lg, shadow-2xl)
- **Icon Containers** - Gradient backgrounds for icon wrapping

### Page-by-Page Enhancements

#### Landing Page
- ✨ **Hero Section**: Larger text, gradient headings, animated particles
- 🎯 **Stats Cards**: Increased size, better spacing, hover effects
- 🎨 **Feature Cards**: Icon animations, improved hover states
- 💰 **Pricing Cards**: Enhanced recommended tier, better CTA buttons
- 🔗 **Footer**: Improved social icons with hover animations

#### Dashboard
- 📊 **Metrics**: Better status indicators with animated pulse
- 📈 **Charts**: Professional card styling for all chart containers
- 🎯 **Header**: Larger typography, gradient text effects

#### Analytics
- 📉 **Charts**: Consistent pro-card styling across all charts
- 🎛️ **Controls**: Enhanced dropdown and export buttons
- 🎨 **Visual Hierarchy**: Better card titles and descriptions

#### About Page
- 🎓 **Mission Card**: Larger text, better badge styling
- 💻 **Tech Stack**: Hover effects on technology cards
- 👥 **Team**: Gradient avatars, improved card layout
- 🔗 **Resources**: Enhanced button styling with hover effects

#### Alerts
- 🚨 **Alert Cards**: Better severity indicators
- 🔍 **Filters**: Professional search and dropdown styling
- 📋 **Detail Panel**: Improved layout and typography

## 🎨 CSS Utility Classes

New utility classes added to `src/index.css`:

```css
.pro-card          /* Professional card with hover effects */
.gradient-text     /* Animated gradient text */
.gradient-bg       /* Animated gradient background */
.premium-gradient  /* Premium overlay gradient */
.hover-lift        /* Hover lift animation */
.shine            /* Shine effect overlay */
```

## 🛠️ Technology Stack

### Frontend Framework
- **React 18.3.1** - Modern React with hooks
- **TypeScript 5.8.3** - Type-safe development
- **Vite 5.4.19** - Lightning-fast build tool

### UI & Styling
- **Tailwind CSS 3.4.17** - Utility-first CSS framework
- **shadcn/ui** - High-quality React components
- **Radix UI** - Accessible component primitives
- **Lucide React** - Beautiful icon system

### State & Data
- **React Router 6.30.1** - Client-side routing
- **TanStack Query 5.83.0** - Data fetching and caching
- **React Hook Form 7.61.1** - Form management
- **Zod 3.25.76** - Schema validation

### Visualization
- **Recharts 2.15.4** - Composable charting library
- **Embla Carousel 8.6.0** - Smooth carousel component

### Development Tools
- **ESLint** - Code linting
- **Vitest** - Unit testing
- **TypeScript ESLint** - TypeScript linting

## 📁 Project Structure

```
smart-city-waste-ai/
├── src/
│   ├── components/
│   │   ├── dashboard/       # Dashboard components
│   │   ├── landing/         # Landing page components
│   │   ├── layout/          # Layout components
│   │   └── ui/              # shadcn/ui components
│   ├── pages/               # Page components
│   │   ├── LandingPage.tsx  # Home/landing page
│   │   ├── DashboardPage.tsx # Main dashboard
│   │   ├── AnalyticsPage.tsx # Analytics & charts
│   │   ├── AlertsPage.tsx   # Alert management
│   │   ├── AboutPage.tsx    # About information
│   │   └── NotFound.tsx     # 404 page
│   ├── hooks/               # Custom React hooks
│   ├── lib/                 # Utilities & mock data
│   │   ├── utils.ts         # Utility functions
│   │   └── mockData.ts      # Demo data
│   ├── test/                # Test files
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles & animations
├── public/                  # Static assets
│   └── robots.txt
├── index.html               # HTML template
├── package.json             # Dependencies
├── tailwind.config.ts       # Tailwind config
├── vite.config.ts           # Vite config
├── tsconfig.json            # TypeScript config
└── vitest.config.ts         # Test config
```

## 🎯 Key Features

### AI & Detection
- **Real-time Detection** - YOLOv8-powered object recognition
- **Dual-Agent System** - Cross-validation for 99%+ accuracy
- **Smart Routing** - Automatic waste categorization
- **Predictive Analytics** - Contamination trend forecasting

### User Experience
- **Responsive Design** - Works on all screen sizes
- **Dark Theme** - Professional dark mode throughout
- **Smooth Animations** - Staggered fade-ins and transitions
- **Interactive Charts** - Real-time data visualization

### Performance
- **Edge Processing** - Can run on Raspberry Pi
- **Fast Build Times** - Vite's instant HMR
- **Optimized Bundle** - Tree-shaking and code splitting
- **Type Safety** - Full TypeScript coverage

## 🎨 Customization Guide

### Changing Colors

Edit color variables in `src/index.css`:

```css
:root {
  --primary: 160 84% 39%;      /* Green */
  --secondary: 217 91% 60%;    /* Blue */
  --accent: 38 92% 50%;        /* Orange */
}
```

### Adding Components

All UI components are in `src/components/ui/` and follow shadcn/ui patterns.

### Modifying Animations

Animation keyframes are at the bottom of `src/index.css`:
- `gradient-shift` - Text gradient animation
- `gradient-move` - Background gradient animation
- `fade-in-up` - Fade in with upward motion
- `shine` - Shine effect overlay
- `float` - Floating particle animation

## 🚀 Deployment

### Build for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 🧪 Testing

Run tests:
```bash
npm run test
```

Run tests in watch mode:
```bash
npm run test:watch
```

## 📊 Performance

The app is optimized for:
- Fast initial load
- Smooth animations (60fps)
- Efficient re-renders
- Minimal bundle size

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

MIT License

---

**Built with ❤️ for Smart Cities**
