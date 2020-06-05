from setuptools import setup, find_packages

import musicfiletools

setup(name='musicfiletools',
      version=musicfiletools.__version__,
      description='Tools to work with music file (MP3, FLAC, ...)',
      long_description='A collection of tools to work with music files', 
      url='http://github.com/hifiberry/musicfiletools',
      author='Daniel Matuschek',
      author_email='daniel@hifiberry.com',
      license='MIT',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5'
          'Programming Language :: Python :: 3.6'
          'Programming Language :: Python :: 3.7'
          'Programming Language :: Python :: 3.8'
      ],
      packages=find_packages(),
      install_requires=['mutagen'],
      scripts=[],
      keywords='mp3, m4a, flac, metadata, cover',
      scripts=['scripts/getcovers.py' ],
      zip_safe=False)
