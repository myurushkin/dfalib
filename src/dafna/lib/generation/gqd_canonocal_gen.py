from dafna.shared import Context

def preporcess_pattern(pattern):
    pattern = pattern.replace(" ", "")
    return pattern


def create(strength: int, ctx: Context):
    ggg = 'g' * strength
    pattern = preporcess_pattern("X* {ggg} X+ {ggg} X+ {ggg} X+ {ggg} X*".format(ggg=ggg))
    return [ctx.create_pattern(pattern)]

    