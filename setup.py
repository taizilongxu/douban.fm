#-*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

VERSION = '0.1.7'

setup(name='douban.fm',
      version=VERSION,
      description="a tiny and smart cli player of douban.fm based on Python",
      long_description="""a tiny and smart cli player of douban.fm based on Python""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python douban douban.fm terminal',
      author='taizilongxu',
      author_email='468137306@qq.com',
      url='https://github.com/taizilongxu/douban.fm',
      license='MIT',
      packages=find_packages(exclude=['examples', 'tests']),
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
