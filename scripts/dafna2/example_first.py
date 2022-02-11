import dafna
import functools


class DFA:
    def minimize(self):
        pass

class Item:
    def __init__(self, reg_expr):
        self.reg_expr = reg_expr
        self.dfa = None

    def minimal_string_count(self):
        pass

    def __and__(self, other):
        return Item("")

    def __or__(self, other):
        return Item("")

class Context:
    def creatItem(self):
        pass


class Item:
    def __init__(self):
        pass


if __name__ == "__main__":
    with dafna.creatContext() as ctx:
        ctx.createItem("X", "a|g|c|t")
        TRPs = [ctx.createItem("X*  {0}  X{4}X*  t  X{3}X*  {0}  X*".format(left)) for left in ['a', 'g', 'c', 't']]
        TRP = functools.reduce(lambda a, b: a | b, TRPs)

        HRP = ctx.createItem("X*  a  X{4}X*  t  X{3}X*  b  X*")

        RandonString16 = ctx.createItem(" ".join(["X"]*16))

        result = TRP & RandonString16 & TRP
        result.minimal_string_count()

        result.setName("RESULT")
        result.printRegularExpression()


        # item = regular expression = DFA (different representations)
        #
        #





