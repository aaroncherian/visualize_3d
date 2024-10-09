import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { templateCompilerOptions } from '@tresjs/core';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue({
      ...templateCompilerOptions,
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      // Proxy API requests from the frontend to the backend
      '/api': {
        target: 'http://localhost:8000',  // The backend server (FastAPI)
        changeOrigin: true,               // Ensures correct origin headers
        secure: false,                    // Disable if using HTTPS with self-signed certs
        rewrite: (path) => path.replace(/^\/api/, ''), // Removes the /api prefix before sending to the backend
      },
    },
  },
});
