#
# init4boot lvm2md plugin
#
# (c) 2009 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

#
# This is the upper level of scanning and re-scanning lvm2 and md
# devices.  Nobody knows how often these are stacked.
# So: just try about three times (should be enough for the first)
#

import os

class lvm2md:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts


    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def deps(self):
                return ["lvm2", "md"]

            def output(self, ofile):
                ofile.write("""
if check_bv "md"; then
  if check_bv "lvm2"; then
    logp "Scanning lvm2 and md devices"
    for i in 0 1 2;
    do 
       log "lvm2/md scan round $i"
       lvm2_scan
       md_scan
    done
    log "Finished scanning"
  else
    logp "Only md (without lvm2)"
    md_scan
  fi
else
  if check_bv "lvm2"; then
    logp "Only lvm2 (without md)"
    lvm2_scan
  else
    logp "Neither md not lvm2 will be handled"
  fi
fi

""")
        return SetupHighLevelTransport()

