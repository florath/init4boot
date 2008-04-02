#
# init4boot iSCSI plugin
#
# (c) 2008 by flonatel
#
# For licencing details see COPYING
#

import os

class iSCSI:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def output(self, ofile):
                ofile.write("""
  iscsi:*)
    boot_type="iscsi"
    boot_args=${clp_rfs#iscsi:}
    bv_deps="${bv_deps} network"
    ;;
""")
        return CommandLineEvaluation()


    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def output(self, ofile):
                ofile.write("""
if [ "${boot_type}" = "iscsi" ]; then
  logp "Setting up iSCSI"
  modprobe -q sd_mod
  modprobe -q iscsi_tcp
  eval ${boot_args}

  log "Starting iscsid"
  mkdir -p /etc/iscsi
  echo "InitiatorName=$localiqn" >/etc/iscsi/initiatorname.iscsi
  # Start iscsid with -f which logs to stdout / stderr instead of
  # syslog (which is not available at this time).
  /bin/iscsid -d 0 -f >/tmp/iscsid-stdout.log 2>/tmp/iscsid-stderr.log &
  echo $! >/etc/iscsi/iscsid.pid

  log "Login at all iSCSI ports"
  one_portal_reached=false
  for portal in `echo ${portals} | tr "," " "` ; do 
    alltargets=`iscsiadm -m discovery -t sendtargets -p ${portal}| tr " " "%"` 
    if [ $? -eq 0 ] ; then 
        log "Discovered iSCSI portal at ${portal} with targets=${alltargets}"
        one_portal_reached=true
        for ats in ${alltargets}; do
            target=${ats#*%*}
            port=${ats%*%*}
            log "Login into port ${port} at target ${target}"
            iscsiadm -m node -T $target -p $port -l
        done
    fi 
  done
  if [ "false" = "${one_portal_reached}" ]; then
        panic "No iSCSI portal reachable"
  fi
  logpe
fi
""")
        return SetupHighLevelTransport()


    def go_PrepareRootDir(self):

        class PrepareRootDir:
            def output(self, ofile):
                ofile.write("""
logp "Postmount iSCSI setup"
mkdir -p ${rootmnt}/etc/iscsi
cp -a /etc/iscsi ${rootmnt}/etc
logpe
""")
        return PrepareRootDir()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy_exec("usr/sbin/iscsid")
                c.copy_exec("usr/bin/iscsiadm")

                c.copytree(os.path.join(c.opts.root_dir, "lib"),
                           os.path.join(c.tmpdir, "lib"), "libnss_.*")

                # The password file is needed.
                # (If not, the error
                #   'peeruser_unix: unknown local user with uid 0'
                # occurs.)
                f = file(os.path.join(c.tmpdir, "etc/passwd"), "w")
                f.write("root:x:0:0:root:/root:/bin/bash\n")
                f.close()

        return Copy()
