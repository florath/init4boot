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

from init4boot.lib.Plugins import Plugins
from init4boot.lib.MakeInitramfs.MIPhases import MIPhases

class HandlePlugins:

    def __init__(self, opts):
        self.opts = opts
        # Create the directory where everything goes:
        self.tmpdir = tempfile.mkdtemp(prefix = "make_initramfs-")

    def __del__(self):
        # Removing temporary dir
#        self.remove_tmp_dir()
        print "rm -fr %s" % self.tmpdir

    def log(self, m):
        print "*** " + m

    # There is no recursive rm by default in python
    def remove_tmp_dir(self):
        for root, dirs, files in os.walk(self.tmpdir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.tmpdir)

    def cpln(self, filere, dirs, destdir):
        lre = re.compile(filere)
        for direntry in dirs:
            source_dir = os.path.join(self.opts.root_dir, direntry)
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

    def copy(self, source, destdir):
        destpath = os.path.join(self.tmpdir, destdir)
        if not os.path.isdir(destpath):
            os.makedirs(destpath)
        shutil.copy2(os.path.join(self.opts.root_dir, source), destpath)

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

    def create_initramfs(self):
        # Read in all the plugins
        phaseclass = MIPhases()

        plugins = Plugins(phaseclass, self.opts.plugins_dir, None, self.opts)
        plugins.load()
        # All plugins are loaded now, so execute them
        plugins.execute(self)
        
