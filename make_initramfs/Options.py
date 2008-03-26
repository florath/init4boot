#
# (c) 2008 by flonatel
#
# For licencing details see COPYING
#
import sys
from optparse import OptionParser

class Options:

    def __init__(self):
        parser = OptionParser()
        parser.add_option("-k", "--kernel-version", dest="kernel_version",
                          action="store", type="string",
                          help="Specify the kernel version")
        parser.add_option("-r", "--root-dir", dest="root_dir",
                          action="store", type="string",
                          help="Specify an (alternative) root dir "
                          + "to get the modules and binaries from")

        (self.options, args) = parser.parse_args()

        print self.options.kernel_version

        if self.options.kernel_version == None:
            print "*** Error: option kernel_version is missing"
            sys.exit(1)

        if self.options.root_dir == None:
            print "*** Warning: no root dir specified; using / as root dir"
            self.options.root_dir = ""
            
