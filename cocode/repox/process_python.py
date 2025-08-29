import ast
from typing import List

from pipelex import log
from pipelex.tools.exceptions import RootException
from pipelex.types import StrEnum

from cocode.utils import format_with_ruff


class PythonProcessingError(RootException):
    pass


class PythonProcessingRule(StrEnum):
    INTERFACE = "interface"
    INTEGRAL = "integral"
    IMPORTS = "imports"


def python_integral(python_code: str) -> str:
    """
    Return it all
    """
    return python_code


def python_interface(python_code: str) -> str:
    """
    Format the python code only retaining interface code and docstrings.
    Also keeps Enum/StrEnum values and ignores private methods.
    """
    try:
        tree = ast.parse(python_code)
        output_lines: List[str] = []
        _format_interface(node=tree, lines=output_lines)
        interface_code = "\n".join(output_lines)
        reformatted_code = format_with_ruff(interface_code)
        return reformatted_code
    except SyntaxError:
        return "# Invalid Python code"


def python_imports_list(python_code: str) -> str:
    """
    Extract all non-private entities defined at the root level of the Python module.
    Returns a comma-separated list of public entity names that can be imported.
    """
    try:
        tree = ast.parse(python_code)
        entities: List[str] = []

        # Only look at direct children of the Module node
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                entities.append(node.name)
            elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                entities.append(node.name)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_") and len(target.id) > 1:
                        entities.append(target.id)

        return ", ".join(sorted(set(entities)))
    except SyntaxError:
        return "# Invalid Python code"


def _get_docstring(node: ast.AST) -> str | None:
    """Extract docstring from an AST node if it exists."""
    if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef)):
        return None

    if not node.body:
        return None

    first = node.body[0]
    if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
        return first.value.value
    return None


def _is_enum_class(node: ast.ClassDef) -> bool:
    """Check if a class is an Enum or StrEnum."""
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in ("Enum", "StrEnum"):
            return True
        # Handle cases where Enum is imported from enum module
        if isinstance(base, ast.Attribute) and base.attr in ("Enum", "StrEnum"):
            return True
    return False


def _format_interface(node: ast.AST, lines: List[str]) -> None:
    """Format AST node retaining only interface elements."""
    if isinstance(node, ast.Module):
        docstring = _get_docstring(node)
        if docstring:
            lines.append('"""')
            lines.extend(docstring.splitlines())
            lines.append('"""')
            lines.append("")

        for item in node.body:
            if isinstance(item, (ast.ClassDef, ast.FunctionDef)) and not item.name.startswith("_"):
                _format_interface(item, lines)

    elif isinstance(node, ast.ClassDef):
        is_enum = _is_enum_class(node)
        lines.append(f"class {node.name}:")
        docstring = _get_docstring(node)
        if docstring:
            lines.append('    """')
            lines.extend(f"    {line}" for line in docstring.splitlines())
            lines.append('    """')

        if is_enum:
            # For Enum classes, include all assignments
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for target in item.targets:
                        if isinstance(target, ast.Name) and not target.id.startswith("_"):
                            lines.append(f"    {ast.unparse(item)}")
        else:
            # For regular classes, only include non-private methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    _format_interface(item, lines)
            if not any(isinstance(item, ast.FunctionDef) and not item.name.startswith("_") for item in node.body):
                lines.append("    ...")
        lines.append("")

    elif isinstance(node, ast.FunctionDef):
        args = ast.unparse(node.args)
        lines.append(f"    def {node.name}({args}):")
        docstring = _get_docstring(node)
        if docstring:
            lines.append('        """')
            lines.extend(f"        {line}" for line in docstring.splitlines())
            lines.append('        """')
        lines.append("        ...")
        lines.append("")

    else:
        log.debug(f"This node is not processed: {node}")
