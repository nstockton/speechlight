# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
from unittest import TestCase, mock

# Speechlight Modules:
from speechlight.dummy import Speech


class TestDummy(TestCase):
	def setUp(self) -> None:
		self.text: str = "This is a test."
		self.speech: Speech = Speech()

	def tearDown(self) -> None:
		del self.speech

	def test_braille(self) -> None:
		self.speech.braille(self.text)

	@mock.patch("speechlight.dummy.Speech.braille")
	@mock.patch("speechlight.dummy.Speech.say")
	def test_output(self, mock_say: mock.Mock, mock_braille: mock.Mock) -> None:
		self.speech.output(self.text, True)
		mock_say.assert_called_once_with(self.text, True)
		mock_braille.assert_called_once_with(self.text)

	@mock.patch("speechlight.dummy.Speech.silence")
	def test_say(self, mock_silence: mock.Mock) -> None:
		self.speech.say(self.text)
		self.speech.say(self.text, True)
		mock_silence.assert_called_once()

	def test_silence(self) -> None:
		self.speech.silence()

	def test_speaking(self) -> None:
		self.assertFalse(self.speech.speaking())
