import ctypes, os
import pathlib
import uuid
from dafna.internal import *
from graphviz import Source
from dafna.strength import *

class Context:
    def __init__(self):
        self.patterns = {}
        self.simple_patterns = {}

    def create_pattern(self, regular_expr, simple=False, name=None):
        if simple == False:
            regular_expr = self.private_update_regular_expr(regular_expr)

            result = Automata(self, regular_expr=regular_expr, name=name)
            self.patterns[result.name] = result
            return self.patterns[result.name]

        assert name != None
        self.simple_patterns[name] = regular_expr

    def private_update_regular_expr(self, reg_expr):
        for name, val in self.simple_patterns.items():
            val = "({})".format(val)
            reg_expr = reg_expr.replace(name, val)
        return reg_expr


class Automata:
    def __init__(self, ctx, regular_expr=None, name=None):
        self.obj = None
        self.ctx = ctx
        self.name = name
        if regular_expr != None:
            self.obj = dafna_create_automata(str.encode(regular_expr))

        if self.name == None:
            self.name = str(uuid.uuid4())

    def state_count(self):
        return dafna_automata_state_count(self.obj)

    def add(self, second):
        assert self.ctx == second.ctx
        tmp = self.obj
        self.obj = dafna_sum_automata(self.obj, second.obj)
        dafna_delete_automata(tmp)
        return self

    def intersect(self, second):
        assert self.ctx == second.ctx
        tmp = self.obj
        self.obj = dafna_intersect_automata(self.obj, second.obj)
        dafna_delete_automata(tmp)
        return self

    def minimize(self):
        tmp = self.obj
        self.obj = dafna_find_min_automata(self.obj)
        dafna_delete_automata(tmp)
        return self

    def min_strings(self):
        it = dafna_min_strings_iterator_create(self.obj)
        while dafna_min_strings_iterator_at_end(it) == False:
            next_value = dafna_min_strings_iterator_value(it)
            yield  next_value.decode('utf-8')
            dafna_min_strings_iterator_next(it)
        dafna_min_strings_iterator_delete(it)


def draw(autamata):
    text = dafna_generate_visualization_script(autamata.obj).decode("utf-8")
    src = Source(text)
    src.render(filename='test.gv', view=True)


def psum(*arg):
    result = None
    for item in arg:
        if type(item) is list:
            for it in tqdm.tqdm(item):
                result = (result.add(it) if result != None else it).minimize()
            continue
        assert type(item) is Automata
        result = (result.add(item) if result != None else it).minimize()
    return result


import tqdm
def pintersect(*arg):
    result = None
    for item in arg:
        if type(item) is list:
            for it in tqdm.tqdm(item):
                result = (result.intersect(it) if result != None else it).minimize()
            continue
        assert type(item) is Automata
        result = (result.intersect(item) if result != None else it).minimize()
    return result



def preporcess_pattern(pattern):
    pattern = pattern.replace(" ", "")
    return pattern

def createGQD(m, ctx):
    ggg = 'g'*m
    pattern = preporcess_pattern("X* {ggg} X+ {ggg} X+ {ggg} X+ {ggg} X*".format(ggg=ggg))
    return ctx.create_pattern(pattern)

def createHRP(counts, ctx):
    comp = {'a':'t', 't':'a', 'c':'g', 'g':'c'}

    values = [v * counts[v] for v in 'atgc']
    comp_values = [comp[v] * counts[v] for v in 'atgc']
    pattern = preporcess_pattern('X*' + 'X*'.join(values) + 'XXXX*' + 'X*'.join(reversed(comp_values)) + 'X*')
    return ctx.create_pattern(pattern)

if __name__ == "__main__":
    ctx = Context()
    X = ctx.create_pattern("a|c|g|t", simple=True, name="X")

    GQDs = [createGQD(m, ctx) for m in range(1, 5)]
    HRPs = [createHRP({'a': 3, 't': 1, 'g': 1, 'c': 1}, ctx)]

    result = pintersect(GQDs + HRPs)
    for ss in result.min_strings():
        print("{}: {}".format(ss, str(analyze_string(ss, [True]*4))))


