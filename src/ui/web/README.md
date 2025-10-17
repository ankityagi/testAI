# StudyBuddy React Frontend

Modern, responsive React frontend for the StudyBuddy educational platform.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- FastAPI backend running on `http://localhost:8000`

### Installation

```bash
cd src/ui/web
npm install
```

### Development

```bash
npm run dev
```

The app will start on `http://localhost:5173` with hot module replacement.

### Build

```bash
npm run build
```

Production build output: `dist/`

## 📁 Project Structure

```
src/ui/web/
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── panels/        # Feature panels (Children, Practice, Progress, Standards)
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── Toast.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/          # React contexts for state management
│   │   ├── AuthContext.tsx
│   │   ├── ChildrenContext.tsx
│   │   └── PracticeContext.tsx
│   ├── pages/             # Top-level page components
│   │   ├── Auth.tsx       # Login/Signup
│   │   ├── Dashboard.tsx  # Main application
│   │   └── ThemeDemo.tsx  # Design system showcase
│   ├── services/          # API client and service layer
│   │   ├── apiClient.ts   # Axios instance with interceptors
│   │   ├── auth.service.ts
│   │   ├── children.service.ts
│   │   ├── questions.service.ts
│   │   ├── progress.service.ts
│   │   └── standards.service.ts
│   ├── types/             # TypeScript type definitions
│   │   └── api.ts
│   ├── App.tsx            # Root component with routing
│   └── main.tsx           # Application entry point
├── vite.config.ts         # Vite configuration with proxy
├── tsconfig.json          # TypeScript configuration
├── .env.example           # Environment variable template
└── package.json
```

## 🎨 Features

### Authentication
- Login and signup forms
- JWT token management
- Protected routes with automatic redirects
- Logout functionality

### Child Management
- Add/edit/delete child profiles
- Grade and ZIP code tracking
- Child selection for personalized practice

### Practice Sessions
- Subject/topic/difficulty selection
- Interactive multiple-choice questions
- Real-time feedback (correct/incorrect)
- Session statistics (accuracy, questions answered)
- Subtopic-based adaptive learning

### Progress Tracking
- Overall accuracy and streak visualization
- Subject-specific breakdown
- Color-coded progress bars
- Motivational empty states

### Standards Reference
- Browse Common Core standards
- Filter by subject and grade
- Organized by domain and sub-domain

## 🔧 Configuration

### Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

```env
# Development (uses Vite proxy to localhost:8000)
VITE_API_BASE_URL=

# Production
VITE_API_BASE_URL=https://your-api-domain.com
```

## 🧪 Testing & Quality

```bash
# Format code
npm run format

# Check formatting
npm run format:check

# Type check
npm run typecheck

# Lint
npm run lint

# Run all checks
npm run format:check && npm run typecheck && npm run lint
```

## 🎨 Design System

Located in `../../core/theme/`:

- **Colors**: iOS-inspired palette with primary, success, error, and neutral colors
- **Typography**: Readable font scale (xs to 7xl)
- **Spacing**: Consistent 4px-based spacing scale
- **Animations**: Smooth transitions with spring-based easing
- **Shadows**: Subtle elevation for depth
- **Border Radius**: Friendly rounded corners

View the design system at `/theme-demo` route.

## 🏗️ Architecture

### State Management
Uses React Context API for global state:
- **AuthContext**: User authentication state and token management
- **ChildrenContext**: Child profiles and selection
- **PracticeContext**: Practice session state and question flow

### API Integration
- **Axios** client with request/response interceptors
- Automatic JWT token injection
- Centralized error handling
- Type-safe API calls with TypeScript interfaces

### Routing
- **React Router v7** for client-side routing
- Protected routes with authentication checks
- Automatic redirects for unauthenticated users

## 📦 Production Build

### Build Stats
- Bundle size: ~311KB (98KB gzipped)
- All quality checks passing (format, typecheck, lint)

## 🛠️ Development Workflow

1. **Start backend**: `make dev` (from project root)
2. **Start frontend**: `npm run dev` (from src/ui/web)
3. **Open browser**: `http://localhost:5173`
4. **Make changes**: Files auto-reload on save

## 📚 Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
