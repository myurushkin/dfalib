import dafna


def createGQD(m, ctx):
    pattern = "X* g{m} X+ g{m} X+ g{m} X+ g{m} X*"
    return ctx.create_pattern(pattern, "GQD[{}]".format(m))

def createHRP(a, t, g, c, ctx):
    pattern = "X*  a{a} X* t{t} X* c{c} X* g{g} X{3}X* c{g} X* g{c} X* a{t} X* t{a} X*"
    return ctx.create_pattern(pattern, "HRP[{}]".format(m))

def createTRP(a, g, m, ctx):
    pattern = "X* (g{g} a{a}){m} X{3}X* (c{g} t{a}){m} X{3}X*"
    return ctx.create_pattern(pattern, "TRP[{}]".format(m))


if __name__ == "__main__":
    ctx = dafna.Context()
    #X = ctx.createAutomata("a|c|g|t", "X")
    GQDs = [createGQD(m, ctx) for m in range(2, 20)]

    GQDs[0].state_count()
    GQDs[0].minimize()
    GQDs[0].state_count()
    GQDs[1].plot()

    result = dafna.intersect(dafna.sum(GQDs), dafna.sum(TRPs), dafna.sum(HRps))