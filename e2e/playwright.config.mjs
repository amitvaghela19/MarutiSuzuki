import path from "path";
import { fileURLToPath } from "url";
import { defineConfig } from "@playwright/test";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(__dirname, "..");
const py = path.join(root, ".venv", "Scripts", "python.exe");

export default defineConfig({
  testDir: ".",
  timeout: 120_000,
  use: {
    baseURL: "http://127.0.0.1:5173",
    headless: true,
  },
  webServer: [
    {
      command: `"${py}" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000`,
      url: "http://127.0.0.1:8000/api/health",
      cwd: root,
      reuseExistingServer: true,
      timeout: 120_000,
    },
    {
      command: "npm run build && npm run preview",
      url: "http://127.0.0.1:5173",
      cwd: path.join(root, "frontend"),
      reuseExistingServer: true,
      timeout: 180_000,
    },
  ],
});
