#
# multipath iSCSI plugin
#
# (c) 2008-2009 by flonatel (sf@flonatel.org)
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class multipath(object):
    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return fsutils.must_exist(self.__root_dir, ["sbin"], "multipath") \
            and fsutils.must_exist(self.__root_dir, ["sbin"], "kpartx")

    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:
            def output(self, ofile):
                ofile.write("""
  multipath:*)
    bv_deps="${bv_deps} network multipath"
    ;;
""")
        return CommandLineEvaluation()

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                ofile.write("""
if check_bv "multipath"; then
  logp "Handling multipath"
  modprobe dm-multipath
  modprobe dm-emc
  modprobe dm-round-robin
fi
""")
        return HandleInitialModuleSetup()
    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            # iSCSI must be done before multipath
            def deps(self):
                return ["iSCSI", ]

            def output(self, ofile):
                ofile.write("""
multipath:*)
  maybe_break multipath
  logp "Handling multipath"

  if [ -e /bin/multipath ]; then

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
;;                
""")
        return SetupHighLevelTransport()
    


# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy_exec("sbin/multipath")
                c.copy_exec("sbin/kpartx")
                c.copy_exec_w_path("devmap_name", ["sbin", ])
                c.copy_exec_w_path("dmsetup", ["sbin", ])
                # Not available in Debian stable
                # (Part of kpartx package which is only available in unstable)
                #                c.copy("lib/udev/dmsetup_env", "lib/udev")

                # Copy all the dependend multipath so libs
                c.copytree("lib/multipath", "lib/multipath")

        return Copy()
