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

import create_init

class MakeInitramfs:

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

    # It is not possbile to call the ldd, because the executables
    # might even not executed on the current system.  So the only
    # way to do, is to copy all the libs over.
    def copy_so_libs(self):
        self.cpln("lib.*\.so.*", ["lib", "usr/lib", "lib64", ], "lib")

    # Copy the /lib/ld* things
    def copy_ldso(self):
        self.cpln("ld.*", ["lib", "lib64"], "lib")

    # Source is in root_dir, dest in tmp dir
    def copy_exec(self, source):
        dest = "bin"
        if source[0] == "/":
            source = source[1:]
        shutil.copy2(os.path.join(self.opts.root_dir, source),
                     os.path.join(self.tmpdir, dest))

    def create_sysdirs(self):
        self.log("Creating subdirs")
        # Note: the lib/modules and lib/firmware is automatically
        #       generated when copying these.
        for d in ["bin", "etc"]:
            os.makedirs(os.path.join(self.tmpdir, d))

    def copy_modules(self):
        self.log("Copy modules")
        shutil.copytree(os.path.join(self.opts.root_dir, "lib/modules"),
                        os.path.join(self.tmpdir, "lib/modules"), True)
        self.log("Copy firmware")
        shutil.copytree(os.path.join(self.opts.root_dir, "lib/firmware"),
                        os.path.join(self.tmpdir, "lib/firmware"), True)

    def copy_klibc(self):
        self.log("Copy klibc binaries")
        sdir = os.path.join(self.opts.root_dir, "usr/lib/klibc/bin")
        for d in os.listdir(sdir):
            shutil.copy2(os.path.join(sdir, d),
                         os.path.join(self.tmpdir, "bin"))

        self.log("Copy klibc libs")
        sdir = os.path.join(self.opts.root_dir, "lib")
        lre = re.compile("klibc-.*\.so")
        for d in os.listdir(sdir):
            if lre.match(d):
                shutil.copy2(os.path.join(sdir, d),
                             os.path.join(self.tmpdir, "lib"))

    def copy_busybox(self):
        self.log("Copy busybox")
        self.copy_exec("/bin/busybox")
        os.symlink("/bin/busybox", os.path.join(self.tmpdir, "bin/sh"))
        
    def create_initramfs(self):
        self.create_sysdirs()
        self.copy_modules()
        # Not sure about the klib things:
        #  The problem is, that there are some programs that are needed
        #  (e.g. run-init, fstype, ipconfig) that are needed and not
        #  available with the some libc.
        self.copy_klibc()

        print "XXXX Create init and copy it to /init"
        create_init.main()
        os.chmod("init", 0766)
        shutil.copy2("init", self.tmpdir)

        self.copy_so_libs()
        self.copy_ldso()
        self.copy_busybox()

        self.log("Copy modutils")
        self.copy_exec("/sbin/modprobe")
        self.copy_exec("/sbin/depmod")
        self.copy_exec("/sbin/rmmod")

        self.log("Creating cpio archive")
        outfile = "initrd.img-" + self.opts.kernel_version
        os.system("P=$PWD && cd %s &&  find . | " \
                  "cpio --quiet -o -H newc | gzip >$P/%s"
                  % (self.tmpdir, outfile))

