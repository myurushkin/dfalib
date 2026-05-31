from dafna.lib.generation import preprocess_pattern
from dafna.shared import Context


def create(strength: int, ctx: Context):
    """Build a canonical hairpin pattern of the given strength.

    A hairpin of strength ``s`` is a stem of ``s`` complementary base pairs around
    a loop of at least three nucleotides. The canonical form used here is an
    ``a``-stem closed by a ``t``-stem (``a`` pairs with ``t``), which the strength
    function scores at exactly ``s`` regardless of the ``X`` fillers.

    Requires the simple pattern ``X`` (= ``a|c|g|t``) to be registered in ``ctx``.
    """
    a_stem = "a" * strength
    t_stem = "t" * strength
    # ``XXXX*`` is a loop of length >= 3 (the minimum biological hairpin loop).
    pattern = preprocess_pattern("X* {a} XXXX* {t} X*".format(a=a_stem, t=t_stem))
    return [ctx.create_pattern(pattern)]
