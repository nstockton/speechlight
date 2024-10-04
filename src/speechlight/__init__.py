# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import platform
import sys

# Third-party Modules:
from knickknacks.platforms import getDirectoryPath


__version__: str = "0.0.0"


SYSTEM_ARCHITECTURE: str = platform.architecture()[0]
LIB_DIRECTORY: str = getDirectoryPath("speech_libs")


if sys.platform == "win32":  # pragma: no cover
	from .windows import Speech
elif sys.platform == "darwin":  # pragma: no cover
	from .darwin import Speech
else:  # pragma: no cover
	from .dummy import Speech

speech: Speech = Speech()
__all__: list[str] = ["Speech", "speech"]
