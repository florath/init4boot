#
# init4boot nw_dhcp plugin
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

import os

class nw_dhcp:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def go_SetupLowLevelTransport(self):

        class SetupLowLevelTransport:

            def output(self, ofile):
                ofile.write("""
     dhcp)
       # Interface must be enabled (if not this results in: network down)
       ifconfig ${device} up
       udhcpc -i ${device} -q -t 120 -T 1
       ;;
""")
        return SetupLowLevelTransport()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def __init__(self, opts):
                self.opts = opts

            def output(self, c):
                # To get rid of the error:
                # udhcpc: script /usr/share/udhcpc/default.script failed: \
                #    No such file or directory
                os.makedirs(os.path.join(c.tmpdir, "usr/share/udhcpc"))

                filename = os.path.join(c.tmpdir, 
                                        "usr/share/udhcpc/default.script")
                f = file(filename, "w")
                f.write("""#!/bin/sh

# udhcpc script edited by Tim Riker <Tim@Rikers.org>
#               edited by Andreas Florath to adapt for init4boot

[ -z "$1" ] && echo "Error: should be called from udhcpc" && exit 1

RESOLV_CONF="/etc/resolv.conf"
[ -n "$broadcast" ] && BROADCAST="broadcast $broadcast"
[ -n "$subnet" ] && NETMASK="netmask $subnet"

case "$1" in
        deconfig)
                ifconfig $interface 0.0.0.0
                ;;

        renew|bound)
                ifconfig $interface $ip $BROADCAST $NETMASK

                if [ -n "$router" ] ; then
                        echo "deleting routers"
                        while route del default gw 0.0.0.0 dev $interface ; do
                                :
                        done

                        metric=0
                        for i in $router ; do
                                route add default gw $i dev $interface metric $((metric++))
                        done
                fi

                echo -n > $RESOLV_CONF
                [ -n "$domain" ] && echo search $domain >> $RESOLV_CONF
                for i in $dns ; do
                        echo adding dns $i
                        echo nameserver $i >> $RESOLV_CONF
                done
                ;;
esac

exit 0

""")
                f.close()
                # And to get rid of the
                # udhcpc: script /usr/share/udhcpc/default.script failed: \
                #    Permission denied
                os.chmod(filename, 0744)
                
        return Copy(self.opts)
