#!/usr/bin/env python
# encoding: utf-8
import logging
import os

# 设置logger
logging.basicConfig(
    format='%(asctime)s - [%(process)d]%(filename)s:%(lineno)d - %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%I:%S',
    filename=os.path.expanduser('~/.doubanfm.log'),
    level=logging.DEBUG
)

log = logging.getLogger()
