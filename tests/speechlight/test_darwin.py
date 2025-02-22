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
from unittest import TestCase, mock

# Speechlight Modules:
from speechlight.darwin import Speech


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
		self.speech.output(self.text, interrupt=True)
		mock_say.assert_called_once_with(self.text, interrupt=True)
		mock_braille.assert_called_once_with(self.text)

	@mock.patch("speechlight.darwin.Speech.silence")
	def test_say(self, mock_silence: mock.Mock) -> None:
		with mock.patch.object(self.speech, "_darwin", mock.Mock()) as mock_darwin:
			self.speech.say(self.text)
			mock_darwin.startSpeakingString_.assert_called_once_with(self.text)
			mock_darwin.reset_mock()
			self.speech.say(self.text, interrupt=True)
			mock_silence.assert_called_once()
			mock_darwin.startSpeakingString_.assert_called_once_with(self.text)

	def test_silence(self) -> None:
		with mock.patch.object(self.speech, "_darwin", mock.Mock()) as mock_darwin:
			self.speech.silence()
			mock_darwin.stopSpeaking.assert_called_once()

	def test_speaking(self) -> None:
		with mock.patch.object(self.speech, "_darwin", mock.Mock()) as mock_darwin:
			mock_darwin.isSpeaking.return_value = False
			self.assertFalse(self.speech.speaking())
			mock_darwin.isSpeaking.assert_called_once()
