import argparse
import os
import sys
import json
from .core import create_code_graph
from .utils import get_logger

logger = get_logger()

def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a code graph for Python projects"
    )
    
    parser.add_argument(
        "directory", 
        help="Directory containing Python files to analyze"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output JSON file path (default: [project_name]_code_graph.json)",
        default=None
    )
    
    parser.add_argument(
        "-n", "--name",
        help="Project name (default: directory name)",
        default=None
    )
    
    parser.add_argument(
        "-c", "--concurrency",
        help="Number of parallel workers (default: 4)",
        type=int,
        default=4
    )
    
    parser.add_argument(
        "-e", "--exclude",
        help="Patterns to exclude (can be specified multiple times)",
        action="append",
        default=None
    )
    
    parser.add_argument(
        "--no-cache",
        help="Disable caching",
        action="store_true"
    )
    
    parser.add_argument(
        "--cache-dir",
        help="Directory to store cache files",
        default=None
    )
    
    parser.add_argument(
        "-d", "--debug",
        help="Enable debug logging",
        action="store_true"
    )
    
    args = parser.parse_args()
    
    try:
        # Create code graph
        code_graph = create_code_graph(
            directory_path=args.directory,
            output_json_path=args.output,
            project_name=args.name,
            concurrency=args.concurrency,
            exclude_patterns=args.exclude,
            use_cache=not args.no_cache,
            cache_dir=args.cache_dir,
            debug=args.debug
        )
        
        # Print summary
        print(f"\nCode Graph Summary:")
        print(f"  Project: {code_graph['name']}")
        print(f"  Packages: {len(code_graph['packages'])}")
        
        total_files = sum(len(pkg['files']) for pkg in code_graph['packages'])
        print(f"  Files: {total_files}")
        
        total_functions = sum(
            sum(len(file['functions']) for file in pkg['files'])
            for pkg in code_graph['packages']
        )
        print(f"  Functions: {total_functions}")
        
        if args.output:
            print(f"\nCode graph saved to: {args.output}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()