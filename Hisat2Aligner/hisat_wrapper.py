# copyright 2017-2018 Regents of the University of California and the Broad Institute. All rights reserved.

import sys
from io import StringIO
import os
import zipfile
import subprocess
from subprocess import PIPE, STDOUT
import shutil

# work directly with sys.argv to avoid having to specify all the parameters that do not change but can just pass through
# so we'l look at the args ourselves and only rewrite as necessary when we see an arg that is not
# passed natively to the hisat call

indexDirToDelete = None
dryRun = False

def rewriteIndex(args, buff, arg, argDict):
    global indexDirToDelete

    # expect either a zip file or a dir,
    # if a zip, unzip it to a dir of the same name
    # The dirname is the prefix as seen by hisat
    #    -x <index.dir>/<index.file.prefix>
    zipOrDirPath = next(args)
    basename = os.path.splitext(os.path.basename(zipOrDirPath))[0]

    if os.path.isfile(zipOrDirPath):
        if not zipOrDirPath.lower().endswith(".zip"):
            print("This should be a zip file, extension is wrong..." + zipOrDirPath)
        # this should be created in os.getcwd() the current working directory which is fine
        os.mkdir(basename)
        # try to unzip
        os.path.splitext(zipOrDirPath)
        zip_ref = zipfile.ZipFile(zipOrDirPath, 'r')
        zip_ref.extractall(basename)
        zip_ref.close()
        zipOrDirPath = basename
        indexDirToDelete = basename
    elif os.path.isdir(zipOrDirPath):
        # for directories we use the convention that the index name prefix is the same as the directory name
        # basename = basename
        basename="genome" # to match the ftp://gpftp.broadinstitute.org/module_support_files/hisat2/index/by_genome/
    else:
        raise ValueError("Index Problem: " + zipOrDirPath + " is neither a zip file nor a directory")


    # else its a dir
    buff.write(u"-x ")
    buff.write(unicode(zipOrDirPath))
    buff.write(u"/")
    buff.write(unicode(basename))



def readFileList(fileList):
    files =[]

    fileReader = open(fileList, 'r')
    for line in fileReader:
        line = line.rstrip('\n')
        line = line.strip()
        result = line.split('\t')
        if len(result) >= 1:
            filepath = result[0]
            assert os.path.exists(filepath), 'File does not exist: ' + filepath

            #if it is a directory then get all the files in that directory
            if os.path.isdir(filepath):
                subFiles = [os.path.join(filepath,fName) for fName in next(os.walk(filepath))[2]]
                subFiles.sort()
                files += subFiles
            else:
                files.append(filepath)
    return ','.join(files)


def readPairs(args, buff, arg, argDict):
    # look to see if we got -1 and -2, and if so write them.  If not we
    # only got -1 so we write it as -U with the next value
    readpairs_1 = readFileList(next(args))


    if ("-2" in argDict):
        readpairs_2 = readFileList(unicode(argDict['-2']))

        buff.write(u" -1 ")
        buff.write(unicode(readpairs_1))
        buff.write(u" -2 ")
        buff.write(unicode(readpairs_2))
    else:
        buff.write(u" -U ")
        buff.write(unicode(readpairs_1))

def softclipPenalty(args, buff, arg, argDict):
    next(args, None)
    min = argDict['-min_softclip_penalty']
    max = argDict['-max_softclip_penalty']
    buff.write(u" --sp ")
    buff.write(unicode(max))
    buff.write(u",")
    buff.write(unicode(min))


def nCeilFunc(args, buff, arg, argDict):
    next(args, None)
    min = argDict['-min_n_ceil']
    max = argDict['-max_n_ceil']
    buff.write(u" --n-ceil L,")
    buff.write(unicode(min ))
    buff.write(u",")
    buff.write(unicode(max ))

def scoreMinFunc(args, buff, arg, argDict):
    next(args)
    min = argDict['-min.score.align']
    max = argDict['-max.score.align']
    buff.write(u" --score-min L,")
    buff.write(unicode(min ))
    buff.write(u",")
    buff.write(unicode(max ))

def canonIntronPenFunc(args, buff, arg, argDict):
    next(args)
    min = argDict['-min_pen-canintronlen']
    max = argDict['-max_pen-canintronlen']
    buff.write(unicode(u" --pen-canintronlen G,"))
   
    buff.write(unicode(str(min)) )
    buff.write(u",")
    buff.write(unicode(str(max)))

def noncanonIntronPenFunc(args, buff, arg, argDict):
    next(args)
    min = argDict['-min_pen-noncanintronlen']
    max = argDict['-max_pen-noncanintronlen']
    buff.write(unicode(u" --pen-noncanintronlen G,"))
    buff.write(unicode(str(min)))
    buff.write(u"," )
    buff.write(unicode(str(max)) )

def outputPrefix(args, buff, arg, argDict):
    val = next(args)
    buff.write(u" -S ")
    buff.write(unicode(val ))
    buff.write(u".sam")

def mappedReads(args, buff, arg, argDict):
    if ("-2" in argDict):
        buff.write(u" --al-conc-gz ")
    else:
        buff.write(u" --al-gz ")
    val = next(args)
    buff.write(unicode(val ))


def unmappedReads(args, buff, arg, argDict):
    if ("-2" in argDict):
        buff.write(u" --un-conc-gz ")
    else:
        buff.write(u" --un-gz ")
    val = next(args)
    buff.write(unicode(val ))

def readGapPenFunc(args, buff, arg, argDict):
    next(args)
    x = argDict['-read.gap.open.pen']
    y = argDict['-read.gap.extend.pen']
    buff.write(u" --rdg ")
    buff.write(unicode(x) )
    buff.write(u",")
    buff.write(unicode(y))


def refGapPenFunc(args, buff, arg, argDict):
    next(args)
    x = argDict['-ref.gap.open.pen']
    y = argDict['-ref.gap.extend.pen']
    buff.write(u" --rfg ")
    buff.write(unicode(x ))
    buff.write(u",")
    buff.write(unicode(y ))

def mismatchPenFunc(args, buff, arg, argDict):
    next(args)
    minp = argDict['-min.mismatch.penalty']
    maxp = argDict['-max.mismatch.penalty']
    buff.write(u" --mp ")
    buff.write(unicode(maxp ))
    buff.write(u",")
    buff.write(unicode(minp) )

def dryRunFlag(args, buff, arg, argDict):
    val = next(args, None)
    if ("True" == val):
        dryRun = True

#######################   these are the catchall handler fuunctions ============
def passThrough(args, buff, arg, argDict):
    val = next(args, None)
    buff.write(unicode(arg) )
    buff.write(u" ")
    buff.write(unicode(val) )
    #print("passthrough on: " + str(arg) + "  with val " + str(val))


def justAFlagPassThrough(args, buff, arg, argDict):
    # don't do anything to the argument but in this case its just a flag with no value following it
    buff.write(unicode(arg) )
    buff.write(u" ")
    #print("just a flag on: "+ arg)



def nullOpt(args, buff, arg, argDict):
    # this is for options that are present in the GP command line to this script
    # but get combined into a compound argument to hisat itself.  We don't want them to pass
    # through, they should just be dropped on the assumtion that another handler consumes them
    # from the arg dict.
    next(args, None)

def nullFlag(args, buff, arg, argDict):
    # this is for flags used as placeholders that should not pass through to the actual hisat2 call.
    # usually this is for a genepattern dropdown that we really want nothing in one case, but thats not
    # an allowable value in a GenePattern selector
    print('')

#######################  END - these two are the catchall handler fuunctions ============




def setupHandlers():
    handlers = {"-index": rewriteIndex,
                "-U": readPairs,
                "-2": nullOpt,
                "-min_softclip_penalty": softclipPenalty,
                "-max_softclip_penalty": nullOpt,
                "-min_n_ceil": nCeilFunc,
                "-max_n_ceil": nullOpt,
                "-min.score.align": scoreMinFunc,
                "-max.score.align": nullOpt,
                "-min_pen-canintronlen": canonIntronPenFunc,
                "-max_pen-canintronlen": nullOpt,
                "-min_pen-noncanintronlen": noncanonIntronPenFunc,
                "-max_pen-noncanintronlen": nullOpt,
                "-S": outputPrefix,
                "--int-quals": justAFlagPassThrough,
                "-f":  justAFlagPassThrough,
                "-p":  passThrough,
                "--fr": justAFlagPassThrough,
                "--rf": justAFlagPassThrough,
                "--ff": justAFlagPassThrough,
                "--phred33": justAFlagPassThrough,
                "--phred64": justAFlagPassThrough,
                "--solexa-quals": justAFlagPassThrough,
                "--ignore-quals": justAFlagPassThrough,
                "--no-mixed": justAFlagPassThrough,
                "--no-discordant": justAFlagPassThrough,
                "--no-spliced-alignment": justAFlagPassThrough,
                "--secondary": justAFlagPassThrough,
                 "-mapped.reads": mappedReads,
                "-unmapped.reads": unmappedReads,
                "-read.gap.open.pen": readGapPenFunc,
                "-read.gap.extend.pen": nullOpt,
                "-ref.gap.open.pen": refGapPenFunc,
                "-ref.gap.extend.pen": nullOpt,
                "-min.mismatch.penalty": mismatchPenFunc,
                "-max.mismatch.penalty": nullOpt,
                "--norc":justAFlagPassThrough,
                "--nofw":justAFlagPassThrough,
                "--norc": justAFlagPassThrough,
                "--WRAPPER_IGNORE": nullFlag,
                "-WRAPPER_IGNORE": nullFlag,
                "-dryRun": dryRunFlag,

                ## below are ones that do not seem to match to the hisat2 doc but that VIB specified
                ## these need to be examined more closely
                #"--max-seeds": nullOpt,
                }
    return handlers



def generate_command():

    handlers = setupHandlers()

    # cache all args by their -? names since some of the cases take multiple GP args
    # and condense them into a single compound hisat arg
    argDict = {}
    allargs = iter(sys.argv)
    next(allargs)
    for arg in allargs:
        if arg.startswith('-'):
            key = arg
            handler = handlers.get(arg, passThrough)

            if not ((handler == justAFlagPassThrough) or (handler == nullFlag)):
                val = next(allargs, None)
                argDict[key] = val
                #print("1. Arg is ->" + str(arg) + "<- val ->"+ val )


    buff = StringIO()
    buff.write(u"hisat2 ")

    allargs = iter(sys.argv)
    next(allargs, None)  # strip off the script's name
    for arg in allargs:
        handler = handlers.get(arg, passThrough)
        #print("arg is " + arg)
        handler(allargs, buff, arg, argDict)
        buff.write(u" ")
        #print("        buff is now " + buff.getvalue())

    return buff.getvalue()



if __name__ == '__main__':

    revised_command = generate_command()

    if dryRun:
        print(revised_command)
    else:
        # print command line to stdout for debugging
        print(revised_command)
        # now call it passing along the same environment we got
        childProcess = subprocess.Popen(revised_command, shell=True, env=os.environ, stdout=PIPE, stderr=PIPE)
        stdout, stderr = childProcess.communicate()
        retval = childProcess.returncode
        if (retval != 0):
                # if non-zero return, print stderr to stderr
                print( stdout ) 
                print  >> sys.stderr, stderr
        else:
                # if not a non-zero stdout, print stderr to stdout since Hisat2Indexer logs non-error
                # stuff to stderr.  Downside is the stderr and stdout are not interlevened
                print(stdout)
                print(stderr)



    if not (indexDirToDelete == None):
        shutil.rmtree(indexDirToDelete)

