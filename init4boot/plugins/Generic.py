#
# This is the generic part - also implemented as a plugin
#
# (c) 2008-2010 by flonatel (sf@flonatel.org)
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

import time
import os
import shutil
import re

from init4boot.lib.BaseLogger import BaseLogger

class Generic(BaseLogger):
    def __init__(self, config, opts):
        BaseLogger.__init__(self, "Generic")
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return True

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
clp_use_std_mount="1"
log()
{
  [ "${verbose}" = "0" ] && return
  d=$(date +"[%Y-%m-%d %H:%M:%S %Z]")
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
  local FS FSTYPE FSSIZE RET
  FS="${1}"
  eval $(fstype "${FS}" 2> /dev/null)

  if [ -z "${FSTYPE}" ]; then
    FSTYPE="unknown"
  fi
  echo "${FSTYPE}"
  return ${RET}
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
nuke()
{
  d=$1
  find $d ! -type d 2>/dev/null | xargs rm -fr -- 
  find $d 2>/dev/null | xargs rm -fr -- 
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
           clp_bv=$(echo ${x#bv=} | tr "," " ")
           ;;
    debug=*)
           clp_debug=$(istrue ${x#debug=})
           ;;
    hostid=*)
           clp_hostid=${x#hostid=}
           ;;
    init=*)
           clp_init=${x#init=}
           ;;
    loadmods=*)
	   clp_loadmods=${x#loadmods=}
	   ;;
    nw=*)
           clp_nw=${x#nw=}
           ;;
    rfs=*)
           clp_rfs=${x#rfs=}
           ;;
    verbose=*)
           clp_verbose=$(istrue ${x#verbose=})
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
[ "${clp_debug}" = "1" ] && exec >/initramfs.debug 2>&1 && set -x
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
mount -t devtmpfs -o size=10M,mode=0755 udev /dev
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
for transform in $(echo ${clp_rfs} | tr ";" " ");
do
case ${transform} in
""")

            def post_output(self, ofile):
                ofile.write("""
  *)
    panic "CommandLineEvaluation: Unknown transformation '${transform}'"
    ;;
esac
done

# Append additional (automatic generated) dependencies
clp_bv="${clp_bv} ${bv_deps}"
log "Boot variant(s) (manual plus automatic): '${clp_bv}'"
""")
        return CommandLineEvaluation()

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def prepare(self, ofile):
                ofile.write("""
lognp HandleInitialModuleSetup
maybe_break HandleInitialModuleSetup
""")

            def pre_output(self, ofile):
                ofile.write("""
depmod -a
for mod in $(echo ${clp_loadmods} | tr "," " ");
do
    log "Pre-loading module '${mod}'"
    modprobe $mod
done
""")
                
        return HandleInitialModuleSetup()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:
            def pre_output(self, ofile):
                ofile.write("""
for transform in $(echo ${clp_rfs} | tr ";" " ");
do
case ${transform} in
""")
            def post_output(self, ofile):
                ofile.write("""
  *)
    log "SetupHighLevelTransport: Ignoring unknown transformation '${transform}'"
    ;;
esac
done
""")    
        return SetupHighLevelTransport()

    def go_MountRoot(self):

        class MountRoot:
            def pre_output(self, ofile):
                ofile.write("""
if [ ${clp_use_std_mount} = "1" ]; then
  # If the root device hasn't shown up yet, give it a little while
  # to deal with removable devices
  if [ ! -e "${path}" ] || ! $(get_fstype "${path}" >/dev/null); then
    log "Waiting for root file system..."
    maybe_break wait_for_root

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

  # FIXME This has no error checking (Might be even compiled in kernel)
  modprobe ${fstype} >/dev/null 2>&1

  # FIXME This has no error checking
  # Mount root
  mount ${roflag} -t ${fstype} ${clp_rootflags} ${path} ${rootmnt}
fi
""")
        return MountRoot()

    def go_CheckForInit(self):

        class CheckForInit:
            def pre_output(self, ofile):
                ofile.write("""
# Move virtual filesystems over to the real filesystem
log "Move-Mount /sys"
mount -n -o move /sys ${rootmnt}/sys
log "Move-Mount /proc"
mount -n -o move /proc ${rootmnt}/proc
log "Move-Mount finished"

# Check init bootarg
if [ -n "${init}" ] && [ ! -x "${rootmnt}${init}" ]; then
        echo "Target filesystem does not have ${init}."
        init=
fi

# Search for valid init
if [ -z "${init}" ] ; then
        for init in /lib/systemd/systemd /sbin/init /etc/init /bin/init /bin/sh; do
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
maybe_break run_init
log "Running run-init"
exec run-init ${rootmnt} ${init} -v "$@" <${rootmnt}/dev/console >${rootmnt}/dev/console
panic "Could not execute run-init."
""")

        return RunInit()

            
# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy(BaseLogger):

            def __init__(self, opts):
                BaseLogger.__init__(self, "Copy")
                self.opts = opts
                
            def create_sysdirs(self, c):
                self.log_info("Creating subdirs")
                # Note: the lib/modules and lib/firmware is automatically
                #       generated when copying these.
                for d in ["bin", "etc"]:
                    dname = os.path.join(c.tmpdir, d)
                    if not os.path.exists(dname):
                        os.makedirs(dname)

            def copy_modules(self, c):
                self.log_info("Copy modules")
                shutil.copytree(os.path.join(c.opts.root_dir, "lib/modules"),
                                os.path.join(c.tmpdir, "lib/modules"), True)
                self.log_info("Copy firmware")
                shutil.copytree(os.path.join(c.opts.root_dir, "lib/firmware"),
                                os.path.join(c.tmpdir, "lib/firmware"), True)

            def remove_file(self, name, dir):
                for file in os.listdir(dir):
                    fullpath = os.path.join(dir, file)
                    if name == file and os.path.isfile(fullpath):
                        print "Deleting file '%s'" % fullpath
                        os.remove(fullpath)
                    elif os.path.isdir(fullpath):
                        self.remove_file(name, fullpath)

            def remove_modules(self, c, bname):
                self.log_info("Remove some modules")
                self.remove_file(bname + ".ko", os.path.join(c.tmpdir,
                                                             "lib/modules")) 

            # This is only needed for the Fedora way of busybox
            # (and it does no harm under Debian)
            def make_busybox_links(self, c):
                for p in [
                    "cat", 
                    "cp",
                    "date",
                    "find", 
                    "ifconfig", 
                    "ln", 
                    "mkdir", 
                    "mknod", 
                    "mount", 
                    "readlink",
                    "rm",
                    "route", 
                    "tftp", 
                    "tr", 
                    "udhcpc", 
                    "xargs"
                    ]:
                    dest = os.path.join(c.tmpdir, "bin", p)
                    os.symlink("/bin/busybox", dest)

            def copy_busybox(self, c):
                self.log_info("Copy busybox")
                c.copy_exec_w_path("busybox", ["bin", "sbin"])
                dest = os.path.join(c.tmpdir, "bin/sh")
                destdir = os.path.dirname(dest)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                os.symlink("/bin/busybox", dest)
                self.make_busybox_links(c)

            def get_klibc_name(self):
                self.log_debug("get_klibc_name [%s]" % self.opts.root_dir)
                files = os.listdir(os.path.join(self.opts.root_dir, "lib"))
                for f in files:
                    if f.startswith("klibc-"):
                        self.log_debug("Found klibc [%s]" % f)
                        return os.path.join(self.opts.root_dir, "lib/" + f)
                return None
        
            def output(self, c):
                self.create_sysdirs(c)
                self.copy_modules(c)
                # These modules must not be loaded at this time
                # HACK! maybe: move in own plugin and toggle with nonvidia.
                # maybe: insert during init4boot time to blacklist?
                self.remove_modules(c, "nvidiafb")

                mod = __import__("init4boot.lib.CreateInit.InitCreator",
                                 globals(), locals(), "InitCreator")
               
                ci = mod.InitCreator(None, self.opts)
                ci.run(os.path.join(c.tmpdir, "init"))

                self.copy_busybox(c)
                c.copy_exec("/bin/sleep")

                self.log_info("Copy modutils")
                c.copy_exec("/sbin/modprobe")
                c.copy_exec("/sbin/depmod")
                c.copy_exec("/sbin/rmmod")

                # Only for debugging
                #c.copy_exec("/usr/bin/strace")
                #c.copy_exec("/usr/bin/nc")

                # HACK!
                # XXX I think, this was needed for Fedora
                if os.path.exists("/tmp/run-init"):
                    c.copy_exec("/tmp/run-init")

                # For Debian / Ubuntu
                copy_klibc = False
                if os.path.exists("/usr/lib/klibc/bin/run-init"):
                    c.copy_exec("/usr/lib/klibc/bin/run-init")
                    copy_klibc = True
                if os.path.exists("/usr/lib/klibc/bin/fstype"):
                    c.copy_exec("/usr/lib/klibc/bin/fstype")
                    copy_klibc = True

                if copy_klibc:
                    # Have a look for the full pathname of the klibc
                    # (which changes from release to release and from
                    # architecture to architecture).
                    klibcname = self.get_klibc_name()
                    if klibcname:
                        c.copy(klibcname, "lib")

                # HACK!
                os.symlink("/lib", os.path.join(c.tmpdir, "lib64"))

                os.symlink("/bin", os.path.join(c.tmpdir, "sbin"))

        return Copy(self.opts)
    
    def mi_Create(self):

        class Create(BaseLogger):

            def __init__(self, opts):
                BaseLogger.__init__(self, "Generic-Create")
                self.opts = opts

            def output(self, c):
                self.log_info("Creating cpio archive")
                os.system("cd %s &&  find . | " \
                          "cpio --quiet -o -H newc | gzip >%s"
                          % (c.tmpdir, self.opts.output_file))

        return Create(self.opts)
