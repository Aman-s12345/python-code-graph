import os
from typing import List, Optional, Set
import hashlib
import json

def find_python_files(directory: str, exclude_patterns: Optional[List[str]] = None) -> List[str]:
    """
    Find all Python files in a directory, respecting exclusion patterns.
    
    Args:
        directory: The root directory to search
        exclude_patterns: Glob-like patterns to exclude (e.g. "**/venv/**")
        
    Returns:
        List of full paths to Python files
    """
    if exclude_patterns is None:
        exclude_patterns = ["**/venv/**", "**/.git/**", "**/__pycache__/**", "**/node_modules/**"]
        
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs_to_remove = []
        for i, d in enumerate(dirs):
            dir_path = os.path.join(root, d)
            rel_path = os.path.relpath(dir_path, directory)
            if any(_matches_pattern(rel_path, pattern) for pattern in exclude_patterns):
                dirs_to_remove.append(i)
        
        # Remove directories from bottom up to avoid index issues
        for i in sorted(dirs_to_remove, reverse=True):
            dirs.pop(i)
            
        # Find Python files
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, directory)
                if not any(_matches_pattern(rel_path, pattern) for pattern in exclude_patterns):
                    python_files.append(file_path)
                    
    return python_files

def _matches_pattern(path: str, pattern: str) -> bool:
    """
    Check if a path matches a glob-like pattern.
    Simple implementation for common patterns.
    """
    if pattern.startswith('**/'):
        return path.endswith(pattern[3:])
    elif pattern.endswith('/**'):
        return path.startswith(pattern[:-3])
    elif '/**/' in pattern:
        parts = pattern.split('/**/')
        return path.startswith(parts[0]) and path.endswith(parts[1])
    else:
        return path == pattern

def read_file(file_path: str) -> str:
    """Read a file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
        
def compute_file_hash(file_path: str) -> str:
    """Compute a hash of the file contents for caching."""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def ensure_dir(directory: str) -> None:
    """Ensure a directory exists."""
    os.makedirs(directory, exist_ok=True)

