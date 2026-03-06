import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/transcribe': 'http://localhost:8000',
      '/status': 'http://localhost:8000',
      '/result': 'http://localhost:8000',
      '/history': 'http://localhost:8000',
    },
  },
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
  },
})
