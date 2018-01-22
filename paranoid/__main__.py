# Copyright 2018 Max Shinn <max@maxshinnpotential.com>
# 
# This file is part of Paranoid Scientist, and is available under the
# MIT license.  Please see LICENSE.txt in the root directory for more
# information.

import sys
from .testfunctions import test_function

# If called as "python3 -m verify script_file_name.py", then unit test
# script_file_name.py.  By this, we mean call the function
# test_function on each function which has annotations.  Note that we
# must execute the entire file script_file_name.py in order to do
# this, so any time-intensive code should be in a __name__ ==
# "__main__" guard, which will not be executed.
#
# We know if a function has annotations because all annotations are
# passed through the _decorator function (so that we can ensure we
# only use at most one more stack frame no matter how many function
# annotations we have).  The _decorator function will look for the
# global variable __ALL_FUNCTIONS to be defined within the verify
# module.  If it is defined, it will add one copy of each decorated
# function to the list.  Then, we can perform the unit test by
# iterating through each of these.  This has the advantage of allowing
# nested functions and object methods to be discovered for
# verification.
if __name__ == "__main__":
    # Pass exactly one argement: the python file to check
    if len(sys.argv) != 2: # len == 2 because the path to the module is arg 1.
        exit("Invalid argument, please pass a python file")
    # Add the __ALL_FUNCTIONS to the global scope of the verify module
    # and then run the script.  Save the global variables from script
    # execution so that we can find the __ALL_FUNCTIONS variable once
    # the script has finished executing.
    globs = {} # Global variables from script execution
    prefix = "import paranoid as __paranoidmod;__paranoidmod.decorators.__ALL_FUNCTIONS = [];"
    exec(prefix+open(sys.argv[1], "r").read(), globs)
    all_functions = globs["__paranoidmod"].decorators.__ALL_FUNCTIONS
    # Test each function from the script.
    for f in all_functions:
        # Some function executions might take a while, so we print to
        # the screen when we begin testing a function, and then erase
        # it after we finish testing the function.  This is like a
        # make-shift progress bar.
        start_text = "    Testing %s..." % f.__name__
        print(start_text, end="", flush=True)
        ntests = test_function(f)
        # Extra spaces after "Tested %s" compensate for the fact that
        # the string to signal the start of testing function f is
        # longer than the string to signal function f has been tested,
        # so this avoids leaving extra characters on the terminal.
        print("\b"*len(start_text)+"    Tested %i values for %s    " % (ntests, f.__name__), flush=True)
    print("Tested %i functions in %s." % (len(all_functions), sys.argv[1]))

