from dophon import boot
from dophon.annotation import BeanConfig
from test import b_config

BeanConfig(config_file='b_config.py')
print(b_config)
BeanConfig(files=[b_config])

boot.run_app()