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
import tempfile

""" colors.."""
black = "black"
white = "white"
grey = "grey"
green = "green"
red = "red"

"""Text with needs to be modified"""
pangoText = ("<markup> <span face=\"Arial\"><span fgcolor=\"white\">\n"
             "<span size=\"24000\"><b>  Train A             Train B              Train C </b> </span>\n"
             "<span size=\"14000\"><b>     LEADER                       FOLLOWER1                     FOLLOWER2   </b> </span></span>\n\n"
             "<span size=\"15000\"><span fgcolor=\"white\">   V<sub>A</sub> = {0:03d}<span fgcolor=\"{3}\">km/hr</span>               "
             "V<sub>B</sub> = {1:03d}<span fgcolor=\"{4}\">km/hr</span>                   V<sub>C</sub> = {2:03d}<span fgcolor=\"{5}\">km/hr</span>   \n"
             " Accel<sub>A</sub> = {6:+0.1f}m/s<sup>2</sup>          Accel<sub>B</sub> = {7:+0.1f}m/s<sup>2</sup>             Accel<sub>C</sub> = {8:+0.1f}m/s<sup>2</sup></span>\n"
             "</span><span size=\"12000\"><b><span fgcolor=\"black\"><tt> <span bgcolor=\"green\">     WiFi     </span>    <span bgcolor=\"green\">       WiFi         </span>    "
             "<span bgcolor=\"green\">        WiFi        </span></tt></span>\n"
             "<tt><span fgcolor=\"{9}\">                   <span bgcolor=\"{13}\">  Long Range Radar  </span></span>    <span fgcolor=\"{10}\"><span bgcolor=\"{14}\">  Long Range Radar  "
             "</span></span></tt>\n"
             "<tt><span fgcolor=\"{11}\">                   <span bgcolor=\"{15}\"> Short Range Laser  </span></span>    <span fgcolor=\"{12}\"><span bgcolor=\"{16}\"> Short Range Laser  "
             "</span></span></tt></b></span> "
             "</span></markup><span size=\"8000\"></span>\n")

convertcmdTp = ("convert -background '#000A' -gravity south "
              "pango:@{0}/pango.txt {0}/text_{1}")
compositecmdTp = "composite -gravity SouthEast {0}/text_{1} {2} {3}/anno_{4}"


def processDir(dirpath, csvFileName):
    print(("Processing dir " + dirpath))
    pngFile = glob.glob(dirpath + os.sep + "*.png")

    # infer file name from csv row
    if(len(pngFile) == 0):
        print(("No files found in " + dirpath))
        return

    csvFile = csv.reader(open(csvFileName, 'rb'))

    temppath = tempfile.mkdtemp()

    rowIndex = 0
    missingFileCount = 0
    for row in csvFile:
        # infer the color and values
        v1 = int(float(row[0]))
        v2 = int(float(row[1]))
        v3 = int(float(row[2]))

        a1 = float(row[3])
        a2 = float(row[4])
        a3 = float(row[5])

        if(a1 >= 0.01):
            v1Color = green
        elif(a1 < -0.01):
            v1Color = red
        else:
            v1Color = white  # no need to display values lower than these..
            a1 = 0

        if(a2 >= 0.01):
            v2Color = green
        elif(a2 < -0.01):
            v2Color = red
        else:
            v2Color = white
            a2 = 0

        if(a3 >= 0.01):
            v3Color = green
        elif(a3 < -0.01):
            v3Color = red
        else:
            v3Color = white
            a3 = 0

        (longRangeV2, lrV2Color) = ((black, green) if (bool(int(row[6]))) else (grey, white))
        (shortRangeV2, srV2Color) = ((black, green) if (bool(int(row[7]))) else (grey, white))

        (longRangeV3, lrV3Color) = ((black, green) if (bool(int(row[8]))) else (grey, white))
        (shortRangeV3, srV3Color) = ((black, green) if (bool(int(row[9]))) else (grey, white))

        pangoFilepath = os.path.join(temppath, 'pango.txt')
        ptextfile = open(pangoFilepath, 'w')
        ptextfile.write(pangoText.format(v1, v2, v3, v1Color, v2Color, v3Color,
                                        a1, a2, a3,
                                        longRangeV2, longRangeV3, shortRangeV2, shortRangeV3,
                                        lrV2Color, lrV3Color, srV2Color, srV3Color))
        ptextfile.close()

        # get the image here
        imgName = 'image_{0:06d}.png'.format(rowIndex)
        imgPath = os.path.join(dirpath, imgName)

        # process the image and save
        if(os.path.exists(imgPath)):
            convertcmd = convertcmdTp.format(temppath, imgName)
            compositecmd = compositecmdTp.format(temppath, imgName, imgPath, dirpath, imgName)
            #print (convertcmd)
            conRet = call(convertcmd, shell=True)
            if(conRet != 0):
                logging.debug("Failed to run convert cmd")

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
    optp.add_option('-f', '--overlayfile', dest='overlayfile', metavar="FILE",
                    help="File containg overlay information")

    optp.add_option('-d', '--directory', dest='directory', metavar="FILE",
                    help="Directory containing images to overlay")
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

    if(not opts.overlayfile):
        optp.error('Overlay file not given!')

    if(not opts.directory):
        optp.error('Directory not given!')

    # Do some actual work.
    #testOnAImg()
    #processDir('HV_UnitC', 'overlayInfo_20131021_155814.txt')
    #processDir('stest', 'testset.txt')
    processDir(opts.directory, opts.overlayfile)
