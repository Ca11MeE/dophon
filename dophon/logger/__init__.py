import logging

# 此处为日志配置
logging_config={
    # 'filename': 'app.log',
    # 'level': 'logging.DEBUG',
    'format': '%(levelname)s %(name)s: <%(module)s> (%(asctime)s) ==> %(filename)s {%(funcName)s} [line:%(lineno)d] ::: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S'
}

if 'level' in logging_config:
    logging_config['level']=eval(logging_config['level'])
else:
    logging_config['level']=logging.INFO

logging.basicConfig(**logging_config)


def inject_logger(g:dict):
    logger = logging.getLogger(g['__file__'])
    g['logger'] = logger
