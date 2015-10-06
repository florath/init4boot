#
# init4boot lvm2 plugin
#
# (c) 2009 by flonatel (sf@flonatel.org)
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class lvm2(object):
    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return fsutils.must_exist(self.__root_dir, ["sbin"], "lvm")

    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def output(self, ofile):
                ofile.write("""
  lvm:*)
    bv_deps="${bv_deps} lvm"
    ;;
""")
        return CommandLineEvaluation()

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                ofile.write("""
if check_bv "lvm"; then
  logp "Handling LVM"
  modprobe dm-mod
  modprobe dm-snapshot
  modprobe dm-mirror
fi
""")
        return HandleInitialModuleSetup()

  #log "Running lvm2 vgchange"
  ## Split volume group from logical volume.
  #vg=$(echo ${path} | sed -e 's#\(.*\)\([^-]\)-[^-].*#\\1\\2#')
  ## Reduce padded --'s to -'s
  #vg=$(echo ${vg} | sed -e 's#--#-#g')

  #lvm vgchange -aly --ignorelockingfailure ${vg}
  #lvm vgchange -aly --ignorelockingfailure

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def output(self, ofile):
                ofile.write("""
lvm:*)
  logp "Setting up lvm2"
  maybe_break lvm2
  params=$(echo ${transform#lvm:} | tr "," " ")
  if test ${params} = "scan"; then
    lvm pvscan
    lvm vgscan
    lvm vgchange -aly --ignorelockingfailure
    lvm lvscan
  fi
  ;;
""")
        return SetupHighLevelTransport()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.mkdir("etc/lvm")
                c.log("Copy configuration")
                c.copy("etc/lvm/lvm.conf", "etc/lvm")
                c.log("Copy executable lvm")
                c.copy_exec("sbin/lvm")
                #c.ln("sbin/vgchange", "sbin/lvm")
                c.copy_exec("bin/sed")
        return Copy()
