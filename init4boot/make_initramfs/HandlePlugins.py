#
# (c) 2008 by flonatel
#
# For licencing details see COPYING
#
import tempfile
import os
import shutil
import popen2
import re
import sys

from init4boot.lib.ldd import ldd

from init4boot.lib.Plugins import Plugins
from init4boot.lib.MakeInitramfs.MIPhases import MIPhases

class HandlePlugins:

    def __init__(self, opts):
        self.opts = opts
        # Create the directory where everything goes:
        self.tmpdir = tempfile.mkdtemp(prefix = "make_initramfs-")

        self.root_libs = []
        self.root_libs.append(os.path.join(self.opts.root_dir, "usr/lib"))
        self.root_libs.append(os.path.join(self.opts.root_dir, "lib"))

    def __del__(self):
        # Removing temporary dir
        self.remove_tmp_dir()
#        print "rm -fr %s" % self.tmpdir

    def log(self, m):
        print "*** " + m

    # There is no recursive rm by default in python
    def remove_tmp_dir(self):
        for root, dirs, files in os.walk(self.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                fn = os.path.join(root, name)
                if os.path.islink(fn):
                    os.remove(fn)
                else:
                    os.rmdir(fn)
        os.rmdir(self.tmpdir)

    def cpln(self, filere, dirs, destdir):
        lre = re.compile(filere)
        for direntry in dirs:
            source_dir = os.path.join(self.opts.root_dir, direntry)
            if not os.path.isdir(source_dir):
                continue
            dest_dir = os.path.join(self.tmpdir, direntry)
            # When link -> link
            if os.path.islink(source_dir) and not os.path.exists(dest_dir):
                linkto = os.readlink(source_dir)
                os.symlink(linkto, dest_dir)
                continue

            # When file -> copy
            for d in os.listdir(source_dir):
                if lre.match(d):
                    fp_src = os.path.join(source_dir, d)
                    fp_dest = os.path.join(self.tmpdir, destdir, d)
                    if os.path.islink(fp_src):
                        linkto = os.readlink(fp_src)
                        try:
                            os.symlink(linkto, fp_dest)
                        except:
                            pass
                    else:
                        shutil.copy2(fp_src, fp_dest)

    def mkdir(self, destdir):
        destpath = os.path.join(self.tmpdir, destdir)
        if not os.path.isdir(destpath):
            os.makedirs(destpath)

    def copy(self, source, destdir):
        destpath = os.path.join(self.tmpdir, destdir)
        if not os.path.isdir(destpath):
            os.makedirs(destpath)
        shutil.copy2(os.path.join(self.opts.root_dir, source), destpath)

    # Some files are only available on some distributions
    def copy_if_exists(self, source, destdir):
        sourcepath = os.path.join(self.opts.root_dir, source)
        if os.path.exists(sourcepath):
            self.copy(source, destdir)
        else:
            print "+++ Ignoging non-existant file='%s'" % sourcepath

    def copytree(self, src, dst, regexp=".*"):
        fre = re.compile(regexp)
        names = os.listdir(os.path.join(self.opts.root_dir, src))
        dstdir = os.path.join(self.tmpdir, dst)
        if not os.path.exists(dstdir):
            os.makedirs(dstdir)
        for name in names:
            if not fre.match(name):
                continue
            srcname = os.path.join(self.opts.root_dir, src, name)
            dstname = os.path.join(self.tmpdir, dst, name)
            try:
                if os.path.islink(srcname):
                    linkto = os.readlink(srcname)
                    os.symlink(linkto, dstname)
                elif os.path.isdir(srcname):
                    self.copytree(srcname, dstname, regexp)
                else:
                    shutil.copy2(srcname, dstname)
            except (IOError, os.error), why:
                print "Can't copy %s to %s: %s" % \
                      (`srcname`, `dstname`, str(why))    

    # Source is in root_dir, dest in tmp dir
    def copy_exec(self, source_file, ddir="bin"):
        destdir = os.path.join(self.tmpdir, ddir)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        if source_file[0] == "/":
            source_file = source_file[1:]
        source = os.path.join(self.opts.root_dir, source_file)
        shutil.copy2(source, destdir)
        # Get the shared libraries for this
        shared_libs = ldd(source, self.root_libs)
        print "copy_exec %s (shared libs: %s)" % (source, shared_libs)
        for lib in shared_libs:
            if not lib.startswith(self.opts.root_dir):
                # Oops: got a lib outside the root
                print "Library '%s' outside the root - Check the links in the root" % lib
                sys.exit(1)
            rawdlib = lib[len(self.opts.root_dir):]
            if rawdlib[0]=="/":
                rawdlib = rawdlib[1:]
            destlib = os.path.join(self.tmpdir, rawdlib)

            destdir = os.path.dirname(destlib)
            if not os.path.exists(destdir):
                os.makedirs(destdir)
            shutil.copy2(lib, destlib)

    # Copy all executables from one dir - specified by a regexp - to
    # another dir
    def copy_exec_re(self, filere, source_dir, dest_dir):
        lre = re.compile(filere)
        source_path = os.path.join(self.opts.root_dir, source_dir)
        dest_path = os.path.join(self.tmpdir, dest_dir)
        
        for d in os.listdir(source_path):
            if lre.match(d):
                self.copy_exec(os.path.join(source_dir, d), dest_dir)

    def copy_exec_w_path(self, source_file, path):
        if source_file[0] == "/":
            source_file = source_file[1:]
        for p in path:
            spath = os.path.join(self.opts.root_dir, p, source_file)
            if os.path.exists(spath):
                self.copy_exec(spath)
                return
        print "*** File '%s' not found in '%s'" % (source_file, path)

    def create_initramfs(self):
        # Read in all the plugins
        phaseclass = MIPhases()

        plugins = Plugins(phaseclass, self.opts.plugins_dir, None, self.opts)
        plugins.load()
        # All plugins are loaded now, so execute them
        plugins.execute(self)
        
