from fastmcp import FastMCP
import random
import json


# Create the FastMCP server instance
mcp = FastMCP("Simple Calculator Server")

# Tool: Add two numbers
@mcp.tool
def add(a:int, b:int) -> int:
    """Adds two integers together.
    
    Args:
        a: First integer to add.
        b: Second integer to add.
    Returns:
        The sum of a and b.
    """
    return a + b

# Tool: Generate a random number
@mcp.tool
def random_number(min_val: int=1, max_val: int=100) -> int:
    """Generates a random integer between min_val and max_val (inclusive).
    
    Args:
        min_val: The minimum value (inclusive).
        max_val: The maximum value (inclusive).
    Returns:
        A random integer between min_val and max_val.
    """
    return random.randint(min_val, max_val)

# Resource: Server information
@mcp.resource("info://server")
def server_info() -> str:
    """Get information about the server."""
    info = {
        "name": "Simple Calculator Server",
        "version": "1.0.0",
        "description": "A simple calculator server with basic arithmetic operations.",
        "tools": ["add", "random_number"],
        "author": "Ali Ahmad"
    }
    return json.dumps(info)

# Start the FastMCP server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8080)