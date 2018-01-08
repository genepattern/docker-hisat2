import sys
from io import StringIO
import os
import subprocess
import shutil
import zipfile
import glob

indexBaseName = "";

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def generate_command():

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
            buff.write(u" ")
            buff.write(unicode(val))

    print("CWD is " + os.getcwd())
    print("command is " + buff.getvalue())

    #allargs = iter(sys.argv)
    #next(allargs, None)  # strip off the script's name
    #for arg in allargs:
    #    handler = handlers.get(arg, passThrough)
    #    handler(allargs, buff, arg, argDict)
    #    buff.write(u" ")



    #print("\n THE GENERATED COMMAND LINE IS BELOW:\n")
    #print(buff.getvalue())
    return buff.getvalue()

def extractExons():
    gtfFile = None
    allargs = iter(sys.argv)
    next(allargs)
    for arg in allargs:
        if arg.startswith('-gtf'):
            key = arg
            gtfFile = next(allargs, None)

            command = "python /tmp/hisat2/hisat2_extract_splice_sites.py " + gtfFile
            if dryRun:
                print(command)
            else:
                subprocess.call(command, shell=True, env=os.environ)

def extractHaplotyoes():
    vcfFile = None
    allargs = iter(sys.argv)
    next(allargs)
    for arg in allargs:
        if arg.startswith('-vcf'):
            key = arg
            gtfFile = next(allargs, None)

            command = "python /tmp/hisat2/hisat2_extract_snps_haplotypes_VCF.py " + vcfFile
            if dryRun:
                print(command)
            else:
                subprocess.call(command, shell=True, env=os.environ)


if __name__ == '__main__':
    dryRun = False

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
        print(command)
    else:
        subprocess.call(revised_command, shell=True, env=os.environ)

    # now zip up the current directory
    zipf = zipfile.ZipFile(indexBaseName + '.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(os.getcwd(), zipf)
    zipf.close()
    # and remove the indexes
    for f in glob.glob("*.ht2"):
        os.remove(f)



