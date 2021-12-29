# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import os
import sys
from unittest import TestCase
from unittest.mock import Mock, patch

# Speechlight Modules:
from speechlight import utils


class TestUtils(TestCase):
	@patch("speechlight.utils._imp")
	@patch("speechlight.utils.sys")
	def test_get_freezer(self, mock_sys: Mock, mock_imp: Mock) -> None:
		del mock_sys.frozen
		del mock_sys._MEIPASS
		del mock_sys.importers
		mock_imp.is_frozen.return_value = True
		self.assertEqual(utils.get_freezer(), "tools/freeze")
		mock_imp.is_frozen.return_value = False
		self.assertIs(utils.get_freezer(), None)
		mock_sys.importers = True
		self.assertEqual(utils.get_freezer(), "old_py2exe")
		del mock_sys.importers
		for item in ("windows_exe", "console_exe", "dll"):
			mock_sys.frozen = item
			self.assertEqual(utils.get_freezer(), "py2exe")
		mock_sys.frozen = "macosx_app"
		self.assertEqual(utils.get_freezer(), "py2app")
		mock_sys.frozen = True
		self.assertEqual(utils.get_freezer(), "cx_freeze")
		mock_sys.frozen = "some undefined freezer"
		self.assertEqual(utils.get_freezer(), "unknown some undefined freezer")
		mock_sys._MEIPASS = "."
		self.assertEqual(utils.get_freezer(), "pyinstaller")

	def test_is_frozen(self) -> None:
		self.assertIs(utils.is_frozen(), False)

	@patch("speechlight.utils.is_frozen")
	def test_getDirectoryPath(self, mock_is_frozen: Mock) -> None:
		subdirectory: tuple[str, ...] = ("level1", "level2")
		frozen_dir_name: str = os.path.dirname(sys.executable)
		frozen_output: str = os.path.realpath(os.path.join(frozen_dir_name, *subdirectory))
		mock_is_frozen.return_value = True
		self.assertEqual(utils.get_directory_path(*subdirectory), frozen_output)
		unfrozen_dir_name: str = os.path.dirname(utils.__file__)
		unfrozen_output: str = os.path.realpath(os.path.join(unfrozen_dir_name, *subdirectory))
		mock_is_frozen.return_value = False
		self.assertEqual(utils.get_directory_path(*subdirectory), unfrozen_output)
