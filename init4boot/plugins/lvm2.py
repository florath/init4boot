#
# init4boot lvm2 plugin
#
# (c) 2009 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

import os

class lvm2:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts


    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def deps(self):
                return ["multipath", ]

            def output(self, ofile):
                ofile.write("""
if check_bv "lvm2"; then
  logp "Setting up lvm2"
  modprobe -q dm-mod
  modprobe -q dm-snapshot
  modprobe -q dm-mirror
  maybe_break lvm2

  #log "Running lvm2 vgchange"
  ## Split volume group from logical volume.
  #vg=$(echo ${path} | sed -e 's#\(.*\)\([^-]\)-[^-].*#\\1\\2#')
  ## Reduce padded --'s to -'s
  #vg=$(echo ${vg} | sed -e 's#--#-#g')

  #lvm vgchange -aly --ignorelockingfailure ${vg}
  #lvm vgchange -aly --ignorelockingfailure

  lvm2_scan()
  {
    lvm pvscan
    lvm vgscan
    lvm vgchange -aly --ignorelockingfailure
    lvm lvscan
  }
fi

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
