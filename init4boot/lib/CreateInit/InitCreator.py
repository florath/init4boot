#
# (c) 2008 by flonatel
#
# For licensing details see COPYING
#

import os

from init4boot.lib.CreateInit.DataCollector import DataCollector
from init4boot.lib.CreateInit.CIPhases import CIPhases
from init4boot.lib.Plugins import Plugins

class InitCreator:
    def __init__(self, config, opts):
        self.config = config
        self.opts = opts

    def run(self, initfilename="init"):
        dc = DataCollector()
        dc.collect()

        phaseclass = CIPhases()
        plugins = Plugins(phaseclass, self.opts.plugins_dir,
                          self.config, self.opts)
        plugins.load()

        f = file(initfilename, "w")
        plugins.execute(f)
        f.close()
        os.chmod(initfilename, 0766)
