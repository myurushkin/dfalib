from modules import parsers



with open ("E:/projects-git/dfalib/dfalibproj/grammars/minimum_string.txt") as f:
    for line in f.readlines():
        line = line.strip()
        res = parsers.max_gkvadruples_strength(line, "d")
        if line.count("d") >= 8:
            print(line)


