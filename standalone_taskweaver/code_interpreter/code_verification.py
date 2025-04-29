import ast
from typing import List, Optional


def code_snippet_verification(
    code: str,
    verification_on: bool = True,
    allowed_modules: Optional[List[str]] = None,
    blocked_functions: Optional[List[str]] = None,
) -> Optional[List[str]]:
    """
    Verify the code snippet.
    :param code: The code snippet.
    :param verification_on: Whether to verify the code.
    :param allowed_modules: The allowed modules.
    :param blocked_functions: The blocked functions.
    :return: The verification errors.
    """
    if not verification_on:
        return None

    errors = []

    # parse the code
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Syntax error: {e}")
        return errors

    # check imports
    if allowed_modules is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name not in allowed_modules:
                        errors.append(f"Import of module '{name.name}' is not allowed")
            elif isinstance(node, ast.ImportFrom):
                if node.module not in allowed_modules:
                    errors.append(f"Import from module '{node.module}' is not allowed")

    # check blocked functions
    if blocked_functions is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in blocked_functions:
                        errors.append(f"Function '{node.func.id}' is blocked")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in blocked_functions:
                        errors.append(f"Function '{node.func.attr}' is blocked")

    return errors


def format_code_correction_message() -> str:
    """
    Format the code correction message.
    :return: The formatted message.
    """
    return (
        "The code verification has detected some issues. "
        "Please fix the issues and try again."
    )

