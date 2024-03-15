import json
import traceback

def cvt(s):
    """Convert the input to a string, using json.dumps if it's a dictionary or a list."""
    if isinstance(s, str):
        return s
    return json.dumps(s, indent=4, default=str)

def dump(*vals: object) -> None:
    """Print the variable name and its value(s).

    If any of the values contains a newline, print the variable name and the values on separate lines.
    """
    # Get the variable name from the stack trace
    stack = traceback.extract_stack()
    vars = stack[-2][3]

    # Remove the dump() call from the variable name
    vars = " ".join(vars.split(" ")[1:])

    vals = [cvt(v) for v in vals]
    has_newline = sum(1 for v in vals if "\n" in v)

    if vals:
        if has_newline:
            print("%s: " % vars)
            print("\n".join(vals))
        else:
            print("%s: " % vars + ", ".join(vals))
    else:
        print(vars + ":")
