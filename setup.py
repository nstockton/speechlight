# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Third-party Modules:
from setuptools import setup, find_packages

# Local Modules:
from speechlight import __version__ as VERSION, SYSTEM_PLATFORM


REQUIREMENTS = []


if SYSTEM_PLATFORM == "Windows":
	REQUIREMENTS.append("pywin32")


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
	setup_requires=REQUIREMENTS,
	install_requires=REQUIREMENTS,
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Adaptive Technologies",
		"Topic :: Software Development :: Libraries",
	]
)
