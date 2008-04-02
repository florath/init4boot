#
# init4boot plugin to handle local disks
#
# (c) 2008 by flonatel
#
# For licencing details see COPYING
#

class local:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def output(self, ofile):
                ofile.write("""
  local:*)
    boot_type="local"
    boot_args=${clp_rfs#local:}
    ;;
""")

            def post_output(self, ofile):
                ofile.write("""
if [ "${boot_type}" = "local" ]; then
  logp "Setting up local"
  eval ${boot_args}
fi
""")

        return CommandLineEvaluation()
  
