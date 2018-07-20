from setuptools import setup, find_packages

'''
发布命令:
python setup.py bdist_wheel
twine upload dist/dophon-1.0.6-py3.whl
'''

long_description = ''

with open('README.md', 'r') as file:
    long_description = str(file.read().encode(encoding='gbk'),encoding='utf8')

setup(
    name='dophon',
    version='1.0.9',
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
        'schedule>=0.5.0',
        'urllib3>=1.23',
        'Flask_Bootstrap>=3.3.7.1'
    ],
    long_description=long_description
)
