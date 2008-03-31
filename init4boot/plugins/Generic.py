#
# This is the generic part - also implemented as a plugin
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

import time
import os
import shutil
import re

class Generic:

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

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
break="never"
clp_bv=""
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
  log "+ $@"
}
logpe()
{
   echo " " >/dev/null
#  log "- $phasecnt"
}
lognp()
{
  log "+++ Phase ${1} +++"
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
  [ -n "${1}" ] && echo "PANIC: ${1}"
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
  if [ "$FSTYPE" = "unknown" ] && [ -x /lib/udev/vol_id ]; then
    FSTYPE=$(/lib/udev/vol_id -t "${fs}" 2> /dev/null)
  fi
  ret=$?

  if [ -z "${FSTYPE}" ]; then
    FSTYPE="unknown"
  fi
  echo "${FSTYPE}"
  return ${ret}
}
maybe_break()
{
        if [ "${break}" = "$1" ]; then
                panic "Spawning shell within the initramfs (Phase ${break})"
        fi
}
check_bv()
{
    for m in ${clp_bv}; do
	[ "${m}" = "${1}" ] && return 0
    done
    return 1
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
    break=*)
           clp_break=${x#break=}
           ;;
    bv=*)
           clp_bv=`echo ${x#bv=} | tr "," " "`
           ;;
    debug=*)
           clp_debug=`istrue ${x#debug=}`
           ;;
    hostid=*)
           clp_hostid=${x#hostid=}
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
""")

        return CommandLineParsing()

    def go_CommandLineVerbose(self):

        class CommandLineVerbose:
            def pre_output(self, ofile):
                ofile.write("""
[ "${clp_verbose}" = "1" ] && verbose = 1
[ "${clp_debug}" = "1" ] && exec >/tmp/initramfs.debug 2>&1 && set -x
[ -n "${clp_break}" ] && break=${clp_break}
""")
        return CommandLineVerbose()

    def go_InitialSystemSetup(self):

        class InitialSystemSetup:
            def __init__(self, config):
                self.config = config

            def prepare(self, ofile):
                ofile.write("""
lognp InitialSystemSetup
maybe_break InitialSystemSetup
""")

            def pre_output(self, ofile):
                ofile.write("""
[ -d /dev ] || mkdir -m 0755 /dev
[ -d /root ] || mkdir --mode=0700 /root
[ -d /sys ] || mkdir /sys
[ -d /tmp ] || mkdir /tmp
mkdir -p /var/lock
mount -t sysfs -o nodev,noexec,nosuid none /sys 
mount -t tmpfs -o size=10M,mode=0755 udev /dev
[ -e /dev/console ] || mknod /dev/console c 5 1
[ -e /dev/null ] || mknod /dev/null c 1 3
""")

        return InitialSystemSetup(self.config)


    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def prepare(self, ofile):
                ofile.write("""
lognp CommandLineEvaluation
maybe_break CommandLineEvaluation
""")

            def pre_output(self, ofile):
                ofile.write("""
case ${clp_rfs} in
""")

            def post_output(self, ofile):
                ofile.write("""
  *)
    log "Ignoring unknown boot type '${clp_rfs}'"
    ;;
esac
# Append additional (automatic generated) dependencies
clp_bv="${clp_bv} ${bv_deps}"
log "Boot variant(s) (manual plus automatic): '${clp_bv}'"
""")
        return CommandLineEvaluation()

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:
            def pre_output(self, ofile):
                ofile.write("""
depmod -a
""")
                
        return HandleInitialModuleSetup()

    def go_MountRoot(self):

        class MountRoot:
            def pre_output(self, ofile):
                ofile.write("""
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
  echo "ALERT!  ${path} does not exist.  Dropping to a shell!"
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
""")
        return MountRoot()

    def go_CheckForInit(self):

        class CheckForInit:
            def pre_output(self, ofile):
                ofile.write("""
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

# Chain to real filesystem
exec run-init ${rootmnt} ${init} "$@" <${rootmnt}/dev/console >${rootmnt}/dev/console
panic "Could not execute run-init."
""")

        return RunInit()

            
# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:

            def __init__(self, opts):
                self.opts = opts

            # It is not possbile to call the ldd, because the executables
            # might even not executed on the current system.  So the only
            # way to do, is to copy all the libs over.
            def copy_so_libs(self, c):
                c.cpln("lib.*\.so.*", ["lib", "usr/lib", "lib64", ], "lib")

            # Copy the /lib/ld* things
            def copy_ldso(self, c):
                c.cpln("ld.*", ["lib", "lib64"], "lib")

            # Source is in root_dir, dest in tmp dir
            def copy_exec(self, c, source):
                dest = "bin"
                if source[0] == "/":
                    source = source[1:]
                shutil.copy2(os.path.join(c.opts.root_dir, source),
                             os.path.join(c.tmpdir, dest))

            def create_sysdirs(self, c):
                c.log("Creating subdirs")
                # Note: the lib/modules and lib/firmware is automatically
                #       generated when copying these.
                for d in ["bin", "etc"]:
                    dname = os.path.join(c.tmpdir, d)
                    if not os.path.exists(dname):
                        os.makedirs(dname)

            def copy_modules(self, c):
                c.log("Copy modules")
                shutil.copytree(os.path.join(c.opts.root_dir, "lib/modules"),
                                os.path.join(c.tmpdir, "lib/modules"), True)
                c.log("Copy firmware")
                shutil.copytree(os.path.join(c.opts.root_dir, "lib/firmware"),
                                os.path.join(c.tmpdir, "lib/firmware"), True)

            def copy_klibc(self, c):
                c.log("Copy klibc binaries")
                sdir = os.path.join(c.opts.root_dir, "usr/lib/klibc/bin")
                for d in os.listdir(sdir):
                    shutil.copy2(os.path.join(sdir, d),
                                 os.path.join(c.tmpdir, "bin"))

                c.log("Copy klibc libs")
                sdir = os.path.join(c.opts.root_dir, "lib")
                lre = re.compile("klibc-.*\.so")
                for d in os.listdir(sdir):
                    if lre.match(d):
                        shutil.copy2(os.path.join(sdir, d),
                                     os.path.join(c.tmpdir, "lib"))

            def copy_busybox(self, c):
                c.log("Copy busybox")
                self.copy_exec(c, "/bin/busybox")
                os.symlink("/bin/busybox",
                           os.path.join(c.tmpdir, "bin/sh"))
        
            def output(self, c):
                self.create_sysdirs(c)
                self.copy_modules(c)
                # Not sure about the klib things:
                #  The problem is, that there are some programs that are
                #  needed (e.g. run-init, fstype, ipconfig) that are
                #  needed and not available with the some libc.
                self.copy_klibc(c)

                mod = __import__("init4boot.lib.CreateInit.InitCreator",
                                 globals(), locals(), "InitCreator")
               
                ci = mod.InitCreator(None, self.opts)
                ci.run(os.path.join(c.tmpdir, "init"))

                self.copy_so_libs(c)
                self.copy_ldso(c)
                self.copy_busybox(c)

                c.log("Copy modutils")
                self.copy_exec(c, "/sbin/modprobe")
                self.copy_exec(c, "/sbin/depmod")
                self.copy_exec(c, "/sbin/rmmod")

                c.log("Creating cpio archive")
                os.system("P=$PWD && cd %s &&  find . | " \
                          "cpio --quiet -o -H newc | gzip >$P/%s"
                          % (c.tmpdir, self.opts.output_file))

        return Copy(self.opts)
    

    
