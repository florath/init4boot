#
# init4boot nfs plugin
#
# (c) 2009 by flonatel
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licencing details see COPYING
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class nfs(object):

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return fsutils.must_exist(self.__root_dir, ["usr"],
                                  "lib/klibc/bin/nfsmount")

    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def output(self, ofile):
                ofile.write("""
  nfs:*)
    bv_deps="${bv_deps} network nfs"
    ;;
""")
        return CommandLineEvaluation()

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                ofile.write("""
if check_bv "nfs"; then
  logp "Handling NFS"
  modprobe -q nfs
fi
""")
        return HandleInitialModuleSetup()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def output(self, ofile):
                ofile.write("""
nfs:*)
  logp "Setting up NFS"
  readonly="false"
  eval ${boot_args}
  clp_readonly=`istrue ${readonly}`
  maybe_break nfs
  nfs_roflag="-o rw"
  [ ${clp_readonly} = "1" ] && nfs_roflag="-o ro"
  clp_use_std_mount="0"
  logpe
;;
""")
        return SetupHighLevelTransport()

    def go_MountRoot(self):

        class MountRoot:
            def pre_output(self, ofile):
                ofile.write("""
if [ "${boot_type}" = "nfs" ]; then
  logp "Mounting NFS root"
  maybe_break nfs_mount
  log "Mounting with 'nfsmount -o nolock ${nfs_roflag} ${path} ${rootmnt}'"
  nfsmount -o nolock ${nfs_roflag} ${path} ${rootmnt}
fi
""")
        return MountRoot()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                # For Debian
                if os.path.exists("/usr/lib/klibc/bin/nfsmount"):
                    c.copy_exec("/usr/lib/klibc/bin/nfsmount")

        return Copy()
