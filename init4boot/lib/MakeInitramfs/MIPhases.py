#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

class MIPhases:

    def __init__(self):
        stage_cnt = 0
        self.desc = {}

        self.Init = stage_cnt
        self.desc[self.Init] = ("Init", "Initializes the copying")

        stage_cnt+=1
        self.Copy = stage_cnt
        self.desc[self.Copy] = ("Copy", "Copies over the data")

        stage_cnt+=1
        self.Create = stage_cnt
        self.desc[self.Create] = ("Create", "Creates the initramfs")

        stage_cnt+=1
        self.Cleanup = stage_cnt
        self.desc[self.Cleanup] = ("Cleanup",
                                   "Clean up everything - removes tmp files")

        stage_cnt+=1
        self.TheEnd = stage_cnt

        self.function_base = "mi_"
