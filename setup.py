#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name="python-binance-api",
      version="1.1.0",
      description="Binance API client",
      license="MIT",
      install_requires=["simplejson","requests","six", "websocket-client", "Events"],
      author="cnfuyu",
      author_email="cnfuyu@gmail.com",
      url="http://github.com/cnfuyu/python-binance-api",
      packages = find_packages(),
      keywords= "binance",
      zip_safe = True)
