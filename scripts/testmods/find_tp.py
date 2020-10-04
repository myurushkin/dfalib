import argparse
import itertools, tqdm
from modules import parsers

def create_table(kParam, resultStringSize):


    result = []
    excludedStrings = set()
    counter = 0
    for patternSize in tqdm.trange(1, kParam+1):
        assert resultStringSize % patternSize == 0
        for patternString in itertools.product(*(['acgt'] * patternSize)):
            fullString = "".join(patternString) * (resultStringSize // patternSize)

            good = True
            for s in excludedStrings:
                if fullString == s or fullString == s[::-1]:
                    good = False
            if good == False:
                continue

            excludedStrings.add(fullString)
            if patternSize == kParam:
                #print("{}: {}".format(str(counter), fullString))
                result.append(("".join(patternString), fullString))
                #counter += 1

    find_GQD = False
    find_IMT = False
    find_TRP = False
    find_HRP = False

    result_lines = []
    for pattern, fullString in result:
        seq_coefs = parsers.analyze_string(s, [find_GQD, find_IMT, find_TRP, find_HRP])
        #print(seq_coefs)
        result_lines.append((kParam, pattern, fullString) + seq_coefs)
    return result_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Finds TR (Tandem Repeats)')
    parser.add_argument('output_path', type=str)
    parser.add_argument('--k', type=int, default=6)
    parser.add_argument('--result-string-size', type=int, default=60)


    args = parser.parse_args()
    output_path = args.output_path
    resultStringSize = args.result_string_size

    with open(output_path, "w") as f:
        for k in range(1, args.k+1):
            result_lines = create_table(kParam=k, resultStringSize=resultStringSize)
            for line in result_lines:
                f.write("{},{},{}\n".format(line[2], line[0], line[1]))