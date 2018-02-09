#!/bin/bash
# set up a temp dir structure to unzip into
rm -rf zipTmp
mkdir zipTmp
mkdir zipTmp/dir1
mkdir zipTmp/dir2
cp $1 zipTmp/dir1
cp $2 zipTmp/dir2

# unzip the expected file and the job result file
cd zipTmp/dir1
unzip $1
cd ../../zipTmp/dir2
unzip $2

# now diff the dir contents and the first file

diff zipTmp/dir1 dipTmp/dir2
diff zipTmp/dir1/genome.ht1 zipTmp/dir2/genome.ht1
