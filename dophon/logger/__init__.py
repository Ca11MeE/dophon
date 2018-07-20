import logging
from dophon import properties

logging_config = properties.logger_config

if 'level' in logging_config:
    logging_config['level']=eval(logging_config['level'])
else:
    logging_config['level']=logging.INFO

logging.basicConfig(**logging_config)


def inject_logger(g:dict):
    logger = logging.getLogger(g['__file__'])
    g['logger'] = logger
