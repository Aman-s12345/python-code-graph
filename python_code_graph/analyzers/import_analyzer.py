"""
Import analyzer module for Python Code Graph Generator.

This module provides tools for extracting import/dependency information
from Python source files.
"""

import ast
from typing import Dict, List, Any, Set, Optional

class ImportAnalyzer:
    """
    Analyzer for Python import statements.
    
    This class extracts import statements from Python code and provides
    information about module dependencies.
    """
    
    def __init__(self):
        self.imports = []
        self.detailed_dependencies = []
    
    def analyze(self, content: str) -> Dict[str, Any]:
        """
        Analyze a Python file's import statements.
        
        Args:
            content: Python file content
            
        Returns:
            Dict with import information
        """
        try:
            tree = ast.parse(content)
            visitor = ImportVisitor()
            visitor.visit(tree)
            
            self.imports = visitor.imports
            self.detailed_dependencies = visitor.detailed_dependencies
            
            return {
                'imports': self.imports,
                'detailed_dependencies': self.detailed_dependencies
            }
        except SyntaxError as e:
            # Return partial information in case of syntax errors
            return {
                'error': str(e),
                'imports': [],
                'detailed_dependencies': []
            }
            
class ImportVisitor(ast.NodeVisitor):
    """Extract import information from Python files."""
    
    def __init__(self):
        self.imports = []
        self.detailed_dependencies = []
        
    def visit_Import(self, node: ast.Import) -> None:
        """Process simple imports: import x, y, z"""
        for name in node.names:
            alias = name.asname or name.name
            module = name.name
            self.imports.append(module)
            
            detailed = {
                "module": module,
                "imports": [alias]
            }
            
            # Check if this module is already in detailed_dependencies
            existing = next((d for d in self.detailed_dependencies if d["module"] == module), None)
            if existing:
                existing["imports"].append(alias)
            else:
                self.detailed_dependencies.append(detailed)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from x import y, z imports"""
        if node.module is None:  # relative import like "from . import x"
            return
            
        module = node.module
        if node.level > 0:  # Handle relative imports
            module = '.' * node.level + module
            
        self.imports.append(module)
        
        imports = []
        for name in node.names:
            alias = name.asname or name.name
            imports.append(name.name)
            
        detailed = {
            "module": module,
            "imports": imports
        }
        
        # Check if this module is already in detailed_dependencies
        existing = next((d for d in self.detailed_dependencies if d["module"] == module), None)
        if existing:
            existing["imports"].extend(imports)
        else:
            self.detailed_dependencies.append(detailed)

def analyze_imports(content: str) -> Dict[str, Any]:
    """
    Analyze imports in Python content.
    
    Args:
        content: Python code content
        
    Returns:
        Dict with import information
    """
    analyzer = ImportAnalyzer()
    return analyzer.analyze(content)