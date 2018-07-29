import ctypes
import logging
import os
import re
import sys
import platform

p_sys_type = platform.system()

logging_config = {
    # 'filename': 'app.log',
    # 'level': 'logging.DEBUG',
    'format': '%(levelname)s : (%(asctime)s) ==> ::: %(message)s',
    # 'format': '%(levelname)s %(name)s: <%(module)s> (%(asctime)s) ==> %(filename)s {%(funcName)s} [line:%(lineno)d] ::: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}

if 'level' in logging_config:
    logging_config['level'] = eval(logging_config['level'])
else:
    logging_config['level'] = logging.INFO


# 日志过滤非框架打印
class DefFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith('dophon')


# 禁用调度的日志显示
logging.getLogger('schedule').addFilter(DefFilter())


CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0

formatter=logging.Formatter(fmt=logging_config['format'], datefmt=logging_config['datefmt'])

if str(p_sys_type).upper() == 'WINDOWS':
    logging.basicConfig(**logging_config)
else:
    logging._levelToName = {
        CRITICAL: '\033[7;35;40mCRITICAL',
        ERROR: '\033[7;31;40mERROR',
        WARNING: '\033[7;33;40mWARNING',
        INFO: '\033[7;32;40mINFO',
        DEBUG: '\033[7;34;40mDEBUG',
        NOTSET: '\033[7;35;40mNOTSET',
    }
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(formatter)

__foreGroundBLUE = 0x09
__foreGroundGREEN = 0x0a
__foreGroundRED = 0x0c
__foreGroundYELLOW = 0x0e
__stdInputHandle = -10
__stdOutputHandle = -11
__stdErrorHandle = -12

stdOutHandle = ctypes.windll.kernel32.GetStdHandle(__stdOutputHandle)


def setCmdColor(color, handle=stdOutHandle):
    return ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)  # 此处为日志配置


def resetCmdColor():
    setCmdColor(__foreGroundRED | __foreGroundGREEN | __foreGroundBLUE)


class DophonLogger:
    __foreGroundBLUE = 0x09
    __foreGroundGREEN = 0x0a
    __foreGroundRED = 0x0c
    __foreGroundYELLOW = 0x0e

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(*args, **kwargs)
        if str(p_sys_type).upper() == 'WINDOWS':
            pass
        else:
            self.logger.addHandler(sh)
        self.logger.setLevel(logging.DEBUG)

    def info_str(self, message):
        result_str = message + '\033[0m'
        return result_str

    def warning_str(self, message):
        result_str = message + '\033[0m'
        return result_str

    def error_str(self, message):
        result_str = message + '\033[0m'
        return result_str

    def critical_str(self, message):
        result_str = message + '\033[0m'
        return result_str

    def debug_str(self, message):
        result_str = message + '\033[0m'
        return result_str

    def debug(self, *args):
        n_args = []
        for arg in args:
            n_args.append(arg)
        msg = n_args.pop(0)
        message = msg % tuple(n_args)
        if str(p_sys_type).upper() == 'WINDOWS':
            setCmdColor(self.__foreGroundBLUE)
            self.logger.debug(msg=formatter.format(logging.LogRecord(msg=message)))
            resetCmdColor()
        else:
            self.logger.debug(msg=self.debug_str(message))

    def info(self, *args):

        n_args = []
        for arg in args:
            n_args.append(arg)
        msg = n_args.pop(0)
        message = msg % tuple(n_args)
        if str(p_sys_type).upper() == 'WINDOWS':
            self.__foreGroundGREEN
            self.logger.info(msg=message)
            resetCmdColor()
        else:
            self.logger.info(msg=self.info_str(message))

    def warning(self, *args):
        n_args = []
        for arg in args:
            n_args.append(arg)
        msg = n_args.pop(0)
        message = msg % tuple(n_args)
        if str(p_sys_type).upper() == 'WINDOWS':
            setCmdColor(self.__foreGroundYELLOW)
            self.logger.warning(msg=message)
            resetCmdColor()
        else:
            self.logger.warning(msg=self.warning_str(message))

    def error(self, *args):
        n_args = []
        for arg in args:
            n_args.append(arg)
        msg = n_args.pop(0)
        message = msg % tuple(n_args)
        if str(p_sys_type).upper() == 'WINDOWS':
            setCmdColor(self.__foreGroundRED)
            self.logger.error(msg=message)
            resetCmdColor()
        else:
            self.logger.error(msg=self.error_str(message))

    def critical(self, *args):
        n_args = []
        for arg in args:
            n_args.append(arg)
        msg = n_args.pop(0)
        message = msg % tuple(n_args)
        if str(p_sys_type).upper() == 'WINDOWS':
            setCmdColor(self.__foreGroundRED)
            self.logger.critical(msg=message)
            resetCmdColor()
        else:
            self.logger.critical(msg=self.critical_str(message))

    def addFilter(self, *args, **kwargs):
        self.logger.addFilter(*args, **kwargs)


def inject_logger(g: dict):
    # logger = logging.getLogger('dophon.' + re.sub('\..*', '', g['__file__'].split(os.path.sep)[-1]))
    logger = DophonLogger('dophon.' + re.sub('\..*', '', g['__file__'].split(os.path.sep)[-1]))
    logger.addFilter(DefFilter())
    g['logger'] = logger
