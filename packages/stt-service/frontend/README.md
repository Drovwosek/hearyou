# STT Service Frontend

Modern React + TypeScript frontend for the Speech-to-Text service, built with Vite.

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/      # React components
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript type definitions
│   ├── utils/           # Utility functions
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
# Install dependencies
npm install
```

### Development

Run the development server on port 5173:

```bash
npm run dev
```

The dev server will start at `http://localhost:5173` with:
- Hot Module Replacement (HMR)
- TypeScript type checking
- API proxy to backend at `localhost:8000`

### Production Build

Build the application for production:

```bash
npm run build
```

**Build output:** `../static/dist/`

The production build:
- Minifies and optimizes code
- Generates source maps
- Outputs to `../static/dist/` directory (served by Flask backend)
- Includes all assets with cache-busting hashes

### Preview Production Build

Test the production build locally:

```bash
npm run preview
```

## 📦 Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (port 5173) |
| `npm run build` | Build for production → `../static/dist/` |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint for code quality |

## ⚙️ Configuration

### Vite Configuration (`vite.config.ts`)

- **Dev server port:** 5173
- **Build output:** `../static/dist/`
- **API proxy:** Routes `/transcribe`, `/status`, `/result`, `/history` to `localhost:8000`

### TypeScript

- Strict mode enabled
- React 19 types included
- Path aliases supported via `@types/node`

## 🔧 Key Features

- **Real-time transcription status** via Server-Sent Events (SSE)
- **File upload** with progress tracking
- **Transcription history** with localStorage persistence
- **Speaker labeling** support
- **JTBD analysis** integration
- **Shareable results** via task_id URLs

## 🌐 Backend Integration

The frontend expects the following backend endpoints:

- `POST /transcribe` - Upload audio file
- `GET /status/<task_id>` - SSE stream for task status
- `GET /result/<task_id>` - Fetch transcription result
- `GET /history` - Fetch transcription history
- `POST /history/<task_id>` - Save to history
- `DELETE /history` - Clear history

## 🛠️ Development Tips

### Adding New Components

```bash
# Create component file
touch src/components/MyComponent.tsx

# Create component styles
touch src/styles/MyComponent.css
```

### Custom Hooks

Place reusable hooks in `src/hooks/`:

```typescript
// src/hooks/useTranscription.ts
export const useTranscription = () => {
  // Hook logic
};
```

### Type Definitions

Add types to `src/types/index.ts` or create new type files in `src/types/`

### API Utilities

API functions are in `src/utils/api.ts` for centralized backend communication

## 📝 Environment

No `.env` file needed - all configuration is in `vite.config.ts`

## 🐛 Troubleshooting

### Port 5173 already in use

```bash
# Kill process on port 5173
kill -9 $(lsof -t -i:5173)

# Or use a different port
vite --port 5174
```

### Build errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### TypeScript errors

```bash
# Check types without building
npx tsc --noEmit
```

## 📚 Tech Stack

- **React 19** - UI framework
- **TypeScript 5.9** - Type safety
- **Vite 7** - Build tool & dev server
- **ESLint** - Code linting
- **CSS Modules** - Component styling

## 🔗 Links

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

---

**Built with ❤️ for HearYou STT Service**
