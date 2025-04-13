"""Main entry point for Kaido test runner."""

import sys
import asyncio
from .mcp_client import run_test

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: kaido <test_file.md>")
        sys.exit(1)
        
    test_file = sys.argv[1]
    asyncio.run(run_test(test_file))

if __name__ == "__main__":
    main() 