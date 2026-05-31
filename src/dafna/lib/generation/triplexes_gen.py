from dafna.lib.generation import preprocess_pattern
from dafna.shared import Context


def create(strength: int, ctx: Context):
    """Build a canonical triplex pattern of the given strength.

    A triplex of strength ``s`` aligns three tracts ``A``, ``B``, ``C`` of length
    ``s`` joined by two linkers of at least three nucleotides. The canonical form
    used here realises the ``tat`` triad (``A = t{s}``, ``B = a{s}``, ``C = t{s}``),
    which the strength function scores at exactly ``s`` regardless of the ``X``
    fillers.

    Requires the simple pattern ``X`` (= ``a|c|g|t``) to be registered in ``ctx``.
    """
    a_tract = "t" * strength
    b_tract = "a" * strength
    c_tract = "t" * strength
    # ``XXXX*`` linkers are loops of length >= 3.
    pattern = preprocess_pattern(
        "X* {a} XXXX* {b} XXXX* {c} X*".format(a=a_tract, b=b_tract, c=c_tract)
    )
    return [ctx.create_pattern(pattern)]
