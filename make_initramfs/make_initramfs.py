#!/usr/bin/env python
#
# make_initramfs
# Creates the initramfs
#
# (c) 2008 by flonatel
#
# For licensing details see COPYING
#
from HandlePlugins import HandlePlugins
from Options import Options

def main():
    opts = Options()
    
    mi = HandlePlugins(opts.options)
    mi.create_initramfs()

if __name__ == "__main__":
    main()
