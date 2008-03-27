#
# Plugins for MakeInitramfs
#
# Handle loading of plugins
#
# (c) 2008 by flonatel
#
# For licensing details see COPYING
#

import Plugins
import MIPhases

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

