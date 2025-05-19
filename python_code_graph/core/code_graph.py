import os
import json
from typing import Dict, List, Any, Optional, Union, Set
from ..utils import find_python_files, ensure_dir, get_logger
from .file_processor import FileProcessor

logger = get_logger()

def create_code_graph(
        directory_path: str,
        output_json_path: Optional[str] = None,
        project_name: Optional[str] = None,
        concurrency: int = 4,
        exclude_patterns: Optional[List[str]] = None,
        use_cache: bool = True,
        cache_dir: Optional[str] = None,
        debug: bool = False
    ) -> Dict[str, Any]:
    """
    Analyze Python files in a directory and generate a code graph.
    
    Args:
        directory_path: Path to the directory containing Python files
        output_json_path: Path where the JSON output will be saved (optional)
        project_name: Name of the project (default: directory basename)
        concurrency: Number of parallel workers for file processing
        exclude_patterns: Patterns of files/directories to exclude
        use_cache: Whether to use caching for file analysis
        cache_dir: Directory to store cache files
        debug: Enable debug logging
        
    Returns:
        The code graph data as a dictionary
    """
    # Set log level based on debug flag
    if debug:
        logger.set_level(10)  # DEBUG level
    
    # Normalize directory path
    directory_path = os.path.abspath(directory_path)
    
    # Extract project name from directory if not provided
    if not project_name:
        project_name = os.path.basename(directory_path)
    
    # Set default output path if not provided
    if not output_json_path:
        output_json_path = f"{project_name}_code_graph.json"
    
    logger.info(f"Analyzing Python code in {directory_path}")
    logger.info(f"Project name: {project_name}")
    
    # Find all Python files in the directory
    python_files = find_python_files(directory_path, exclude_patterns)
    
    if not python_files:
        logger.warning(f"No Python files found in {directory_path}")
        return {"name": project_name, "packages": []}
    
    logger.info(f"Found {len(python_files)} Python files to analyze")
    
    # Process files
    processor = FileProcessor(
        concurrency=concurrency,
        use_cache=use_cache,
        cache_dir=cache_dir
    )
    file_data = processor.process_files(python_files)
    
    # Transform to the desired format
    code_graph = transform_to_code_graph(file_data, directory_path, project_name)
    
    # Save to JSON file if path provided
    if output_json_path:
        output_dir = os.path.dirname(output_json_path)
        if output_dir:
            ensure_dir(output_dir)
            
        with open(output_json_path, 'w') as f:
            json.dump(code_graph, f, indent=2)
        
        logger.info(f"Code graph saved to: {output_json_path}")
    
    return code_graph

def transform_to_code_graph(
        file_data: List[Dict[str, Any]],
        base_path: str,
        project_name: str
    ) -> Dict[str, Any]:
    """
    Transform the analyzed data to the code graph format.
    
    Args:
        file_data: List of file analysis results
        base_path: Base directory path
        project_name: Project name
        
    Returns:
        Code graph in standard format
    """
    result = {
        "name": project_name,
        "packages": []
    }
    
    # Group by directories/packages
    packages = {}
    
    for file_info in file_data:
        # Skip files with errors
        if 'error' in file_info:
            logger.warning(f"Skipping file with error: {file_info['file_path']}")
            continue
            
        # Get relative path from base_path
        rel_path = os.path.relpath(file_info['file_path'], base_path)
        dir_name = os.path.dirname(rel_path) or '.'
        file_name = os.path.basename(rel_path)
        
        # Create package if it doesn't exist
        if dir_name not in packages:
            packages[dir_name] = {
                "name": dir_name,
                "files": [],
                "dependencies": [],
                "exports": []
            }
        
        # Create file entry
        file_entry = {
            "path": rel_path,
            "types": [],  # For Python classes
            "variables": [],
            "functions": [],
            "dependencies": file_info.get('imports', []),
            "exports": file_info.get('exports', []),
            "detailedDependencies": file_info.get('detailed_dependencies', [])
        }
        
        # Add variables
        for var in file_info.get('variables', []):
            var_entry = {
                "name": var["name"],
                "type": var.get("type", "unknown")
            }
            
            # Add dependencies if any
            var_deps = []
            if var.get("name") in file_info.get('variable_dependencies', {}):
                for dep in file_info['variable_dependencies'][var["name"]]:
                    var_deps.append({dep: "module"})
            elif "dependencies" in var:
                for dep in var["dependencies"]:
                    var_deps.append({dep: "module"})
                    
            var_entry["dependencies"] = var_deps
            file_entry["variables"].append(var_entry)
        
        # Add class types
        for class_name in file_info.get('classes', []):
            type_entry = {
                "name": class_name,
                "file": rel_path,
                "properties": []
            }
            file_entry["types"].append(type_entry)
        
        # Add functions
        for func_name in file_info.get('functions', []):
            lines = file_info.get('function_lines', {}).get(func_name, {'start': 0, 'end': 0})
            length = lines['end'] - lines['start'] + 1
            
            function_entry = {
                "name": func_name,
                "referencedIn": [rel_path],
                "fileName": file_name,
                "startLine": lines['start'],
                "length": length,
                "dependencies": [],
                "types": [],
                "callsTo": file_info.get('function_calls', {}).get(func_name, [])
            }
            file_entry["functions"].append(function_entry)
        
        # Add "root" function to match React output format
        if file_entry["functions"]:
            root_func = {
                "name": "root",
                "referencedIn": [],
                "fileName": file_name,
                "startLine": 1,
                "length": file_info.get('line_count', 0),
                "dependencies": [{imp: "module"} for imp in file_info.get('imports', [])],
                "types": [],
                "callsTo": [],
                "calledBy": []
            }
            
            # Add root func only if it doesn't exist
            if not any(f["name"] == "root" for f in file_entry["functions"]):
                file_entry["functions"].insert(0, root_func)
        
        # Add file to package
        packages[dir_name]["files"].append(file_entry)
        
        # Add exports to package level
        packages[dir_name]["exports"].extend(file_info.get('exports', []))
    
    # Remove duplicates from package exports
    for pkg in packages.values():
        pkg["exports"] = list(set(pkg["exports"]))
    
    # Convert packages dictionary to list
    result["packages"] = list(packages.values())
    
    return result