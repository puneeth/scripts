#!/usr/bin/python2

"""
    An example setup


"""

import logging

def foo():
    """These will only get output if you turn up verbosity."""
    logging.debug("This is debug.")
    logging.info("This is info.")

def bar():
    """These will all be output a default logging levels."""
    logging.warn("Warning!  Things are getting scary.")
    logging.error("Uh-oh, something is wrong.")
    try:
        raise Exception("ZOMG tacos.")
    except:
        logging.exception("Just like error, but with a traceback.")

if '__main__' == __name__:
    # Late import, in case this project becomes a library, never to be run as main again.
    import optparse

    # Populate our options, -h/--help is already there for you.
    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help="Increase verbosity (specify multiple times for more)")
    # Parse the arguments (defaults to parsing sys.argv).
    opts, args = optp.parse_args()

    # Here would be a good place to check what came in on the command line and
    # call optp.error("Useful message") to exit if all it not well.

    log_level = logging.WARNING # default
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG

    # Set up basic configuration, out to stderr with a reasonable default format.
    logging.basicConfig(level=log_level)

    # Do some actual work.
    foo()
    bar()
