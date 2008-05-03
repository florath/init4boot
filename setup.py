#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from distutils.core import setup

package = 'init4boot'
version = '0.2'

def adjust(input, output):
    if os.path.exists(output):
        input_time = os.path.getmtime(input)
        output_time = os.path.getmtime(output)
        setup_time = os.path.getmtime('setup.py')
        if output_time > input_time and output_time > setup_time:
            return
        os.chmod(output, 0644)
        os.remove(output)
    sys.stdout.write('adjusting %s -> %s\n' % (input, output))
    buffer = file(input).read()
    file(output, 'w').write(buffer.replace('@VERSION@', version))
    os.chmod(output, 0444)

#adjust('__init__.py.in', '__init__.py')

setup(name=package, version=version,
      description="Creates init script and initramfs.",
      author='flonatel', author_email='sf@flonatel.org',
      url='http://sourceforge.net/projects/init4boot/',
      license="GPL V3", platforms="all",
      scripts=["i4b-mkinitramfs", ],
      long_description=
 """init4boot is a set of utilities to create an initramfs and 
 corresponding init scripts that are used during boot. 
 It's extensible, supports iSCSI boot and can be used in a 
 Xen environment.""",      
      packages=['init4boot', 'init4boot/create_init',
                'init4boot/make_initramfs', 'init4boot/lib',
                'init4boot/plugins', 'init4boot/lib/CreateInit',
                'init4boot/lib/MakeInitramfs'])
