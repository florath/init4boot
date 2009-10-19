
Hi and Hello!

init4boot provides some scripts to generate a generic initramfs for
your system.  One possible way to use it, is to have an iSCSI root
disk.

Happy booting

Andreas Florath
sf@flonatel.org

===========================================================================

IMPORTANT NOTE:

The NFS root feature is currently experimental.

===========================================================================

Starting with version 0.5 init4boot supports classless routing.  This
feature is based on busybox's udhcpc implementation.  Because this
feature is quite new busybox version 1.15.2 is needed.  (So, e.g. for
Debian Lenny you need to grab the sources and compile it yourself.)

===========================================================================

Short HowTo
-----------

To create an initramfs, call the 'i4b-mkinitramfs' with the options:

-o <initramfs>: the output file name
-r <rootdir>: the root directory from which to take modules, libs and
              binaries.

The rootdir can be an installation done with 'debootstrap' or a copy
of some existing system.  When the second option is used, the
following directories must be copied over (or must be able to access):
   bin etc lib sbin usr
(Note: It is very important, that there must no link to the outer
world, e. g. lib -> /lib64.  In this case the wrong files (from the
build host) will be used.)


===========================================================================

Some parts of the shell script are taken from the initramfs-tools
implementation that can be found at 
http://packages.debian.org/etch/initramfs-tools.  The initramfs-tools
are PUBLIC DOMAIN.

