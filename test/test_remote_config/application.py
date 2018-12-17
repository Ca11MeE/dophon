host = '127.0.0.1'
port = 833
server_processes = 3  # 服务器多进程处理
error_info = 'XML'

# error_code = 'JSON'

logger_config={
            'format': '%(levelname)s ==> ::: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }