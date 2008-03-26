dirs="/bin /sbin /lib* /usr/bin /usr/sbin /usr/lib*"
ssh root@192.168.168.31 "tar -cf - $dirs" | tar -xvf -

Note: replace lib64 -> /lib to lib64 -> lib