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
from speechlight.windows import SPF_ASYNC, SPF_IS_NOT_XML, SPF_PURGE_BEFORE_SPEAK, Speech


class TestWindows(TestCase):  # NOQA: PLR0904
	def setUp(self) -> None:
		self.text: str = "This is a test."
		self.speech: Speech = Speech()

	def tearDown(self) -> None:
		del self.speech

	@mock.patch("speechlight.windows.Speech.jfw_output")
	def test_jfw_braille(self, mock_jfw_output: mock.Mock) -> None:
		self.speech.jfw_braille(self.text)
		mock_jfw_output.assert_called_once_with(self.text, braille=True)

	def test_jfw_output(self) -> None:
		with mock.patch("speechlight.windows.Speech.jfw", mock.PropertyMock()) as mock_jfw:
			text: str = f'{self.text} "quotes"'
			expected_text: str = text.replace('"', "'")
			self.speech.jfw_output(text, braille=True)
			mock_jfw.return_value.RunFunction.assert_called_once_with(f'BrailleString("{expected_text}")')
			mock_jfw.return_value.reset_mock()
			self.speech.jfw_output(self.text, speak=True)
			mock_jfw.return_value.SayString.assert_called_once_with(self.text, 0)
			mock_jfw.return_value.reset_mock()
			self.speech.jfw_output(self.text, speak=True, interrupt=True)
			mock_jfw.return_value.SayString.assert_called_once_with(self.text, 1)
			mock_jfw.return_value.reset_mock()
			self.speech.jfw_output(self.text, braille=False, speak=False)
			self.speech.jfw_output(self.text, braille=True, speak=True, interrupt=True)
			mock_jfw.return_value.SayString.assert_called_once_with(self.text, 1)
			mock_jfw.return_value.RunFunction.assert_called_once_with(f'BrailleString("{self.text}")')

	def test_jfw_running(self) -> None:
		with mock.patch.object(self.speech, "_find_window") as mock_find_window:
			mock_find_window.return_value = 0  # Not found.
			self.assertFalse(self.speech.jfw_running())
			mock_find_window.return_value = 1  # Found.
			self.assertTrue(self.speech.jfw_running())

	@mock.patch("speechlight.windows.Speech.jfw_output")
	def test_jfw_say(self, mock_jfw_output: mock.Mock) -> None:
		self.speech.jfw_say(self.text, interrupt=True)
		mock_jfw_output.assert_called_once_with(self.text, speak=True, interrupt=True)

	def test_jfw_silence(self) -> None:
		with mock.patch("speechlight.windows.Speech.jfw", mock.PropertyMock()) as mock_jfw:
			self.speech.jfw_silence()
			mock_jfw.return_value.StopSpeech.assert_called_once()

	def test_nvda_braille(self) -> None:
		with mock.patch.object(self.speech, "_nvda") as mock_nvda:
			self.speech.nvda_braille(self.text)
			mock_nvda.nvdaController_brailleMessage.assert_called_once_with(self.text)

	@mock.patch("speechlight.windows.Speech.nvda_braille")
	@mock.patch("speechlight.windows.Speech.nvda_say")
	def test_nvda_output(self, mock_nvda_say: mock.Mock, mock_nvda_braille: mock.Mock) -> None:
		self.speech.nvda_output(self.text, interrupt=True)
		mock_nvda_say.assert_called_once_with(self.text, interrupt=True)
		mock_nvda_braille.assert_called_once_with(self.text)

	def test_nvda_running(self) -> None:
		with mock.patch.object(self.speech, "_nvda") as mock_nvda:
			self.speech.nvda_running()
			mock_nvda.nvdaController_testIfRunning.assert_called_once()

	@mock.patch("speechlight.windows.Speech.nvda_silence")
	def test_nvda_say(self, mock_nvda_silence: mock.Mock) -> None:
		with mock.patch.object(self.speech, "_nvda") as mock_nvda:
			self.speech.nvda_say(self.text)
			mock_nvda.nvdaController_speakText.assert_called_once_with(self.text)
			mock_nvda.reset_mock()
			self.speech.nvda_say(self.text, interrupt=True)
			mock_nvda_silence.assert_called_once()
			mock_nvda.nvdaController_speakText.assert_called_once_with(self.text)

	def test_nvda_silence(self) -> None:
		with mock.patch.object(self.speech, "_nvda") as mock_nvda:
			self.speech.nvda_silence()
			mock_nvda.nvdaController_cancelSpeech.assert_called_once()

	def test_sa_braille(self) -> None:
		with mock.patch.object(self.speech, "_sa") as mock_sa:
			self.speech.sa_braille(self.text)
			mock_sa.SA_BrlShowTextW.assert_called_once_with(self.text)

	@mock.patch("speechlight.windows.Speech.sa_braille")
	@mock.patch("speechlight.windows.Speech.sa_say")
	def test_sa_output(self, mock_sa_say: mock.Mock, mock_sa_braille: mock.Mock) -> None:
		self.speech.sa_output(self.text, interrupt=True)
		mock_sa_say.assert_called_once_with(self.text, interrupt=True)
		mock_sa_braille.assert_called_once_with(self.text)

	def test_sa_running(self) -> None:
		with mock.patch.object(self.speech, "_sa") as mock_sa:
			self.speech.sa_running()
			mock_sa.SA_IsRunning.assert_called_once()

	@mock.patch("speechlight.windows.Speech.sa_silence")
	def test_sa_say(self, mock_sa_silence: mock.Mock) -> None:
		with mock.patch.object(self.speech, "_sa") as mock_sa:
			self.speech.sa_say(self.text)
			mock_sa.SA_SayW.assert_called_once_with(self.text)
			mock_sa.reset_mock()
			self.speech.sa_say(self.text, interrupt=True)
			mock_sa_silence.assert_called_once()
			mock_sa.SA_SayW.assert_called_once_with(self.text)

	def test_sa_silence(self) -> None:
		with mock.patch.object(self.speech, "_sa") as mock_sa:
			self.speech.sa_silence()
			mock_sa.SA_StopAudio.assert_called_once()

	def test_sapi_say(self) -> None:
		with mock.patch("speechlight.windows.Speech.sapi", mock.PropertyMock()) as mock_sapi:
			self.speech.sapi_say(self.text)
			mock_sapi.return_value.Speak.assert_called_once_with(self.text, SPF_ASYNC | SPF_IS_NOT_XML)
			mock_sapi.reset_mock()
			self.speech.sapi_say(self.text, interrupt=True)
			mock_sapi.return_value.Speak.assert_called_once_with(
				self.text, SPF_ASYNC | SPF_PURGE_BEFORE_SPEAK | SPF_IS_NOT_XML
			)

	def test_sapi_silence(self) -> None:
		with mock.patch("speechlight.windows.Speech.sapi", mock.PropertyMock()) as mock_sapi:
			self.speech.sapi_silence()
			mock_sapi.return_value.Speak.assert_called_once_with(
				"", SPF_ASYNC | SPF_PURGE_BEFORE_SPEAK | SPF_IS_NOT_XML
			)

	@mock.patch("speechlight.windows.Speech.jfw_braille")
	@mock.patch("speechlight.windows.Speech.jfw_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.sa_braille")
	@mock.patch("speechlight.windows.Speech.sa_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.nvda_braille")
	@mock.patch("speechlight.windows.Speech.nvda_running", return_value=False)
	def test_braille(
		self,
		mock_nvda_running: mock.Mock,
		mock_nvda_braille: mock.Mock,
		mock_sa_running: mock.Mock,
		mock_sa_braille: mock.Mock,
		mock_jfw_running: mock.Mock,
		mock_jfw_braille: mock.Mock,
	) -> None:
		self.speech.braille(self.text)
		mock_nvda_running.return_value = True
		self.speech.braille(self.text)
		mock_nvda_running.return_value = False
		mock_sa_running.return_value = True
		self.speech.braille(self.text)
		mock_sa_running.return_value = False
		mock_jfw_running.return_value = True
		self.speech.braille(self.text)
		mock_jfw_running.return_value = False
		mock_nvda_braille.assert_called_once_with(self.text)
		mock_sa_braille.assert_called_once_with(self.text)
		mock_jfw_braille.assert_called_once_with(self.text)

	@mock.patch("speechlight.windows.Speech.sapi_say")
	@mock.patch("speechlight.windows.Speech.jfw_output")
	@mock.patch("speechlight.windows.Speech.jfw_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.sa_output")
	@mock.patch("speechlight.windows.Speech.sa_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.nvda_output")
	@mock.patch("speechlight.windows.Speech.nvda_running", return_value=False)
	def test_output(
		self,
		mock_nvda_running: mock.Mock,
		mock_nvda_output: mock.Mock,
		mock_sa_running: mock.Mock,
		mock_sa_output: mock.Mock,
		mock_jfw_running: mock.Mock,
		mock_jfw_output: mock.Mock,
		mock_sapi_say: mock.Mock,
	) -> None:
		mock_nvda_running.return_value = True
		self.speech.output(self.text, interrupt=True)
		mock_nvda_running.return_value = False
		mock_sa_running.return_value = True
		self.speech.output(self.text, interrupt=True)
		mock_sa_running.return_value = False
		mock_jfw_running.return_value = True
		self.speech.output(self.text, interrupt=True)
		mock_jfw_running.return_value = False
		self.speech.output(self.text, interrupt=True)
		mock_nvda_output.assert_called_once_with(self.text, interrupt=True)
		mock_sa_output.assert_called_once_with(self.text, interrupt=True)
		mock_jfw_output.assert_called_once_with(self.text, braille=True, speak=True, interrupt=True)
		mock_sapi_say.assert_called_once_with(self.text, interrupt=True)

	@mock.patch("speechlight.windows.Speech.sapi_say")
	@mock.patch("speechlight.windows.Speech.jfw_say")
	@mock.patch("speechlight.windows.Speech.jfw_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.sa_say")
	@mock.patch("speechlight.windows.Speech.sa_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.nvda_say")
	@mock.patch("speechlight.windows.Speech.nvda_running", return_value=False)
	def test_say(
		self,
		mock_nvda_running: mock.Mock,
		mock_nvda_say: mock.Mock,
		mock_sa_running: mock.Mock,
		mock_sa_say: mock.Mock,
		mock_jfw_running: mock.Mock,
		mock_jfw_say: mock.Mock,
		mock_sapi_say: mock.Mock,
	) -> None:
		mock_nvda_running.return_value = True
		self.speech.say(self.text, interrupt=True)
		mock_nvda_running.return_value = False
		mock_sa_running.return_value = True
		self.speech.say(self.text, interrupt=True)
		mock_sa_running.return_value = False
		mock_jfw_running.return_value = True
		self.speech.say(self.text, interrupt=True)
		mock_jfw_running.return_value = False
		self.speech.say(self.text, interrupt=True)
		mock_nvda_say.assert_called_once_with(self.text, interrupt=True)
		mock_sa_say.assert_called_once_with(self.text, interrupt=True)
		mock_jfw_say.assert_called_once_with(self.text, interrupt=True)
		mock_sapi_say.assert_called_once_with(self.text, interrupt=True)

	@mock.patch("speechlight.windows.Speech.sapi_silence")
	@mock.patch("speechlight.windows.Speech.jfw_silence")
	@mock.patch("speechlight.windows.Speech.jfw_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.sa_silence")
	@mock.patch("speechlight.windows.Speech.sa_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.nvda_silence")
	@mock.patch("speechlight.windows.Speech.nvda_running", return_value=False)
	def test_silence(
		self,
		mock_nvda_running: mock.Mock,
		mock_nvda_silence: mock.Mock,
		mock_sa_running: mock.Mock,
		mock_sa_silence: mock.Mock,
		mock_jfw_running: mock.Mock,
		mock_jfw_silence: mock.Mock,
		mock_sapi_silence: mock.Mock,
	) -> None:
		mock_nvda_running.return_value = True
		self.speech.silence()
		mock_nvda_running.return_value = False
		mock_sa_running.return_value = True
		self.speech.silence()
		mock_sa_running.return_value = False
		mock_jfw_running.return_value = True
		self.speech.silence()
		mock_jfw_running.return_value = False
		self.speech.silence()
		mock_nvda_silence.assert_called_once_with()
		mock_sa_silence.assert_called_once_with()
		mock_jfw_silence.assert_called_once_with()
		mock_sapi_silence.assert_called_once_with()

	@mock.patch("speechlight.windows.Speech.jfw_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.sa_running", return_value=False)
	@mock.patch("speechlight.windows.Speech.nvda_running", return_value=False)
	def test_speaking(
		self,
		mock_nvda_running: mock.Mock,
		mock_sa_running: mock.Mock,
		mock_jfw_running: mock.Mock,
	) -> None:
		with mock.patch("speechlight.windows.Speech.sapi", mock.PropertyMock()) as mock_sapi:
			mock_nvda_running.return_value = True
			self.assertFalse(self.speech.speaking())
			mock_nvda_running.return_value = False
			mock_sa_running.return_value = True
			self.assertFalse(self.speech.speaking())
			mock_sa_running.return_value = False
			mock_jfw_running.return_value = True
			self.assertFalse(self.speech.speaking())
			mock_jfw_running.return_value = False
			mock_sapi.return_value.Status.RunningState = 0  # Speaking.
			self.assertTrue(self.speech.speaking())
			mock_sapi.return_value.Status.RunningState = 1  # Not Speaking.
			self.assertFalse(self.speech.speaking())
			mock_sapi.return_value = None
			self.assertFalse(self.speech.speaking())
