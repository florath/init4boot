#!/usr/bin/env python
#
# make_initramfs
# Creates the initramfs
#
# (c) 2008 by flonatel
#
# For licencing details see COPYING
#
from MakeInitramfs import MakeInitramfs
from Options import Options

def main():
    opts = Options()
    
    mi = MakeInitramfs(opts.options)
    mi.create_initramfs()

if __name__ == "__main__":
    main()
