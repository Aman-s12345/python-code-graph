# Python Code Graph Generator

Generate comprehensive code graphs for Python projects. This tool analyzes your Python codebase and creates a detailed JSON representation of its structure, dependencies, and relationships.

<p align="center">
  <img src="https://via.placeholder.com/200x200.png?text=Python+Code+Graph" alt="Python Code Graph Generator Logo" width="200"/>
</p>
<p align="center">
  <a href="https://pypi.org/project/python-code-graph/"><img src="https://img.shields.io/pypi/v/python-code-graph.svg" alt="PyPI version"></a>
  <a href="https://github.com/Aman-s12345/python-code-graph/actions"><img src="https://github.com/Aman-s12345/python-code-graph/workflows/Test/badge.svg" alt="Build Status"></a>
  <a href="https://github.com/Aman-s12345/python-code-graph/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/python-code-graph.svg" alt="License"></a>
  <a href="https://pypi.org/project/python-code-graph/"><img src="https://img.shields.io/pypi/pyversions/python-code-graph.svg" alt="Python Versions"></a>
</p>

## Features

- 📊 Creates detailed code graphs for Python projects
- 🔍 Analyzes functions, classes, variables, and imports
- ⚡ Parallel processing for large codebases
- 💾 Caching for improved performance
- 🧩 Similar format to JavaScript/TypeScript code-graph-generator

## Installation

```bash
pip install python-code-graph
```

## Quick Start

```bash
from python_code_graph import create_code_graph

code_graph = create_code_graph(
    directory_path=".Path/to/my_project",
    output_json_path="output.json"
)
```

## CLI USES
Basic options
```bash
python-code-graph /path/to/your/project -o output.json
```
Advance Options
```bash
python-code-graph [-h] [-o OUTPUT] [-n NAME] [-c CONCURRENCY] [-e EXCLUDE] [--no-cache] [--cache-dir CACHE_DIR] [-d] directory
```

Arguments:

directory: Directory containing Python files to analyze
-o, --output: Output JSON file path (default: [project_name]_code_graph.json)
-n, --name: Project name (default: directory name)
-c, --concurrency: Number of parallel workers (default: 4)
-e, --exclude: Patterns to exclude (can be specified multiple times)
--no-cache: Disable caching
--cache-dir: Directory to store cache files
-d, --debug: Enable debug logging

## Output Format
```bash
{
  "name": "project-name",
  "packages": [
    {
      "name": "package-name",
      "files": [
        {
          "path": "file/path.py",
          "types": [...],
          "variables": [...],
          "functions": [
            {
              "name": "function_name",
              "referencedIn": ["file/path.py"],
              "fileName": "path.py",
              "startLine": 10,
              "length": 5,
              "dependencies": [...],
              "types": [],
              "callsTo": ["other_function"]
            }
          ],
          "dependencies": [...],
          "exports": [...],
          "detailedDependencies": [...]
        }
      ],
      "dependencies": [],
      "exports": []
    }
  ]
}
```
## More on Responce Format
<p align="center">
  <a href="https://www.npmjs.com/package/code-graph-generator"><img  alt="npm version for same project"></a>
</p>

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/amazing-feature)
3. Commit your changes (git commit -m 'Add some amazing feature')
4. Push to the branch (git push origin feature/amazing-feature)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.