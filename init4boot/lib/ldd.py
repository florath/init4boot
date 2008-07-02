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
#
# For licensing details see COPYING
#

import re
import sys
import popen2
import os

#
# Returns a full list of all shared libraries that are needed for the
# prog to run.
# The prog itself must be the full path of the program.
#
def ldd_single(prog):
    rlist = []
    needre = re.compile("  NEEDED\s*(\S*).*")
    cout, cin = popen2.popen2("objdump -p %s" % prog)
    for l in cout:
        m = needre.match(l)
        if m:
            rlist.append(m.group(1))
    return rlist

def ldd(prog, libdirs = ["/usr/lib", "/lib"]):
    fileset = set()
    libstodo = set()
    libsdone = set()

    # Look for the program
    liblist = ldd_single(prog)
    libstodo.update(liblist)

    while len(libstodo) > 0:
        e = libstodo.pop()
        if e in libsdone:
            continue
        # Check where to find the lib.
        found_lib = False
        for lib in libdirs:
            fplib = os.path.join(lib, e)
            if os.path.exists(fplib):
                fileset.add(fplib)
                libsdone.add(e)
                liblist = ldd_single(fplib)
                libstodo.update(liblist)
                found_lib = True

        if found_lib == False:
            print "Library '%s' not found" % e
            sys.exit(1)

    return fileset
                

#
# Small test: call 
#  python ldd.py <prog>
# like
#  python ldd.py /bin/ls
#
if __name__=="__main__":
    print ldd_single(sys.argv[1])

    print ldd(sys.argv[1])
