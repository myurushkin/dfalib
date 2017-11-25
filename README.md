# dfalib

dfalib - is a framework for fast search of minimal sequences which fit to specific patterns. These patterns are formulated in terms of regular expressions It's optimized in c++ and can be used by chemists in their work.

In dfalib the following algorithms are implemented:
  - create DFA from regular expression.
  - DFA minimization.
  - intersection of two DFAs.
  
Instructions


cd <projects-dir>
git clone https://github.com/myurushkin/dfalib
mkdir build
cd build
cmake ../projects
make
cd .projects/dfalib/scripts/testmods
python

dfalibproj/sources/testmod/testmod

