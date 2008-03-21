
Currently only the init - script creation is implemented.
To use init4boot (e.g. for iSCSI boot), install the initramfs-tools
and replace the 'init' script in '/usr/share/initramfs-tools/init' (do
not forget to set execute permissions) and call mkinitramfs.

Happy booting

Andre

===========================================================================

Some parts of the shell script are taken from the initramfs-tools
implementation that can be found at 
http://packages.debian.org/etch/initramfs-tools.  The initramfs-tools
are PUBLIC DOMAIN.

