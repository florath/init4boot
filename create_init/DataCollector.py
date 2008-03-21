#
# DataCollector
#
# This class collects data from the current system and stores them in a map.
#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
#

import popen2

class DataCollector:

    def __init__(self):
        self.data = {}

    def collect(self):
        self.collect_tmpfs_size()

    def collect_tmpfs_size(self):
        self.data["tmpfs_size"] = \
            self.shell_var("/etc/udev/udev.conf", "tmpfs_size")

    def shell_var(self, script, var):
        cout, cin = popen2.popen2("/bin/bash -c 'source %s && echo $%s'"
                                  % (script, var))
        result = cout.read()
        return result[:-1]
