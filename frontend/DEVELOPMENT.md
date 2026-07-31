# Development

## Build Artifacts & Cache

Next.js stores compiled output in `.next/`. This directory is **generated** — never modify it manually, never commit it.

### When build artifacts go stale

Symptoms of a stale `.next` cache:

- `MODULE_NOT_FOUND` errors referencing numeric chunk IDs (e.g. `./611.js`)
- `Cannot read properties of undefined (reading '/_app')` in the browser console
- Pages fail to load after switching branches, upgrading dependencies, or editing `next.config`
- The dev server shows compilation successes but the browser gets runtime errors

### Fixing stale artifacts

```sh
# Remove .next and other generated output
npm run clean

# Clean + start dev server
npm run dev:clean

# Clean + production build
npm run build:clean
```

### When to use each command

| Command | When to use |
|---|---|
| `npm run dev` | Normal development (incremental, fast) |
| `npm run dev:clean` | After switching branches, upgrading Next.js, or if you see chunk-loading errors |
| `npm run build:clean` | Before CI/CD or deployment to ensure a reproducible production build |
| `npm run clean` | Manual cleanup (also run by `dev:clean` and `build:clean`) |

### What gets cleaned

- `.next/` — all compiled output, chunks, server bundles, and cached module graphs
- `node_modules/.cache/` — babel/esbuild/vite caches that can also go stale

## Quick Start

```sh
npm run dev:clean
```

All routes will be compiled fresh.
