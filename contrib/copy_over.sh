dirs="/bin /sbin /lib /usr/bin /usr/sbin /usr/lib /etc/udev"

ssh root@192.168.168.31 "tar -cf - $dirs" | tar -xvf -
