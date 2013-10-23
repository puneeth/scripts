#!/usr/bin/python2

"""
    Annotates the a frame sequence using Imagemagick
        - Uses pango feature of imagemagick


"""

import logging
from subprocess import call
import glob
import os
import csv

""" colors.."""
white = "white"
grey = "grey"

"""Text with needs to be modified"""
pangoText = ("<markup> <span face=\"Arial\"><span fgcolor=\"white\">\n"
             "<span size=\"20000\"><b> UnitA          UnitB          UnitC "
             "</b> </span></span>\n"
             "<span size=\"15000\"><span fgcolor=\"white\">  v={0:03d} km/hr"
             "      v={1:03d} km/hr        v={2:03d} km/hr </span>\n"
             "<span fgcolor=\"white\">                            WiFi</span>"
             "                     <span fgcolor=\"white\">WiFi</span>\n"
             "<span fgcolor=\"{3}\">                            "
             "Long Range</span>         <span fgcolor=\"{4}\">"
             "Long Range</span>\n"
             "<span fgcolor=\"{5}\">                            "
             "Short Range</span>"
             "        <span fgcolor=\"{6}\">Short Range</span> </span> "
             "</span></markup>\n")

convertcmdTp = ("convert -background '#0003' -gravity south "
              "pango:@/tmp/pango.txt /tmp/text_{0}")
compositecmdTp = "composite -gravity SouthEast /tmp/text_{0} {1} {2}/anno_{3}"


def processDir(dirpath, csvFileName):
    print(("Processing dir " + dirpath))
    pngFile = glob.glob(dirpath + os.sep + "*.png")

    # infer file name from csv row
    if(len(pngFile) == 0):
        print(("No files found in " + dirpath))
        return

    csvFile = csv.reader(open(csvFileName, 'rb'))

    rowIndex = 0
    missingFileCount = 0
    for row in csvFile:
        # infer the color and values
        v1 = int(float(row[0]))
        v2 = int(float(row[1]))
        v3 = int(float(row[2]))
        longRangeV2 = (white if (bool(int(row[3])) and not(bool(int(row[4])))) else grey)
        shortRangeV2 = (white if (bool(int(row[4]))) else grey)

        longRangeV3 = (white if (bool(int(row[5])) and not(bool(int(row[6])))) else grey)
        shortRangeV3 = (white if (bool(int(row[6]))) else grey)

        ptextfile = open('/tmp/pango.txt', 'w')
        ptextfile.write(pangoText.format(v1, v2, v3, longRangeV2, longRangeV3,
                                                     shortRangeV2, shortRangeV3))
        ptextfile.close()

        # get the image here
        imgName = 'image_{0:06d}.png'.format(rowIndex)
        imgPath = os.path.join(dirpath, imgName)

        # process the image and save
        if(os.path.exists(imgPath)):
            convertcmd = convertcmdTp.format(imgName)
            compositecmd = compositecmdTp.format(imgName, imgPath, dirpath, imgName)
            #print (convertcmd)
            conRet = call(convertcmd, shell=True)
            if(conRet != 0):
                logging.debug("Failed to run convert cmd")
                return

            #print (compositecmd)
            compRet = call(compositecmd, shell=True)
            if(compRet != 0):
                logging.debug("Failed to run composite cmd")
        else:
            logging.debug("Unable to locate " + imgPath)
            missingFileCount += 1

        rowIndex += 1

    print(("Processed " + str(rowIndex) + ", missing file count : " + str(missingFileCount)))


def testOnAImg():
    """These will only get output if you turn up verbosity."""
    logging.info("Attempting to add text on a test image")
    ptextfile = open('/tmp/pango.txt', 'w')
    ptextfile.write(pangoText.format(100, 20, 30, white, white, white, white))
    ptextfile.close()
    filename = "testimage.png"
    convertcmd = convertcmdTp.format(filename)
    compositecmd = compositecmdTp.format(filename, filename, '.', filename)

    #print (convertcmd)
    conRet = call(convertcmd, shell=True)
    if(conRet != 0):
        logging.debug("Failed to run convert cmd")
        return

    #print (compositecmd)
    compRet = call(compositecmd, shell=True)
    if(compRet != 0):
        logging.debug("Failed to run composite cmd")


if '__main__' == __name__:
    # Late import, in case this project becomes a library,
    # never to be run as main again.
    import optparse

    # Populate our options, -h/--help is already there for you.
    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help="Increase verbosity (specify multiple times for more)")
    # Parse the arguments (defaults to parsing sys.argv).
    opts, args = optp.parse_args()

    # Here would be a good place to check what came in on the command line and
    # call optp.error("Useful message") to exit if all it not well.

    log_level = logging.WARNING  # default
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG

    # Set up basic configuration, out to stderr with
    # a reasonable default format.
    logging.basicConfig(level=log_level)

    # Do some actual work.
    #testOnAImg()
    processDir('HV_UnitC', 'overlayInfo_20131021_155814.txt')
