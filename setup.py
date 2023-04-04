from setuptools import setup, find_packages
import sys
sys.path.append(".")

from strembed.utils import do_fixes

setup(name = 'strembed',
      packages = find_packages(include = ['strembed', 'strembed.*',
                                          # 'partfindv1_frozen', 'partfindv1_frozen.*',
                                          # 'partfindv1_frozen.Model', 'partfindv1_frozen.Model*'
                                          'data', 'data.*']),
      install_requires = [])

# HR 24/03/23 Executable/script switch to avoid all this UNPLEASANTNESS
if getattr(sys, 'frozen', False):
    print("\n# Running as executable... #")
else:
    print("\n# Running as normal Python script... #")
    do_fixes()