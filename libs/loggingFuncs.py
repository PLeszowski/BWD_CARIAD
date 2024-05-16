# -*- coding: utf-8 -*-
"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                    Copyright 2019 All Rights Reserved.
            APTIV ADVANCED SAFETY & USER EXPERIENCE PROPRIETARY

           THIS SOFTWARE IS ADVANCED SAFETY & USER EXPERIENCE PROPRIETARY.
            IT MUST NOT BE DISTRIBUTED TO ANYBODY OUTSIDE OF APTIV.

        THIS SOFTWARE INCLUDES NO WARRANTIES, EXPRESS OR IMPLIED, WHETHER
        ORAL, OR WRITTEN WITH RESPECT TO THE SOFTWARE OR OTHER MATERIAL,
            INCLUDING BUT NOT LIMITED TO ANY IMPLIED WARRANTIES OF
       MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE, OR ARISING FROM
           A COURSE OF PERFORMANCE OR DEALING, OR FROM USAGE OR TRADE, OR OF
                   NON-INFRINGEMENT OF ANY PATENTS OF THIRD PARTIES.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                            Author: Szymon Maj
Logger Handler

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                History

date            author          version       Comment

22 Feb 2019     Szymon Maj      0.1.0         Initial Release


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                                To Do

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

from pathlib import Path
import logging


def setup_logger(name, log_file: Path, level=logging.DEBUG):
    """Function setup as many loggers as you want"""
    formatter = logging.Formatter('%(asctime).19s:%(levelname)s|%(message)s')
    handler = logging.FileHandler(str(log_file))
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


def print_and_log(logger, message: str, log_type='info', indention_level=0) -> None:
    indention = '....'
    message_to_log = message
    message = '{}{}'.format(indention * indention_level, message)
    if logger is None:
        print("Logger not set!!!!!!!")
    if log_type.lower() == 'critical':
        if logger is not None:
            logger.critical(message_to_log)
        print(message)
        return
    if log_type.lower() == 'error':
        if logger is not None:
            logger.error(message_to_log)
        print(message)
        return
    if log_type.lower() == 'warning' or log_type.lower() == 'warn':
        if logger is not None:
            logger.warning(message_to_log)
        print(message)
        return
    if log_type.lower() == 'info':
        if logger is not None:
            logger.info(message_to_log)
        print(message)
        return
    if log_type.lower() == 'debug':
        if logger is not None:
            logger.debug(message_to_log)
        return
    if logger is not None:
        logger.critical(message_to_log)
    print(message)
