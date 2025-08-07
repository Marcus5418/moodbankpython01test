import { defineConfig } from 'vite'

export default defineConfig({
  root: '.',
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000',
      '/track': 'http://localhost:5000',
      '/insights': 'http://localhost:5000',
      '/solutions': 'http://localhost:5000'
    }
  },
  build: {
    outDir: 'dist'
  }
})
