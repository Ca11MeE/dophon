# coding:utf-8
from dophon import docker_boot


docker_boot.run_as_docker('Bootstrap.py',attach_cmd=True, extra_package={
        'dophon': '*'
    })