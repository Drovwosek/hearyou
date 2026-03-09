# React Frontend Deployment Guide

## Overview

The STT service frontend has been migrated from vanilla JavaScript to React + TypeScript. The production build is served by the same FastAPI backend.

## Architecture

```
Frontend (React + Vite)
    ↓ npm run build
static/dist/
    ├── index.html
    └── assets/
        ├── index-[hash].js
        └── index-[hash].css
    ↓ Docker COPY
FastAPI Backend
    ├── Serves index.html at /
    └── Mounts /assets/* for JS/CSS
```

## Development Workflow

### 1. Local Development

Start the frontend dev server with hot reload:

```bash
cd frontend
npm install
npm run dev
```

This runs on `http://localhost:3000` with API proxy to the backend.

Make sure the backend is running:
```bash
# Option A: Docker
docker-compose up

# Option B: Local Python
python app.py
```

### 2. Making Changes

- Edit React components in `frontend/src/`
- Changes hot-reload instantly
- Test all features before building

### 3. Build for Production

```bash
cd frontend
npm run build
```

This creates optimized files in `../static/dist/`.

### 4. Test Production Build Locally

```bash
cd frontend
npm run preview
```

Opens preview server on `http://localhost:4173`.

## Deployment to Docker

### Quick Deploy (recommended)

```bash
# 1. Build frontend
cd frontend
npm run build
cd ..

# 2. Rebuild and restart container
docker-compose down
docker-compose build
docker-compose up -d
```

### Manual Deploy Steps

If you need more control:

```bash
# 1. Build React app
cd frontend
npm run build

# 2. Verify dist files exist
ls -la ../static/dist/

# 3. Stop container
cd ..
docker-compose down

# 4. Build new image (includes updated app.py and static files)
docker-compose build

# 5. Start container
docker-compose up -d

# 6. Verify deployment
curl http://localhost:8000/
docker logs hearyou-stt
```

## Troubleshooting

### 404 on assets

**Problem:** `/assets/index-[hash].js` returns 404

**Solution:**
- Check `static/dist/assets/` exists and has files
- Verify `app.py` has: `app.mount("/assets", StaticFiles(directory="static/dist/assets"), name="assets")`
- Rebuild Docker image

### Blank page

**Problem:** Page loads but shows blank screen

**Solution:**
- Open browser DevTools console
- Check for JavaScript errors
- Verify API endpoints are accessible: `curl http://localhost:8000/formats`
- Check Docker logs: `docker logs hearyou-stt`

### Old version still showing

**Problem:** Changes don't appear after rebuild

**Solution:**
- Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
- Check Docker image ID: `docker images | grep stt-service`
- Verify container is using new image: `docker ps`
- Force rebuild: `docker-compose build --no-cache`

### EventSource not connecting

**Problem:** Status updates don't stream

**Solution:**
- Check CORS settings in `app.py`
- Verify EventSource endpoint: `curl http://localhost:8000/status/test/stream`
- Check browser Network tab for SSE connection

## Backend Changes

The following was modified in `app.py`:

```python
# Serve React build instead of vanilla HTML
@app.get("/", response_class=HTMLResponse)
async def root(response: Response):
    html_path = Path(__file__).parent / "static" / "dist" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding='utf-8')
    # ... fallback

# Mount static assets
app.mount("/assets", StaticFiles(directory="static/dist/assets"), name="assets")
```

## Rollback Procedure

If the React version has issues, rollback to vanilla JS:

```bash
# 1. Restore old app.py
git checkout main packages/stt-service/app.py

# Or manually change:
# - html_path = Path(__file__).parent / "static" / "index.html"
# - Comment out: app.mount("/assets", ...)

# 2. Rebuild
docker-compose down
docker-compose build
docker-compose up -d
```

The original `static/index.html` is backed up as `static/index.html.backup`.

## Production Checklist

Before deploying to production:

- [ ] All features tested (upload, diarization, JTBD, history)
- [ ] Build completes without errors
- [ ] Assets load correctly (check DevTools Network tab)
- [ ] EventSource streaming works
- [ ] Mobile responsive design verified
- [ ] Browser cache busting works
- [ ] Docker logs show no errors
- [ ] Backup original files created

## CI/CD Integration

For automated deployments:

```bash
#!/bin/bash
# deploy.sh

set -e  # Exit on error

echo "Building React frontend..."
cd packages/stt-service/frontend
npm install
npm run build

echo "Building Docker image..."
cd ..
docker-compose build

echo "Restarting service..."
docker-compose down
docker-compose up -d

echo "Deployment complete!"
docker ps | grep hearyou-stt
```

Make executable: `chmod +x deploy.sh`

## Monitoring

Check service health:

```bash
# Container status
docker ps | grep hearyou-stt

# Application logs
docker logs -f hearyou-stt

# Test API
curl http://localhost:8000/formats

# Test frontend
curl http://localhost:8000/ | grep "HearYou"
```

## Performance Notes

- React build is optimized with tree-shaking and minification
- Gzipped bundle: ~65 KB (JS) + ~1.7 KB (CSS)
- No runtime overhead compared to vanilla JS
- EventSource streaming performance identical

## Next Steps

Optional improvements:

1. Add error boundary components
2. Implement loading skeletons
3. Add toast notifications (react-hot-toast)
4. Dark mode toggle
5. Drag & drop file upload
6. Progressive Web App (PWA) support

See `frontend/README.md` for development details.
