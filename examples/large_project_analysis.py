"""
Example of analyzing a large project with python-code-graph.

This example shows how to configure the library for optimal performance
with large codebases.
"""

import os
import time
from python_code_graph import create_code_graph

def main():
    # Directory to analyze (use a large project like Django or Flask)
    target_dir = os.path.expanduser("~/projects/django")
    
    # Start timing
    start_time = time.time()
    
    # Configure for optimal performance with large projects
    code_graph = create_code_graph(
        directory_path=target_dir,
        output_json_path="django_code_graph.json",
        project_name="Django",
        concurrency=8,  # Increase for more parallelism
        exclude_patterns=[
            "**/tests/**",        # Skip test files
            "**/__pycache__/**",  # Skip cache directories
            "**/migrations/**",   # Skip Django migrations
            "**/venv/**",         # Skip virtual environments
            "**/docs/**",         # Skip documentation
        ],
        use_cache=True,           # Enable caching
        cache_dir="./django_cache",
        debug=False
    )
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Print summary
    print(f"\nAnalysis completed in {elapsed_time:.2f} seconds")
    print(f"Project: {code_graph['name']}")
    print(f"Packages: {len(code_graph['packages'])}")
    
    # Count total files and functions
    total_files = sum(len(pkg['files']) for pkg in code_graph['packages'])
    print(f"Files analyzed: {total_files}")
    
    total_functions = sum(
        sum(len(file['functions']) for file in pkg['files'])
        for pkg in code_graph['packages']
    )
    print(f"Functions found: {total_functions}")
    
    # Find the largest packages
    packages_by_size = sorted(
        code_graph['packages'],
        key=lambda p: len(p['files']),
        reverse=True
    )
    
    print("\nLargest packages:")
    for i, pkg in enumerate(packages_by_size[:5], 1):
        print(f"{i}. {pkg['name']}: {len(pkg['files'])} files")

if __name__ == "__main__":
    main()