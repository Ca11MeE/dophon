from dophon import boot

# 启动服务器
if '__main__' == __name__:
    boot.bootstrap_app()
    # 启动服务器
    boot.run_app_ssl()

