host='127.0.0.1'
port=18080
server_processes=3
blueprint_path=['/routes']
mq={'remote_center': False}
remote_prop={'base': '127.0.0.1:833', 'mark': ['config', 'get'], 'method': 'get'}
logger_config={'format': '%(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}
