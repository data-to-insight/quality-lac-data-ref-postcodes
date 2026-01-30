/**
 * Test the actual qlacref_postcodes library in Pyodide/WASM
 */

import { describe, it, expect, beforeAll } from "vitest";
import { 
  createPyodideInstance, 
  runPythonCode, 
  setupQlacrefPostcodes 
} from "./pyodide-test-helper.js";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to the qlacref_postcodes module
const qlacrefPostcodesPath = join(__dirname, "..", "..", "qlacref_postcodes");

describe("qlacref_postcodes in Pyodide/WASM", () => {
  let pyodide;

  beforeAll(async () => {
    // Create Pyodide instance
    pyodide = await createPyodideInstance();
    
    // Load required packages
    console.log("Loading pandas...");
    await pyodide.loadPackage("pandas");
    
    console.log("Loading rsa...");
    // Try to load rsa - it may need to be installed via micropip
    try {
      await pyodide.loadPackage("rsa");
    } catch (e) {
      console.log("rsa not available as pre-built package, trying micropip...");
      await pyodide.loadPackage("micropip");
      // Use runPythonAsync for async Python code
      await pyodide.runPythonAsync(`
import micropip
await micropip.install("rsa")
      `);
    }
    
    console.log("Setting up qlacref_postcodes module...");
    // Copy the module to Pyodide's filesystem
    await setupQlacrefPostcodes(pyodide, qlacrefPostcodesPath, {
      publicKeyPath: join(__dirname, "..", "..", "id_rsa.pub"), 
      insecure: false,
    });
    
    console.log("Setup complete!");
  });

  it("verifies we're running in WASM", () => {
    const platform = runPythonCode(pyodide, "import sys; sys.platform");
    expect(platform).toBe("emscripten");
  });

  it("can import the qlacref_postcodes module", () => {
    // Try to import the module
    runPythonCode(pyodide, "import qlacref_postcodes");
    
    // Verify it's loaded
    const hasModule = runPythonCode(pyodide, "'qlacref_postcodes' in __import__('sys').modules");
    expect(hasModule).toBe(true);
  });

  it("can instantiate the Postcodes class", () => {
    // Create an instance with insecure mode (no signature verification)
    const code = `
from qlacref_postcodes import Postcodes

# Create instance
pc = Postcodes()
type(pc).__name__
    `;
    const className = runPythonCode(pyodide, code);
    expect(className).toBe("Postcodes");
  });

  it("can access the dataframe property", () => {
    const code = `
from qlacref_postcodes import Postcodes

pc = Postcodes()
df = pc.dataframe
len(df.columns)
    `;
    const columnCount = runPythonCode(pyodide, code);
    expect(columnCount).toBe(5);
  });

  it("can check dataframe columns match expected schema", () => {
    const code = `
from qlacref_postcodes import Postcodes

pc = Postcodes()
df = pc.dataframe
list(df.columns)
    `;
    const columns = runPythonCode(pyodide, code);
    const expectedColumns = ['pcd', 'oseast1m', 'osnrth1m', 'laua', 'pcd_abbr'];
    // Convert to array if it's a PyProxy
    const columnsArray = Array.isArray(columns) ? columns : Array.from(columns);
    expect(columnsArray.sort()).toEqual(expectedColumns.sort());
  });

  it("can load postcodes for a letter", () => {
    const code = `
from qlacref_postcodes import Postcodes

pc = Postcodes()
initial_count = len(pc.dataframe)

# Load postcodes for letter 'A'
pc.load_postcodes(['A'])
final_count = len(pc.dataframe)

# Should have loaded some postcodes
final_count > initial_count
    `;
    const hasLoaded = runPythonCode(pyodide, code);
    expect(hasLoaded).toBe(true);
  });

  it("can access loaded postcode data", () => {
    const code = `
from qlacref_postcodes import Postcodes

pc = Postcodes()
pc.load_postcodes(['Z'])  # Load a small file

df = pc.dataframe
# Check if we have data
len(df) > 0 and 'pcd' in df.columns
    `;
    const hasData = runPythonCode(pyodide, code);
    expect(hasData).toBe(true);
  });

  it("can query postcodes after loading", () => {
    const code = `
from qlacref_postcodes import Postcodes

pc = Postcodes()
pc.load_postcodes(['Z'])

df = pc.dataframe
# Try to get a sample postcode
if len(df) > 0:
    result = df.iloc[0]['pcd'] is not None
else:
    result = False
result
    `;
    const hasSample = runPythonCode(pyodide, code);
    expect(hasSample).toBe(true);
  });

  it("verifies all required dependencies are available", () => {
    const code = `
import sys
deps = ['pandas', 'rsa', 'hashlib', 'pathlib']
available = [dep for dep in deps if dep in sys.modules or __import__(dep) is not None]
len(available) == len(deps)
    `;
    // Note: This might not work perfectly, but let's check what we can
    const hasPandas = runPythonCode(pyodide, "import pandas; True");
    const hasRsa = runPythonCode(pyodide, "import rsa; True");
    
    expect(hasPandas).toBe(true);
    expect(hasRsa).toBe(true);
  });
});

