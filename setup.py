# coding: utf-8
import pypandoc as pypandoc
from setuptools import setup, find_packages

'''
发布命令:
python setup.py bdist_wheel
twine upload dist/  <dophon.whl>
'''

long_description = ''

try:
    long_description = pypandoc.convert('README.md', 'rst')
    long_description = long_description.replace("\r","") # THAT $%^$*($ ONE
except OSError:
    print("Pandoc not found. Long_description conversion failure.")
    import io
    # pandoc is not installed, fallback to using raw contents
    with io.open('README.md', encoding="utf-8") as f:
        long_description = f.read()

setup(
    name='dophon',
    version='1.1.5',
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
