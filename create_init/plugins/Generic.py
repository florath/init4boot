#
# This is the generic part - also implemented as a plugin
#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
#

import time

class Generic:

    def __init__(self, config):
        self.config = config

    def go_Intro(self):

        class Intro:

            def pre_output(self, ofile):
                ofile.write("""#!/bin/sh
#
# *** AUTOMATICALLY GENERATED SCRIPT: DO NOT EDIT! ***
#
# This script was created by init4boot on %s
#
""" % time.ctime())

        return Intro()


    def go_FunctionDefinition(self):

        class FunctionDefinition:

            def pre_output(self, ofile):
                ofile.write("""
verbose=1
log()
{
  [ "${verbose}" = "0" ] && return
  d=`date +"[%Y-%m-%d %H:%M:%S %Z]"`
  echo ${d} init4boot "$@"
}
phasecnt=0
logp()
{
  phasecnt=$((${phasecnt} + 1))
  log "+++ Phase $phasecnt start +++ $@"
}
logpe()
{
  log "+++ Phase $phasecnt end   +++"
}
istrue()
{
  [ "${1}" = "y" ] && echo "1"
  [ "${1}" = "yes" ] && echo "1"
  [ "${1}" = "true" ] && echo "1"
  [ "${1}" = "on" ] && echo "1"
  [ "${1}" = "1" ] && echo "1"
  return "0"
}
panic()
{
  PS1='(initramfs) ' /bin/sh -i </dev/console >/dev/console 2>&1
}
# Parameter: device node to check
# Echos fstype to stdout
# Return value: indicates if an fs could be recognized
get_fstype ()
{
  local fs fstype fssize ret
  fs="${1}"
  # vol_id has a more complete list of file systems,
  # but fstype is more robust
  eval $(fstype "${fs}" 2> /dev/null)
  if [ "$fstype" = "unknown" ] && [ -x /lib/udev/vol_id ]; then
    fstype=$(/lib/udev/vol_id -t "${fs}" 2> /dev/null)
  fi
  ret=$?

  if [ -z "${fstype}" ]; then
    fstype="unknown"
  fi
  echo "${fstype}"
  return ${ret}
}

# Global variables
rootmnt=/root
""")

        return FunctionDefinition()
        

    def go_CommandLineParsing(self):

        class CommandLineParsing:

            def pre_output(self, ofile):
                ofile.write("""
log "Starting up system from initramfs."
[ -d /proc ] || mkdir /proc
mount -t proc -o nodev,noexec,nosuid none /proc
for x in $(cat /proc/cmdline); do
  case ${x} in
    debug=*)
           clp_debug=`istrue ${x#debug=}`
           ;;
    init=*)
           clp_init=${x#init=}
           ;;
    nw=*)
           clp_nw=${x#nw=}
           ;;
    rfs=*)
           clp_rfs=${x#rfs=}
           ;;
    verbose=*)
           clp_verbose=`istrue ${x#verbose=}`
           ;;
""")
                
            def post_output(self, ofile):
                ofile.write("""
    # The following parameters are known to exists and
    # they are evaluated during kernel startup.
    console=*)
           ;;
    *)
           log "Ignoring unknown command line parameter '${x}'"
           ;;
  esac
done
logpe
""")

        return CommandLineParsing()

    def go_CommandLineVerbose(self):

        class CommandLineVerbose:
            def pre_output(self, ofile):
                ofile.write("""
[ "${clp_verbose}" = "1" ] && verbose = 1
[ "${clp_debug}" = "1" ] && exec >/tmp/initramfs.debug 2>&1 && set -x
""")
        return CommandLineVerbose()

    def go_InitialSystemSetup(self):

        class InitialSystemSetup:
            def __init__(self, config):
                self.config = config
            
            def pre_output(self, ofile):
                ofile.write("""
logp "Setting up system devs for boot"

[ -d /dev ] || mkdir -m 0755 /dev
[ -d /root ] || mkdir --mode=0700 /root
[ -d /sys ] || mkdir /sys
[ -d /tmp ] || mkdir /tmp
mkdir -p /var/lock
mount -t sysfs -o nodev,noexec,nosuid none /sys 
mount -t tmpfs -o size=%s,mode=0755 udev /dev
[ -e /dev/console ] || mknod /dev/console c 5 1
[ -e /dev/null ] || mknod /dev/null c 1 3
logpe
""" % self.config["tmpfs_size"])

        return InitialSystemSetup(self.config)


    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:
            def pre_output(self, ofile):
                ofile.write("""
logp "Evaluating command line options"
case ${clp_rfs} in
""")

            def post_output(self, ofile):
                ofile.write("""
  *)
    log "Ignoring unknown boot type '${clp_rfs}'"
    ;;
esac
logpe
""")
        return CommandLineEvaluation()

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:
            def pre_output(self, ofile):
                ofile.write("""
logp "Handling Modules"
depmod -a
logpe
""")
                
        return HandleInitialModuleSetup()

    def go_MountRoot(self):

        class MountRoot:
            def pre_output(self, ofile):
                ofile.write("""
logp "Mounting root file system"
# If the root device hasn't shown up yet, give it a little while
# to deal with removable devices
if [ ! -e "${path}" ] || ! $(get_fstype "${path}" >/dev/null); then
  log "Waiting for root file system..."

  # Default delay is 180s
  if [ -z "${clp_rootdelay}" ]; then
    slumber=180
  else
    slumber=${clp_rootdelay}
  fi
  if [ -x /sbin/usplash_write ]; then
    /sbin/usplash_write "TIMEOUT ${slumber}" || true
  fi

  slumber=$(( ${slumber} * 10 ))
  while [ ! -e "${path}" ] \
          || ! $(get_fstype "${path}" >/dev/null); do
    /bin/sleep 0.1
    slumber=$(( ${slumber} - 1 ))
    [ ${slumber} -gt 0 ] || break
  done

  if [ -x /sbin/usplash_write ]; then
    /sbin/usplash_write "TIMEOUT 15" || true
  fi
fi

# We've given up, but we'll let the user fix matters if they can
while [ ! -e "${path}" ]; do
  echo "ALERT!  ${pathT} does not exist.  Dropping to a shell!"
  echo "  Check your root= boot argument (cat /proc/cmdline)"
  panic " Check for missing modules (cat /proc/modules), or device files (ls /dev)"
done

# Get the root filesystem type if not set
if [ -z "${clp_rootfstype}" ]; then
  fstype=$(get_fstype "${path}")
else
  fstype=${clp_rootfstype}
fi

if [ "${clp_readonly}" = "y" ]; then
  roflag=-r
else
  roflag=-w
fi

# FIXME This has no error checking
modprobe ${fstype}

# FIXME This has no error checking
# Mount root
mount ${roflag} -t ${fstype} ${clp_rootflags} ${path} ${rootmnt}
logpe
""")
        return MountRoot()

    def go_CheckForInit(self):

        class CheckForInit:
            def pre_output(self, ofile):
                ofile.write("""
logp "Post mount setup"
# Move virtual filesystems over to the real filesystem
mount -n -o move /sys ${rootmnt}/sys
mount -n -o move /proc ${rootmnt}/proc

# Check init bootarg
if [ -n "${init}" ] && [ ! -x "${rootmnt}${init}" ]; then
        echo "Target filesystem does not have ${init}."
        init=
fi

# Search for valid init
if [ -z "${init}" ] ; then
        for init in /sbin/init /etc/init /bin/init /bin/sh; do
                if [ ! -x "${rootmnt}${init}" ]; then
                        continue
                fi
                break
        done
fi

# No init on rootmount
if [ ! -x "${rootmnt}${init}" ]; then
        panic "No init found. Try passing init= bootarg."
fi
""")
        return CheckForInit()

    def go_RunInit(self):

        class RunInit:
            def pre_output(self, ofile):
                ofile.write("""
# Confuses /etc/init.d/rc
if [ -n ${debug} ]; then
        unset debug
fi

logpe
# Chain to real filesystem
exec run-init ${rootmnt} ${init} "$@" <${rootmnt}/dev/console >${rootmnt}/dev/console
panic "Could not execute run-init."
""")

        return RunInit()
