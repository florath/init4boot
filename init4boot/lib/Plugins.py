#
# Plugins
#
# Handle loading of plugins
#
# (c) 2008 by flonatel
#
# For licensing details see COPYING
#

import os
from init4boot.lib.TopologicalSort import topological_sort

class Plugins:

    def __init__(self, phaseclass, path, config, opts):
        self.path = path
        self.config = config
        self.opts = opts
        self.phaseclass = phaseclass
        # Init all the phases
        self.plugins = {}
        for stage in xrange(0, self.phaseclass.TheEnd):
            self.plugins[stage] = {}

    def load(self):
        for filename in os.listdir(os.path.join(
                 self.path, "init4boot", "plugins")):
            if not filename.endswith(".py"):
                continue
            modulename = filename[:-3]

            # Skip __init__.py
            if modulename == "__init__":
                continue

            print "Importing module '%s'" % modulename
            module = __import__("init4boot.plugins.%s" % modulename,
                                globals(), locals(), modulename)

            o = eval("module.%s(self.config, self.opts)" % modulename)

            for stage in xrange(0, self.phaseclass.TheEnd):
                fname = "%s%s" % (self.phaseclass.function_base,
                                   self.phaseclass.desc[stage][0])
                if fname not in dir(o):
                    continue
                print "  ... found %s" % fname
                pplug = eval("o." + fname + "()")
                self.plugins[stage][modulename] = pplug

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

    def execute(self, conf):
        for phase in xrange(0, self.phaseclass.TheEnd):
            print "Phase %d: %s" % (phase, self.phaseclass.desc[phase][0]) 
            sorted = self.dep_sort(self.plugins[phase])
            print "   sorted deps=%s" % sorted
            for t in sorted:
                if "prepare" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].prepare(conf)
            for t in sorted:
                if "pre_output" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].pre_output(conf)
            for t in sorted:
                if "output" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].output(conf)
            # The closing will be done reverse!
            sorted.reverse()
            for t in sorted:
                if "post_output" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].post_output(conf)
            for t in sorted:
                if "cleanup" in dir(self.plugins[phase][t]):
                    self.plugins[phase][t].cleanup(conf)
        
