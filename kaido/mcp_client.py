"""MCP client implementation for natural language test execution."""

import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import os

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from dotenv import load_dotenv

console = Console()

class MCPClient:
    """MCP client for executing natural language tests using Claude."""
    
    def __init__(self):
        """Initialize the MCP client."""
        load_dotenv()  # load environment variables from .env
        
        # Get API key from environment
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise RuntimeError("CLAUDE_API_KEY environment variable is not set")
            
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=api_key)
        self.available_tools = []
        
    async def connect_to_server(self):
        """Connect to the Playwright MCP server."""
        try:
            # Connect to Playwright MCP server
            server_params = StdioServerParameters(
                command="npx",
                args=["@playwright/mcp@latest"],
                env=None
            )
            
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(ClientSession(stdio, write))
            
            await self.session.initialize()
            
            # List available tools
            response = await self.session.list_tools()
            self.available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]
            
            console.print("\nConnected to Playwright MCP server with tools:", [tool["name"] for tool in self.available_tools])
        except Exception as e:
            await self.cleanup()
            raise RuntimeError(f"Failed to connect to Playwright MCP server: {str(e)}")

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools."""
        messages = [{"role": "user", "content": query}]
        
        try:
            # Get available tools
            response = await self.session.list_tools()
            available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]

            # Initial Claude API call
            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=messages,
                tools=available_tools
            )
            
            final_text = []
            
            for content in response.content:
                if content.type == 'text':
                    final_text.append(content.text)
                elif content.type == 'tool_use':
                    tool_name = content.name
                    tool_args = content.input
                    
                    # Execute tool call
                    result = await self.session.call_tool(tool_name, tool_args)
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                    # Continue conversation with tool results
                    if hasattr(content, 'text') and content.text:
                        messages.append({
                            "role": "assistant",
                            "content": content.text
                        })
                    messages.append({
                        "role": "user",
                        "content": result.content
                    })
                    
                    # Get next response from Claude
                    response = self.anthropic.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=1000,
                        messages=messages,
                    )
                    final_text.append(response.content[0].text)
            
            return "\n".join(final_text)
        except Exception as e:
            raise RuntimeError(f"Failed to process query: {str(e)}")

    async def chat_loop(self):
        """Run an interactive chat loop"""
        console.print("\nMCP Client Started!")
        console.print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                console.print("\n" + response)
                    
            except Exception as e:
                console.print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()

async def run_test(test_file: str):
    """Run a test from a file."""
    client = MCPClient()
    try:
        await client.connect_to_server()
        
        with open(test_file, 'r') as f:
            test_content = f.read()
        
        result = await client.process_query(test_content)
        console.print("\nTest Result:")
        console.print(result)
            
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        asyncio.run(MCPClient().chat_loop())
    else:
        asyncio.run(run_test(sys.argv[1])) 