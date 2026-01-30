import { defineConfig } from 'vitest/config';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Resolve pyodide path - works with both npm and pnpm
function resolvePyodidePath() {
  // Try npm-style path first (node_modules/pyodide)
  const npmPath = resolve(__dirname, 'node_modules/pyodide');
  if (existsSync(npmPath)) {
    return npmPath;
  }
  
  // Try pnpm-style path (node_modules/.pnpm/pyodide@0.22.1/node_modules/pyodide)
  const pnpmPath = resolve(__dirname, 'node_modules/.pnpm/pyodide@0.22.1/node_modules/pyodide');
  if (existsSync(pnpmPath)) {
    return pnpmPath;
  }
  
  // Fallback to npm path
  return npmPath;
}

export default defineConfig({
  test: {
    environment: 'node',
  },
  resolve: {
    alias: {
      // Ensure proper path resolution for Pyodide (works with both npm and pnpm)
      'pyodide': resolvePyodidePath(),
    },
  },
  // Handle WASM and binary files
  assetsInclude: ['**/*.wasm', '**/*.tar', '**/*.data'],
});

