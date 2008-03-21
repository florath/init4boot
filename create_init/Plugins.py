#
# Plugins
#
# Handle loading of plugins
#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
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
            
            print "Found module '%s'. Importing..." % modulename
            module = __import__(modulename)

            o = eval("module.%s(self.config)" % modulename)

            for stage in xrange(0, I4BPhases.TheEnd):
                fname = "go_%s" % I4BPhases.Desc[stage][0]
                if fname not in dir(o):
                    print "... skipping method '%s'" % fname
                    continue
                pplug = eval("o." + fname + "()")
                print "+++++++++++++++++*"
                print pplug
                self.plugins[stage][modulename] = pplug
                print self.plugins[stage]

