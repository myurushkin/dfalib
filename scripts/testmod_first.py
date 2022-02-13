from dafna import *

if __name__ == "__main__":
    ctx = Context()
    X = ctx.create_pattern("a|c|g|t", simple=True, name="X")
    GQDs = [createGQD(m, ctx) for m in range(2, 21)]
    print(list(psum(GQDs).min_strings()))
