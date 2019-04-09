from dophon import docker_boot

docker_boot.run_as_docker(
    'Bootstrap.py',
    attach_cmd=True,
    # package_repository='https://mirrors.aliyun.com/pypi/simple/',
    extra_package={

        'dophon': '*'
    }
)
