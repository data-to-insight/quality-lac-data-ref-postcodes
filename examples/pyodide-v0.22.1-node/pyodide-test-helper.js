/**
 * Helper utilities for testing Python code in Pyodide/WASM
 */

import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { existsSync } from "fs";
import { loadPyodide } from "pyodide";

// Get the directory of this file
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Find the pyodide package directory - works with both npm and pnpm
function findPyodidePath() {
  // Try npm-style path first (node_modules/pyodide)
  const npmPath = join(__dirname, "node_modules", "pyodide");
  if (existsSync(npmPath)) {
    return npmPath;
  }
  
  // Try pnpm-style path (node_modules/.pnpm/pyodide@0.22.1/node_modules/pyodide)
  const pnpmPath = join(__dirname, "node_modules", ".pnpm", "pyodide@0.22.1", "node_modules", "pyodide");
  if (existsSync(pnpmPath)) {
    return pnpmPath;
  }
  
  // Fallback to npm path
  return npmPath;
}

const pyodidePath = findPyodidePath();

/**
 * Creates a Pyodide instance configured for Node.js testing
 * @param {Object} options - Options to pass to loadPyodide
 * @returns {Promise} A promise that resolves to a Pyodide instance
 */
export async function createPyodideInstance(options = {}) {
  const pyodide = await loadPyodide({
    indexURL: pyodidePath,
    ...options,
  });
  
  // Verify we're running in WASM
  const platform = pyodide.runPython("import sys; sys.platform");
  if (platform !== "emscripten") {
    throw new Error(`Expected platform 'emscripten', got '${platform}'`);
  }
  
  return pyodide;
}

/**
 * Loads a Python file or string into Pyodide
 * @param {Pyodide} pyodide - The Pyodide instance
 * @param {string} code - Python code as a string
 * @param {boolean} convertToJs - Whether to convert PyProxy to JS (default: true)
 * @returns {*} The result of executing the code
 */
export function runPythonCode(pyodide, code, convertToJs = true) {
  const result = pyodide.runPython(code);
  if (convertToJs && result && typeof result.toJs === 'function') {
    return result.toJs({ dict_converter: Object.fromEntries });
  }
  return result;
}

/**
 * Loads a Python file from the filesystem into Pyodide
 * @param {Pyodide} pyodide - The Pyodide instance
 * @param {string} filePath - Path to the Python file
 * @returns {Promise} A promise that resolves when the file is loaded
 */
export async function loadPythonFile(pyodide, filePath) {
  const fs = await import("fs/promises");
  const code = await fs.readFile(filePath, "utf-8");
  return pyodide.runPython(code);
}

/**
 * Checks if a Python module can be imported in Pyodide
 * @param {Pyodide} pyodide - The Pyodide instance
 * @param {string} moduleName - Name of the module to check
 * @returns {boolean} True if the module can be imported
 */
export function canImportModule(pyodide, moduleName) {
  try {
    pyodide.runPython(`import ${moduleName}`);
    return true;
  } catch (e) {
    return false;
  }
}

/**
 * Copies a directory from the filesystem to Pyodide's virtual filesystem
 * @param {Pyodide} pyodide - The Pyodide instance
 * @param {string} sourceDir - Source directory path
 * @param {string} targetDir - Target directory in Pyodide's filesystem (default: same as source basename)
 * @returns {Promise} A promise that resolves when the copy is complete
 */
export async function copyDirectoryToPyodide(pyodide, sourceDir, targetDir = null) {
  const fs = await import("fs/promises");
  const path = await import("path");
  
  if (!targetDir) {
    targetDir = `/${path.basename(sourceDir)}`;
  }
  
  // Ensure target directory exists in Pyodide
  pyodide.runPython(`
import os
os.makedirs('${targetDir}', exist_ok=True)
  `);
  
  // Recursively copy files
  async function copyRecursive(source, target) {
    const entries = await fs.readdir(source, { withFileTypes: true });
    
    for (const entry of entries) {
      const sourcePath = path.join(source, entry.name);
      const targetPath = `${target}/${entry.name}`;
      
      if (entry.isDirectory()) {
        // Create directory in Pyodide
        pyodide.runPython(`import os; os.makedirs('${targetPath}', exist_ok=True)`);
        await copyRecursive(sourcePath, targetPath);
      } else {
        // Copy file to Pyodide
        const fileData = await fs.readFile(sourcePath);
        const uint8Array = new Uint8Array(fileData.buffer, fileData.byteOffset, fileData.byteLength);
        
        // Write to Pyodide's filesystem
        pyodide.runPython(`
import os
os.makedirs(os.path.dirname('${targetPath}'), exist_ok=True)
        `);
        
        pyodide.FS.writeFile(targetPath, uint8Array);
      }
    }
  }
  
  await copyRecursive(sourceDir, targetDir);
  return targetDir;
}

/**
 * Sets up the qlacref_postcodes module in Pyodide
 * @param {Pyodide} pyodide - The Pyodide instance
 * @param {string} sourceDir - Path to the qlacref_postcodes directory
 * @param {Object} options - Options for setup
 * @param {boolean} options.insecure - Skip signature verification (default: true for testing)
 * @param {string} options.publicKeyPath - Path to public key file (optional)
 * @returns {Promise} A promise that resolves when setup is complete
 */
export async function setupQlacrefPostcodes(pyodide, sourceDir, options = {}) {
  const path = await import("path");
  const { insecure = true, publicKeyPath = null } = options;
  
  // Copy the module directory to Pyodide's filesystem
  const targetDir = await copyDirectoryToPyodide(pyodide, sourceDir);
  
  // Add the parent directory to Python path so we can import the module
  const parentDir = path.dirname(targetDir);
  pyodide.runPython(`
import sys
sys.path.insert(0, '${parentDir}')
  `);
  
  // Set environment variables for testing
  if (insecure) {
    pyodide.runPython(`
import os
os.environ['QLACREF_PC_INSECURE'] = 'True'
    `);
  } else if (publicKeyPath) {
    const fs = await import("fs/promises");
    const keyContent = await fs.readFile(publicKeyPath, "utf-8");
    // Copy key to Pyodide filesystem
    const keyPath = "/tmp/id_rsa.pub";
    pyodide.FS.writeFile(keyPath, new TextEncoder().encode(keyContent));
    
    pyodide.runPython(`
import os
os.environ['QLACREF_PC_KEY'] = '${keyPath}'
    `);
  }
  
  return targetDir;
}

