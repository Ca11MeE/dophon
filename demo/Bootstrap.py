from dophon import boot
import threading

# 启动服务器
def run():
    boot.bootstrap_app()
    # 启动服务器
    boot.run_app_ssl()

run()

