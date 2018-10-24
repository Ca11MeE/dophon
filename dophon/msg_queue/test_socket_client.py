from socket import *

host = '127.0.0.1'
port = 9999
bufsize = 1024
addr = (host, port)
client = socket(AF_INET, SOCK_STREAM)
client.connect(addr)
data = '111'
while True:
    client.send(bytes('%s' % data,encoding='utf-8'))
    data = client.recv(bufsize)
    print(data.strip())
client.close()
