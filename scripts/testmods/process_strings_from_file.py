import argparse, tqdm
import itertools, re
from modules import parsers

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check strength of input list')
    parser.add_argument('input_path', type=str)
    parser.add_argument('--output_path', type=str, default=None)
    parser.add_argument('--find-GQD', type=int, default=0)
    parser.add_argument('--find-IMT', type=int, default=1)
    parser.add_argument('--find-HRP', type=int, default=0)
    parser.add_argument('--find-TRP', type=int, default=0)

    args = parser.parse_args()

    input_path = args.input_path
    output_path = args.output_path
    if output_path == None:
        output_path = input_path + ".processed.csv"

    find_GQD = bool(args.find_GQD)
    find_IMT = bool(args.find_IMT)
    find_HRP = bool(args.find_HRP)
    find_TRP = bool(args.find_TRP)


    with open(output_path, "w") as output:
        output.write(",".join(["{}"] * 5).format("string", "GQD", "IMT", "TRP", "HRP") + "\n")
        with open(input_path, "r") as input:
            lines = input.readlines()
            lines = list(map(lambda x: re.sub('[\n\r]', '', x), lines))
        for line in tqdm.tqdm(lines):
            sequence = line.split(",")[0]
            seq_coefs = parsers.analyze_string(sequence, [find_GQD, find_IMT, find_TRP, find_HRP])
            output.write(",".join(["{}"]*5).format(*((sequence,) + seq_coefs))+ "\n")
