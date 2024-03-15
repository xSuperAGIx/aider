from pathlib import Path
from typing import Dict, List, Union

# Use absolute import for dump
from dump import dump  # type: ignore


def safe_abs_path(path: Union[str, Path]) -> str:
    """
    Returns an absolute path, which safely returns a full (not 8.3) windows path.
    """
    try:
        path = Path(path).resolve()
    except Exception as e:
        raise ValueError(f"Invalid path: {path}. Error: {e}")
    return str(path)


def show_messages(
    messages: List[Dict[str, Union[str, Dict[str, str]]]],
    title: str = None,
    functions: dict = None,
) -> None:
    """
    Displays the given messages and function calls.
    """
    if title:
        print(title.upper() + ("*" * 50))

    for msg in messages:
        role = msg["role"].upper()
        content = msg.get("content")
        if content:
            print(f"{role}:")
            print("\n".join(content.splitlines()))
            print()

        function_call = msg.get("function_call")
        if function_call:
            print(f"{role} function call: {function_call}\n")

    if functions:
        dump(functions, indent=4)
