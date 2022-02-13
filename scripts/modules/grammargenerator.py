import itertools
from modules import helpers

class GrammarGenerator:
    def __init__(self):
        pass

    def create(self, find_GQD, find_IMT, find_TRP, find_HRP, min_size, hrps=[]):
        result = ""

        names = []
        if find_GQD == True:
            i1 = ("GQD", self.generate_gquadruplex(20))
            result += "{} = {}\n".format(i1[0], i1[1])
            result += "\n"
            names.append("({})".format(i1[0]))

        if find_IMT == True:
            i2 = ("IMT", self.gerate_imotiv(20, 20))
            result += "{} = {}\n".format(i2[0], i2[1])
            result += "\n"
            names.append("({})".format(i2[0]))

        if find_HRP == True:
            items3 = self.generate_hairpins_from_set(hrps)
            items3 = [("HRP_" + str(i + 1), items3[i]) for i in range(len(items3))]
            for item in items3:
                result += "{} = {}\n".format(item[0], item[1])
            result += "\n"
            names.append("({})".format(" | ".join(x[0] for x in items3)))

        if find_TRP > 0:
            trps_list = helpers.get_triplex_set(find_TRP)
            items = []
            for index, x in enumerate(trps_list):
                items.append(("TRP_" + str(index + 1), "X* {} X{{3}}X* {} X{{3}}X* {} X*".format(*x)))
            for item in items:
                result += "{} = {}\n".format(item[0], item[1])
            result += "\n"
            names.append("({})".format(" | ".join(x[0] for x in items)))

        #if find_TRP == True:
            # items4 = self.generate_triplexes()
            # items4 = [("TRP_" + str(i+1), items4[i]) for i in range(len(items4))]
            # for item in items4:
            #     result += "{} = {}\n".format(item[0], item[1])
            # result += "\n"
            # names.append("({})".format(" | ".join(x[0] for x in items4)))

        if min_size > 0:
            names.append("LENGTH")
            result += "LENGTH = {}\n".format("X" * min_size)
        result += "X = (a|c|g|t)\n"
        result += "result = {}".format("\\\n\t".join(names))
        return result

    def generate_gquadruplex(self, count = 1):
        return "X*  g{m}  X{3}X*  g{m}  X{3}X*  g{m}  X{3}X*  g{m}   X*" + ",   m=[1:{}]".format(count)

    def gerate_imotiv(self, count1, count2):
        return "X*  c{a}  X{3}X*  c{b}  X{3}X*  c{a}  X{3}X*  c{b}   X*" + ",   a=[1:{}], b=[1:{}]".format(str(count1), str(count2))


    def generate_hairpins_from_set(self, hrps):
        result = []

        opposite_chars = {}
        opposite_chars['a'] = 't'
        opposite_chars['t'] = 'a'
        opposite_chars['c'] = 'g'
        opposite_chars['g'] = 'c'

        for left_part in hrps:
            right_part = "".join(opposite_chars[x] for x in left_part)
            result.append("X*  {} X{{3}}X* {} X*".format(left_part, right_part))
        return result


    def generate_hairpins(self, a_range = (1,1), t_range = (1,1), c_range = (1,1), g_range = (1,1)):
        result = []

        opposite_chars = {}
        opposite_chars['a'] = 't'
        opposite_chars['t'] = 'a'
        opposite_chars['c'] = 'g'
        opposite_chars['g'] = 'c'

        perms = itertools.permutations(['a', 't', 'c', 'g'])
        index = 1
        for item in perms:
            s1 = ""
            s2 = ""
            for ch in item:
                s1 = s1 + "{}{{{}}}".format(ch, ch)
                s2 = "{}{{{}}}".format(opposite_chars[ch], ch) + s2
            result.append("X*  {} X{{4}}X* {} X*".format(s1, s2) +
                          ", a=[{}:{}], t=[{}:{}], c=[{}:{}], g=[{}:{}]".format(a_range[0], a_range[1],
                                                                                t_range[0], t_range[1],
                                                                                c_range[0], c_range[1],
                                                                                g_range[0], g_range[1]))
            index += 1
        return result

    # this set contains error (we decided to use two kinds of triplex sets)
    # def generate_triplexes(self):
    #     # A.A-T
    #     # A.T-A
    #     # A.G-C
    #     # A.C-G
    #     # T.A-T
    #     # T.T-A
    #     # T.G-C
    #     # T.C-G
    #     # G.A-T
    #     # G.T-A
    #     # G.G-C
    #     # G.C-G
    #     # C.A-T
    #     # C.T-A
    #     # C.G-C
    #     # C.C-G
    #
    #     patterns = ["aat", "ata", "agc", "acg", "tat", "tta", "tgc", "tcg",
    #                 "gat", "gta", "ggc", "gcg", "cat", "cta", "cgc", "ccg"]
    #
    #     patterns_all = []
    #     for item in patterns:
    #         patterns_all.append(item[::-1])
    #         patterns_all.extend(patterns)
    #     patterns4_all = list(set(patterns_all))
    #
    #     result = []
    #     index = 1
    #     for item in patterns4_all:
    #         ch1 = item[0]
    #         ch2 = item[1]
    #         ch3 = item[2]
    #         result.append("X*  {}  X{{3}}X*  {}  X{{3}}X*  {}  X*".format(ch1, ch2, ch3))
    #         index += 1
    #     return result
