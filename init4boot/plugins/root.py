#
# init4boot root plugin
#
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

#
# This module sets the root path
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class root(object):

    def __init__(self, config, opts):
        self.config = config
        self.opts = opts
        self.__root_dir = opts.root_dir

    def check(self):
        return True

    def go_CommandLineEvaluation(self):

        class CommandLineEvaluation:

            def output(self, ofile):
                ofile.write("""
  root:*)
    ;;
""")
        return CommandLineEvaluation()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def deps(self):
                return []

            def output(self, ofile):
                ofile.write("""
root:*)
  logp "Processing root"
  params=$(echo ${transform#root:} | tr "," " ")
  path=""
  for param in ${params}; do
    case "${param}" in
      dev=*)
          path=${param#dev=}
          ;;
      *)
          panic "Invalid param in 'root' [${param}]"
          ;;
     esac
  done
  test -z "${path}" && panic "root: dev not specified"
  ;;      
""")
        return SetupHighLevelTransport()

