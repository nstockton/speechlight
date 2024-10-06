"""COM server for Speechlight."""


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Future Modules:
from __future__ import annotations

# Third-party Modules:
import win32com.server.register

# Speechlight Modules:
from speechlight import Speech


# You can register this COM Server by running it with the '--register' argument on the command line.
# You can unregister this COM Server by running it with the '--unregister' argument on the command line.


class SpeechlightServer(Speech):
	"""A COM server which exposes Speechlight."""

	_public_methods_: list[str] = ["braille", "say", "silence", "output"]
	_public_attrs_: list[str] = []
	# You can generate a different clsid with pythoncom.CreateGuid()
	_reg_clsid_: str = "{77DFDF59-D59D-4D8B-88A1-2F8F21D75DD7}"
	_reg_desc_: str = "The Speechlight COM Server"
	_reg_progid_: str = "speechlight"

	def __init__(self) -> None:
		"""Defines the constructor."""
		super().__init__()


if __name__ == "__main__":
	win32com.server.register.UseCommandLine(SpeechlightServer)
