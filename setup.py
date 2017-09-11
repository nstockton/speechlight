from __future__ import print_function
import sys

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup


if sys.version_info <= (2, 7):
	error = "Requires Python Version 2.7 or above... exiting."
	print(error, file=sys.stderr)
	sys.exit(1)


requirements = []

setup(
	name="speechlight",
	version="1.0",
	description="A lightweight Python library providing a common interface to multiple TTS and screen reader APIs",
	scripts=[],
	url="https://github.com/nstockton/speechlight",
	packages=["speechlight"],
	license="Mozilla Public License 2.0 (MPL 2.0)",
	platforms="Posix; MacOS X; Windows",
	setup_requires=requirements,
	install_requires=requirements,
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3.0",
		"Programming Language :: Python :: 3.1",
		"Programming Language :: Python :: 3.2",
		"Programming Language :: Python :: 3.3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
		"Topic :: Software Development :: Libraries",
	]
)
