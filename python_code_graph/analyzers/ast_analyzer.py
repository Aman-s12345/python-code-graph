import ast
from collections import defaultdict
from typing import Dict, List, Any, Optional, Set, Tuple

class FunctionVisitor(ast.NodeVisitor):
    """Extract function and method information from Python files."""
    
    def __init__(self):
        self.functions = []
        self.current_function = None
        self.function_calls = defaultdict(list)
        self.function_lines = {}
        self.exports = []
        self.classes = []
        self.class_methods = defaultdict(list)
        self.current_class = None
        self.variables = []
        self.variable_dependencies = defaultdict(list)
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Skip if this is a class method (handled separately)
        if self.current_class:
            self.class_methods[self.current_class].append(node.name)
            
        # Record function info
        func_name = node.name
        self.functions.append(func_name)
        self.function_lines[func_name] = {
            'start': node.lineno,
            'end': self._find_last_line(node)
        }
        
        # Check if function is exported
        if func_name.startswith('__') and func_name.endswith('__'):
            pass  # Skip magic methods for exports
        elif node.decorator_list:
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'export':
                    self.exports.append(func_name)
        else:
            # Functions at module level are considered "exported"
            if not self.current_class and not self.current_function:
                self.exports.append(func_name)
        
        # Visit the function body to find function calls
        parent_function = self.current_function
        self.current_function = func_name
        self.generic_visit(node)
        self.current_function = parent_function
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        # Handle async functions the same way as regular functions
        self.visit_FunctionDef(node)
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        class_name = node.name
        self.classes.append(class_name)
        self.exports.append(class_name)  # Classes at module level are exported
        
        parent_class = self.current_class
        self.current_class = class_name
        self.generic_visit(node)
        self.current_class = parent_class
        
    def visit_Call(self, node: ast.Call) -> None:
        if not self.current_function:
            self.generic_visit(node)
            return
            
        if isinstance(node.func, ast.Name):
            # Direct function call like func()
            func_name = node.func.id
            self.function_calls[self.current_function].append(func_name)
            
            # Check for special 'useState' equivalent in Python
            if func_name == 'useState' and len(node.args) > 0:
                # This is similar to React's useState hook
                # We'll need to track this in the parent Assign node
                pass
                
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            # Method call like obj.method()
            self.function_calls[self.current_function].append(node.func.attr)
        
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign) -> None:
        # Look for assignments like module.exports = X or exports = Y
        if (isinstance(node.targets[0], ast.Name) and 
            node.targets[0].id in ['exports', '__all__']):
            if isinstance(node.value, ast.List):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Str):
                        self.exports.append(elt.s)
                    elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        self.exports.append(elt.value)
        
        # Handle variable assignments
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                var_type = self._infer_type(node.value)
                
                # Check if this is a "state" variable (similar to React's useState)
                is_state = False
                if (isinstance(node.value, ast.Call) and 
                    isinstance(node.value.func, ast.Name) and 
                    node.value.func.id == 'useState'):
                    is_state = True
                    var_type = 'State'
                elif (isinstance(node.value, ast.Subscript) and 
                      isinstance(node.value.value, ast.Name) and 
                      node.value.value.id == 'state'):
                    is_state = True
                    var_type = 'State'
                
                # Add to variables with context
                if self.current_function:
                    context = f"in {self.current_function}"
                elif self.current_class:
                    context = f"in {self.current_class}"
                else:
                    context = "module-level"
                
                # Add appropriate suffix for state variables
                display_name = var_name
                if is_state:
                    display_name = f"{var_name} (State)"
                
                self.variables.append({
                    "name": display_name,
                    "type": var_type,
                    "context": context
                })
                
                # Track dependencies
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        self.variable_dependencies[var_name].append(node.value.func.id)
            
            # Handle tuple unpacking (like message, setMessage = useState(...))
            elif isinstance(target, ast.Tuple):
                # Check if this is a "useState" equivalent pattern
                if (isinstance(node.value, ast.Call) and 
                    isinstance(node.value.func, ast.Name) and 
                    node.value.func.id in ['useState', 'React.useState']):
                    
                    # Extract the variable names from the tuple
                    if len(target.elts) >= 2:
                        state_var = target.elts[0]
                        setter_var = target.elts[1]
                        
                        if isinstance(state_var, ast.Name) and isinstance(setter_var, ast.Name):
                            # Add state variable
                            self.variables.append({
                                "name": f"{state_var.id} (State)",
                                "type": "State",
                                "dependencies": ["useState"]
                            })
                            
                            # Add setter variable
                            self.variables.append({
                                "name": f"{setter_var.id} (State Setter)",
                                "type": "StateSetter",
                                "dependencies": [state_var.id]
                            })
        
        self.generic_visit(node)
        
    def _infer_type(self, node: ast.AST) -> str:
        """Infer the type of a value node."""
        if isinstance(node, (ast.Str, ast.Constant)) and isinstance(getattr(node, 'value', None), str):
            return 'str'
        elif isinstance(node, (ast.Num, ast.Constant)) and isinstance(getattr(node, 'value', None), (int, float)):
            return 'number'
        elif isinstance(node, ast.List):
            return 'list'
        elif isinstance(node, ast.Dict):
            return 'dict'
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return node.func.attr
        return 'unknown'
        
    def _find_last_line(self, node: ast.AST) -> int:
        """Find the last line of a node, including all its children."""
        last_line = node.lineno
        for child in ast.iter_child_nodes(node):
            if hasattr(child, 'lineno'):
                last_line = max(last_line, child.lineno)
                # Recursively check children
                child_last_line = self._find_last_line(child)
                last_line = max(last_line, child_last_line)
        return last_line


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


def analyze_python_ast(content: str) -> Dict[str, Any]:
    """Analyze a Python file's AST to extract code structure."""
    try:
        tree = ast.parse(content)
        
        # Extract imports
        import_visitor = ImportVisitor()
        import_visitor.visit(tree)
        
        # Extract code structure and function calls
        function_visitor = FunctionVisitor()
        function_visitor.visit(tree)
        
        return {
            'functions': function_visitor.functions,
            'function_calls': dict(function_visitor.function_calls),
            'function_lines': function_visitor.function_lines,
            'imports': import_visitor.imports,
            'detailed_dependencies': import_visitor.detailed_dependencies,
            'exports': function_visitor.exports,
            'classes': function_visitor.classes,
            'class_methods': function_visitor.class_methods,
            'variables': function_visitor.variables,
            'variable_dependencies': function_visitor.variable_dependencies
        }
    except SyntaxError as e:
        # Return partial information in case of syntax errors
        return {
            'error': str(e),
            'functions': [],
            'imports': [],
            'exports': [],
            'variables': []
        }