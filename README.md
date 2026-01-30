# Quality LAC Data Reference - Postcodes

This is a redistribution of the **ONS Postcode Directory** shaped
to be used in the Quality Lac Data project.

This repository contains PyPI distribution of a
subset of this dataset as well as the scripts to
generate them from source.

Source: Office for National Statistics licensed under the Open Government Licence v.3.0

Read more about this dataset here:

* https://geoportal.statistics.gov.uk/datasets/3635ca7f69df4733af27caf86473ffa1/about

To keep distribution small, the data is stored in msgpack format
with brotli compression. This provides efficient serialization
without the security concerns and version coupling issues associated
with pickle. 

## Regular updates

When a new postcode distribution is available, download it and add it to the source folder and
at the same time delete the existing file from this location. There can only be one file
in the source folder at a time.

After updating the postcode sources, regenerate the output files using the CLI command:

```bash
python -m qlacref_postcodes generate source/ONSPD_NOV_2025.zip
```

Or if you have the CLI extra installed:

```bash
postcodes generate source/ONSPD_NOV_2025.zip
```

This will regenerate the output files for each letter of the alphabet in the 
qlacref_postcodes directory. 

Commit everything to GitHub. If ready to make a release, make sure to update the version in 
[pyproject.toml](./pyproject.toml), push to GitHub and then create a GitHub release. The 
[GitHub Action](.github/workflows/python-publish.yml) will then create the distribution files and
upload to [PyPI][pypi].

Release naming should follow a pseudo-[semantic versioning][semver] format:
`<YEAR>.<MONTH>.<PATCH>`. Alpha and beta releases can be flagged by appending 
`-alpha.<number>` and `-beta.<number>`. 

For example, the August 2021 release is named [2021.8][2021.8] with the associated tag [v2021.8][tag-v2021.8].

### Version Resolution

The package includes robust version resolution that works across different Python
environments, including Pyodide/WASM. The version can be accessed programmatically:

```python
import qlacref_postcodes
print(qlacref_postcodes.__version__)
```

The version resolver uses multiple fallback strategies to reliably detect the
package version:
1. Parses `pyproject.toml` directly (most reliable for pre-releases)
2. Uses `importlib.metadata.version()` (standard Python environments)
3. Iterates through installed distributions (works better in Pyodide/WASM)
4. Falls back to "unknown" if all strategies fail

**Development Versioning**: For development branches, we recommend using `.devX`
suffixes (e.g., `2025.11.1.dev0`, `2025.11.1.dev1`). These are PEP 440 compliant
and work seamlessly with the version resolver. The `.devX` format clearly
indicates development versions while maintaining compatibility with package
management tools.

Example development versions:
- `2025.11.1.dev0` - First development version for 2025.11.1
- `2025.11.1.dev1` - Second development version
- `2025.11.1-alpha.1` - Alpha release (for testing before final release)
- `2025.11.1-beta.1` - Beta release

The version resolver returns the exact version string as written in `pyproject.toml`,
not the PEP 440 normalized version used in wheel filenames. This ensures consistent
version reporting across all environments.

## Development Environment

This project includes a VS Code devcontainer configuration for a consistent development environment.

### Devcontainer Setup

The `.devcontainer/` directory contains:
- **Dockerfile**: Based on Python 3.8 with conservative build tools (for compatibility with old numpy/pandas versions)
- **devcontainer.json**: VS Code configuration for the container

The devcontainer:
- Uses Python 3.8 (Debian Bullseye)
- Installs Poetry 1.8.5
- Configures Poetry to keep the virtual environment in the project directory (`virtualenvs.in-project true`)
- Automatically runs `poetry install` when the container is created
- Includes VS Code Python extensions (Python and Pylance)

To use the devcontainer:
1. Open the project in VS Code
2. When prompted, click "Reopen in Container" (or use Command Palette: "Dev Containers: Reopen in Container")
3. The container will build and install dependencies automatically

The devcontainer uses conservative versions of build tools (pip<24, setuptools<60, wheel<0.39, Cython<3) to ensure compatibility with older numpy/pandas versions required for Pyodide compatibility.

## Command Line Interface (CLI)

The package includes an optional CLI for generating postcode files and searching
postcodes. The CLI is available as an optional extra to keep the core package
lightweight.

### Installation

To install with CLI support:

```bash
pip install quality-lac-data-ref-postcodes[cli]
```

Or with Poetry:

```bash
poetry install --extras cli
```

### Usage

Once installed, you can use the CLI via:

```bash
python -m qlacref_postcodes <command>
```

Or if installed as a script:

```bash
postcodes <command>
```

### Available Commands

#### `generate`

Convert a source ZIP file to msgpack.br format files:

```bash
postcodes generate source/ONSPD_NOV_2025.zip [output_dir]
```

- `input_file`: Path to the source ZIP file (required)
- `output_dir`: Output directory (defaults to package directory)

This command:
- Extracts and parses the CSV file from the ZIP
- Maps source columns to expected format (pcd7→pcd, east1m→oseast1m, etc.)
- Splits postcodes by first letter
- Saves each letter's data as a compressed msgpack file

#### `to_parquet`

Convert a source ZIP file to Parquet format:

```bash
postcodes to_parquet source/ONSPD_NOV_2025.zip [output_file]
```

- `input_file`: Path to the source ZIP file (required)
- `output_file`: Output file path (defaults to input filename with .parquet extension)

#### `search`

Search for postcodes interactively with formatted table output:

```bash
postcodes search "SW1A" [--data-dir /path/to/data]
```

- `partial_postcode`: Partial postcode to search for (required)
- `--data-dir`: Optional path to data directory (defaults to package directory)

The search command displays results in a formatted table with columns for
postcode, easting, northing, and local authority code.

### Example Workflow

```bash
# Generate postcode files from source
postcodes generate source/ONSPD_NOV_2025.zip

# Search for postcodes
postcodes search "SW1A"

# Convert to Parquet for other tools
postcodes to_parquet source/ONSPD_NOV_2025.zip output.parquet
```

## Testing in Pyodide/WASM

This project includes examples for testing the library in Pyodide (WebAssembly) environments. Pyodide allows Python code to run in browsers and Node.js using WebAssembly.

### Why Test in Pyodide?

Testing in Pyodide ensures:
1. **WASM Compatibility**: Your code works in WebAssembly environments
2. **Browser Compatibility**: If you plan to run Python in browsers
3. **Cross-Platform**: Verify your code works in JavaScript runtimes
4. **Package Compatibility**: Ensure dependencies work in Pyodide

### Browser Example

The browser example (`examples/pyodide-v0.22.1-browser/`) demonstrates testing the library in a web browser using Pyodide.

**Important**: The browser example requires the wheel to be built first before testing.

#### Setup

1. Build the wheel:
   ```bash
   poetry build
   ```
   This creates the wheel file in the `dist/` directory.

2. Start the Flask server:
   ```bash
   poetry run serve
   ```
   Or run directly:
   ```bash
   python examples/pyodide-v0.22.1-browser/app.py
   ```

The server will:
- Check if the wheel exists in `dist/` before starting (provides helpful error if missing)
- Start on `http://localhost:8123` (or the port specified by `PORT` environment variable)
- Serve an HTML page that loads Pyodide from CDN
- Automatically install the built wheel in the browser environment

#### Usage

1. Open your browser and navigate to `http://localhost:8123` (or the port shown in the server output)
2. Wait for Pyodide to load (may take a moment on first load)
3. Enter Python code in the left panel
4. Click "Run Code" or press Ctrl+Enter
5. View output in the right panel

The page includes example scripts:
- **Basic**: Check platform and Python version
- **Columns**: Inspect the dataframe structure
- **Load**: Load postcodes for a specific letter
- **Query**: Query and display loaded postcode data

**Note**: The browser example automatically installs required packages (msgpack, brotli) via Pyodide's package system.

### Node.js Example

The Node.js example (`examples/pyodide-v0.22.1-node/`) uses Vitest to test the library in Pyodide/WASM within a Node.js environment.

#### Setup

1. Navigate to the example directory:
   ```bash
   cd examples/pyodide-v0.22.1-node
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

#### Running Tests

```bash
# Run all tests
pnpm test

# Run specific test file
pnpm test test.test.js

# Run tests in watch mode
pnpm test --watch
```

#### How It Works

The Node.js example:
- Uses Vitest as the test runner
- Creates a Pyodide instance configured for Node.js
- Copies the `qlacref_postcodes` module to Pyodide's virtual filesystem
- Loads required packages (pandas, msgpack, brotli) via Pyodide's package system
- Verifies WASM execution by checking `sys.platform == "emscripten"`

The test helper (`pyodide-test-helper.js`) provides utilities:
- `createPyodideInstance()`: Creates a configured Pyodide instance
- `runPythonCode()`: Executes Python code
- `loadPythonFile()`: Loads Python files from disk
- `setupQlacrefPostcodes()`: Sets up the module in Pyodide with proper configuration

#### Testing Your Code

The example includes tests that:
- Verify WASM execution environment
- Test module import and instantiation
- Test dataframe access and column structure
- Test loading postcodes for specific letters
- Test querying loaded postcode data

You can modify the tests in `test-qlacref-postcodes.test.js` to test your specific use cases.

### Key Differences

- **Browser Example**: Interactive testing in a web browser, requires built wheel, uses Flask server
- **Node.js Example**: Automated testing with Vitest, can test source code directly, runs in Node.js environment

Both examples verify that code is running in WASM by checking `sys.platform == "emscripten"`.

### Troubleshooting

#### Browser Example

**Pyodide fails to load**:
- Check your internet connection (Pyodide loads from CDN)
- Check browser console for errors
- Try refreshing the page

**Wheel installation fails**:
- Ensure the wheel file exists in `dist/`
- Check that the Flask server can access the `dist/` directory
- Verify the wheel path in `index.html` matches your actual wheel filename

**Module import errors**:
- Make sure all dependencies (pandas, msgpack, brotli) are loading correctly
- Check the browser console for detailed error messages

#### Node.js Example

**Module Not Found Errors**:
- Check that `indexURL` is set correctly in the test helper
- Verify the Pyodide package path is correct
- Ensure WASM files are accessible

**Package Loading Issues**:
- Check if the package is available in Pyodide
- Verify package version compatibility
- Check network connectivity (first load downloads from CDN)

**Path Issues**:
- Ensure `indexURL` is set to a directory path (not a URL)
- Use absolute paths when possible
- Check Vitest configuration

### Resources

- [Pyodide Documentation](https://pyodide.org/)
- [Pyodide Packages](https://pyodide.org/en/stable/usage/packages-in-pyodide.html)
- [Vitest Documentation](https://vitest.dev/)

[pypi]: https://pypi.org/project/quality-lac-data-ref-postcodes/
[semver]: https://semver.org/
[2021.8]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-postcodes/releases/tag/v2021.8
[tag-v2021.8]: https://github.com/SocialFinanceDigitalLabs/quality-lac-data-ref-postcodes/tree/v2021.8
