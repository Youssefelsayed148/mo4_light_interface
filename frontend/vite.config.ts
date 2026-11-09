/// <reference types="vitest/config" />
import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(import.meta.dirname, 'src') },
  },
  server: {
    port: 5173,
    // Mirrors the Vercel rewrite: /api/* goes to the FastAPI backend.
    proxy: { '/api': process.env.API_PROXY_TARGET ?? 'http://localhost:8010' },
    // File events do not cross the Windows -> Docker bind mount; poll in the container.
    watch: process.env.VITE_USE_POLLING ? { usePolling: true } : undefined,
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    css: false,
  },
})
