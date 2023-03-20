from setuptools import setup, find_packages
import sys
sys.path.append(".")
setup(name = 'strembed',
      packages = find_packages(include = ['strembed', 'strembed.*',
                                          'partfindv1_frozen', 'partfindv1_frozen.*',
                                          # 'partfindv1_frozen.Model', 'partfindv1_frozen.Model*'
                                          'data', 'data.*']),
      install_requires = [])