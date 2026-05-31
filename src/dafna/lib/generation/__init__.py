def preprocess_pattern(pattern: str) -> str:
    """Remove whitespace from a generator pattern before compiling it.

    Generators write patterns with spaces for readability (``"X* g X+ g X*"``);
    the automata compiler expects them stripped.
    """
    return pattern.replace(" ", "")
