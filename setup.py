# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='LRE',
    version='0.0.1',
    description='Lexical Rule Engine',
    url='https://github.com/ovixiao/lre',
    author='ovix',
    author_email='ovix@qq.com',
    license='MIT',
    install_requires=['six', 'jieba'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='sas ecc lexical rule',
    packages=find_packages(),
)
