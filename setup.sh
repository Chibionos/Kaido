#!/bin/bash

# Exit on error
set -e

echo "Setting up Natural Language Test Runner..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is required but not installed. Please install Node.js first."
    echo "Visit https://nodejs.org/ for installation instructions."
    exit 1
fi

# Check if Python 3.10 is installed
if ! command -v python3.10 &> /dev/null; then
    echo "Python 3.10 is required but not installed. Please install Python 3.10 first."
    exit 1
fi

# Install UV if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing UV package manager..."
    curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-installer.sh | sh
fi

# Create virtual environment using UV
echo "Creating Python virtual environment..."
uv venv

# Activate virtual environment based on OS
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source .venv/bin/activate
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    echo "Unsupported OS. Please activate the virtual environment manually."
    exit 1
fi

# Create .python-version file
echo "Creating .python-version file..."
echo "3.10" > .python-version

# Install Python dependencies using UV
echo "Installing Python dependencies..."
uv pip compile pyproject.toml -o uv.lock
uv pip install -e .

# Install Playwright MCP globally
echo "Installing Playwright MCP..."
npm install -g @playwright/mcp@latest

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOL
CLAUDE_API_KEY=
MCP_PLAYWRIGHT_URL=http://localhost:8931/sse
EOL
    echo "Please add your Claude API key to the .env file"
fi

echo "Setup complete! Please ensure you have added your Claude API key to the .env file."
echo "To run tests:"
echo "1. Start the Playwright MCP server: npx @playwright/mcp@latest --port 8931"
echo "2. Run a test: kaido test.md" 