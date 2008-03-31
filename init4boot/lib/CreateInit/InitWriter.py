#
# (c) 2008 by flonatel
#
# For licensing details see COPYING
#

# XXX Cleanup: use the new generic Plugin / execute handling

import I4BPhases
import os
from TopologicalSort import topological_sort

class InitWriter:

    def __init__(self, config, plugins):
        self.config = config
        self.plugins = plugins

    def dep_sort(self, l):
        deps = {}
        for plugin in l.keys():
            # Get deps only if implemented
            if "deps" in dir(l[plugin]):
                deps[plugin] = l[plugin].deps()
            else:
                deps[plugin] = []

        ts = topological_sort(deps)
        ts.reverse()
        return ts

    def write(self, fname):
        f = file(fname, "w")
        for phase in xrange(0, I4BPhases.TheEnd):
            print "Phase %d: %s" % (phase, I4BPhases.Desc[phase][0]) 
            sorted = self.dep_sort(self.plugins[phase])
            print "   sorted deps=%s" % sorted
            # XXX ToDo: This is a hack and shoud go to Generic
            if phase>1:
                f.write("lognp %s\n" % I4BPhases.Desc[phase][0])
                f.write("maybe_break %s\n" % I4BPhases.Desc[phase][0])
            for t in sorted:
                if "prepare" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].prepare(f)
            for t in sorted:
                if "pre_output" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].pre_output(f)
            for t in sorted:
                if "output" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].output(f)
            # The closing will be done reverse!
            sorted.reverse()
            for t in sorted:
                if "post_output" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].post_output(f)
            for t in sorted:
                if "cleanup" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].cleanup(f)
        f.close()
        os.chmod(fname, 0766)