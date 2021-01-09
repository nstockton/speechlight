# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import platform
from typing import TYPE_CHECKING, List

# Local Modules:
from .utils import get_directory_path


SYSTEM_ARCHITECTURE: str = platform.architecture()[0]
SYSTEM_PLATFORM: str = platform.system()
LIB_DIRECTORY: str = get_directory_path("speech_libs")


if TYPE_CHECKING:  # pragma: no cover
	from .dummy import Speech
else:  # pragma: no cover
	if SYSTEM_PLATFORM == "Windows":
		from .windows import Speech
	elif SYSTEM_PLATFORM == "Darwin":
		from .darwin import Speech
	else:
		from .dummy import Speech

speech: Speech = Speech()
__all__: List[str] = ["speech"]
