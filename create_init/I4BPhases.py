#
# (c) 2008 by flonatel GmbH & Co. KG
#
# For licencing details see COPYING
#

#
# These are the stages for the init
#

stage_cnt = 0

# Contains two elements: the first is the method name,
# the second the description
Desc = {}

Intro = stage_cnt
Desc[Intro] = ("Intro", 
               "Writes out the #!/bin/sh and some initial comments")
stage_cnt+=1

FunctionDefinition = stage_cnt
Desc[FunctionDefinition] = ("FunctionDefinition",
    "Define functions at the top of the init script")
stage_cnt+=1

CommandLineParsing = stage_cnt
Desc[CommandLineParsing] = ("CommandLineParsing",
    "Command line parsing is done first to get the 'verbose' and 'debug' switches working as soon as possible.")
stage_cnt+=1

CommandLineVerbose = stage_cnt
Desc[CommandLineVerbose] = ("CommandLineVerbose",
    "Handle only the 'verbose' and 'debug' options.")
stage_cnt+=1

InitialSystemSetup = stage_cnt
Desc[InitialSystemSetup] = ("InitialSystemSetup",
    "During initial system setup, the mandatory devices are created.")
stage_cnt+=1

CommandLineEvaluation = stage_cnt
Desc[CommandLineEvaluation] = ("CommandLineEvaluation",
    "Other command line parameters (beneath 'verbose' and 'debug') are evaluated")
stage_cnt+=1

HandleInitialModuleSetup = stage_cnt
Desc[HandleInitialModuleSetup] = ("HandleInitialModuleSetup",
    "Module setup is done: e. g. running depmod and loading the mandatory modules")
stage_cnt+=1

SetupLowLevelTransport = stage_cnt
Desc[SetupLowLevelTransport] = ("SetupLowLevelTransport",
    "Handle the low level transport layer, e.g. the network")
stage_cnt+=1

SetupHighLevelTransport = stage_cnt
Desc[SetupHighLevelTransport] = ("SetupHighLevelTransport",
    "Handle the higher level transport layer, e.g. login, tunnel setup, iSCSI login")
stage_cnt+=1
                                 
SetupDiskDevices = stage_cnt
Desc[SetupDiskDevices] = ("SetupDiskDevices",
    "Setup the disk devices that are needed for the root file system (When this stage is finished, the root device must be available)")
stage_cnt+=1

MountRoot = stage_cnt
Desc[MountRoot] = ("MountRoot", "Mount the root dir")
stage_cnt+=1

PrepareRootDir = stage_cnt
Desc[PrepareRootDir] = ("PrepareRootDir", "Prepare the new and fresh mounted root dir")
stage_cnt+=1

CheckForInit = stage_cnt
Desc[CheckForInit] = ("CheckForInit", "Check for init")
stage_cnt+=1

RunInit = stage_cnt
Desc[RunInit] = ("RunInit", "Run the new init")
stage_cnt+=1

TheEnd = stage_cnt
Desc[TheEnd] = ("TheEnd", "Symbolic for 'The End'")

