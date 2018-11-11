# dfalib

## Description

dfalib - is a framework for fast search of minimal sequences which fit to specific patterns. These patterns are formulated in terms of regular expressions It's optimized in C++ and can be used by chemists in their work.

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

## Example of usage:

Search of the strongest strings of minimum length which contain all patterns:
``` bash
PYTHONPATH="${PROJECTS_DIR}/dfalib/scripts" python "${PROJECTS_DIR}/dfalib/scripts/testmods/find_strongest_sequences.py" --find-GQD 1 --find-IMT 1 --find-HRP 1 --find-TRP 1  "${PROJECTS_DIR}/build/dfalibproj/sources/testmod/testmod" ./output.txt
```

Output:
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

Output represents list of the strongest sequences of minimum size which correspond to search requirements.
The stength of sequence is vector of values. 

## Strength vector description

Stength vector of sequence has the following format 
```(a, b, c, d)```

where a, b, c, d correspond to a number of GQD, IMT, HRP, TRP patterns found in the sequence.
If particular attribute is equal to -1 it means that it was not specified in search parameters and is out of interest.

In the output presented all sequences (19 in total) which are the smallest and contain at least one triplex. The size is 9 and all of them have only 1 triplex. Extra facts which are proved automatically:

1) There're no sequences of size lesser then 9 which have at least 1 triplex.
2) There're no suquences of size 9 which have more then 1 triplex.

## Arguments description:
* --find-GQD <0 or 1>. The argument enables search of sequences with GQD pattern. Default value is 0. 
* --find-IMT <0 or 1>. The argument enables search of sequences with IMT pattern. Default value is 0.
* --find-HRP <0 or 1>. The argument search of sequences with HRP pattern. Default value is 0.
* --find-TRP <0 or 1>. The argument search of sequences with TRP pattern. Default value is 0.
* --length <positive number>. Default value is 1. Minimal size of sequence. 
