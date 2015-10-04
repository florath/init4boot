#
# (c) 2015 by Andreas Florath <andreas@florath.net>
#
# For licencing details see COPYING
#

import logging

class BaseLogger(object):
    """This is the base logger class:
    when there is a need to log something, this class can be
    inherited."""

    def __init__(self, name, level=logging.DEBUG):
        # create logger with name
        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(level)
        # create stream handler which logs even debug messages
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(name)s | %(message)s')
        sh.setFormatter(formatter)
        # add the handlers to the logger
        self.__logger.addHandler(sh)
        self.log_debug("Finished setting up logger for [%s]" % name)

    def log_debug(self, msg):
        self.__logger.debug(msg)

    def log_info(self, msg):
        self.__logger.info(msg)

    def log_warn(self, msg):
        self.__logger.warning(msg)
        
    def log_error(self, msg):
        self.__logger.error(msg)
