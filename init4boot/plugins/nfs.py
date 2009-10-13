#
# init4boot nfs plugin
#
# (c) 2009 by flonatel
#
# For licencing details see COPYING
#

class nfs:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    
    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def output(self, ofile):
                ofile.write("""
  nfs:*)
    boot_type="nfs"
    boot_args=${clp_rfs#nfs:}
    bv_deps="${bv_deps} network"
    ;;
""")
        return CommandLineEvaluation()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def output(self, ofile):
                ofile.write("""
if [ "${boot_type}" = "nfs" ]; then
  logp "Setting up NFS"
  modprobe -q nfs
  readonly="false"
  eval ${boot_args}
  clp_readonly=`istrue ${readonly}`
  maybe_break nfs
  nfs_roflag="-o rw"
  [ ${clp_readonly} = "1" ] && nfs_roflag="-o ro"
  clp_use_std_mount="0"
  logpe
fi
""")
        return SetupHighLevelTransport()

    def go_MountRoot(self):

        class MountRoot:
            def pre_output(self, ofile):
                ofile.write("""
if [ "${boot_type}" = "nfs" ]; then
  logp "Mounting NFS root"
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
