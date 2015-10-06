#
# init4boot decrypt plugin
#
# (c) 2015 by Andreas Florath (andreas@florath.org)
#
# For licensing details see COPYING
#

#
# This module handles (LUKS) decryption of disks
#

import os

from init4boot.lib.FilesystemUtils import fsutils

class decrypt(object):

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
  decrypt:*)
    bv_deps="${bv_deps} decrypt"
    ;;
""")
        return CommandLineEvaluation()

    def go_HandleInitialModuleSetup(self):

        class HandleInitialModuleSetup:

            def output(self, ofile):
                """/dev/random is needed"""
                ofile.write("""
if check_bv "decrypt"; then
  logp "Handling decrypt"
  modprobe dm_crypt
  ##test ! -e /dev/random && mknod -m 666 /dev/random c 1 8
  ##test ! -e /dev/urandom && mknod -m 666 /dev/urandom c 1 9
fi
""")
        return HandleInitialModuleSetup()

    def go_SetupHighLevelTransport(self):

        class SetupHighLevelTransport:

            def deps(self):
                return []

            def output(self, ofile):
                """Handle parameters like:
decrypt:dev=/dev/mmcblk0p2,name=decdisk,keyfile=/dev/disk/by-id/${ENC_DISK_ID},decmod=luks,tries=3,keyfile_size=4096,keyfile_offset=512;"""

                ofile.write("""
decrypt:*)
  params=$(echo ${transform#decrypt:} | tr "," " ")
  maybe_break decrypt
  decrypt_tries="5"
  decrypt_decmod="luks"
  decrypt_keyfile=""
  decrypt_keyfile_size=""
  decrypt_keyfile_offset="0"
  decrypt_name="decdisk"
  decrypt_dev=""
  for param in ${params}; do
    case ${param} in
      keyfile=*)
          decrypt_keyfile=${param#keyfile=}
          ;;
      decmod=*)
          decrypt_decmod=${param#decmod=}
          ;;
      tries=*)
          decrypt_tries=${param#tries=}
          ;;
      keyfile_size=*)
          decrypt_keyfile_size=${param#keyfile_size=}
          ;;
      keyfile_offset=*)
          decrypt_keyfile_offset=${param#keyfile_offset=}
          ;;
      name=*)
          decrypt_name=${param#name=}
          ;;
      dev=*)
          decrypt_dev=${param#dev=}
          ;;
      *)
          panic "Invalid param in 'decrypt' [${param}]"
          ;;
     esac
  done
  test -z "${decrypt_keyfile}" && panic "decrypt: keyfile not specified"
  test -z "${decrypt_keyfile_size}" && panic "decrypt: keyfile size not specified"
  test -z "${decrypt_dev}" && panic "decrypt: device not specified"
  /sbin/cryptsetup open --type ${decrypt_decmod} \
     --key-file ${decrypt_keyfile} --keyfile-offset ${decrypt_keyfile_offset} \
     --keyfile-size ${decrypt_keyfile_size} \
     ${decrypt_dev} ${decrypt_name}
  RC=$?
  if test "${RC}" -ne 0; then
     panic "cryptsetup failed with return code [${RC}]"
  fi
  ;;
""")
        return SetupHighLevelTransport()

# ======================================================================
# === Create hooks

    def mi_Copy(self):

        class Copy:
            def output(self, c):
                c.copy_exec("sbin/cryptsetup")
        return Copy()
