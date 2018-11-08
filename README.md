# dfalib

## Description

dfalib - is a framework for fast search of minimal sequences which fit to specific patterns. These patterns are formulated in terms of regular expressions It's optimized in c++ and can be used by chemists in their work.

In dfalib the following algorithms are implemented:
  - create DFA from regular expression.
  - DFA minimization.
  - intersection of two DFAs.
  
## Program compilation:

``` bash
PROJECTS_DIR="path/to/dir/for/dfalib"
cd $PROJECTS_DIR
git clone https://github.com/myurushkin/dfalib
mkdir build
cd build
cmake ../dfalib
make
```

## Example of usage python script:

Example: Find strongest srings of minimum length which contain all patterns:
``` bash
PYTHONPATH="${PROJECTS_DIR}/dfalib/scripts" python "${PROJECTS_DIR}/dfalib/scripts/testmods/find_strongest_sequences.py" --find-GQD 1 --find-IMT 1 --find-HRP 1 --find-TRP 1  "${PROJECTS_DIR}/build/dfalibproj/sources/testmod/testmod" ./output.txt
```

Example of output:
```
aaaataaag: (-1, -1, -1, 1)
agaataaag: (-1, -1, -1, 1)
aagataaag: (-1, -1, -1, 1)
aggataaag: (-1, -1, -1, 1)
aaagtaaag: (-1, -1, -1, 1)
agagtaaag: (-1, -1, -1, 1)
aaggtaaag: (-1, -1, -1, 1)
agggtaaag: (-1, -1, -1, 1)
aaaatgaag: (-1, -1, -1, 1)
agaatgaag: (-1, -1, -1, 1)
aagatgaag: (-1, -1, -1, 1)
aggatgaag: (-1, -1, -1, 1)
aaagtgaag: (-1, -1, -1, 1)
agagtgaag: (-1, -1, -1, 1)
aaggtgaag: (-1, -1, -1, 1)
agggtgaag: (-1, -1, -1, 1)
aaaatcaag: (-1, -1, -1, 1)
agaatcaag: (-1, -1, -1, 1)
aagatcaag: (-1, -1, -1, 1)
```

## Arguments description:
* --find-GQD <0 or 1>. The argument enables search of sequences with GQD pattern. Default value is 0. 
* --find-IMT <0 or 1>. The argument enables search of sequences with IMT pattern. Default value is 0.
* --find-HRP <0 or 1>. The argument search of sequences with HRP pattern. Default value is 0.
* --find-TRP <0 or 1>. The argument search of sequences with TRP pattern. Default value is 0.
* --length <positive number>. Default value is 1. Minimal size of sequence. 
