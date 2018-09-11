# -*- coding: utf-8 -*-
from dophon import cluster_boot

def run():
    cluster_boot.main_freeze()
    # 此处的port参数为集群起始内部监听端口
    cluster_boot.run_clusters(clusters=10, start_port=8800,outer_port=True)

if '__main__' == __name__ :
    run()