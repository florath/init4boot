
Hi and Hello!

Currently only the init - script creation is implemented.
To use init4boot (e.g. for iSCSI boot), install the initramfs-tools
and replace the 'init' script in '/usr/share/initramfs-tools/init' (do
not forget to set execute permissions) and call mkinitramfs.

Note:  The 'Attic' directory contains the old and first version of the
iSCSI boot.  This was a patch against the existing initramfs-tools.
This was added, because it contains some more aspects of the direction
and contais some things, that are not implemented in the new version.
After some time, when everything is taken to the new version, the
'Attic' directory should vanish.


Happy booting

Andre


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

