# HearYou STT Service - React Frontend

Modern React + TypeScript frontend for the HearYou transcription service.

## Development

### Prerequisites

- Node.js 18+ 
- npm

### Installation

```bash
cd frontend
npm install
```

### Development Server

Start the dev server with hot reload:

```bash
npm run dev
```

This will start the frontend on `http://localhost:3000` with API proxy to `http://localhost:8000`.

Make sure the backend FastAPI server is running on port 8000:

```bash
# In the parent directory
python app.py
```

### Build for Production

Build optimized static files:

```bash
npm run build
```

This creates production-ready files in `../static/dist/`.

### Preview Production Build

Preview the production build locally:

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── UploadForm.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── TranscriptionResult.tsx
│   │   ├── SpeakerBlock.tsx
│   │   ├── JTBDAnalysis.tsx
│   │   └── History.tsx
│   ├── types/           # TypeScript types
│   │   └── index.ts
│   ├── utils/           # Utility functions
│   │   ├── api.ts       # API calls and history
│   │   └── textFormatting.ts  # Speaker text processing
│   ├── App.tsx          # Main app component
│   ├── App.css
│   ├── main.tsx         # Entry point
│   └── index.css
├── index.html
├── vite.config.ts       # Vite configuration
├── tsconfig.json        # TypeScript config
└── package.json
```

## Features

- **File Upload**: Audio/video files up to 25GB
- **Speaker Diarization**: Identify and separate speakers
- **JTBD Analysis**: Jobs-to-be-Done analysis toggle
- **Real-time Progress**: Streaming status updates via EventSource
- **History**: Local storage of recent transcriptions
- **Responsive Design**: Mobile and desktop support
- **Copy to Clipboard**: Quick text copying

## Technology Stack

- **React 18** with TypeScript
- **Vite** for fast builds and HMR
- **CSS Modules** for component styling
- **EventSource API** for streaming updates
- **LocalStorage** for history persistence

## API Integration

The frontend communicates with the FastAPI backend via these endpoints:

- `POST /transcribe` - Upload and start transcription
- `GET /status/{task_id}/stream` - EventSource for progress updates
- `GET /result/{task_id}` - Fetch completed transcription

## Deployment

The production build is served by the FastAPI backend:

1. Build: `npm run build`
2. Files go to `../static/dist/`
3. Backend serves `static/dist/index.html` at root
4. Assets are mounted at `/assets/*`

No separate deployment needed - it's all served by the FastAPI app.

## Development Notes

- Uses TypeScript for type safety
- Components are functional with hooks
- No state management library needed (useState/useEffect sufficient)
- Maintains exact feature parity with vanilla JS version
- Preserves ultra-compact speaker spacing design
