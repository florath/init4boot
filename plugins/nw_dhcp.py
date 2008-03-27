#
# init4boot nw_dhcp plugin
#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
#

class nw_dhcp:

    def __init__(self, config):
        self.config = config

    def go_SetupLowLevelTransport(self):

        # XXX Add dep to network

        class SetupLowLevelTransport:

            def output(self, ofile):
                ofile.write("""
     dhcp)
       ipconfig -c dhcp -d ${device}
       ;;
""")
        return SetupLowLevelTransport()
