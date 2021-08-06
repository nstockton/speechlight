# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import pathlib
import platform
import sys
from typing import List

# Third-party Modules:
from setuptools import setup  # type: ignore[import]


if sys.version_info < (3, 7):
	raise NotImplementedError("Only Python 3.7+ is supported.")


NAME: str = "Speechlight"
DESCRIPTION: str = (
	"A lightweight Python library providing a common interface to multiple TTS and screen reader APIs."
)
KEYWORDS: str = "blind jaws jfw nvda speech tts screenreader screen reader"
AUTHOR: str = "Nick Stockton"
AUTHOR_EMAIL: str = "nstockton@users.noreply.github.com"
VERSION: str = "1.4"
URL: str = "https://github.com/nstockton/speechlight"
# The directory containing this file
HERE: pathlib.Path = pathlib.Path(__file__).parent
README: str = (HERE / "README.md").read_text()
REQUIREMENTS: List[str] = []


if platform.system() == "Windows":
	REQUIREMENTS.append("pywin32")


setup(
	python_requires=">=3.7",
	name=NAME,
	keywords=KEYWORDS,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	version=VERSION,
	description=DESCRIPTION,
	long_description=README,
	long_description_content_type="text/markdown",
	url=URL,
	package_dir={"speechlight": "speechlight"},
	packages=["speechlight"],
	package_data={"speechlight": ["py.typed", "speech_libs/*"]},
	zip_safe=False,
	setup_requires=REQUIREMENTS,
	install_requires=REQUIREMENTS,
	scripts=[],
	license="Mozilla Public License 2.0 (MPL 2.0)",
	platforms="Posix; MacOS X; Windows",
	classifiers=[
		"License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"Programming Language :: Python",
		"Development Status :: 5 - Production/Stable",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Topic :: Adaptive Technologies",
		"Topic :: Software Development :: Libraries",
	],
)
