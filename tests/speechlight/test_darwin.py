# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import platform
from unittest import TestCase, mock, skipUnless


SYSTEM_PLATFORM: str = platform.system()


if SYSTEM_PLATFORM == "Darwin":
	from speechlight.darwin import Speech


@skipUnless(SYSTEM_PLATFORM == "Darwin", "only runs on macOS")
class TestDarwin(TestCase):
	def setUp(self) -> None:
		self.text: str = "This is a test."
		self.speech: Speech = Speech()

	def tearDown(self) -> None:
		del self.speech

	def test_braille(self) -> None:
		self.speech.braille(self.text)

	@mock.patch("speechlight.darwin.Speech.braille")
	@mock.patch("speechlight.darwin.Speech.say")
	def test_output(self, mock_say: mock.Mock, mock_braille: mock.Mock) -> None:
		self.speech.output(self.text, True)
		mock_say.assert_called_once_with(self.text, True)
		mock_braille.assert_called_once_with(self.text)

	@mock.patch("speechlight.darwin.Speech.silence")
	def test_say(self, mock_silence: mock.Mock) -> None:
		with mock.patch.object(self.speech, "darwin", mock.Mock()) as mock_darwin:
			self.speech.say(self.text)
			mock_darwin.startSpeakingString_.assert_called_once_with(self.text)
			mock_darwin.reset_mock()
			self.speech.say(self.text, True)
			mock_silence.assert_called_once()
			mock_darwin.startSpeakingString_.assert_called_once_with(self.text)

	def test_silence(self) -> None:
		with mock.patch.object(self.speech, "darwin", mock.Mock()) as mock_darwin:
			self.speech.silence()
			mock_darwin.stopSpeaking.assert_called_once()

	def test_speaking(self) -> None:
		with mock.patch.object(self.speech, "darwin", mock.Mock()) as mock_darwin:
			mock_darwin.isSpeaking.return_value = False
			self.assertFalse(self.speech.speaking())
			mock_darwin.isSpeaking.assert_called_once()
