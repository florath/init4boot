#!/usr/bin/env python
#
# create_initrd.py
# Creates an initrd from a given set of configuration parameters and
# uses the system wide installed eirt modules.
#
# (c) 2008 by flonatel
#
# For licencing details see COPYING
#

from InitWriter import InitWriter
from DataCollector import DataCollector
from Plugins import Plugins

def main():
    dc = DataCollector()
    dc.collect()

    ## XXX DIRTY HACK!
    plugins = Plugins("../create_init/plugins", dc.data)
    plugins.load()
    
    iw = InitWriter(dc.data, plugins.plugins)
    iw.write()

if __name__ == "__main__":
    main()
