#
# (c) 2008 by flonatel
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
        self.copy = stage_cnt
        self.desc[self.copy] = ("Copy", "Copies over the data")

        stage_cnt+=1
        self.cleanup = stage_cnt
        self.desc[self.cleanup] = ("Cleanup",
                                   "Clean up everything - removes tmp files")

        stage_cnt+=1
        self.TheEnd = stage_cnt

        self.function_base = "mi_"
