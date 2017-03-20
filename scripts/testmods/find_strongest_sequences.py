# -*- coding: utf-8 -*-

import time
import itertools
from modules import grammargenerator
from modules import parsers
import subprocess
import json


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

tmp_dirpath = r"E:\projects-git\dfalib\tmp"
next_grammar_path = "{}/next_grammar.txt".format(tmp_dirpath)
config_path = "{}/config.json".format(tmp_dirpath)
executor = r"E:\build\dfalib\sources\testmod\Release\testmod.exe"
executor_result_path = "{}/next_result.txt".format(tmp_dirpath)

# test
# best_sequences = []
# with open(executor_result_path) as f:
#     lines = [x.strip() for x in f.readlines()]
#     for seq in lines:
#         seq_coefs = parsers.analyze_string(seq)
#
#         good = True
#         for _, other_coefs in best_sequences:
#             if is_less_equal(seq_coefs, other_coefs):
#                 good = False
#                 break
#         if good == True:
#             best_sequences.append((seq, seq_coefs))
#             best_sequences = list(filter(
#                 lambda x: x[0] == seq or not is_less_equal(x[1], seq_coefs), best_sequences))
#print(best_sequences)


best_sequences = []
hrps = list(itertools.product("acgt", "acgt", "acgt", "acgt", "acgt"))
hrps = [''.join(x) for x in hrps]

gen = grammargenerator.GrammarGenerator()

batch = []

t1=time.time()
progress = 0
for hrp in hrps:
    progress += 1
    batch.append(hrp)
    if len(batch) < 5:
        continue

    grammar = gen.create(hrps = batch)
    batch = []
    with open(next_grammar_path, "w") as f:
        f.write(grammar)


    with open(config_path, "w") as f:
        json.dump({"grammar-filepath": next_grammar_path,
                   "tmp-dirpath" : tmp_dirpath,
                   "output-filepath": executor_result_path}, f)

    cmd_values = [executor, config_path]
    p = subprocess.Popen(cmd_values)

    (output, err) = p.communicate()
    p_status = p.wait()

    t2 = time.time()


    print("progress: {}, time till finish: {}".format(int(progress * 100 / len(hrps))),
          (t2 - t1) / progress * (len(hrps) - progress))
    with open(executor_result_path) as f:
        lines = [x.strip() for x in f.readlines()]
        if len(lines) > 0 and len(lines[0]) > 17:
            continue

        changed = False
        for seq in lines:
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
                changed = True

        if changed == True:
            print(best_sequences)
