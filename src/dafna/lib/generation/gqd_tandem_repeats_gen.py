from dafna.shared import Context

def preporcess_pattern(pattern):
    pattern = pattern.replace(" ", "")
    return pattern


def create(strength: int, ctx: Context):
    result_pattern = "".join(["X*"] + ["gY"] * (4 * strength-1) + ["gX*"])
    pattern = preporcess_pattern(result_pattern)
    return [ctx.create_pattern(pattern)]