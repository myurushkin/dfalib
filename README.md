# dfalib

## Description

dfalib - is a framework for fast search of minimal sequences which fit to specific patterns. These patterns are formulated in terms of regular expressions It's optimized in c++ and can be used by chemists in their work.

In dfalib the following algorithms are implemented:
  - create DFA from regular expression.
  - DFA minimization.
  - intersection of two DFAs.
  
## Program compilation:

PROJECTS_DIR="path/to/dir/for/dfalib"

``` bash
cd $PROJECTS_DIR
git clone https://github.com/myurushkin/dfalib
mkdir build
cd build
cmake ../dfalib
make
```

## execute python script:
``` bash
PYTHONPATH="${PROJECTS_DIR}/dfalib/scripts" python "${PROJECTS_DIR}/dfalib/scripts/testmods/find_strongest_sequences.py" --find-GQD 1 --find-IMT 1 --find-HRP 1 --find-TRP 1  "${PROJECTS_DIR}/build/dfalibproj/sources/testmod/testmod" ./output.txt
```


