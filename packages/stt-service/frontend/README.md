# STT Service Frontend

Modern React + TypeScript frontend for the Speech-to-Text service, built with Vite.

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/      # React components (UploadForm, ProgressBar, etc.)
│   ├── hooks/           # Custom React hooks (useHistory, useJTBD, useUpload)
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions (API helpers)
│   ├── styles/          # CSS and styling files
│   ├── App.tsx          # Main application component
│   └── main.tsx         # Application entry point
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript configuration
└── package.json         # Dependencies and scripts
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend STT service running on `http://localhost:8000`

### Installation

```bash
# Navigate to frontend directory
cd packages/stt-service/frontend

# Install dependencies
npm install
```

### Development

Run the development server on port 5173:

```bash
npm run dev
```

The dev server will start at `http://localhost:5173` with:
- ✨ Hot Module Replacement (HMR) - instant updates on file changes
- 🔍 TypeScript type checking
- 🔌 API proxy to backend at `localhost:8000`

**Access the app:** Open http://localhost:5173 in your browser

### Production Build

Build the application for production:

```bash
npm run build
```

**Build output location:** `../static/dist/`

The production build:
- ⚡ Minifies and optimizes code
- 📦 Bundles all dependencies
- 🗺️ Generates source maps
- 🎯 Outputs to `../static/dist/` directory (served by Flask backend)
- 🔖 Includes all assets with cache-busting hashes

### Preview Production Build

Test the production build locally:

```bash
npm run preview
```

## 📦 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server on port 5173 with HMR |
| `npm run build` | Build for production → outputs to `../static/dist/` |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint for code quality checks |

## ⚙️ Configuration

### Vite Configuration (`vite.config.ts`)

- **Dev server port:** 5173
- **Build output directory:** `../static/dist/`
- **API proxy configuration:**
  - `/transcribe` → `http://localhost:8000`
  - `/status` → `http://localhost:8000`
  - `/result` → `http://localhost:8000`
  - `/history` → `http://localhost:8000`

### TypeScript Configuration

- Strict mode enabled for type safety
- React 19 types included
- ES2020 target
- ESNext module system

## 🔧 Key Features

- **Real-time transcription status** via Server-Sent Events (SSE)
- **File upload** with drag & drop support
- **Progress tracking** with visual feedback
- **Transcription history** with localStorage persistence
- **Speaker labeling** for multi-speaker audio
- **JTBD analysis** integration
- **Shareable results** via task_id URLs
- **Responsive design** for mobile and desktop

## 🌐 Backend Integration

The frontend communicates with these backend endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcribe` | Upload audio file for transcription |
| GET | `/status/<task_id>` | SSE stream for real-time task status |
| GET | `/result/<task_id>` | Fetch completed transcription result |
| GET | `/history` | Retrieve transcription history |
| POST | `/history/<task_id>` | Save transcription to history |
| DELETE | `/history` | Clear all history |

## 🛠️ Development Guide

### Adding New Components

```bash
# Create component file
touch src/components/MyComponent.tsx

# Create component styles (if needed)
touch src/components/MyComponent.css
```

Example component structure:
```typescript
import React from 'react';
import './MyComponent.css';

interface MyComponentProps {
  title: string;
}

const MyComponent: React.FC<MyComponentProps> = ({ title }) => {
  return (
    <div className="my-component">
      <h2>{title}</h2>
    </div>
  );
};

export default MyComponent;
```

### Creating Custom Hooks

Place reusable hooks in `src/hooks/`:

```typescript
// src/hooks/useMyHook.ts
import { useState, useEffect } from 'react';

export const useMyHook = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // Hook logic
  }, []);
  
  return { data };
};
```

### Adding Type Definitions

Define types in `src/types/index.ts` or create dedicated type files:

```typescript
// src/types/index.ts
export interface TranscriptionResult {
  text: string;
  task_id: string;
  filename: string;
  // ... more fields
}
```

### API Utilities

API functions are centralized in `src/utils/api.ts` for consistent backend communication:

```typescript
// Example API call
export const uploadFile = async (file: File): Promise<string> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('/transcribe', {
    method: 'POST',
    body: formData,
  });
  
  return response.json();
};
```

## 📁 Folder Structure Details

### `/src/components/`
React components organized by feature:
- `UploadForm.tsx` - File upload interface
- `ProgressBar.tsx` - Progress indicator
- `TranscriptionResult.tsx` - Display transcription results
- `History.tsx` - Transcription history list
- `JTBDAnalysis.tsx` - Jobs-to-be-Done analysis display

### `/src/hooks/`
Custom React hooks for reusable logic:
- `useUpload.ts` - File upload state management
- `useHistory.ts` - History localStorage operations
- `useJTBD.ts` - JTBD analysis processing

### `/src/utils/`
Utility functions:
- `api.ts` - Backend API communication
- Helper functions for data formatting

### `/src/types/`
TypeScript type definitions for type safety

### `/src/styles/`
Global styles and CSS modules

## 📝 Environment

No `.env` file needed - all configuration is in `vite.config.ts`

## 🐛 Troubleshooting

### Port 5173 Already in Use

```bash
# Find and kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use a different port
vite --port 5174
```

### Build Errors

```bash
# Clear cache and reinstall dependencies
rm -rf node_modules package-lock.json
npm install
npm run build
```

### TypeScript Type Errors

```bash
# Check types without building
npx tsc --noEmit

# Check specific file
npx tsc --noEmit src/components/MyComponent.tsx
```

### API Connection Issues

1. Verify backend is running: `http://localhost:8000`
2. Check proxy configuration in `vite.config.ts`
3. Open browser console for network errors

### Hot Module Replacement Not Working

1. Ensure you're importing components correctly
2. Check file extensions (.tsx for React components)
3. Restart dev server: `npm run dev`

## 📊 Performance Tips

- Use React.memo() for expensive components
- Implement lazy loading with React.lazy()
- Optimize images in `/public` folder
- Monitor bundle size: `npm run build -- --mode production`

## 🧪 Testing

```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint -- --fix
```

## 📚 Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2 | UI framework |
| TypeScript | 5.9 | Type safety |
| Vite | 7.3 | Build tool & dev server |
| ESLint | 9.39 | Code linting |

## 🔗 Useful Links

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

## 🚦 Build Status

✅ **All requirements met:**
- ✓ Vite + React + TypeScript initialized
- ✓ All dependencies installed
- ✓ Folder structure complete (components, hooks, types, utils, styles)
- ✓ Vite configured for port 5173
- ✓ Build outputs to `../static/dist/`
- ✓ App.tsx with full application structure
- ✓ Production build script working

---

**Built with ❤️ for HearYou STT Service**
