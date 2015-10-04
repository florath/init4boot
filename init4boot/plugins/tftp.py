#
# init4boot tftp plugin
#
# Security Waring: All and every data that is transferred unencrypted
# and all and everybody can get all the data from the tftp server.
# NEVER EVER use this to transfer configuration files that contain
# username and / or passwords.
#
# (c) 2008 by flonatel (sf@flonatel.org)
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licencing details see COPYING
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class tftp:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return True

    def go_CommandLineParsing(self):

        class CommandLineParsing:

            def output(self, ofile):
                ofile.write("""
    tftp=*)
      clp_tftp=${x#tftp=}
      ;;
""")
        return CommandLineParsing()

    
    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:
            def cleanup(self, ofile):
                ofile.write("""
if check_bv "tftp"; then
  log "Network boot variant is needed for tftp"
  bv_deps="${bv_deps} network"
fi
""")
        return CommandLineEvaluation()


    def go_SetupLowLevelTransport(self):

        class SetupLowLevelTransport:
            def cleanup(self, ofile):
                ofile.write("""
if check_bv "tftp"; then
   logp "Setting up tftp"
   maybe_break tftp

   for server in `echo ${clp_tftp} | tr "," " "`; do
     tftp -g -r ${clp_hostid}.tar -l /tftp.tar ${server}
     [ $? -eq 0 ] && break
   done
       
   if [ -f /tftp.tar ]; then
      log "Extracting archive"
      tar -xf /tftp.tar
      if [ -x /tftp.sh ]; then
        log "Sourcing /tftp.sh script"
        . /tftp.sh
        log "Finished sourcing"
      fi
   fi
   logpe
fi
""")
        return SetupLowLevelTransport()
   
# ======================================================================
# === Create hooks

    def mi_Copy(self):

        # tar and atftp is needed
        class Copy:
            def output(self, c):
# Use busybox instead
#                c.copy_exec("usr/bin/atftp")
                c.copy_exec("bin/tar")

                c.copytree(os.path.join(c.opts.root_dir, "lib"),
                           os.path.join(c.tmpdir, "lib"), "libnss_.*")

                etcdir = os.path.join(c.tmpdir, "etc")
                if not os.path.exists(etcdir):
                    os.makedirs(etcdir)
                f = file(os.path.join(c.tmpdir, "etc/services"), "w")
                f.write("""
tftp            69/udp
""")
                f.close()
                
        return Copy()
