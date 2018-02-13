import subprocess
import os
import uuid
import sys
import shutil


def extractIndex(execsh_file):
    # first get the hisat command line
    file = open(execsh_file, "r")
    command = None
    for line in file:
        if line.startswith("hisat2"):
            command = line

    # now get the index which follows the -x
    lineBits = command.split()
    indexVal = None
    for index, bit in enumerate(lineBits):
        if lineBits[index] == "-x":
            indexVal = lineBits[index + 1]

    # now, if its a zip file it will look like /path.../<zipfile>.zip/prefix
    # otherwise its a directory /path.../directory/prefix
    # if its a zipfile we want to unzip it into a directory called <zipfile>.zip
    # so that we do not need to rewrite the command line inside the exec.sh script
    # 
    fileOrDir = indexVal[:indexVal.rfind('/')]

    if (os.path.isfile(fileOrDir)):
        # rename it so we can expand it to the same name
        unique_filename = str(uuid.uuid4())
        os.rename(fileOrDir, unique_filename)
        print("renamed " + fileOrDir + " to " + unique_filename)

        dirLower = fileOrDir.lower()
        indexDirName = fileOrDir
        # make the old filename into a directory
        os.makedirs(indexDirName)
        # move the archive to the directory that has its old name
        shutil.move(unique_filename, fileOrDir + "/" + unique_filename)

        if ((dirLower.endswith(".zip"))):
            # unzip a zip file
            cmnd = ["unzip " + unique_filename]
        elif ((dirLower.endswith(".tar.gz")) or (dirLower.endswith(".tar"))):
            # gunzip and untar a tarball
            cmnd = ["tar -xzf " + unique_filename]
            print("cmnd is " + cmnd[0])
        elif (dirLower.endswith(".gz")):
            # unzip a gziped file
            cmnd = ["gunzip " + unique_filename]
        else:
            print("Doing nothing with " + fileOrDir)
            cmnd = None

        if (cmnd is not None):
            try:
                output = subprocess.check_output(
                    cmnd, stderr=subprocess.STDOUT, shell=True, timeout=33,
                    universal_newlines=True, cwd=indexDirName)
            except subprocess.CalledProcessError as exc:
                print("Uncompressing index Status : FAIL", exc.returncode, exc.output)
            else:
                print("Uncompressing index Output: \n{}\n".format(output))


execFile = sys.argv[1]
extractIndex(execFile)
