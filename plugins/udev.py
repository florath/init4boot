#
# init4boot udev plugin
#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
#

class udev:

    def __init__(self, config):
        self.config = config

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                ofile.write("""
if check_bv "udev"; then
  logp "Handling udev"
  echo > /proc/sys/kernel/hotplug
  mkdir -p /dev/.udev/db/
  udevd --daemon
  mkdir -p /dev/.udev/queue/
  udevtrigger
  udevsettle || true
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

  # ignore any failed event because the init script will trigger
  # again all events
  nuke /dev/.udev/queue/

  # Optionally move the real filesystem's /dev to beneath our tmpfs
  if [ -e /etc/udev/udev.conf ]; then
    . /etc/udev/udev.conf
  fi
  if [ -z "$no_static_dev" ]; then
    mkdir -m 0700 -p /dev/.static/
    mkdir /dev/.static/dev/
    mount -n -o bind $rootmnt/dev /dev/.static/dev
  fi

  # Now move it all to the real filesystem
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
                # From udevhelper and udev
                c.log("Copy hotplug.functions")
                c.copy("lib/udev/hotplug.functions", "lib/udev")
                c.log("Copy ide.agent")
                c.copy("lib/udev/ide.agent", "lib/udev")
                c.log("Copy *_id progs")
                c.cpln(".*_id", ["lib/udev", ], "lib/udev")

                # From udev only
                c.log("Copy udef config files from etc")
                c.copytree("etc/udev", "etc/udev")
                # XXX Not existsing : c.copy("etc/scsi_id.config", "etc")
                # WHY: rm -f $DESTDIR/etc/udev/rules.d/*_cd-aliases-generator.rules
                c.log("Copy used binaries")
                c.copy("sbin/udevd", "bin")
                c.copy("sbin/udevtrigger", "bin")
                c.copy("sbin/udevsettle", "bin")

        return Copy()
