from dafna import *
import time, tqdm
from itertools import product



def preporcess_pattern(pattern):
    pattern = pattern.replace(" ", "")
    return pattern


def createGQD(m, ctx):
    ggg = 'g' * m
    pattern = preporcess_pattern("X* {ggg} X+ {ggg} X+ {ggg} X+ {ggg} X*".format(ggg=ggg))
    return ctx.create_pattern(pattern)


def createIMT(x, y, ctx):
    cx = 'c' * x
    cy = 'c' * y
    pattern = preporcess_pattern("X* {cx} X+ {cy} XX+ {cx} X+ {cy} X*".format(cx=cx, cy=cy))
    return ctx.create_pattern(pattern)


def createTRPs(n, ctx, tt=0):
    assert n <= 10
    main_strings = list(product('ga', repeat=n))
    main_strings = list(map(lambda x: "".join(x), main_strings))

    result = []

    comp = {'g': 'c', 'a': 't'}
    comp_strings = list(map(lambda x: "".join(comp[c] for c in x), main_strings))

    if tt == 0 or tt == 1:
        for main_string, comp_string in zip(main_strings, comp_strings):
            values = [main_string, "".join(list(reversed(comp_string))), comp_string]
            result.append(values)

    if tt == 0 or tt == 2:
        for main_string, comp_string in zip(main_strings, comp_strings):
            values = [comp_string, "".join(list(reversed(main_string))), comp_string]
            result.append(values)

    comp2 = {'g': 'ga', 'a': 'ta'}
    if tt == 0 or tt == 3:
        for main_string, comp_string in zip(main_strings, comp_strings):
            tmp = [comp2[c] for c in main_string]
            tmp2 = list(map(lambda x: "".join(x), list(product(*tmp))))

            for comp2_string in tmp2:
                comp2_string = comp2_string
                values = ([comp_string, "".join(list(reversed(main_string))), comp2_string])
                result.append(values)

    if tt == 0 or tt == 4:
        for main_string, comp_string in zip(main_strings, comp_strings):
            tmp = [comp2[c] for c in main_string]
            tmp2 = list(map(lambda x: "".join(x), list(product(*tmp))))

            for comp2_string in tmp2:
                comp2_string = comp2_string
                values = ([main_string, "".join(list(reversed(comp_string))), comp2_string])
                result.append(values)

    patterns = list(map(lambda values: 'X*' + "XXX+".join(values) + 'X*', result))
    return [ctx.create_pattern(p) for p in patterns]


def mytest(size):
    from itertools import islice

    def chunk(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    ctx = Context()
    X = ctx.create_pattern("a|c|g|t", simple=True, name="X")
    GQDs = [createGQD(m, ctx) for m in range(2, 21)]

    TRPs = createTRPs(2, ctx)
    IMTs = []
    for x in range(1, 21):
        for y in range(max(1, x - 1), x + 2):
            IMTs.append(createIMT(x, y, ctx))

    string_size_pattern = ctx.create_pattern('X' * size)
    chunk_size = 2

    task_count = len(list(chunk(GQDs, chunk_size))) * len(list(chunk(TRPs, chunk_size))) * len(list(chunk(IMTs, chunk_size)))
    with tqdm.tqdm(total=task_count) as pbar:
        for GQD_range in chunk(GQDs, chunk_size):
            for TRP_range in chunk(TRPs, chunk_size):
                for IMT_range in chunk(IMTs, chunk_size):
                    pintersect([psum(GQD_range), psum(TRP_range), psum(IMT_range), string_size_pattern])
                    pbar.update(1)


if __name__ == "__main__":
    for n in [50, 55]:
        start = time.time()
        mytest(n)
        end = time.time()
        print("{n}, {t}".format(n=n, t=end-start))

