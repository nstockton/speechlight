# Copyright (c) 2025 Nick Stockton
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# -----------------------------------------------------------------------------
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# -----------------------------------------------------------------------------
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import platform
import sys
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING

# Third-party Modules:
from knickknacks.platforms import get_directory_path


SYSTEM_ARCHITECTURE: str = platform.architecture()[0]
LIB_DIRECTORY: Path = Path(get_directory_path("speech_libs"))


if sys.platform == "win32":  # pragma: no cover
	from .windows import Speech
elif sys.platform == "darwin":  # pragma: no cover
	from .darwin import Speech
else:  # pragma: no cover
	from .dummy import Speech
speech: Speech = Speech()


__version__: str = "0.0.0"
if not TYPE_CHECKING:
	with suppress(ImportError):
		from ._version import __version__


__all__: list[str] = [
	"LIB_DIRECTORY",
	"SYSTEM_ARCHITECTURE",
	"Speech",
	"__version__",
	"speech",
]
