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
import I4BPhases

class Plugins:

    def __init__(self, path, config):
        self.path = path
        self.plugins = {}
        for stage in xrange(0, I4BPhases.TheEnd):
            self.plugins[stage] = {}
        self.config = config

    def load(self):
        for filename in os.listdir(self.path):
            if not filename.endswith(".py"):
                continue
            modulename = filename[:-3]

            print "Importing module '%s'" % modulename
            module = __import__(modulename)

            o = eval("module.%s(self.config)" % modulename)

            for stage in xrange(0, I4BPhases.TheEnd):
                fname = "go_%s" % I4BPhases.Desc[stage][0]
                if fname not in dir(o):
                    continue
                pplug = eval("o." + fname + "()")
                self.plugins[stage][modulename] = pplug

