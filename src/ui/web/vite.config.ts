import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/core': path.resolve(__dirname, '../../core'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/children': 'http://localhost:8000',
      '/questions': 'http://localhost:8000',
      '/attempts': 'http://localhost:8000',
      '/progress': 'http://localhost:8000',
      '/sessions': 'http://localhost:8000',
      '/standards': 'http://localhost:8000',
      '/admin': 'http://localhost:8000',
    },
  },
});
