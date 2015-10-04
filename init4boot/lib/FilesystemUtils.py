#
# (c) 2015 by Andreas Florath <andreas@florath.net>
#
# For licencing details see COPYING
#

import os
from init4boot.lib.BaseLogger import BaseLogger

class FileSystemUtils(BaseLogger):

    def __init__(self):
        BaseLogger.__init__(self, "FileSystemUtils")

    def must_exist(self, path, dirlist, filename):
        for dirname in dirlist:
            if os.path.exists(os.path.join(path, dirname, filename)):
                return True
        self.log_warn("File does not exists [%s] [%s] [%s]" %
                      (path, dirlist, filename))
        return False
        
fsutils = FileSystemUtils()
