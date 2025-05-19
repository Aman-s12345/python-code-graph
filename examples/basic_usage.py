"""
Basic usage example for python-code-graph.

This example shows how to generate a code graph for a small project.
"""

from python_code_graph import create_code_graph

def main():
    # Generate a code graph for a project
    code_graph = create_code_graph(
        directory_path="./my_project",
        output_json_path="my_project_graph.json",
        concurrency=4,
        debug=True
    )
    
    # Print some information from the code graph
    print(f"Project: {code_graph['name']}")
    print(f"Packages: {len(code_graph['packages'])}")
    
    # Access specific information
    if code_graph['packages']:
        package = code_graph['packages'][0]
        print(f"First package: {package['name']}")
        
        if package['files']:
            file = package['files'][0]
            print(f"First file: {file['path']}")
            
            if file['functions']:
                func = file['functions'][0]
                print(f"First function: {func['name']}")
                print(f"  Calls to: {func.get('callsTo', [])}")

if __name__ == "__main__":
    main()