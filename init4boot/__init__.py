#
# init4boot __init__.pY
#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

"""init4boot is a set of tools for creating a initramfs."""

__package__ = "init4boot"
__all__ = ["create_init", "make_initramfs", "plugins", "lib" ]

#
# Add shared library path to sys.path
#
import os, sys
sys.path.append(os.path.join(os.path.split(__file__)[0], sys.platform))
del os
del sys

