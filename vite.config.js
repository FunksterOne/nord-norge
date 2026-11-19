import { defineConfig } from 'vite';
import { readdirSync, readFileSync, cpSync, mkdirSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
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
    for (const dir of ['geo', 'data', 'og']) if (existsSync(resolve(root, dir))) cpSync(resolve(root, dir), resolve(root, 'dist', dir), { recursive: true });
  }
});

// Versjonsnummer på de klassiske skriptene: ?v=<innholdshash> legges på assets/data.js og assets/app.js i hver side ved
// bygging. Nettleseren mellomlagrer filene i en time (vercel.json), og uten nummer kunne ny HTML møte en gammel data.js,
// slik at figurer som venter på en ny datablokk ble stående tomme. Hashen endres bare når filen endres.
const versjonerLegacy = () => {
  const hash = f => createHash('sha256').update(readFileSync(resolve(root, 'assets', f))).digest('hex').slice(0, 10);
  return {
    name: 'versjoner-legacy-assets',
    apply: 'build',
    transformIndexHtml: {
      order: 'post',
      handler: html => {
        const v = { 'data.js': hash('data.js'), 'app.js': hash('app.js') };
        return html.replace(/(src=")(\/?assets\/(data\.js|app\.js))(")/g, (_m, a, sti, f, b) => `${a}${sti}?v=${v[f]}${b}`);
      }
    }
  };
};

export default defineConfig({
  build: { rollupOptions: { input: pages }, assetsDir: '_build', chunkSizeWarningLimit: 900 },
  server: { port: 8123 },
  preview: { port: 8123 },
  plugins: [copyLegacy(), versjonerLegacy()]
});
