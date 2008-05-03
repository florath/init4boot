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
        parser.add_option("-o", "--output", dest="output_file",
                          action="store", type="string",
                          help="The file name of the output file")
        parser.add_option("-r", "--root-dir", dest="root_dir",
                          action="store", type="string",
                          help="Specify an (alternative) root dir "
                          + "to get the modules and binaries from")
        parser.add_option("-p", "--plugins", dest="plugins_dir",
                          action="store", type="string",
                          help="The name of the plugin dir. " +
                          "Default: /usr/share/pyshared")

        (self.options, args) = parser.parse_args()

        if self.options.output_file == None:
            print "*** Error: option output is missing"
            sys.exit(1)

        if self.options.root_dir == None:
            print "*** Warning: no root dir specified; using / as root dir"
            self.options.root_dir = ""
            
        if self.options.plugins_dir == None:
            self.options.plugins_dir = "/usr/share/pycentral/init4boot/site-packages"
            
