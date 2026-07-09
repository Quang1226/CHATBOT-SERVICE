import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';
import cssInjectedByJsPlugin from 'vite-plugin-css-injected-by-js';

export default defineConfig({
  plugins: [
    react(),
    cssInjectedByJsPlugin()
  ],
  build: {
    rollupOptions: {
      // Chỉ định 2 đầu vào khác nhau
      input: {
        admin: './index.html',         // Cửa chính: Build ra Web Admin
        widget: './src/widget.jsx'     // Cửa phụ: Build ra file JS nhúng
      },
      output: {
        manualChunks: undefined,
        // Tự động đặt tên file đầu ra dựa trên tên của input
        entryFileNames: (assetInfo) => {
          if (assetInfo.name === 'widget') {
            return 'vnj-chatbot.js'; // File nhúng giữ tên đẹp và cố định
          }
          return 'assets/[name]-[hash].js'; // File của admin thì tự sinh mã hash
        }
      }
    }
  }
});