import sys
from io import StringIO
import os
import zipfile
import subprocess

# work directly with sys.argv to avoid having to specify all the parameters that do not change but can just pass through
# so we'l look at the args ourselves and only rewrite as necessary when we see an arg that is not
# passed natively to the hisat call

def rewriteIndex(args, buff, arg, argDict):
    # expect either a zip file or a dir,
    # if a zip, unzip it to a dir of the same name
    # The dirname is the prefix as seen by hisat
    #    -x <index.dir>/<index.file.prefix>
    zipOrDirPath = next(args)
    basename = os.path.splitext(os.path.basename(zipOrDirPath))[0]

    if os.path.isfile(zipOrDirPath):
        if not zipOrDirPath.lower().endsWith(".zip"):
            print("This should be a zip file, extension is wrong..." + zipOrDirPath)

        # this should be created in os.getcwd() the current working directory which is fine
        os.mkdir(basename)
        # try to unzip
        os.path.splitext(zipOrDirPath)
        zip_ref = zipfile.ZipFile(zipOrDirPath, 'r')
        zip_ref.extractall(basename)
        zip_ref.close()
        zipOrDirPath = basename
    elif os.path.isdir(zipOrDirPath):
        # for directories we use the convention that the index name prefix is the same as the directory name
        basename = basename
    else:
        raise ValueError("Index Problem: " + zipOrDirPath + " is neither a zip file nor a directory")

    # else its a dir
    buff.write(u"-x ")
    buff.write(unicode(zipOrDirPath))
    buff.write(u"/")
    buff.write(unicode(basename))




def readPairs(args, buff, arg, argDict):
    # look to see if we got -1 and -2, and if so write them.  If not we
    # only got -1 so we write it as -U with the next value
    readpairs_1 = next(args)
    if ("-2" in argDict):
        buff.write(u" -1 ")
        buff.write(unicode(readpairs_1))
        buff.write(u" -2 ")
        buff.write(unicode(argDict['-2']))
    else:
        buff.write(u" -U ")
        buff.write(unicode(readpairs_1))

def softclipPenalty(args, buff, arg, argDict):
    next(args, None)
    min = argDict['-min_softclip_penalty']
    max = argDict['-max_softclip_penalty']
    buff.write(u" -sp ")
    buff.write(unicode(min))
    buff.write(u",")
    buff.write(unicode(max))


def nCeilFunc(args, buff, arg, argDict):
    next(args, None)
    min = argDict['-min_n_ceil']
    max = argDict['-max_n_ceil']
    buff.write(u" --n-ceil L,")
    buff.write(unicode(min))
    buff.write(u",")
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
    buff.write(unicode(" --pen-canonintronlen G,"))
   
    buff.write(unicode(str(min)) )
    buff.write(u",")
    buff.write(unicode(str(max)))

def noncanonIntronPenFunc(args, buff, arg, argDict):
    next(args)
    min = argDict['-min_pen-noncanintronlen']
    max = argDict['-max_pen-noncanintronlen']
    buff.write(unicode(" --pen-noncanonintronlen G,"))
    buff.write(unicode(str(min)))
    buff.write(u"," )
    buff.write(unicode(str(max)) )

def outputPrefix(args, buff, arg, argDict):
    val = next(args)
    buff.write(u" -S ")
    buff.write(unicode(val ))
    if not val.lower().endswith(".sam"):
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
    x = argDict['-min.mismatch.penalty']
    y = argDict['-max.mismatch.penalty']
    buff.write(u" --mp ")
    buff.write(unicode(x ))
    buff.write(u",")
    buff.write(unicode(y) )


#######################   these two are the catchall handler fuunctions ============
def passThrough(args, buff, arg, argDict):
    val = next(args, None)
    buff.write(unicode(arg) )
    buff.write(u" ")
    buff.write(unicode(val) )
    print("passthrough on: " + str(arg) + "  with val " + str(val))


def justAFlagPassThrough(args, buff, arg, argDict):
    # don't do anything to the argument but in this case its just a flag with no value following it
    buff.write(unicode(arg) )
    buff.write(u" ")
    print("just a flag on: "+ arg)



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
                "--fr": justAFlagPassThrough,
                "--rf": justAFlagPassThrough,
                "--ff": justAFlagPassThrough,
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
                "--WRAPPER_IGNORE": nullFlag
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
                print("1. Arg is ->" + str(arg) + "<- val ->"+ val )
            else:
                print("  i.a  Arg is ->" + str(arg)  + "<-  " )

    print("CWD is " + os.getcwd())
    buff = StringIO()
    buff.write(u"hisat2 ")

    allargs = iter(sys.argv)
    next(allargs, None)  # strip off the script's name
    for arg in allargs:

        handler = handlers.get(arg, passThrough)
        handler(allargs, buff, arg, argDict)
        buff.write(u" ")

        print("\n "+ buff.getvalue())

    print("THE COMMAND LINE IS BELOW:\n")
    print(buff.getvalue())
    return buff.getvalue()


if __name__ == '__main__':
    revised_command = generate_command()
    # now call it passing along the same environment we got
    subprocess.call(revised_command, shell=True, env=os.environ)

