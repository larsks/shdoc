from setuptools import setup, find_packages
from shdoc import __version__

with open('requirements.txt') as fd:
    requires = fd.read().splitlines()

setup(name='shdoc',
      author='Lars Kellogg-Stedman',
      author_email='lars@oddbit.com',
      url='https://github.com/larsks/shdoc',
      version=__version__,
      packages=find_packages(),
      install_requires=requires,
      package_data={'shdoc': [
          'data/*',
      ]},
      entry_points={'console_scripts': [
          'shdoc = shdoc.main:main',
          'shdoc-tangle = shdoc.tangle:main',
          'shdoc-weave = shdoc.weave:main',
          'shdoc-json = shdoc.jsondump:main',
      ]})
