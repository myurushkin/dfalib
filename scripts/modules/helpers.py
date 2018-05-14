
def get_triplex_set(kind=1):
    assert kind == 1 or kind == 2
    if kind == 1:
        return ['tac', 'taa', 'tag', 'cgg', 'atg', 'cgt', 'cga', 'cgc', 'tat']
    return ['cat', 'agc', 'cgc', 'gat', 'ggc', 'tgc', 'tat', 'gta', 'aat']