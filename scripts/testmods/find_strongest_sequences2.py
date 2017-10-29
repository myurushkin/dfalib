# -*- coding: utf-8 -*-

import os
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

result_dirpath = r"/home/misha/projects-git/dfalib/results"
suffixes = ["default", "18", "19", "20"]
expected_lengths = [17, 18, 19, 20]

for i in range(len(suffixes)):
    suffix = suffixes[i]
    expected_length = expected_lengths[i]
    print("analyze {}...".format(suffix))

    best_sequences = []
    input_path = os.path.join(result_dirpath, "result_{}.txt".format(suffix))

    with open(input_path) as f:
        while True:
            seq = f.readline().strip()
            if len(seq) == 0:
                break
            assert len(seq) == expected_length
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
        with open(os.path.join(result_dirpath, "result_min_{}.txt".format(suffix)), "w") as f:
            for seq in best_sequences:
                f.write("{}\n".format(seq))