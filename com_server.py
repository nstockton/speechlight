# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# You can register this COM Server by running it with the --register argument on the command line (default action if no arguments given).
# You can unregister this COM Server by running it with the --unregister argument on the command line.


import win32com.server.register

from speechlight import Speech


class SpeechLightServer(Speech):
	_public_methods_ = ["braille", "say", "silence", "output"]
	_public_attrs_ = []
	# You can generate a different clsid with pythoncom.CreateGuid()
	_reg_clsid_ = "{77DFDF59-D59D-4D8B-88A1-2F8F21D75DD7}"
	_reg_desc_ = "The Speech Light COM Server"
	_reg_progid_ = "SpeechLight"

	def __init__(self):
		Speech.__init__(self)


if __name__ == "__main__":
	win32com.server.register.UseCommandLine(SpeechLightServer)
