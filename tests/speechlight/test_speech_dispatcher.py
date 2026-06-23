# Copyright (C) 2026 Nick Stockton
# SPDX-License-Identifier: MIT
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
import io
from unittest import TestCase, mock

# Speechlight Modules:
from speechlight.speech_dispatcher import Speech


@mock.patch("speechlight.speech_dispatcher.sys.stdout", io.StringIO())  # Prevent output from print.
class TestSpeechDispatcher(TestCase):
	def setUp(self) -> None:
		self.text: str = "This is a test."
		self.speech: Speech = Speech()

	def tearDown(self) -> None:
		del self.speech

	def test_braille(self) -> None:
		self.speech.braille(self.text)

	@mock.patch("speechlight.speech_dispatcher.Speech.braille")
	@mock.patch("speechlight.speech_dispatcher.Speech.say")
	def test_output(self, mock_say: mock.Mock, mock_braille: mock.Mock) -> None:
		self.speech.output(self.text, interrupt=True)
		mock_say.assert_called_once_with(self.text, interrupt=True)
		mock_braille.assert_called_once_with(self.text)

	@mock.patch("speechlight.speech_dispatcher.Speech.silence")
	def test_say(self, mock_silence: mock.Mock) -> None:
		with mock.patch.object(self.speech, "_sd", mock.Mock()) as mock_sd:
			self.speech.say(self.text)
			mock_sd.speak.assert_called_once()
			mock_sd.reset_mock()
			self.speech.say(self.text, interrupt=True)
			mock_silence.assert_called_once()
			mock_sd.speak.assert_called_once()

	def test_silence(self) -> None:
		with mock.patch.object(self.speech, "_sd", mock.Mock()) as mock_sd:
			self.speech.silence()
			mock_sd.cancel.assert_called_once()

	def test_speaking(self) -> None:
		self.speech._is_speaking = True  # NOQA: SLF001
		self.assertEqual(self.speech.speaking(), self.speech._is_speaking)  # NOQA: SLF001
		self.speech._is_speaking = False  # NOQA: SLF001
		self.assertEqual(self.speech.speaking(), self.speech._is_speaking)  # NOQA: SLF001
