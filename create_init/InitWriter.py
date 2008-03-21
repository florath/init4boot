#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
#
import I4BPhases

class InitWriter:

    def __init__(self, config, plugins):
        print "Init"
        self.config = config
        self.plugins = plugins

    def dep_sort(self, l):
        return l

    def write(self):
        f = file("init", "w")
        for stage in xrange(0, I4BPhases.TheEnd):
            sorted = self.dep_sort(self.plugins[stage])
            for t in sorted:
                if "pre_output" in dir(self.plugins[stage][t]):
                    self.plugins[stage][t].pre_output(f)
            for t in sorted:
                if "output" in dir(self.plugins[stage][t]):
                    self.plugins[stage][t].output(f)
            for t in sorted:
                if "post_output" in dir(self.plugins[stage][t]):
                    self.plugins[stage][t].post_output(f)
        f.close()

