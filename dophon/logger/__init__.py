import logging
import os
import re

# 此处为日志配置
logging_config = {
    # 'filename': 'app.log',
    # 'level': 'logging.DEBUG',
    'format': '%(levelname)s : (%(asctime)s) ==> ::: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}

if 'level' in logging_config:
    logging_config['level'] = eval(logging_config['level'])
else:
    logging_config['level'] = logging.INFO

logging.basicConfig(**logging_config)


# 日志过滤非框架打印
class DefFilter(logging.Filter):
    def filter(self, record):
        return record.name.startswith('dophon')


# 禁用调度的日志显示
logging.getLogger('schedule').addFilter(DefFilter())


def inject_logger(g: dict):
    logger = logging.getLogger('dophon.' + re.sub('\..*', '', g['__file__'].split(os.path.sep)[-1]))
    logger.addFilter(DefFilter())
    g['logger'] = logger
