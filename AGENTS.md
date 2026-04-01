# AGENTS.md

## Cursor Cloud specific instructions

### Overview

AI Plagiarism Checker — a client-side React SPA (Vite + TypeScript) that uses Google Gemini AI to analyze documents for plagiarism. No backend server or database; all logic runs in the browser.

### Dev server

- `npm run dev` starts Vite on port 3000 (host `0.0.0.0`).
- The app requires a `GEMINI_API_KEY` in `.env.local` at the repo root. Without a valid key the UI loads but document analysis calls will fail.
- Vite config maps the env var via `process.env.GEMINI_API_KEY` and `process.env.API_KEY`.

### Available scripts (see `package.json`)

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start Vite dev server (port 3000) |
| `npm run build` | Production build to `dist/` |
| `npm run preview` | Preview production build |

### Lint / Type-check

- No ESLint config is present in the repo; linting is not configured.
- TypeScript type-checking: `npx tsc --noEmit`

### Testing

- No test framework or test files exist in the repo. There are no automated tests to run.

### Gotchas

- `package-lock.json` is committed; use `npm install` (not `npm update`) to get reproducible installs.
- Tailwind CSS is loaded from a CDN `<script>` tag, not installed as a dependency.
- `pdfjs-dist` worker is loaded from a CDN URL hard-coded in `utils/fileReader.ts`.
