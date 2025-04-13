# Natural Language Test Runner

A cross-platform command-line tool that executes natural language test cases using Claude MCP Protocol and Playwright.

## Features

- Natural language test case execution from `.test.md` files
- Cross-platform support (Windows, macOS, Linux)
- Environment-based configuration
- Playwright-based browser automation
- Rich console output
- Clean dependency management with UV
- Automated test runner with nice reporting

## System Requirements

- Python 3.9 or higher
- Git
- Internet connection (for installing dependencies)

## Quick Setup

### On Unix-like Systems (macOS, Linux)

```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-directory>

# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

### On Windows

```powershell
# Clone the repository
git clone <your-repo-url>
cd <repo-directory>

# Run the setup script (you may need to set execution policy)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup.ps1
```

The setup scripts will:
1. Install UV if not already installed
2. Create a virtual environment
3. Install all dependencies
4. Install Playwright browsers
5. Create a template .env file

## Manual Setup

If you prefer to set up manually or the setup scripts don't work for you:

```bash
# Install UV
curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Unix
.\.venv\Scripts\Activate.ps1  # On Windows

# Install dependencies
uv pip install -e .

# Install Playwright browsers
playwright install chromium

# Create .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env
```

## Usage

### Creating a New Test

```bash
nltest new my_test
```

This creates a new test file at `tests/my_test.test.md` with a template structure.

### Running Tests

You can run tests in several ways:

#### Using the Test Runner Scripts

For the best experience with nice formatting and reporting:

On Unix-like systems:
```bash
./run_tests.sh
```

On Windows:
```powershell
.\run_tests.ps1
```

The test runner will:
- Find all `.test.md` files in the `tests` directory
- Run each test with proper environment setup
- Show progress with colored output
- Provide a summary of passed/failed tests
- List any failed tests for easy reference

#### Using the CLI Directly

For more control over test execution:

```bash
# Run a single test file
nltest run tests/my_test.test.md nltest/server.py

# Run all tests in a directory
nltest run tests nltest/server.py
```

## Test File Format

Create test files with `.test.md` extension using the following format:

```markdown
# Test Case: Login Flow

## Setup
- Navigate to login page
- Clear any existing sessions

## Steps
1. Enter username "testuser@example.com"
2. Enter password "password123"
3. Click login button

## Assertions
- Should see welcome message
- URL should contain "/dashboard"
```

## Environment Variables

Required environment variables in `.env`:
- `ANTHROPIC_API_KEY`: Your Claude API key

## Development

To set up a development environment:

```bash
# Clone the repository
git clone <your-repo-url>
cd <repo-directory>

# Create development environment
uv venv
source .venv/bin/activate  # On Unix
.\.venv\Scripts\Activate.ps1  # On Windows

# Install in editable mode
uv pip install -e .
```

## Troubleshooting

### Common Issues

1. **UV Installation Fails**
   - Ensure you have appropriate permissions
   - Try installing manually from the UV GitHub releases

2. **Virtual Environment Issues**
   - Delete the `.venv` directory and try creating it again
   - Ensure Python 3.9+ is in your PATH

3. **Playwright Installation**
   - If browser installation fails, try running `playwright install` manually
   - Check system requirements for Playwright

4. **API Key Issues**
   - Ensure your Anthropic API key is correctly set in `.env`
   - Check that the `.env` file is in the correct location

5. **Test Runner Issues**
   - Make sure the virtual environment is activated
   - Check that the server script exists at `nltest/server.py`
   - Verify all test files have the `.test.md` extension
   - Look for error messages in the colored output

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Verify your Python version (`python --version`)
3. Check UV is installed correctly (`uv --version`)
4. Ensure all environment variables are set
5. Try running the setup script again

## License

[Your License Here]
