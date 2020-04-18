#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, shutil
from setuptools.command.install import install
from distutils.core import setup, Extension
from setuptools import setup, find_namespace_packages 



TARGET_PATH = f'{os.environ["HOME"]}/.lk_scraper/'
SOURCE_PATH = 'config_files/'


if not os.path.isdir(TARGET_PATH):
	os.makedirs(TARGET_PATH, exist_ok=True)

src = os.path.join(os.getcwd(), SOURCE_PATH)

for file_name in os.listdir(src):
    full_file_name = os.path.join(src, file_name)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, TARGET_PATH)


setup(name='lk_scrapper',
      version='1.0',
      author='Jean-Louis Quéguiner',
      author_email='jean-louis.queguiner@gadz.org',
      packages=find_namespace_packages(),
      install_requires=[
          'selenium',
          'PyYAML',
          'beautifulsoup4'
      ],
      include_package_data=True
     )


