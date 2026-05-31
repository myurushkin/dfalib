def triplex_max_strength_for_patterns(val, patterns, dir):
    result = 0
    #value = val.lower()
    best_picture = []
    for strength in range(1, len(val)):
        for indent in range(len(val)):
            for linker_first_size in range(3, len(val)):
                for linker_second_size in range(3, len(val)):
                    if indent + 3 * strength + linker_first_size + linker_second_size > len(val):
                        break

                    B_0 = indent+strength+linker_first_size
                    C_0 = indent + strength + linker_first_size + strength + linker_second_size

                    A = val[indent: indent+strength]
                    B = val[B_0: B_0+strength]
                    C = val[C_0: C_0 + strength]

                    assert len(B) == strength


                    check = True
                    current_picture = []
                    for i in range(strength):
                        check = False
                        for p in patterns:
                            if A[i][1] != p[0]:
                                continue
                            if dir == 1:
                                if B[len(B) - i - 1][1] != p[1]:
                                    continue
                                if C[i][1] != p[2]:
                                    continue
                                current_picture.append((A[i][0], B[len(B) - i - 1][0]))
                                current_picture.append((C[i][0], B[len(B) - i - 1][0]))
                            else:
                                if B[len(B) - i - 1][1] != p[2]:
                                    continue
                                if C[i][1] != p[1]:
                                    continue
                                current_picture.append((A[i][0], C[i][0]))
                                current_picture.append((C[i][0], B[len(B) - i - 1][0]))

                            check = True
                            if i  == 8:
                                a = 1
                            break

                        if check == False:
                            break
                    if check == True:
                        result = max(result, strength)
                        best_picture = current_picture
                        break
                if result == strength:
                    break
            if result == strength:
                break
        if result != strength:
            break

    for i in range(len(val)-1):
        best_picture.append((i, i+1))
    return result, best_picture


def triplex_max_strength(val):
    patterns_first = [
        'tat', 'cat', 'cgc', 'ggc', 'agc', 'gta', 'tcg', 'ccg'
    ]

    # patterns_second = [
    #     'tta', 'cta', 'ccg', 'gcg', 'acg', 'gat', 'tgc', 'cgc'
    # ]

    val = list(enumerate(val.lower()))
    return max(*[triplex_max_strength_for_patterns(val, patterns_first, dir=1),
                  triplex_max_strength_for_patterns(val[::-1], patterns_first, dir=1),
                 triplex_max_strength_for_patterns(val, patterns_first, dir=-1),
                 triplex_max_strength_for_patterns(val[::-1], patterns_first, dir=-1)], key=lambda x: x[0])
