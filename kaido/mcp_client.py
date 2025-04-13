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
        """Process a query using Claude and available tools in a ReAct style loop."""
        system_prompt = """You are a test automation assistant that follows a ReAct (Reason + Act) approach.
For each step, you must:

1. THINK: Analyze the current state and plan the next action
   - What is the current state?
   - What needs to be done next?
   - What should be verified?

2. ACT: Execute the planned action using available tools
   - Choose the appropriate tool
   - Provide correct parameters
   - Execute the action

3. OBSERVE: Verify the results
   - Check if the action succeeded
   - Verify the expected state
   - Determine if we can proceed

4. REPEAT: Continue the loop until all test steps are complete

Format your responses as:
THINK: [Your analysis of the current state and next steps]
ACT: [The action you're taking]
OBSERVE: [Verification of results]
NEXT: [What needs to be done next]

Available browser tools:
Navigation:
- browser_navigate: Navigate to a URL
- browser_navigate_back: Go back to previous page
- browser_navigate_forward: Go forward in browser history

Page Interaction:
- browser_click: Click on an element
- browser_type: Type text into an input field
- browser_press_key: Press a keyboard key
- browser_hover: Hover over an element
- browser_drag: Drag and drop elements
- browser_select_option: Select an option from a dropdown
- browser_file_upload: Upload a file to the page

Waiting and State:
- browser_wait: Wait for an element to be visible/present
- browser_snapshot: Get the current page state and DOM structure
- browser_take_screenshot: Capture a screenshot of the page

Tab Management:
- browser_tab_new: Open a new browser tab
- browser_tab_close: Close the current tab
- browser_tab_list: List all open tabs
- browser_tab_select: Switch to a specific tab

Other:
- browser_close: Close the browser
- browser_install: Install browser dependencies
- browser_pdf_save: Save the current page as PDF

For each step:
1. Choose the appropriate tool for the action
2. Execute it with the correct parameters
3. Verify the result using browser_snapshot if needed
4. Continue to the next step immediately
5. Do not stop until all steps are completed

Important: 
- Execute ALL steps in sequence
- After each tool call, proceed to the next step immediately
- Use browser_wait appropriately before interactions to ensure elements are ready
- Verify results after important actions using browser_snapshot"""

        messages = [
            {"role": "user", "content": "Please execute the following test using the ReAct approach:\n\n" + query}
        ]
        
        try:
            # Get available tools
            response = await self.session.list_tools()
            available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in response.tools]

            final_text = []
            
            while True:
                # Get next action from Claude
                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=messages,
                    tools=available_tools
                )
                
                has_tool_call = False
                for content in response.content:
                    if content.type == 'text':
                        final_text.append(content.text)
                    elif content.type == 'tool_use':
                        has_tool_call = True
                        tool_name = content.name
                        tool_args = content.input
                        
                        # Execute action
                        result = await self.session.call_tool(tool_name, tool_args)
                        
                        # Get current state for verification
                        state = await self.session.call_tool('browser_snapshot', {})
                        
                        # Format the state information
                        state_text = str(state.content[0].text) if state.content else "No state available"
                        
                        # Log the ReAct cycle
                        final_text.append(f"\nTHINK: Current step - {tool_name}")
                        final_text.append(f"ACT: Executing {tool_name} with parameters: {tool_args}")
                        final_text.append(f"OBSERVE: Result: {result.content}")
                        final_text.append(f"STATE: Current page state:\n{state_text}")
                        
                        # Continue conversation with results
                        messages.append({
                            "role": "assistant",
                            "content": f"""
THINK: I executed {tool_name}
ACT: Action completed with parameters {tool_args}
OBSERVE: 
- Action Result: {result.content}
- Current Page State: {state_text}
NEXT: Let me analyze the results and determine the next step."""
                        })
                        messages.append({
                            "role": "user",
                            "content": """Based on the current state:
1. Was the last action successful?
2. What is the next step in our test sequence?
3. What specific action should we take next?

Please respond in ReAct format and execute the next action."""
                        })
                        break
                
                if not has_tool_call:
                    # Check if we're done or if Claude needs prompting
                    if "test completed" in response.content[0].text.lower():
                        break
                    messages.append({
                        "role": "user",
                        "content": """What is the next action we need to take? Please analyze and respond in ReAct format:
THINK: [Analyze current state and next required step]
ACT: [Specify the next action needed]
OBSERVE: [What should we verify]
NEXT: [Execute the action]"""
                    })
            
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