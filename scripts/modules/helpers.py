
def get_triplex_set(kind=1):
    assert kind == 1 or kind == 2
    if kind == 1:
        return ['tat', 'tta', 'ata', 'tcg', 'cta', 'agc', 'gcb', 'cgc', 'gat']
    return ['tac', 'gta', 'tag', 'cta', 'cgg', 'cat', 'cga', 'gcc', 'gct']