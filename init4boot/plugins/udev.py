#
# init4boot udev plugin
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

import os

class udev:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                ofile.write("""
if check_bv "udev"; then
  logp "Handling udev"
  echo > /sys/kernel/uevent_helper
  mkdir -p /dev/.udev/db/
  udevd --daemon
  mkdir -p /dev/.udev/queue/ /dev/.udev/rules.d/
  udevadm trigger
  udevadm settle || true
  logpe
fi
""")
        return HandleInitialModuleSetup()

    def go_PrepareRootDir(self):

        class PrepareRootDir:
            def output(self, ofile):
                ofile.write("""
if check_bv "udev"; then
  logp "Prepare root dir udev setup"
  # Stop udevd, we'll miss a few events while we run init, but we catch up
  for proc in /proc/[0-9]*; do
    [ -x $proc/exe ] || continue
    [ "$(readlink $proc/exe)" != /sbin/udevd ] || kill ${proc#/proc/}
  done

  # move the /dev tmpfs to the rootfs
  mount -n -o move /dev $rootmnt/dev

  # create a temporary symlink to the final /dev for other initramfs scripts
  nuke /dev
  ln -s $rootmnt/dev /dev
  logpe
fi
""")
        return PrepareRootDir()


# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.mkdir("lib/udev")
                # From udevhelper and udev
                c.log("Copy hotplug.functions")
                # This only exists on Debian4 (and not on FC9)
                c.copy_if_exists("lib/udev/hotplug.functions", "lib/udev")
                c.log("Copy ide.agent")
                # This only exists on Debian4 (and not on FC9)
                c.copy_if_exists("lib/udev/ide.agent", "lib/udev")
                c.log("Copy *_id progs")
                # Copied files are executables
                c.copy_exec_re(".*_id", "lib/udev", "lib/udev")
                # From udev only
                c.log("Copy udef config files from etc")
                c.copytree("etc/udev", "etc/udev")
                # XXX Not existsing : c.copy("etc/scsi_id.config", "etc")
                # WHY: rm -f $DESTDIR/etc/udev/rules.d/*_cd-aliases-generator.rules
                c.log("Copy used binaries")
                c.copy_exec("sbin/udevd")
                c.copy_exec("sbin/udevadm")

                # Group is needed to not get
                # lookup_group: specified group 'XXX' unknown
                f = file(os.path.join(c.tmpdir, "etc/group"), "a")
                f.write("""
root:x:0:root
tty:x:5:
disk:x:6:root
floppy:x:19:
vcsa:x:69:
uucp:x:14:uucp
kmem:x:9:
lp:x:7:daemon,lp
""")
                f.close()

                f = file(os.path.join(c.tmpdir, "etc/passwd"), "a")
                f.write("""
vcsa:x:69:69:virtual console memory owner:/dev:/sbin/nologin
""")
                f.close()


        return Copy()
