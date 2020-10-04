import argparse
import itertools
from modules import parsers

def create_table(kParam, resultStringSize):


    result = []
    excludedStrings = set()
    counter = 0
    for patternSize in range(1, kParam+1):
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
    find_TRP = True
    find_HRP = True

    result_lines = []
    for pattern, fullString in result:
        seq_coefs = parsers.analyze_string(s, [find_GQD, find_IMT, find_TRP, find_HRP])
        #print(seq_coefs)
        result_lines.append((kParam, pattern, fullString) + seq_coefs)
    return result_lines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Finds TR (Tandem Repeats)')
    parser.add_argument('output_path', type=str)
    # parser.add_argument('--find-GQD', type=int, default=0)
    # parser.add_argument('--find-IMT', type=int, default=0)
    # parser.add_argument('--find-HRP', type=int, default=0)
    # parser.add_argument('--find-TRP', type=int, default=0)
    parser.add_argument('--k', type=int, default=1)

    args = parser.parse_args()
    output_path = args.output_path

    with open(output_path, "w") as f:
        f.write(",".join(["{}"]*7).format("k", "pattern", "string", "GQD", "IMT", "TRP", "HRP") + "\n")
        for k in range(1, args.k+1):
            result_lines = create_table(kParam=k, resultStringSize=12)
            for line in result_lines:
                f.write(",".join(["{}"]*7).format(*line) + "\n")