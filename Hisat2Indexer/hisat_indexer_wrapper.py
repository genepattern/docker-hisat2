# copyright 2017-2018 Regents of the University of California and the Broad Institute. All rights reserved.

import sys
from io import StringIO
import os
import subprocess
import time



indexBaseName = "genome"
dryRun = False
vcf = False
gtf = False

def generate_command():
    global indexBaseName
    buff = StringIO()
    buff.write(u"hisat2-build ")

    allargs = iter(sys.argv)

    # skip the filename
    next(allargs)
    for arg in allargs:
        if (arg.startswith('-fasta')):
            # should be a file list
            val = next(allargs, None)
            buff.write(u" ")

            with open(val) as f:
                content = f.readlines()
            # you may also want to remove whitespace characters like `\n` at the end of each line
            content = [x.strip() for x in content]

            isFirst = True
            for x in content:
                if isFirst==True:
                    isFirst = False
                else:
                    buff.write(u",")
                buff.write(unicode(x))


        if arg.startswith('-indexname'):
            key = arg
            val = next(allargs, None)
            indexBaseName = val
            print("Index base name is " + indexBaseName)
            buff.write(u" ")
            buff.write(unicode(val))

    if gtf:
        print("Including exons and splice sites from gtf file (if any).")
        if os.path.exists("ss.txt"):
            buff.write(u" --ss ss.txt ")
        if os.path.exists("exons.txt"):
            buff.write(u" --exon exons.txt ")



    if vcf:
        print("including haplotypes")
        buff.write(u" --snp haplo.snp")

    return buff.getvalue()

def extractExons():
    global gtf
    gtfFile = None
    allargs = iter(sys.argv)
    next(allargs)
    for arg in allargs:
        if arg.startswith('-gtf'):
            gtf = True
            key = arg
            gtfFile = next(allargs, None)

            command1 = "python /tmp/hisat2/hisat2_extract_splice_sites.py > ss.txt " + gtfFile
            command2 = "python /tmp/hisat2/hisat2_extract_exons.py > exons.txt " + gtfFile

            if dryRun:
                print(command1)
                print("\n")
                print(command2)
            else:
                res1 = subprocess.call(command1, shell=True, env=os.environ)
                res2 = subprocess.call(command2, shell=True, env=os.environ)



def extractHaplotyoes():
    global vcf
    vcfFile = None
    allargs = iter(sys.argv)
    next(allargs)
    argDict = {}
    for arg in allargs:
        val =  next(allargs, None)
        argDict[arg] = val

    vcfFile = argDict.get('-vcf', None)

    if vcfFile is not None:
        vcf = True
        fasta = argDict.get('-fasta')

        command = "python /tmp/hisat2/hisat2_extract_snps_haplotypes_VCF.py " + fasta + " " + vcfFile + " haplo "
        if dryRun:
            print(command)
        else:
            subprocess.call(command, shell=True, env=os.environ)



if __name__ == '__main__':

    allargs = iter(sys.argv)
    next(allargs)
    for arg in allargs:
        if arg.startswith('-dryRun'):
            val = next(allargs, None)
            if ("True" == val):
                dryRun = True


    extractExons()
    extractHaplotyoes()

    revised_command = generate_command()
    # now call it passing along the same environment we got
    if dryRun:
        print(revised_command)
    else:
        subprocess.call(revised_command, shell=True, env=os.environ)

    subprocess.call("zip "+indexBaseName+".zip *.ht2", shell=True, env=os.environ)

    subprocess.call("rm *.ht2", shell=True, env=os.environ)
    if os.path.exists("ss.txt"):
        subprocess.call("rm ss.txt", shell=True, env=os.environ)
    if os.path.exists("exons.txt"):
        subprocess.call("rm exons.txt", shell=True, env=os.environ)







