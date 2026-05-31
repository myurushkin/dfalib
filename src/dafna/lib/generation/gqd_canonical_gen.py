from dafna.lib.generation import preprocess_pattern
from dafna.shared import Context


def create(strength: int, ctx: Context):
    """Build a canonical G-quadruplex pattern of the given strength.

    Requires the simple pattern ``X`` (= ``a|c|g|t``) to be registered in ``ctx``.
    """
    ggg = 'g' * strength
    pattern = preprocess_pattern("X* {ggg} X+ {ggg} X+ {ggg} X+ {ggg} X*".format(ggg=ggg))
    return [ctx.create_pattern(pattern)]
