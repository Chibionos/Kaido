#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo "Please run setup.sh first to set up the environment"
    exit 1
fi

# Activate virtual environment
if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
    source .venv/bin/activate
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    source .venv/Scripts/activate
else
    echo -e "${RED}Error: Unsupported OS${NC}"
    exit 1
fi

# Check if server script exists
SERVER_SCRIPT="nltest/server.py"
if [ ! -f "$SERVER_SCRIPT" ]; then
    echo -e "${RED}Error: Server script not found at $SERVER_SCRIPT${NC}"
    exit 1
fi

# Function to run tests in a directory
run_tests() {
    local test_dir=$1
    local total=0
    local passed=0
    local failed=0
    local failed_tests=()

    # Find all .test.md files
    while IFS= read -r test_file; do
        ((total++))
        echo -e "\n${BLUE}${BOLD}Running test: ${test_file}${NC}"
        echo "----------------------------------------"
        
        if nltest run "$test_file" "$SERVER_SCRIPT"; then
            ((passed++))
            echo -e "${GREEN}✓ Test passed${NC}"
        else
            ((failed++))
            failed_tests+=("$test_file")
            echo -e "${RED}✗ Test failed${NC}"
        fi
    done < <(find "$test_dir" -name "*.test.md")

    # Print summary
    echo -e "\n${BOLD}Test Summary${NC}"
    echo "----------------------------------------"
    echo -e "Total tests:  $total"
    echo -e "Passed:       ${GREEN}$passed${NC}"
    if [ $failed -gt 0 ]; then
        echo -e "Failed:       ${RED}$failed${NC}"
        echo -e "\n${RED}Failed tests:${NC}"
        for test in "${failed_tests[@]}"; do
            echo -e "${RED}  ✗ $test${NC}"
        done
    else
        echo -e "Failed:       ${GREEN}$failed${NC}"
        echo -e "\n${GREEN}All tests passed!${NC}"
    fi
}

# Default test directory
TEST_DIR="tests"

# Check if test directory exists
if [ ! -d "$TEST_DIR" ]; then
    echo -e "${RED}Error: Test directory not found at $TEST_DIR${NC}"
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ] && [ ! -f .env ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not found${NC}"
    echo "Please set your API key in .env file"
    exit 1
fi

# Run the tests
echo -e "${BLUE}${BOLD}Starting test run...${NC}"
run_tests "$TEST_DIR" 