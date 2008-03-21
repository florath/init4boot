#
# multipath iSCSI plugin
#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
#

class multipath:
    
    def __init__(self, config):
        self.config = config

    # This is a hack because of the current lacking dependency implementation
    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def post_output(self, ofile):
                ofile.write("""
if [ -e /sbin/multipath ]; then
  logp "Handling multipath"

  modprobe dm-multipath
  modprobe dm-emc

  # Multipath needs in some situations more than one run
  for i in 1 2 3 ; do
    /sbin/multipath
    sleep 1
    /sbin/multipath -ll
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
    /sbin/kpartx -a ${disk}
  done

  logpe
fi
""")
        return SetupHighLevelTransport()
    
