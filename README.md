# Quality LAC Data Reference - Postcodes

This is a redistribution of the **ONS Postcode Directory** shaped
to be used in the Quality Lac Data project.

This repository contains PyPI and npm distributions of
subsets of this dataset as well as the scripts to
generate them from source.

Source: Office for National Statistics licensed under the Open Government Licence v.3.0

Read more about this dataset here:

* https://geoportal.statistidcs.gov.uk/datasets/ons::ons-postcode-directory-august-2021/about

To keep distribution small, only pickled dataframes compatible 
with pandas 1.0.5 are included. This will hopefully change
once we figure out how to do different versions as extras.

As pickle is inherently unsafe, the SHA-512 checksum for each file
is included in [hashes.txt](qlacref_postcodes/hashes.txt). This
file is signed with [this key](./id_rsa.pub). 

When downloading from PyPI, specify the environment variable
`QLACREF_PC_KEY` to either be the public key itself, or a path
to where it can be loaded from. The checksums are then verified
and each file checked before unpickling. 

## Regular updates

When a new postcode distribution is available, download it and add it to the source folder and
at the same time delete the existing file from this location. There can only be one file
in the source folder at a time.

After updating the postcode sources, run the script found in `bin/generate-output-files.py` to 
regenerate the output files for each letter of the alphabet. These end up in the 
qlacref_postcodes directory.

To sign the postcodes, you need the distribution private key. Run the script `bin/sign-files.py` to
create the signed checksum file. 

Commit everything to GitHub. If ready to make a release, make sure to update the version in 
[pyproject.toml](./pyproject.toml), push to GitHub and then create a GitHub release. The 
[GitHub Action](.github/workflows/python-publish.yml) will then create the distribution files and
upload to [PyPI][pypi].

Release naming should follow a pseudo-[semantic versioning][semver] format:
`<YEAR>.<MONTH>.<PATCH>`. Alpha and beta releases can be flagged by appending 
`-alpha.<number>` and `-beta.<number>`. 

For example, the August 2021 release is named [2021.8][2021.8] with the associated tag [v2021.8][tag-v2021.8].

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

**Note**: The browser example uses insecure mode for testing (no signature verification). The `QLACREF_PC_INSECURE` environment variable is set to `'True'` automatically.

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
- Loads required packages (pandas, rsa) via Pyodide's package system
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
- Make sure all dependencies (pandas, rsa) are loading correctly
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
