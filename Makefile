#
# Makefile for init4boot
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

I=init4boot-0.0.2

PYSETUP = python setup.py

install:
	$(PYSETUP) install

tarball:
	mkdir ${I}
	cp -a ChangeLog COPYING debian doc i4b-mkinitramfs init4boot \
	    Makefile Readme.txt setup.py Tested.txt ${I}
	find ${I} -name ".svn" | xargs rm -fr
	tar -cvf ${I}.tar ${I}
	bzip2 -9 ${I}.tar
	rm -fr ${I}


