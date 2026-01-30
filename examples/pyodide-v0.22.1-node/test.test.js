import { describe, it, expect, beforeAll } from "vitest";
import { createPyodideInstance, runPythonCode, canImportModule } from "./pyodide-test-helper.js";

describe("pyodide in node", () => {
  let pyodide;

  beforeAll(async () => {
    // Create a Pyodide instance once for all tests
    // This is faster than creating a new instance for each test
    pyodide = await createPyodideInstance();
  });

  it("runs python in WASM", async () => {
    // Verify we're running in Pyodide/WASM
    const platform = runPythonCode(pyodide, "import sys; sys.platform");
    expect(platform).toBe("emscripten");
    
    // Test basic Python execution
    const result = runPythonCode(pyodide, "1 + 2 + 3");
    expect(result).toBe(6);
  });

  it("can import standard library modules", () => {
    // Test that we can import Python modules
    runPythonCode(pyodide, "import math");
    const pi = runPythonCode(pyodide, "math.pi");
    expect(pi).toBeCloseTo(3.14159, 5);
    
    // Test other standard library modules
    runPythonCode(pyodide, "import json");
    runPythonCode(pyodide, "import os");
    runPythonCode(pyodide, "import sys");
  });

  it("can execute Python functions", () => {
    // Define and call a Python function
    runPythonCode(pyodide, `
def add(a, b):
    return a + b
`);
    const result = runPythonCode(pyodide, "add(5, 3)");
    expect(result).toBe(8);
  });

  it("can work with Python data structures", () => {
    // Test Python lists
    runPythonCode(pyodide, "my_list = [1, 2, 3, 4, 5]");
    const length = runPythonCode(pyodide, "len(my_list)");
    expect(length).toBe(5);
    
    // Test Python dictionaries
    runPythonCode(pyodide, "my_dict = {'a': 1, 'b': 2, 'c': 3}");
    const value = runPythonCode(pyodide, "my_dict['b']");
    expect(value).toBe(2);
  });

  it("can check module availability", () => {
    // Check if standard library modules are available
    expect(canImportModule(pyodide, "math")).toBe(true);
    expect(canImportModule(pyodide, "json")).toBe(true);
    expect(canImportModule(pyodide, "os")).toBe(true);
    
    // Note: pandas and other packages need to be loaded separately
    // expect(canImportModule(pyodide, "pandas")).toBe(false); // Not loaded by default
  });
});
