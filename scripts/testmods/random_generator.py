# -*- coding: utf-8 -*-

import sys, os
sys.path.append('../')

from modules import helpers

if __name__ == "__main__":
    random_strings = helpers.generate_random_strings(60, 60, 2746)
    with open("random_strings.csv", "w") as f:
        for str in random_strings:
            f.write(str)
            f.write('\n')
