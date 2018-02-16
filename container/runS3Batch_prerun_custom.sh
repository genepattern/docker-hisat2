# copyright 2017-2018 Regents of the University of California and the Broad Institute. All rights reserved.

##################################################
# MODIFICATION FOR  LOADING GENOME INDEX Directory for Hisat2 
##################################################

export LD_LIBRARY_PATH=/ngs-sdk.1.3.0-linux/lib64:$LD_LIBRARY_PATH
export HISAT2_HOME=/hisat2-2.1.0
echo Executable is $5
python3 /usr/local/bin/extractIndexIfNecessary.py  $5 




