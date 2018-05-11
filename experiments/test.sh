#!/bin/sh


BUILD_DIR="/home/misha/projects-git/dfalib/build/dfalibproj/sources/testmod"

cd ../scripts/testmods
python find_strongest_sequences.py --find-GQD 1 --find-IMT 1 --find-TRP 1 --find-HRP 1 $BUILD_DIR/testmod ./output1.txt
python find_strongest_sequences.py --find-GQD 1 --find-IMT 1 --find-TRP 2 --find-HRP 1 $BUILD_DIR/testmod ./output2.txt
python find_strongest_sequences.py --find-GQD 1 --find-IMT 1 --find-TRP 1 --find-HRP 0 $BUILD_DIR/testmod ./output3.txt
python find_strongest_sequences.py --find-GQD 1 --find-IMT 1 --find-TRP 2 --find-HRP 0 $BUILD_DIR/testmod ./output4.txt 

