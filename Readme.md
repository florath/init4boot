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

## Creating
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

## Usage
To use the initrd created by init4boot, there is the need to adapt the
boot kernel parameters.  The location of the parameters are highly
dependend which boot program you are using.

When you are using grub, you can find the kernel parameters typically
in the file */boot/grub/grub.cfg*. Have a look for menuentry and there
for linux.

When you are using 'Das U-Boot' for embedded systems (like Raspberry
Pi 2), the parameters are in the u-boot configuration file, like
*/boot/boot.cfg* or */boot/firmware/boot.cfg*.
Do not forget to call the mkimage after changing this file.

# Known to Run
This is a list of all systems where init4boot is known to work:
* Debian Jessie armhf on Raspberry Pi 2 with u-boot

# Thanks
Some ideas and parts of the shell scripts are taken from the
initramfs-tools.  This implementation that can be found at
http://anonscm.debian.org/cgit/kernel/initramfs-tools.git

