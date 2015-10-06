#
# init4boot md plugin
#
# (c) 2009 by flonatel (sf@flonatel.org)
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class md(object):
    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir
        
    def check(self):
        return fsutils.must_exist(self.__root_dir, ["sbin"], "mdadm")

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                ofile.write("""
if check_bv "md"; then
  logp "Handling md"
  log "Loading md modules"
  MD_MODULES="linear multipath raid0 raid1 raid456 raid10"
  for m in ${MD_MODULES};
  do
    modprobe -q $m
  done

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
fi
""")
        return HandleInitialModuleSetup()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def deps(self):
                return []

            def output(self, ofile):
                ofile.write("""
md:*)
  logp "Setting up md"
  maybe_break md
  panic "TODO: use lvm2md.py"

  #md_scan()
  #{
  #  mdadm --examine --scan >> $CONFIG
  #  log "Assembling all md arrays"
  #
  #  if mdadm --assemble --scan --run --auto=yes $extra_args; then
  #    log "assembled all arrays."
  #  else
  #    log "failed to assemble all arrays."
  #  fi
  #
  #  if [ -x "$(command -v udevsettle)" ]; then
  #    log "Waiting for udev to process events"
  #    udevsettle 10
  #  fi
  #}
;;

""")
        return SetupHighLevelTransport()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy_exec("sbin/mdadm")

        return Copy()
