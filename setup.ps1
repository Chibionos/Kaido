# Check if Python 3.10 is installed
$pythonVersion = python --version 2>&1
if (!($pythonVersion -match "Python 3\.10\.*")) {
    Write-Host "Python 3.10 is required but not found. Please install Python 3.10"
    exit 1
}

# Create .python-version file
Write-Host "Creating .python-version file..."
"3.10" | Out-File -FilePath .python-version -Encoding UTF8 -NoNewline

# Check if uv is installed
if (!(Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "Installing uv..."
    iwr -useb https://github.com/astral-sh/uv/releases/latest/download/uv-installer.ps1 | iex
}

# Create and activate virtual environment
Write-Host "Creating virtual environment..."
uv venv

# Activate virtual environment
Write-Host "Activating virtual environment..."
.\.venv\Scripts\Activate.ps1

# Install dependencies using uv
Write-Host "Installing dependencies..."
uv pip compile pyproject.toml -o uv.lock
uv pip install -e .

# Install Playwright browsers
Write-Host "Installing Playwright browsers..."
playwright install chromium

# Create .env file if it doesn't exist
if (!(Test-Path .env)) {
    Write-Host "Creating .env file..."
    "ANTHROPIC_API_KEY=" | Out-File -FilePath .env -Encoding UTF8
    Write-Host "Please add your Anthropic API key to the .env file"
}

Write-Host "Setup complete! You can now run 'kaido' commands."
Write-Host "Don't forget to set your ANTHROPIC_API_KEY in the .env file." 