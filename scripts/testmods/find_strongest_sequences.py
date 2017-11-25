# -*- coding: utf-8 -*-

import time, shutil
import itertools
from modules import grammargenerator
from modules import parsers
import subprocess
import json
import tempfile
import argparse
import tqdm


def is_less_equal(v1, v2):
    assert len(v1) == len(v2)
    for i in range(len(v1)):
        if v1[i] > v2[i]:
            return False
    return True

"""
В цикле генерим разные грамматики, скармливаем оптимизатору и находим
самые сильные соединения
"""
def processLines(lines, best_sequences, verbose=False):
    if len(lines) == 0:
        return best_sequences

    if len(best_sequences) > 0:
        if len(best_sequences[0]) < len(lines[0]):
            return best_sequences
        if len(best_sequences[0]) > len(lines[0]):
            best_sequences = []

    space = lines if verbose==False else tqdm.tqdm(lines)
    for seq in space:
        seq_coefs = parsers.analyze_string(seq)
        good = True
        for _, other_coefs in best_sequences:
            if is_less_equal(seq_coefs, other_coefs):
                good = False
                break
        if good == True:
            best_sequences.append((seq, seq_coefs))
            best_sequences = list(filter(
                lambda x: x[0] == seq or not is_less_equal(x[1], seq_coefs), best_sequences))
    return best_sequences

def calculate_min_lines(next_grammar_path, config_path, tmp_dirpath, executor_result_path, executor):
    with open(next_grammar_path, "w") as f:
        f.write(grammar)
    with open(config_path, "w") as f:
        json.dump({"grammar-filepath": next_grammar_path,
                   "tmp-dirpath": tmp_dirpath,
                   "output-filepath": executor_result_path}, f)

    cmd_values = [executor, config_path]
    p = subprocess.Popen(cmd_values)
    (output, err) = p.communicate()
    p_status = p.wait()

    with open(executor_result_path) as f:
        lines = [x.strip() for x in f.readlines()]
    return lines


if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Finds strongest sequences and outputs to output file')
        parser.add_argument('executor_path', type=str)
        parser.add_argument('output_path', type=str)
        parser.add_argument('--find-GQD', type=int, default=0)
        parser.add_argument('--find-IMT', type=int, default=0)
        parser.add_argument('--find-HRP', type=int, default=0)
        parser.add_argument('--find-TRP', type=int, default=0)

        args = parser.parse_args()
        executor = args.executor_path
        output_path = args.output_path
        find_GQD = bool(args.find_GQD)
        find_IMT = bool(args.find_IMT)
        find_HRP = bool(args.find_HRP)
        find_TRP = bool(args.find_TRP)

        if find_GQD == False and find_IMT == False and find_HRP == False and find_TRP == False:
            raise ValueError("Invalid configuration")

        tmp_dirpath =  tempfile.mkdtemp()
        next_grammar_path = "{}/next_grammar.txt".format(tmp_dirpath)
        config_path = "{}/config.json".format(tmp_dirpath)
        executor_result_path = "{}/next_result.txt".format(tmp_dirpath)

        best_sequences = []
        hrps = list(itertools.product("acgt", "acgt", "acgt", "acgt", "acgt"))
        hrps = [''.join(x) for x in hrps]

        gen = grammargenerator.GrammarGenerator()
        if find_HRP == False:
            grammar = gen.create(find_GQD, find_IMT, find_TRP, find_HRP)
            lines = calculate_min_lines(next_grammar_path, config_path, tmp_dirpath, executor_result_path, executor)
            best_sequences = processLines(lines, best_sequences, verbose=True)
        else:
            batch = []
            t1=time.time()
            progress = 0
            for hrp in hrps:
                progress += 1
                batch.append(hrp)
                if len(batch) < 5:
                    continue

                grammar = gen.create(find_GQD, find_IMT, find_TRP, find_HRP, hrps=batch)
                batch = []

                lines = calculate_min_lines(next_grammar_path, config_path, tmp_dirpath, executor_result_path, executor)
                t2 = time.time()
                dt = t2 - t1
                best_sequences = processLines(lines, best_sequences)
                print("progress: {}, time till finish: {}".format(
                    int(progress * 100 / len(hrps)), dt / progress * (len(hrps) - progress)))

        with open(output_path, "w") as f:
            for line in best_sequences:
                f.write(best_sequences)
                f.write("\n")

        shutil.rmtree(tmp_dirpath)
    except ValueError as e:
        print(e.message)