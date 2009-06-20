#
# init4boot md plugin
#
# (c) 2009 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

import os

class md:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts


    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def deps(self):
                return ["multipath", "lvm2"]

            def output(self, ofile):
                ofile.write("""
if check_bv "md"; then
  logp "Setting up md"
  log "Loading md modules"
  MD_MODULES="linear multipath raid0 raid1 raid456 raid10"
  for m in ${MD_MODULES};
  do
    modprobe -q $m
  done
  maybe_break md

  if [ ! -f /proc/mdstat ]; then
    panic "Cannot initialise md subsystem (/proc/mdstat missing)"
    exit 1
  fi

  log "Trying to create mdadm config file"
  CONFIG=/etc/mdadm/mdadm.conf
  mkdir -p ${CONFIG%/*}
  echo DEVICE partitions > $CONFIG

  # prevent writes/syncs so that resuming works (#415441).
  echo 1 > /sys/module/md_mod/parameters/start_ro

  md_scan()
  {
    mdadm --examine --scan >> $CONFIG
    log "Assembling all md arrays"

    if mdadm --assemble --scan --run --auto=yes $extra_args; then
      log "assembled all arrays."
    else
      log "failed to assemble all arrays."
    fi

    if [ -x "$(command -v udevsettle)" ]; then
      log "Waiting for udev to process events"
      udevsettle 10
    fi
  }
fi

""")
        return SetupHighLevelTransport()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy_exec("sbin/mdadm")

        return Copy()
