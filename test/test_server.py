from dophon import boot
from dophon.annotation import BeanConfig
import b_config

boot.GC_INFO = True

BeanConfig(config_file='b_config.py')  # 单文件名形式实例管理器初始化
BeanConfig(files=[b_config])  # 实例管理器初始化,由于已经初始化一个管理器,此管理器初始化跳过

boot.run_app()
