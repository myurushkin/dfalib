
def traverse_gkvadruples(string, ch, last_pos, last_group_id, groups):
    MinSBetweenGroups = 3
    new_pos = string.find(ch, last_pos + 1)
    if new_pos < 0:
        count = {}
        count[0] = count[1] = count[2] = count[3] = 0
        for gr in groups:
            count[gr[1]] += 1
        return min(count[0], count[1], count[2], count[3])

    result1 = traverse_gkvadruples(string, ch, new_pos, last_group_id, groups)


    current_group_id = last_group_id
    groups.append((new_pos, current_group_id))
    result2 = traverse_gkvadruples(string, ch, new_pos, current_group_id, groups)
    del groups[-1]
    if result2 > result1:
        result1 = result2

    if last_group_id < 3 and new_pos - groups[-1][0] > MinSBetweenGroups:
        current_group_id = last_group_id + 1
        groups.append((new_pos, current_group_id))
        result2 = traverse_gkvadruples(string, ch, new_pos, current_group_id, groups)
        del groups[-1]
        if result2 > result1:
            result1 = result2
    return result1

def max_gkvadruples_strength(string, ch):
    currentPos = string.find(ch)
    if currentPos < 0:
        return -1

    last_group_id = 0
    groups = [(currentPos, last_group_id)]
    return traverse_gkvadruples(string, ch, currentPos, last_group_id, groups)




with open ("E:/projects-git/dfalib/dfalibproj/grammars/minimum_string.txt") as f:
    for line in f.readlines():
        line = line.strip()
        res = max_gkvadruples_strength(line, "d")
        if line.count("d") >= 8:
            print(line)
        # if res != 1:
        #     res = max_gkvadruples_strength(line, "d")
        #     print(res)
        # a = 1


