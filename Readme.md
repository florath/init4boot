# init4boot
python based initramfs creator that supports NFS, iSCSI, LVM

# Introduction
init4boot provides some scripts to generate a generic initramfs for
different system.  It was desined with debootstrap in mind:
alternative implementations like initramfs-tools do - at least - have
some problems with this.

# Features & Differences to other implementations
There are some features which make init4boot unique.  Other
implementations handle this in a different way.

## Features
* *There is only one initrd.*  One init4boot initrd can be used to boot
  **all**.  There is no need for creating new initrds for each system.
* *Full debootstrap support.*  init4boot does not make any assumptions
  about the host or target system.
* *Complete control.*  No assumptions, no heuristics what is or can in
  the host / target system.  Everything can be specified on the
  command line or via an tftp server.

## Drawbacks
* Because everything is in 'the' initrd, it's big.  Booting takes
  longer. 

# HowTo
To create an initramfs, call the 'i4b-mkinitramfs' with the options:

* -o <initramfs>: the output file name
* -r <rootdir>: the root directory from which to take modules, libs and
  binaries.

The rootdir can be an installation done with 'debootstrap' or a copy
of some existing system.  When using a copy of the existing system, the
following directories must be copied over (or must be able to access):

    bin etc lib sbin usr

Note: It is very important, that there must no link to the outer
world, e. g. lib -> /lib64.  In this case the wrong files (from the
build host) will be used.

# Known to Run
This is a list of all systems where init4boot is known to work:
* Debian Jessie armhl on Raspberry Pi 2 with u-boot

# Thanks
Some ideas and parts of the shell scripts are taken from the
initramfs-tools.  This implementation that can be found at
http://anonscm.debian.org/cgit/kernel/initramfs-tools.git

