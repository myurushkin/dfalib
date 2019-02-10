# -*- coding: utf-8 -*-

import sys, os
sys.path.append('../')


from modules import parsers

if __name__ == "__main__":
    seq = "tgactgactgactgactgactgac"

    find_GQD = True
    find_IMT = True
    find_TRP = True
    find_HRP = True
    result = parsers.analyze_string(seq, [find_GQD, find_IMT, find_TRP, find_HRP])
    print("GQD strength = {}".format(result[0]))
    print("IMT strength = {}".format(result[1]))
    print("HRP strength = {}".format(result[2]))
    print("TRP strength = {}".format(result[3]))
