#
# init4boot tftp plugin
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licencing details see COPYING
#

import os

class tftp:

    def __init__(self, config):
        self.config = config

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
   for server in `echo ${clp_tftp} | tr "," " "`; do
     atftp --get -r ${clp_hostid}.tar -l /tftp.tar ${server}
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
                c.copy("usr/bin/atftp", "bin")
                c.copy("bin/tar", "bin")

                f = file(os.path.join(c.tmpdir, "etc/services"), "w")
                f.write("""
tftp            69/udp
""")
                f.close()
                
        return Copy()
