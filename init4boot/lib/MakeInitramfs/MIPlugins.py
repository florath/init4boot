#
# Plugins for MakeInitramfs
#
# Handle loading of plugins
#
# (c) 2008 by flonatel
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

from init4boot.lib.Plugins import Plugins
from init4boot.make_initramfs.MIPhases import MIPhases

class MIPlugins(Plugins):

    def __init__(self, path, config):
        Plugins.__init__(path, config)
        self.plugins = {}

    def load(self):
        Plugins.load()

        for m in self.modobjs:
            for stage in xrange(0, MIPhases.TheEnd):
                fname = "mi_%s" % MIPhases.Desc[stage][0]
                if fname not in dir(o):
                    continue
                pplug = eval("o." + fname + "()")
                self.plugins[stage][modulename] = pplug

