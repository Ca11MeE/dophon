from setuptools import setup,find_packages

setup(
    name='dophon',
    version='0.0.5',
    packages=find_packages(),
    url='https://github.com/Ca11MeE/dophon',
    license='Apache 2.0',
    author='CallMeE',
    author_email='ealohu@163.com',
    description='dophon web framework like springboot',
    install_requires=[
        'flask>=1.0.2',
        'PyMySQL>=0.9.0',
        'pyOpenSSL>=18.0.0',
        'schedule>=0.5.0'
    ]
)
