import os
import stat
import sys

from pathlib import Path
from typing import List

from loguru import logger

from config import allowed_dirs


def resolve_home(path: str) -> str:
    """Expand ~, ~/ and ${HOME} in a path to the user's home directory."""
    # Expand ${HOME}
    path = os.path.expandvars(path)
    # Expand ~ and ~/
    if path == '~':
        path = os.path.expanduser('~')
    elif path.startswith('~/'):
        path = os.path.join(os.path.expanduser('~'), path[2:])    
    
    return path


def validate_allowed_directories(allowed_directories: List[str]):
    for _, dir_arg in enumerate(allowed_directories):
        expanded_dir = resolve_home(dir_arg)
        if not os.path.exists(expanded_dir):
            logger.error(f"Directory {dir_arg} does not exist")
            sys.exit(1)
        if not os.path.isdir(expanded_dir):
            logger.error(f"{dir_arg} is not a directory")
            sys.exit(1)

def normalize_path(path: str) -> str:
    """Normalize path consistently"""
    return os.path.normpath(path)



async def create_safe_path(path_to_validate: str) -> str:
    """Validate that a path is within allowed directories
    
    Args:
        path_to_validate (str): Path to validate
    
    Returns:
        str: Validated path
    """
    expanded_path = resolve_home(path_to_validate)
    absolute = os.path.abspath(expanded_path)
    normalized_requested = normalize_path(absolute)
    
    is_allowed = any(normalized_requested.startswith(dir) for dir in allowed_dirs)
    if not is_allowed:
        raise ValueError(f"Access denied - path outside allowed directories: {absolute} not in {', '.join(allowed_dirs)}")
    
    # Handle symlinks by checking their real path
    try:
        real_path = os.path.realpath(absolute)
        normalized_real = normalize_path(real_path)
        is_real_path_allowed = any(normalized_real.startswith(dir) for dir in allowed_dirs)
        if not is_real_path_allowed:
            raise ValueError("Access denied - symlink target outside allowed directories")
        return real_path
    except OSError:
        # For new files that don't exist yet, verify parent directory
        parent_dir = os.path.dirname(absolute)
        try:
            real_parent_path = os.path.realpath(parent_dir)
            normalized_parent = normalize_path(real_parent_path)
            is_parent_allowed = any(normalized_parent.startswith(dir) for dir in allowed_dirs)
            if not is_parent_allowed:
                raise ValueError("Access denied - parent directory outside allowed directories")
            return absolute
        except OSError:
            raise ValueError(f"Parent directory does not exist: {parent_dir}")


def get_file_size(path: Path) -> int:
    """Return the size of a file in bytes."""
    return path.stat().st_size if path.is_file() else 0

def get_dir_size(path: Path) -> int:
    """Return the total size of all files in a directory (recursively) in bytes."""
    return sum(f.stat().st_size for f in path.rglob('*') if f.is_file()) if path.is_dir() else 0

def get_permissions(path: Path) -> str:
    """Return the permissions of a file or directory as a string (e.g., 'rwxr-xr-x')."""
    mode = path.stat().st_mode
    return stat.filemode(mode)
