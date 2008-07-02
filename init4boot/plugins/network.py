#
# init4boot network plugin
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

class network:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def go_SetupLowLevelTransport(self):

        class SetupLowLevelTransport:

            def pre_output(self, ofile):
                ofile.write("""
if check_bv "network"; then
  logp "Handling network"
  maybe_break network

  for nwdev in `echo ${clp_nw} | tr "," " "`; do
    device=${nwdev%:*}
    mepa=${nwdev#*:}

    case ${mepa} in
""")

            def post_output(self, ofile):
                ofile.write("""
      *)
        log "Ignoring unknown network parameter: ${mepa}"
        ;;
    esac
  done
  logpe
fi
""")
        return SetupLowLevelTransport()
