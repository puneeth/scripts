#!/usr/bin/python2

"""
    Annotates the a frame sequence using Imagemagick
        - Uses pango feature of imagemagick


"""

import logging
from subprocess import call

""" colors.."""
white = "white"
grey = "grey"

"""Text with needs to be modified"""
pangoText = ("<markup> <span face=\"Arial\"><span fgcolor=\"white\">\n"
             "<span size=\"20000\"><b> UnitA          UnitB          UnitC "
             "</b> </span></span>\n"
             "<span size=\"15000\"><span fgcolor=\"white\">  v=100 km/hr      "
             "v=080 km/hr        v=045 km/hr </span>\n"
             "<span fgcolor=\"white\">                            WiFi</span>"
             "                     <span fgcolor=\"white\">WiFi</span>\n"
             "<span fgcolor=\"{0}\">                            "
             "Long Range</span>         <span fgcolor=\"{1}\">"
             "Long Range</span>\n"
             "<span fgcolor=\"{2}\">                            "
             "Short Range</span>"
             "        <span fgcolor=\"{3}\">Short Range</span> </span> "
             "</span></markup>\n")

convertcmdTp = ("convert -background '#0003' -gravity south "
              "pango:@/tmp/pango.txt /tmp/text_{0}")
compositecmdTp = "composite -gravity SouthEast /tmp/text_{0} {1} anno_{2}"


def testOnAImg():
    """These will only get output if you turn up verbosity."""
    logging.info("Attempting to add text on a test image")
    ptextfile = open('/tmp/pango.txt', 'w')
    ptextfile.write(pangoText.format(white, white, white, white))
    ptextfile.close()
    filename = "testimage.png"
    convertcmd = convertcmdTp.format(filename)
    compositecmd = compositecmdTp.format(filename, filename, filename)

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
    testOnAImg()
