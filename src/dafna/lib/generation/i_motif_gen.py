from dafna.shared import Context

def preporcess_pattern(pattern):
    pattern = pattern.replace(" ", "")
    return pattern


def create(n: int, m: int, a: int, b: int, c: int, ctx: Context):
    result_pattern = "".join(["X*", "c"*n, "X"*a, 'c'*m, 'X'*b, 'c'*n, 'X'*c, 'c'*m, 'X*'])
    pattern = preporcess_pattern(result_pattern)
    return [ctx.create_pattern(pattern)]