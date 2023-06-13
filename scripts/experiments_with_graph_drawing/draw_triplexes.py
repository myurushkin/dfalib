from  dafna.lib.visualization.graph import show_graph, create_graph
from dafna.lib.strength.strength import triplex_max_strength

if __name__ == "__main__":
    example = 'gatccggatccggatccggatccggatccggatccggatccggatccggatccggatccg'
    #example = 'TCTCTCtttCTCTCTcccAGAGAG'

    result, picture = triplex_max_strength(example)
    print(result)

    G = create_graph(example, picture)
    
    #G = create_graph("TCTCTCtttCTCTCTcccAGAGAG", [(0, 18), (0, 1), (18, 14), (18, 17), (18, 19), (14, 13), (14, 15), (1, 19), (1, 2), (19, 13), (19, 20), (13, 12), (2, 20), (2, 3), (20, 12), (20, 21), (12, 11), (3, 21), (3, 4), (21, 11), (21, 22), (11, 10), (4, 22), (4, 5), (22, 10), (22, 23), (10, 9), (5, 23), (5, 6), (23, 9), (9, 8), (6, 7), (7, 8), (15, 16), (16, 17)])
    
    #G = create_graph("acgt", [(2,0), (3, 1), (0, 1), (1, 2), (2, 3), (0, 3)])
    show_graph(G)   