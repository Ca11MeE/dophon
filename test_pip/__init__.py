from dophon import docker_boot

docker_boot.run_as_docker(
    entity_file_name='Bootstrap.py',
    # package_repository='https://mirrors.aliyun.com/pypi/simple/',
    attach_cmd=True, extra_package={
        'dophon': '*'
    })
