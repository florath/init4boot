#
# ldd
#
# Tries to get all the shared libraries that are needed to run a given
# binary.
# This is done with objdump, because this can be used without running
# the program itself.  (This is not acceptable, because then it is not
# possible to create a initramfs for a different system.  This is also
# the reason, why ldd cannot be used: this called the ld.so with some
# special environment, but the program itself must be able to run on
# the machine.)
#
# (c) 2008 by flonatel (sf@flonatel.org)
# (c) 2015 by Andreas Florath (andreas@florath.net)
#
# For licensing details see COPYING
#

import re
import sys
import popen2
import os
import fnmatch
import logging

logger = logging.getLogger(__name__)

def ldd_single(prog):
    """Returns a full list of all shared libraries that are needed for the
    prog to run.
    The prog itself must be the full path of the program."""

    rset = set()
    needre = re.compile("  NEEDED\s*(\S*).*")
    cout, cin = popen2.popen2("objdump -p %s" % prog)
    for l in cout:
        m = needre.match(l)
        if m:
            rset.add(m.group(1))
    return rset

def find_lib(lib, libdirs):
    """Find a lib in the dirtrees specified by libdirs."""
    result = set()
    for libdir in libdirs:
        for root, dirs, files in os.walk(libdir):
            for name in files:
                if lib == name:
                    result.add(os.path.join(root, name))
    return result

def ldd(prog, libdirs = ["/usr/lib", "/lib"]):
    """Finds all the libraries the given program depends on.
    
    The implementation is not that straight forward, because 
    libraries can depend on other libraries"""

    # This is the set that is returned
    fileset = set()
    # The set of libraries to check
    # (this can be extended when libraries depend on other libraries)
    libstodo = ldd_single(prog)
    # These are already handled
    libsdone = set()

    while len(libstodo) > 0:
        lib = libstodo.pop()
        if lib in libsdone:
            continue
        # Check where to find the lib.
        libpaths = find_lib(lib, libdirs)
        if libpaths == None:
            print("Library '%s' for program '%s' not found" % (e, prog))
            sys.exit(1)
            
        fileset.update(libpaths)
        libsdone.add(lib)

        for nlib in libpaths:
            libstodo.update(ldd_single(nlib))

    return fileset

#
# Small test: call 
#  python ldd.py <prog>
# like
#  python ldd.py /bin/ls
#
if __name__=="__main__":
    logger.debug("Hello")
    print(ldd_single(sys.argv[1]))
    print(ldd(sys.argv[1]))
