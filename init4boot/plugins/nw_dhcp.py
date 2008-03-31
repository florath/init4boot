#
# init4boot nw_dhcp plugin
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

class nw_dhcp:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def go_SetupLowLevelTransport(self):

        class SetupLowLevelTransport:

            def output(self, ofile):
                ofile.write("""
     dhcp)
       ipconfig -c dhcp -d ${device}
       ;;
""")
        return SetupLowLevelTransport()
