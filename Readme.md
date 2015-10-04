# init4boot
python based initramfs creator that supports NFS, iSCSI, LVM

# Introduction
init4boot provides some scripts to generate a generic initramfs for
different system.  It was desined with debootstrap in mind:
alternative implementations like initramfs-tools do - at least - have
some problems with this.

# HowTo
To create an initramfs, call the 'i4b-mkinitramfs' with the options:

-o <initramfs>: the output file name
-r <rootdir>: the root directory from which to take modules, libs and
              binaries.

The rootdir can be an installation done with 'debootstrap' or a copy
of some existing system.  When using a copy of the existing system, the
following directories must be copied over (or must be able to access):

    bin etc lib sbin usr

Note: It is very important, that there must no link to the outer
world, e. g. lib -> /lib64.  In this case the wrong files (from the
build host) will be used.

# Thanks
Some parts of the shell script are taken from the initramfs-tools
implementation that can be found at
http://anonscm.debian.org/cgit/kernel/initramfs-tools.git

