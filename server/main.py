import json
import os
import sys
import shutil
from typing import List

import typer

from pathlib import Path
from mcp.server.fastmcp import FastMCP
from loguru import logger

from utils import create_safe_path, get_dir_size, get_file_size, get_permissions, validate_allowed_directories



# Initialize server
mcp = FastMCP("my-fs-mcp")


@mcp.tool()
def file_info(path: str) -> str:
    """Get meta-information about a file"""
    path_obj = Path(path)

    if not path_obj.exists():
        return f"Path not found: {path}"

    try:
        stat_info = path_obj.stat()
        file_type = "directory" if path_obj.is_dir() else "file"

        info = [
            f"Path: {path}",
            f"Type: {file_type}",
            f"Size (in bytes): {stat_info.st_size}",
            f"Modified: {stat_info.st_mtime}",
            f"Created: {stat_info.st_ctime}",
            f"Perm:: {get_permissions(Path(path))}",
        ]

        info_text = "\n".join(info)
        return f"File Info:\n{info_text}"

    except PermissionError:
        return f"Permission denied accessing: {path}"
    except Exception as e:
        return f"Error getting file info: {str(e)}"

@mcp.tool()
def ls(path: str = os.path.expanduser("~/Bonkers")) -> str:
    """List files in a directory with metadata"""

    path_obj = Path(path)

    if not path_obj.exists():
        return f"Directory not found: {path}"

    if not path_obj.is_dir():
        return f"Path is not a directory: {path}"

    try:
        files = []
        for item in path_obj.iterdir():
            elem_info = {}
            elem_info["name"] = item.name
            file_type = "directory" if item.is_dir() else "file"
            elem_info["type"] = file_type
            elem_info["size_in_bytes"] = get_dir_size(item) if item.is_dir() else get_file_size(item)
            elem_info["perm"] = get_permissions(item)
            files.append(elem_info)

        if not files:
            return f"Directory is empty: {path}"

        return json.dumps(files, indent=2)

    except PermissionError:
        return f"Permission denied accessing: {path}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@mcp.tool()
async def mkdir(path: str, overwrite: bool = False) -> str:
    """Create a directory at the given path. If overwrite is True, 
    remove and recreate if it exists. Safety: disallows absolute paths
    and parent-relative paths."""
    
    logger.info(f"Path passed to create dir: {path}")
    path_obj = Path(await create_safe_path(path))
    logger.info(f"Creating dir on {path_obj}")
    
    
    # Safety net: disallow absolute paths and parent-relative paths
    # if path_obj.is_absolute():
    #     return "Error: Absolute paths are not allowed."
    # if any(part == ".." for part in path_obj.parts):
    #     return "Error: Parent-relative paths ('..') are not allowed."
    try:
        if path_obj.exists():
            if not path_obj.is_dir():
                return f"Path exists and is not a directory: {path}"
            if overwrite:
                shutil.rmtree(path_obj)
                path_obj.mkdir(parents=True, exist_ok=True)
                return f"Directory overwritten: {path}"
            else:
                return f"Directory already exists: {path}"
        else:
            path_obj.mkdir(parents=True, exist_ok=True)
            return f"Directory created: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@mcp.tool()
def current_user() -> str:
    """Return the username of the user executing commands."""
    try:
        import getpass
        return getpass.getuser()
    except Exception as e:
        return f"Error getting current user: {str(e)}"

@mcp.tool()
async def list_workspaces() -> str:
    """Returns the list of directories (workspaces) that this server is allowed to access.
    
    These should be the only directories available to access/act on files.
    
    Returns:
        str: A newline-separated list of allowed directories
    """
    return f"Workspaces:\n{chr(10).join(allowed_dirs)}"


from config import allowed_dirs


def main(workspace: str = os.path.expanduser("~/Bonkers"), debug: bool = False):
    
    try:
        # logger.info(f"Current workspaces: {allowed_dirs} {type(allowed_dirs)}")
        logger.info(f"Current workspace: {workspace}")
        global allowed_dirs
        allowed_dirs.append(workspace)
        logger.info(f"Validating workspace directories {allowed_dirs}...")
        validate_allowed_directories(allowed_dirs)
        logger.info("Worspace validation completed successfully")
        if debug:
            logger.info("Starting File Manager MCP Server...")
            logger.info(f"Workspace (allowed dir): {allowed_dirs}")
        mcp.run()

    except KeyboardInterrupt:
        logger.warning("Ctrl+C caught! Exiting...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Exception {e}")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
