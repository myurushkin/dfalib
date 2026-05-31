from dafna.lib.generation import preprocess_pattern
from dafna.shared import Context


def create(n: int, m: int, a: int, b: int, c: int, ctx: Context):
    """Build an i-motif pattern.

    Requires the simple pattern ``X`` (= ``a|c|g|t``) to be registered in ``ctx``.
    """
    result_pattern = "".join(["X*", "c" * n, "X" * a, 'c' * m, 'X' * b, 'c' * n, 'X' * c, 'c' * m, 'X*'])
    pattern = preprocess_pattern(result_pattern)
    return [ctx.create_pattern(pattern)]
