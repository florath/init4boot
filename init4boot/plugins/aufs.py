#
# init4boot aufs plugin
#
# (c) 2010 by flonatel
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licencing details see COPYING
#

from init4boot.lib.FilesystemUtils import fsutils

class aufs(object):

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return fsutils.must_exist(self.__root_dir,
                                  ["usr/sbin", "sbin"], "mount.aufs") 

    def go_SetupDiskDevices(self):

        class SetupDiskDevices:
            def output(self, ofile):
                ofile.write("""
if check_bv "aufs"; then
  logp "Setup aufs devices"
  modprobe aufs
  mkdir -p /aufsro
  mkdir -p /aufsrw
  maybe_break aufs
  aufsroot=${rootmnt}
  rootmnt=/aufsro
  clp_use_std_mount="0"
  logpe
fi
""")
        return SetupDiskDevices()

    def go_MountRoot(self):

        class MountRoot:

            def deps(self):
                return ["Generic", "nfs"]

            def pre_output(self, ofile):
                ofile.write("""
if check_bv "aufs"; then
  logp "Mount aufs root"
  mount -t tmpfs tmpfs /aufsrw
  mount -t aufs -o br:/aufsrw=rw:/aufsro=ro none ${aufsroot}
  chmod 755 ${aufsroot}
  mkdir -p ${aufsroot}/aufsro
  mount --move /aufsro ${aufsroot}/aufsro
  mkdir -p ${aufsroot}/aufsrw
  mount --move /aufsrw ${aufsroot}/aufsrw
  maybe_break aufs_mount
  rootmnt=${aufsroot}
  # Please Do-Not-Ask: the /root must obviously accessed at least once
  # to get everything fine...
  ls ${rootmnt}/* >/dev/null 2>&1
  logpe
fi
""")
        return MountRoot()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy_exec_w_path("mount.aufs", ["usr/sbin", "sbin"])

        return Copy()
