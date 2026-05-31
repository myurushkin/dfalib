from dafna.lib.generation import preprocess_pattern
from dafna.shared import Context


def create(strength: int, ctx: Context):
    """Build a G-quadruplex tandem-repeat pattern of the given strength.

    Requires the simple patterns ``X`` (= ``a|c|g|t``) and ``Y`` (= ``a|c|t``)
    to be registered in ``ctx``.
    """
    result_pattern = "".join(["X*"] + ["gY"] * (4 * strength - 1) + ["gX*"])
    pattern = preprocess_pattern(result_pattern)
    return [ctx.create_pattern(pattern)]
