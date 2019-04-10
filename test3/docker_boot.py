from dophon import docker_boot


def run():
    docker_boot.run_as_docker('TestRoute.py', package_repository='https://mirrors.aliyun.com/pypi/simple/')


run()
