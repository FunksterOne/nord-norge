import { defineConfig } from 'vite';
import { readdirSync, cpSync, mkdirSync } from 'node:fs';
import { resolve } from 'node:path';

const root = import.meta.dirname;
const pages = Object.fromEntries(
  readdirSync(root).filter(f => f.endsWith('.html')).map(f => [f.replace(/\.html$/, ''), resolve(root, f)])
);

// Klassiske skript (assets/data.js, assets/app.js) bundles ikke av Vite; de kopieres som de er.
const copyLegacy = () => ({
  name: 'copy-legacy-assets',
  closeBundle() {
    mkdirSync(resolve(root, 'dist/assets'), { recursive: true });
    for (const f of ['data.js', 'app.js']) cpSync(resolve(root, 'assets', f), resolve(root, 'dist/assets', f));
    cpSync(resolve(root, 'geo'), resolve(root, 'dist/geo'), { recursive: true });
  }
});

export default defineConfig({
  build: { rollupOptions: { input: pages }, assetsDir: '_build', chunkSizeWarningLimit: 900 },
  server: { port: 8123 },
  preview: { port: 8123 },
  plugins: [copyLegacy()]
});
