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

"""COM server for Speechlight."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
from typing import ClassVar

# Third-party Modules:
import win32com.server.register

# Speechlight Modules:
from speechlight import Speech


# You can register this COM Server by running it with the '--register' argument on the command line.
# You can unregister this COM Server by running it with the '--unregister' argument on the command line.


class SpeechlightServer(Speech):
	"""A COM server which exposes Speechlight."""

	_public_methods_: ClassVar[list[str]] = ["braille", "say", "silence", "output"]
	_public_attrs_: ClassVar[list[str]] = []
	# You can generate a different clsid with pythoncom.CreateGuid.
	_reg_clsid_: ClassVar[str] = "{77DFDF59-D59D-4D8B-88A1-2F8F21D75DD7}"
	_reg_desc_: ClassVar[str] = "The Speechlight COM Server"
	_reg_progid_: ClassVar[str] = "speechlight"

	def __init__(self) -> None:
		"""Defines the constructor."""
		super().__init__()


if __name__ == "__main__":
	win32com.server.register.UseCommandLine(SpeechlightServer)
