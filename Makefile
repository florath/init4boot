#
# Makefile for init4boot
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

I=init4boot-0.3

PYSETUP = python setup.py

install:
	$(PYSETUP) install

tarball:
	mkdir ${I}
	cp -a ChangeLog COPYING debian doc i4b-mkinitramfs init4boot \
	    Makefile Readme.txt setup.py Tested.txt ${I}
	find ${I} -name ".svn" | xargs rm -fr
	find ${I} -name "*~" | xargs rm -fr
	rm -fr ${I}/doc/screenshots
	rm -fr ${I}/doc/*.pdf
	rm -fr ${I}/debian/init4boot
	rm -fr ${I}/debian/init4boot-doc
	rm -fr ${I}/debian/init4boot-client
	tar -cvf ${I}.tar ${I}
	bzip2 -9 ${I}.tar
	rm -fr ${I}


