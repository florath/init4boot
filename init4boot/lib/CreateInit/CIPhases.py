#
# (c) 2008 by flonatel (sf@flonatel.org)
#
# For licensing details see COPYING
#

#
# These are the stages for the init
#

class CIPhases:

    def __init__(self):
        stage_cnt = 0
        self.desc = {}

        self.Intro = stage_cnt
        self.desc[self.Intro] = ("Intro", 
             "Writes out the #!/bin/sh and some initial comments")

        stage_cnt+=1
        self.FunctionDefinition = stage_cnt
        self.desc[self.FunctionDefinition] = ("FunctionDefinition",
             "Define functions at the top of the init script")

        stage_cnt+=1
        self.CommandLineParsing = stage_cnt
        self.desc[self.CommandLineParsing] = ("CommandLineParsing",
             "Command line parsing is done first to get the 'verbose' "
             + "and 'debug' switches working as soon as possible.")

        stage_cnt+=1
        self.CommandLineVerbose = stage_cnt
        self.desc[self.CommandLineVerbose] = ("CommandLineVerbose",
             "Handle only the 'verbose' and 'debug' options.")

        stage_cnt+=1
        self.InitialSystemSetup = stage_cnt
        self.desc[self.InitialSystemSetup] = ("InitialSystemSetup",
             "During initial system setup, the mandatory devices are created.")

        stage_cnt+=1
        self.CommandLineEvaluation = stage_cnt
        self.desc[self.CommandLineEvaluation] = ("CommandLineEvaluation",
             "Other command line parameters (beneath 'verbose' and "
             + "'debug') are evaluated")

        stage_cnt+=1
        self.HandleInitialModuleSetup = stage_cnt
        self.desc[self.HandleInitialModuleSetup] = ("HandleInitialModuleSetup",
             "Module setup is done: e. g. running depmod and loading "
             + "the mandatory modules")

        stage_cnt+=1
        self.SetupLowLevelTransport = stage_cnt
        self.desc[self.SetupLowLevelTransport] = ("SetupLowLevelTransport",
             "Handle the low level transport layer, e.g. the network")

        stage_cnt+=1
        self.SetupHighLevelTransport = stage_cnt
        self.desc[self.SetupHighLevelTransport] = ("SetupHighLevelTransport",
             "Handle the higher level transport layer, e.g. "
             + "login, tunnel setup, iSCSI login")

        stage_cnt+=1
        self.SetupDiskDevices = stage_cnt
        self.desc[self.SetupDiskDevices] = ("SetupDiskDevices",
             "Setup the disk devices that are needed for the root file "
             + "system (When this stage is finished, the root device must "
             + "be available)")

        stage_cnt+=1
        self.MountRoot = stage_cnt
        self.desc[self.MountRoot] = ("MountRoot", "Mount the root dir")

        stage_cnt+=1
        self.PrepareRootDir = stage_cnt
        self.desc[self.PrepareRootDir] = ("PrepareRootDir",
             "Prepare the new and fresh mounted root dir")

        stage_cnt+=1
        self.CheckForInit = stage_cnt
        self.desc[self.CheckForInit] = ("CheckForInit", "Check for init")

        stage_cnt+=1
        self.RunInit = stage_cnt
        self.desc[self.RunInit] = ("RunInit", "Run the new init")

        stage_cnt+=1
        self.TheEnd = stage_cnt
        self.desc[self.TheEnd] = ("TheEnd", "Symbolic for 'The End'")


        self.function_base = "go_"

