#
# (c) 2008 by flonatel
#
# For licensing details see COPYING
#
from InitWriter import InitWriter
from DataCollector import DataCollector
from Plugins import Plugins

class CreateInit():

    def run(self, initfilename="init"):
        dc = DataCollector()
        dc.collect()

        ## XXX DIRTY HACK!
        plugins = Plugins("plugins", dc.data)
        plugins.load()
    
        iw = InitWriter(dc.data, plugins.plugins)
        iw.write(initfilename)
