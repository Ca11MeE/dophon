from setuptools import setup, find_packages


'''
发布命令:
python setup.py bdist_wheel
twine upload dist/  <dophon.whl>
'''

setup(
    name='dophon_db',
    version='1.0.0',
    packages=find_packages(),
    url='https://github.com/Ca11MeE/dophon',
    license='Apache 2.0',
    author='CallMeE',
    author_email='ealohu@163.com',
    description='dophon mysql module',
    install_requires=[
        'PyMySQL>=0.9.0',
        'schedule>=0.5.0',
    ]
)