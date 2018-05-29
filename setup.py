from __future__ import print_function
import sys
if sys.version_info <= (2, 7):
	error = "Requires Python Version 2.7 or above... exiting."
	print(error, file=sys.stderr)
	sys.exit(1)

from setuptools import setup, find_packages

from speechlight import __version__ as VERSION

requirements = ["pywin32"]

setup(
	name="speechlight",
	author="Nick Stockton",
	author_email="nstockton@gmail.com",
	version=VERSION,
	description="A lightweight Python library providing a common interface to multiple TTS and screen reader APIs",
	scripts=[],
	url="https://github.com/nstockton/speechlight",
	package_dir={"speechlight": "speechlight"},
	packages=find_packages(),
	package_data={"speechlight.speech_libs": ["*.dll"]},
	include_package_data=True,
	zip_safe=False,
	license="Mozilla Public License 2.0 (MPL 2.0)",
	platforms="Posix; MacOS X; Windows",
	setup_requires=requirements,
	install_requires=requirements,
	classifiers=[
		"Development Status :: 4 - Beta",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Software Development :: Libraries",
	]
)
