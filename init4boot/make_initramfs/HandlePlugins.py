#
# (c) 2008-2009 by flonatel
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
from init4boot.lib.BaseLogger import BaseLogger

class HandlePlugins(BaseLogger):

    def __init__(self, opts):
        BaseLogger.__init__(self, "HandlePlugins")
        self.opts = opts
        # Create the directory where everything goes:
        self.tmpdir = tempfile.mkdtemp(prefix = "make_initramfs-")

        self.root_libs = []
        self.root_libs.append(os.path.join(self.opts.root_dir, "usr/lib"))
        self.root_libs.append(os.path.join(self.opts.root_dir, "lib"))

        # Read in all the plugins
        self.__phaseclass = MIPhases()
        self.__plugins = Plugins("HandlePlugins",
                                 self.__phaseclass, self.opts.plugins_dir,
                                 None, self.opts)

    def __del__(self):
        # Removing temporary dir
        self.remove_tmp_dir()
#        print "rm -fr %s" % self.tmpdir

    def log(self, m):
        self.log_info("FIX LOG MSG! [%s]" % m)

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

    def ln(self, source, destdir):
        destpath = os.path.join(self.tmpdir, destdir)
        os.symlink(source, destpath)

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

    def get_realpath_in_chroot(self, filename):
        tsource = filename
        while os.path.islink(tsource):
            res = os.readlink(tsource)
            tsource_orig = tsource
            self.log_error("RRRR %s %s" % (tsource, res))
            if res[0] == "/":
                res = res[1:]
                tsource = os.path.join(self.opts.root_dir, res)
            else:
                tsource = os.path.join(os.path.dirname(tsource), res)
            self.log_debug("copy_exec follow link [%s] -> [%s]"
                           % (tsource_orig, tsource))
        return tsource
               
    def copy_exec(self, source_file, ddir="bin"):
        """Source is in root_dir, dest in tmp dir"""
        self.log_debug("copy_exec [%s] -> [%s]" % (source_file, ddir))
        destdir = os.path.join(self.tmpdir, ddir)
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        if source_file[0] == "/":
            source_file = source_file[1:]
        source = os.path.join(self.opts.root_dir, source_file)
        self.log_debug("copy_exec internal [%s] -> [%s]" % (source, destdir))

        # ToDo: Handling link can also be done in the initram to
        #       safe some memory
        # Check for links!
        real_source = self.get_realpath_in_chroot(source)
        
        self.log_debug("copy_exec copy [%s] -> [%s]"
                       % (real_source, os.path.join(destdir,
                                                    os.path.basename(source))))
        shutil.copy2(real_source,
                     os.path.join(destdir, os.path.basename(source)))
        # Get the shared libraries for this
        shared_libs = ldd(source, self.root_libs)
        for lib in shared_libs:
            self.log_debug("Checking for lib [%s]" % lib)
            if not lib.startswith(self.opts.root_dir):
                # Oops: got a lib outside the root
                print("Library [%s] outside the root" % lib)
                sys.exit(1)
            rawdlib = lib[len(self.opts.root_dir):]
            if rawdlib[0]=="/":
                rawdlib = rawdlib[1:]
            self.log_debug("Normalized lib path [%s]" % rawdlib)
                
            destlib = os.path.join(self.tmpdir, rawdlib)

            destdir = os.path.dirname(destlib)
            if not os.path.exists(destdir):
                os.makedirs(destdir)

            real_lib = self.get_realpath_in_chroot(lib)
                
            self.log_debug("copy_exec copy_lib [%s] -> [%s]"
                           % (real_lib, destlib))
            shutil.copy2(real_lib, destlib)

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
        self.log_debug("copy_exec_w_path: source [%s] path [%s]"
                       % (source_file, path))
        if source_file[0] == "/":
            source_file = source_file[1:]
        for p in path:
            spath = os.path.join(self.opts.root_dir, p, source_file)
            if os.path.exists(spath):
                self.copy_exec(os.path.join(p, source_file))
                return
        self.log_error("File '%s' not found in '%s'" % (source_file, path))

    def create_initramfs(self):
        self.log_debug("create_initramfs called")
        self.__plugins.load()
        # All plugins are loaded now, so execute them
        self.__plugins.execute(self)
        
