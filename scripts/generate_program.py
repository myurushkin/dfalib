__author__ = 'misha'

import itertools


result = "big_grammar.txt"


def createI1():
    return ("I1", "X*  d{m}  X{3}X*  d{m}  X{3}X*  d{m}  X{3}X*  d{m}   X*,   m=[1:20]")

def createI2():
    return ("I2", "X*  c{a}  X{3}X*  c{a}  X{6}X*  c{a}  X{3}X*  c{a}   X*,   a=[1:20]")


items = []
items.append(createI1())
items.append(createI2())

items3 = []
items4 = []

opposite_chars = {}
opposite_chars['a'] = 'b'
opposite_chars['b'] = 'a'
opposite_chars['c'] = 'd'
opposite_chars['d'] = 'c'

perms = itertools.permutations(['a', 'b', 'c', 'd'])
index = 1
for item in perms:
    s1 = ""
    s2 = ""
    for ch in item:
        s1 = s1 + "{}{{{}}}".format(ch, ch)
        s2 = "{}{{{}}}".format(opposite_chars[ch], ch) + s2
    items3.append(("I3_{}".format(index), "X*  {} X{{4}}X* {} X*, a=[1:1], b=[1:1], c=[1:1], d=[1:1]".format(s1, s2)))
    index += 1

# index = 1
# for ch1 in ['a', 'b', 'c', 'd']:
#     for ch2 in ['a', 'b', 'c', 'd']:
#         for ch3 in ['a', 'b', 'c', 'd']:
#             items4.append(("I4_{}".format(index), "X*  {}  X{{4}}X*  {}  X{{3}}X*  {}  X*".format(ch1, ch2, ch3)))
#             index += 1



# A.A-T
# A.T-A
# A.G-C
# A.C-G
# T.A-T
# T.T-A
# T.G-C
# T.C-G
# G.A-T
# G.T-A
# G.G-C
# G.C-G
# C.A-T
# C.T-A
# C.G-C
# C.C-G

# A - a
# T - b
# C - c
# G - d

patterns4 = [ "AAT", "ATA", "AGC", "ACG",
              "TAT", "TTA", "TGC", "TCG",
              "GAT", "GTA", "GGC", "GCG",
              "CAT", "CTA", "CGC", "CCG"]

patterns4_all = []
for item in patterns4:
    patterns4_all.append(item[::-1])
patterns4_all.extend(patterns4)
patterns4_all = list(set(patterns4_all))


index = 1
for item in patterns4_all:
    item = item.replace("A", "a")\
        .replace("T", "b")\
        .replace("C", "c")\
        .replace("G", "d")
    ch1 = item[0]
    ch2 = item[1]
    ch3 = item[2]
    items4.append(("I4_{}".format(index), "X*  {}  X{{4}}X*  {}  X{{3}}X*  {}  X*".format(ch1, ch2, ch3)))
    index += 1

with open(result, "w") as f:
    i1 = createI1()
    f.write("{} = {}\n".format(i1[0], i1[1]))

    i2 = createI2()
    f.write("{} = {}\n".format(i2[0], i2[1]))
    f.write("\n")
    for item in items3:
        f.write("{} = {}\n".format(item[0], item[1]))
    f.write("\n")
    for item in items4:
        f.write("{} = {}\n".format(item[0], item[1]))

    f.write("X = (a|b|c|d)\n")

    f.write("result = {} {}  \\\n\t ({}) \\\n\t ({}) \n".format(i1[0], i2[0], " | ".join([x[0] for x in items3])
                                                                , " | ".join([x[0] for x in items4])))






