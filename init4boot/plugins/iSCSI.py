#
# init4boot iSCSI plugin
#
# (c) 2008,2010 by flonatel
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licencing details see COPYING
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class iSCSI(object):

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return fsutils.must_exist(self.__root_dir,
                                  ["usr/sbin", "sbin"], "iscsid") \
            and fsutils.must_exist(self.__root_dir,
                                   ["usr/sbin", "sbin", "usr/bin"], "iscsiadm")

    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def output(self, ofile):
                ofile.write("""
  iscsi:*)
    bv_deps="${bv_deps} network iscsi"
    ;;
""")
        return CommandLineEvaluation()


    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                ofile.write("""
if check_bv "iscsi"; then
  logp "Handling iSCSI"
  modprobe sd_mod
  modprobe iscsi_tcp
fi
""")
        return HandleInitialModuleSetup()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def output(self, ofile):
                ofile.write("""
iscsi:*)
  logp "Starting up iSCSI"
  eval ${boot_args}
  maybe_break iscsi

  log "Starting iscsid"
  mkdir -p /etc/iscsi
  echo "InitiatorName=$localiqn" >/etc/iscsi/initiatorname.iscsi

  cat >/etc/iscsi/iscsid.conf <<EOF
node.startup = manual
EOF

  clp_usechap=`istrue ${usechap}`
  if [ ${clp_usechap} -eq "1" ]; then
    cat >>/etc/iscsi/iscsid.conf <<EOF
node.session.auth.authmethod = CHAP
EOF
    if [ -n ${un_out} ]; then
      cat >>/etc/iscsi/iscsid.conf <<EOF
node.session.auth.username = ${un_out}
node.session.auth.password = ${pw_out}
EOF
    fi
    if [ -n ${un_in} ]; then
      cat >>/etc/iscsi/iscsid.conf <<EOF
node.session.auth.username_in = ${un_in}
node.session.auth.password_in = ${pw_in}
EOF
    fi
    if [ -n ${disc_un_out} ]; then
      cat >>/etc/iscsi/iscsid.conf <<EOF
discovery.sendtargets.auth.authmethod = CHAP
discovery.sendtargets.auth.username = ${disc_un_out}
discovery.sendtargets.auth.password = ${disc_pw_out}
EOF
    fi
  fi

  # Start iscsid with -f which logs to stdout / stderr instead of
  # syslog (which is not available at the time of boot).
  /bin/iscsid -d 0 -f >/tmp/iscsid-stdout.log 2>/tmp/iscsid-stderr.log &
  echo $! >/etc/iscsi/iscsid.pid

  if [ -n "${portals}" ]; then
    log "Login to all iSCSI portals"
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
  else
    log "Login to all targets which are marked automatically"
    iscsiadm -m node -L automatic
  fi
  logpe
;;
""")
        return SetupHighLevelTransport()

    def go_PrepareRootDir(self):

        class PrepareRootDir:
            def output(self, ofile):
                ofile.write("""
if [ "${boot_type}" = "iscsi" ]; then
    logp "Postmount iSCSI setup"
    mkdir -p ${rootmnt}/etc/iscsi
    cp -a /etc/iscsi ${rootmnt}/etc
    log "Finished iSCSI setup"
    logpe
fi
""")
        return PrepareRootDir()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy_exec_w_path("iscsid", ["usr/sbin", "sbin"])
                c.copy_exec_w_path("iscsiadm", ["usr/sbin", "sbin", "usr/bin"])

                c.copytree(os.path.join(c.opts.root_dir, "lib"),
                           os.path.join(c.tmpdir, "lib"), "libnss_.*")

                # On fedora /var/lib/iscsi is needed
                vli = os.path.join(c.opts.root_dir, "var/lib/iscsi")
                if os.path.exists(vli):
                    c.copytree(vli, 
                               os.path.join(c.tmpdir, "var/lib/iscsi"), ".*")

                # The password file is needed.
                # (If not, the error
                #   'peeruser_unix: unknown local user with uid 0'
                # occurs.)
                f = file(os.path.join(c.tmpdir, "etc/passwd"), "a")
                f.write("root:x:0:0:root:/root:/bin/bash\n")
                f.close()

                ddir = os.path.join(c.tmpdir, "var/run")
                if not os.path.exists(ddir):
                    os.makedirs(ddir)

        return Copy()
