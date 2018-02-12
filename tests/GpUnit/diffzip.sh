#!/bin/bash
# set up a temp dir structure to unzip into
rm -rf zipTmp
mkdir zipTmp
mkdir zipTmp/dir1
mkdir zipTmp/dir2

cp $1  zipTmp/dir1/1.zip
cp $2  zipTmp/dir2/1.zip
# unzip the expected file and the job result file
cd zipTmp/dir1
unzip 1.zip
rm 1.zip 

cd ../../zipTmp/dir2
unzip 1.zip
rm 1.zip

# now diff the dir contents and the first file
cd ../..

diff zipTmp/dir1 zipTmp/dir2
