from dophon import docker_boot

docker_boot.run_as_docker(
    entity_file_name='bootstrap.py',
    package_repository='https://mirrors.aliyun.com/pypi/simple/',
    extra_package={
        'dophon': '*'
    },
    save_image=True,
    attach_cmd=True,
)
