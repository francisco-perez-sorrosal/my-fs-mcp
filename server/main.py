import os
import sys
import argparse
from mcp.server.fastmcp import FastMCP

print("About to parse args...", file=sys.stderr)

# Parse command line arguments
parser = argparse.ArgumentParser(description="Filesystem Access MCP Server")
parser.add_argument(
    "--workspace", default=os.path.expanduser("~/Documents"), help="Workspace directory"
)
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
args = parser.parse_args()

print("Initializing server...", file=sys.stderr)

# Initialize server
mcp = FastMCP("my-fs-mcp")


@mcp.tool()
def ls() -> str:
    """List files and dirs"""
    print("Calling tool...", file=sys.stderr)
    return "TODOOOOOOOOOOO"


if __name__ == "__main__":
    print("On main...", file=sys.stderr)
    if args.debug:
        print("Starting File Manager MCP Server...", file=sys.stderr)
        print(f"Workspace: {args.workspace}", file=sys.stderr)

    mcp.run()
