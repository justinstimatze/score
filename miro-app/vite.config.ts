import fs from "fs";
import { resolve } from "path";
import type { Connect } from "vite";
import { defineConfig } from "vite";

// Data files (plays_strips.json, plays_mechanisms.json, plays_info.json):
//
// Default: the three files in public/ are copied into dist/ automatically
// by Vite's static asset handling and served at / in dev mode.
//
// Override: set SCORE_DATA_DIR to a directory containing your full library.
// The middleware below intercepts requests for those files and serves them
// from the custom directory instead, overriding the public/ copies.
const DATA_FILES = ["plays_strips.json", "plays_mechanisms.json", "plays_info.json"];

function makeDataMiddleware(dir: string): Connect.NextHandleFunction {
  return (req, res, next) => {
    const name = req.url?.split("?")[0]?.replace(/^\//, "");
    if (name && DATA_FILES.includes(name)) {
      const filePath = resolve(dir, name);
      if (fs.existsSync(filePath)) {
        res.setHeader("Content-Type", "application/json");
        fs.createReadStream(filePath).pipe(res as NodeJS.WritableStream);
        return;
      }
    }
    next();
  };
}

const customDataDir = process.env["SCORE_DATA_DIR"];

export default defineConfig({
  root: ".",
  base: "./",
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        // Headless entry point — loaded by Miro automatically on board open
        main: resolve(__dirname, "index.html"),
        // Panel UI — opened via openPanel() when icon is clicked
        panel: resolve(__dirname, "panel.html"),
      },
    },
  },
  server: {
    port: 5174,
    host: "0.0.0.0",
  },
  preview: {
    port: 5174,
    host: "0.0.0.0",
  },
  plugins: customDataDir && fs.existsSync(customDataDir)
    ? [
        {
          name: "score-data-override",
          configureServer(server) {
            server.middlewares.use(makeDataMiddleware(customDataDir));
          },
          configurePreviewServer(server) {
            server.middlewares.use(makeDataMiddleware(customDataDir));
          },
        },
      ]
    : [],
});
