import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import Icons from "unplugin-icons/vite";
import ElementPlus from 'unplugin-element-plus/vite'

// https://vite.dev/config/
export default defineConfig({
  base: '/webui/',
  plugins: [
    vue(),
    vueDevTools(),
    Icons({
      compiler: 'vue3',
      autoInstall: true,
    }),
    ElementPlus({
      // options
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
