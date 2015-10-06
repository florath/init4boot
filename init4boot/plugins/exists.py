#
# init4boot exists plugin
#
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

#
# This module check for the existance of the specified disk
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class exists(object):

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
  exists:*)
    ;;
""")
        return CommandLineEvaluation()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def deps(self):
                return []

            def output(self, ofile):
                ofile.write("""
exists:*)
  logp "Processing exists"
  params=$(echo ${transform#exists:} | tr "," " ")
  wait_file="20"
  check_file=""
  for param in ${params}; do
    case "${param}" in
      file=*)
          check_file=${param#file=}
          ;;
      wait=*)
          wait_file=${param#wait=}
          ;;
      *)
          panic "Invalid param in 'exists' [${param}]"
          ;;
     esac
  done
  test -z "${check_file}" && panic "exists: file not specified"

  log "Waiting ${wait_file}s for file ${check_file}"
  slnumber=$(( ${wait_file} * 10 ))
  while test ! -e "${check_file}"; do
    /bin/sleep 0.1
    slnumber=$(( ${slnumber} - 1 ))
    test ${slnumber} -gt 0 || break
  done
  if test -e "${check_file}"; then
    log "File ${check_file} appeared in $(( ( ${wait_file} * 10 - ${slnumber} ) / 10 ))s"
  else
    panic "File ${check_file} does not show up"
  fi
  ;;      
""")
        return SetupHighLevelTransport()

