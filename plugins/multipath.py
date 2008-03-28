#
# multipath iSCSI plugin
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

import os

class multipath:
    
    def __init__(self, config):
        self.config = config

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            # iSCSI must be done before multipath
            def deps(self):
                return ["iSCSI", ]

            def output(self, ofile):
                ofile.write("""
if check_bv "multipath"; then
  maybe_break multipath
  logp "Handling multipath"

  if [ -e /bin/multipath ]; then

    modprobe dm-multipath
    modprobe dm-emc
    modprobe dm-round-robin

    # Multipath needs in some situations more than one run
    for i in 1 2 3 ; do
      /bin/multipath
      sleep 1
      /bin/multipath -ll
    done

    log "Accessing all disk once to get the state corrected"
    # Note that the following can take about 30 seconds for EACH disk.
    # So the things executed in parallel
    ddpids=""
    for disk in /dev/mapper/*; do
      [ "${disk}" = "/dev/mapper/control" ] && continue
      log "... ${disk}"
      dd if=${disk} of=/dev/null bs=1024 count=1 >/dev/null 2>&1 &
      ddpids="${ddpids} $!"
    done
    log "Waiting for possible multipath switchover to end"
    wait ${ddpids}

    log "Creating block devices for partitions"
    for disk in /dev/mapper/*; do
      [ "${disk}" = "/dev/mapper/control" ] && continue
      log "... ${disk}"
      /bin/kpartx -a ${disk}
    done

  else
    log "Multipath enabled, but binary not available - ignoring multipath"
  fi

  logpe
fi
""")
        return SetupHighLevelTransport()
    
    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:
            def cleanup(self, ofile):
                ofile.write("""
if check_bv "multipath" ; then
   clp_bv="${clp_bv} udev"
   log "Adding boot variant udev which is needed for multipath"
fi
""")
        return CommandLineEvaluation()


# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy("sbin/multipath", "bin")
                c.copy("sbin/kpartx", "bin")
                c.copy("sbin/devmap_name", "bin")
                c.copy("sbin/dmsetup", "bin")
                c.copy("lib/udev/dmsetup_env", "lib/udev")
                c.copy("sbin/mpath_prio_alua", "bin")
                c.copy("sbin/mpath_prio_emc", "bin")
                c.copy("sbin/mpath_prio_hp_sw", "bin")
                c.copy("sbin/mpath_prio_rdac", "bin")
                c.copy("sbin/mpath_prio_netapp", "bin")
                c.copy("sbin/mpath_prio_random", "bin")
                c.copy("sbin/mpath_prio_hds_modular", "bin")
                c.copy("sbin/mpath_prio_balance_units", "bin")

        return Copy()
