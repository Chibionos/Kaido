#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_step() {
    echo -e "${BLUE}==>${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Check if virtual environment exists
log_step "Checking virtual environment..."
if [ ! -d ".venv" ]; then
    log_error "Virtual environment not found. Please run setup.sh first."
fi
log_success "Virtual environment found"

# Activate virtual environment based on OS
log_step "Activating virtual environment..."
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source .venv/bin/activate
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    log_error "Unsupported OS. Please activate the virtual environment manually."
fi
log_success "Virtual environment activated"

# Check if .env file exists and required variables are set
log_step "Checking environment configuration..."
if [ ! -f ".env" ]; then
    log_error "Error: .env file not found. Please run setup.sh first."
fi

# Check CLAUDE_API_KEY
if ! grep -q "CLAUDE_API_KEY=" .env || [ -z "$(grep "CLAUDE_API_KEY=" .env | cut -d '=' -f2)" ]; then
    log_error "CLAUDE_API_KEY not set in .env file. Please add your Claude API key to the .env file"
fi
log_success "Environment variables verified"

# Check if test file argument is provided
if [ -z "$1" ]; then
    log_error "Please provide a test file path. Usage: ./run.sh <test_file.md>"
fi

# Check if test file exists
if [ ! -f "$1" ]; then
    log_error "Test file '$1' not found"
fi
log_success "Test file found: $1"

# Remind about MCP server
log_step "Checking prerequisites..."
echo "Make sure the Playwright MCP server is running:"
echo "  npx @playwright/mcp@latest --port 8931"
echo ""

log_step "Starting Natural Language Test Runner..."
echo "Test file: $1"
echo "MCP Server: http://localhost:8931/sse"
echo ""

# Run the test using kaido command
kaido "$1"

# Check if the command was successful
if [ $? -eq 0 ]; then
    log_success "Test execution completed successfully"
else
    log_error "Test execution failed"
fi 