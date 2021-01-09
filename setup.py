# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import platform
from typing import List

# Third-party Modules:
from setuptools import find_packages, setup


NAME: str = "Speechlight"
DESCRIPTION: str = (
	"A lightweight Python library providing a common interface to multiple TTS and screen reader APIs."
)
AUTHOR: str = "Nick Stockton"
AUTHOR_EMAIL: str = "nstockton@gmail.com"
VERSION: str = "1.2"
URL: str = "https://github.com/nstockton/speechlight"
REQUIREMENTS: List[str] = []


if platform.system() == "Windows":
	REQUIREMENTS.append("pywin32")


setup(
	name=NAME,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	version=VERSION,
	description=DESCRIPTION,
	scripts=[],
	url=URL,
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
	],
)
