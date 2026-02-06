
# Cognitive Recycling Infrastructure AI Dashboard

## Overview
A modern, real-time waste management intelligence dashboard featuring live detection simulation, predictive analytics, and interactive visualizations. Built with React, TypeScript, Tailwind CSS, and Recharts.

---

## 🎨 Design System

### Theme
- **Dark mode primary** with optional light mode toggle
- **Primary Green**: #10B981 (sustainability)
- **Secondary Blue**: #3B82F6 (technology)  
- **Accent Orange**: #F59E0B (alerts/warnings)
- **Dark Background**: #0F172A with subtle gradients
- **Glassmorphism cards** with backdrop blur effects

### Typography
- Modern sans-serif fonts
- Monospace styling for logs/timestamps

---

## 📄 Pages & Navigation

### 1. Landing Page (`/`)
- Animated gradient hero with floating particles effect
- Title: "Autonomous Waste Intelligence for Smart Cities"
- Tagline: "Detect → Reason → Decide → Quantify → Improve"
- CTA buttons linking to dashboard and features
- Feature highlights with scroll animations
- Deployment pricing cards (3 tiers)
- Impact calculator section
- System architecture visualization
- Professional footer

### 2. Live Dashboard (`/dashboard`)
- **Split-screen layout**:
  - Left: Simulated video feed with animated bounding boxes
  - Right: Real-time decision stream (color-coded routing)
- Real-time metrics cards with counter animations
- Predictive alert banner with action buttons
- Dual-agent flow visualization
- Quick stats overview

### 3. Analytics (`/analytics`)
- **Line Chart**: 7-day contamination trends
- **Pie Chart**: Waste stream distribution
- **Bar Chart**: Items by category
- **Area Chart**: Accuracy over time
- Date range selector
- Export functionality

### 4. Alerts (`/alerts`)
- Filterable alert history table
- Severity badges (warning, critical, info)
- Alert details with recommendations
- Mark as resolved/dismissed
- Search and filter controls

### 5. About (`/about`)
- Project overview and mission
- Technology stack breakdown
- Team/contact information
- GitHub link

---

## ⚡ Core Features

### Live Detection Simulation
- Randomized waste item detection (bottles, cups, containers, etc.)
- Confidence scores (0.85-0.99)
- Animated bounding boxes appearing/disappearing
- 30 FPS indicator display
- Updates every 2 seconds

### Decision Stream
- Scrolling log with timestamps
- Color-coded routing decisions:
  - 🔵 Blue: Recyclable
  - 🟢 Green: Organic
  - ⚪ Gray: Landfill
  - 🔴 Red: Manual Inspection
  - 🟠 Orange: Hazardous

### Metrics Dashboard
6 KPI cards with real-time updates:
- Items Processed Today (animated counter)
- Contamination Alerts (badge)
- System Accuracy (% with trend)
- Efficiency Score (progress bar)
- CO₂ Saved (green badge)
- Recovery Value (dollar amount)

### Predictive Alert System
- Prominent warning card
- Displays contamination predictions
- Shows impact analysis
- Action buttons (Dismiss / Take Action)
- Pulsing animation for urgency

### Impact Calculator
- Input: Items/day, contamination rate
- Output: CO₂ savings, revenue potential, labor reduction
- Interactive sliders

---

## 🔧 Technical Implementation

### Components Structure
- Layout components with responsive sidebar
- Reusable metric cards
- Chart wrappers
- Alert components
- Detection simulation hooks
- Mock data generators

### Animations (CSS/Tailwind)
- Fade-in on scroll
- Counter animations
- Pulsing alerts
- Smooth hover transitions
- Gradient background animation

### Data Simulation
- Real-time mock data generators
- Random detection events
- Dynamic metric updates
- Alert simulation

---

## 📱 Responsive Design
- Mobile-first approach
- Collapsible navigation sidebar
- Stacked layouts on small screens
- Touch-friendly interactions
- All breakpoints: sm/md/lg/xl

---

## 🚀 Additional Features
- Dark/Light mode toggle
- Toast notifications for alerts
- Search/filter in decision stream
- Export reports as PDF
- Notification badge system

