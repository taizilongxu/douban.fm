#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages
import sys, os
"""
打包的用的setup必须引入，
"""

VERSION = '0.2.0'
with open('README.rd') as f:
    long_description = f.read()

setup(name='douban.fm',
      version=VERSION,
      description="a tiny and smart cli player of douban.fm based on Python",
      long_description=long_description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python douban douban.fm terminal',
      author='taizilongxu',
      author_email='468137306@qq.com',
      url='https://github.com/taizilongxu/douban.fm',
      license='MIT',
      packages=['douban'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
        'termcolor',
      ],
      entry_points={
        'console_scripts':[
            'douban.fm = douban.douban:main'
        ]
      },
)
