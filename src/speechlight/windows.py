# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import ctypes
import os
import sys
from collections.abc import Callable
from contextlib import suppress
from typing import Any, Optional

# Local Modules:
from . import LIB_DIRECTORY, SYSTEM_ARCHITECTURE
from .base import BaseSpeech


if sys.platform == "win32":  # pragma: no cover
	import win32com.client
	from pywintypes import com_error as ComError


# SAPI constants
SPF_ASYNC: int = 1  # Specifies that the Speak call should be asynchronous.
SPF_PURGE_BEFORE_SPEAK: int = 2  # Purges all pending speak requests prior to this speak call.
SPF_IS_NOT_XML: int = 16  # The input text will not be parsed for XML markup.


class MockNVDA(object):  # pragma: no cover
	def nvdaController_brailleMessage(self, text: str) -> None:
		pass

	def nvdaController_speakText(self, text: str) -> None:
		pass

	def nvdaController_cancelSpeech(self) -> None:
		pass

	def nvdaController_testIfRunning(self) -> int:
		return -1


class MockSA(object):  # pragma: no cover
	def SA_BrlShowTextW(self, text: str) -> None:
		pass

	def SA_SayW(self, text: str) -> None:
		pass

	def SA_StopAudio(self) -> None:
		pass

	def SA_IsRunning(self) -> int:
		return 0


class Speech(BaseSpeech):
	def __init__(self) -> None:  # pragma: no cover
		self._sapi: Optional[Any] = None
		self._jfw: Optional[Any] = None
		if sys.platform == "win32":
			self.find_window: ctypes._NamedFuncPointer = ctypes.WinDLL("user32").FindWindowW
			self.find_window.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
			self.find_window.restype = ctypes.c_void_p
			self.nvda: ctypes.WinDLL
			self.sa: ctypes.WinDLL
			if SYSTEM_ARCHITECTURE == "32bit":
				self.nvda = ctypes.windll.LoadLibrary(
					os.path.join(LIB_DIRECTORY, "nvdaControllerClient32.dll")
				)
				self.sa = ctypes.windll.LoadLibrary(os.path.join(LIB_DIRECTORY, "SAAPI32.dll"))
			else:
				self.nvda = ctypes.windll.LoadLibrary(
					os.path.join(LIB_DIRECTORY, "nvdaControllerClient64.dll")
				)
				self.sa = ctypes.windll.LoadLibrary(os.path.join(LIB_DIRECTORY, "SAAPI64.dll"))
			self.nvda.nvdaController_brailleMessage.argtypes = (ctypes.c_wchar_p,)
			self.nvda.nvdaController_speakText.argtypes = (ctypes.c_wchar_p,)
			self.sa.SA_BrlShowTextW.argtypes = (ctypes.c_wchar_p,)
			self.sa.SA_SayW.argtypes = (ctypes.c_wchar_p,)
		else:
			self.find_window: Callable[..., None] = lambda *args: None
			self.nvda = MockNVDA()
			self.sa = MockSA()

	@property
	def sapi(self) -> Any:  # type: ignore[misc] # pragma: no cover
		"""The SAPI COM object."""
		if sys.platform == "win32":
			with suppress(ComError):
				self._sapi = win32com.client.Dispatch("SAPI.SpVoice")
		return self._sapi

	@property
	def jfw(self) -> Any:  # type: ignore[misc] # pragma: no cover
		"""The JFW COM object."""
		if sys.platform == "win32":
			with suppress(ComError):
				self._jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
		return self._jfw

	def jfw_braille(self, text: str) -> None:
		"""
		Brailles text using JFW.

		Args:
			text: The text to braille.
		"""
		self.jfw_output(text, braille=True)

	def jfw_output(
		self,
		text: str,
		braille: Optional[bool] = None,
		speak: Optional[bool] = None,
		interrupt: Optional[bool] = None,
	) -> None:
		"""
		Outputs text using JFW.

		Args:
			text: The output text.
			braille: Output text in braille.
			speak: Output text using speech.
			interrupt: True if the speech should be silenced before speaking.
		"""
		jfw = self.jfw
		if jfw is not None:
			if speak:
				jfw.SayString(text, int(bool(interrupt)))
			if braille:
				jfw.RunFunction('BrailleString("{text}")'.format(text=text.replace('"', "'")))

	def jfw_running(self) -> bool:
		"""
		Determines if JFW is running.

		Returns:
			True if JFW is running, False otherwise.
		"""
		return bool(self.find_window("JFWUI2", None))

	def jfw_say(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Speak text using JFW.

		Args:
			text: The text to be spoken.
			interrupt: True if the speech should be silenced before speaking.
		"""
		self.jfw_output(text, speak=True, interrupt=interrupt)

	def jfw_silence(self) -> None:
		"""Cancels JFW speech and flushes the speech buffer."""
		jfw = self.jfw
		if jfw is not None:
			jfw.StopSpeech()

	def nvda_braille(self, text: str) -> None:
		"""
		Brailles text using NVDA.

		Args:
			text: The text to braille.
		"""
		self.nvda.nvdaController_brailleMessage(text)

	def nvda_output(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Outputs text using NVDA.

		Args:
			text: The output text.
			interrupt: True if the speech should be silenced before speaking.
		"""
		self.nvda_say(text, interrupt)
		self.nvda_braille(text)

	def nvda_running(self) -> bool:
		"""
		Determines if NVDA is running.

		Returns:
			True if NVDA is running, False otherwise.
		"""
		return bool(self.nvda.nvdaController_testIfRunning() == 0)

	def nvda_say(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Speak text using NVDA.

		Args:
			text: The text to be spoken.
			interrupt: True if the speech should be silenced before speaking.
		"""
		if interrupt:
			self.nvda_silence()
		self.nvda.nvdaController_speakText(text)

	def nvda_silence(self) -> None:
		"""Cancels NVDA speech and flushes the speech buffer."""
		self.nvda.nvdaController_cancelSpeech()

	def sa_braille(self, text: str) -> None:
		"""
		Brailles text using System Access.

		Args:
			text: The text to braille.
		"""
		self.sa.SA_BrlShowTextW(text)

	def sa_output(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Outputs text using System Access.

		Args:
			text: The output text.
			interrupt: True if the speech should be silenced before speaking.
		"""
		self.sa_say(text, interrupt)
		self.sa_braille(text)

	def sa_running(self) -> bool:
		"""
		Determines if System Access is running.

		Returns:
			True if System Access is running, False otherwise.
		"""
		return bool(self.sa.SA_IsRunning())

	def sa_say(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Speak text using System Access.

		Args:
			text: The text to be spoken.
			interrupt: True if the speech should be silenced before speaking.
		"""
		if interrupt:
			self.sa_silence()
		self.sa.SA_SayW(text)

	def sa_silence(self) -> None:
		"""Cancels System Access speech and flushes the speech buffer."""
		self.sa.SA_StopAudio()

	def sapi_say(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Speak text using SAPI.

		Args:
			text: The text to be spoken.
			interrupt: True if the speech should be silenced before speaking.
		"""
		if self.sapi is not None:
			if interrupt:
				self.sapi.Speak(text, SPF_ASYNC | SPF_PURGE_BEFORE_SPEAK | SPF_IS_NOT_XML)
			else:
				self.sapi.Speak(text, SPF_ASYNC | SPF_IS_NOT_XML)

	def sapi_silence(self) -> None:
		"""Cancels SAPI speech and flushes the speech buffer."""
		if self.sapi is not None:
			self.sapi.Speak("", SPF_ASYNC | SPF_PURGE_BEFORE_SPEAK | SPF_IS_NOT_XML)

	def braille(self, text: str) -> None:
		if self.nvda_running():
			self.nvda_braille(text)
		elif self.sa_running():
			self.sa_braille(text)
		elif self.jfw_running():
			self.jfw_braille(text)

	def output(self, text: str, interrupt: Optional[bool] = None) -> None:
		if self.nvda_running():
			self.nvda_output(text, interrupt)
		elif self.sa_running():
			self.sa_output(text, interrupt)
		elif self.jfw_running():
			self.jfw_output(text, braille=True, speak=True, interrupt=interrupt)
		else:
			self.sapi_say(text, interrupt)

	def say(self, text: str, interrupt: Optional[bool] = None) -> None:
		if self.nvda_running():
			self.nvda_say(text, interrupt)
		elif self.sa_running():
			self.sa_say(text, interrupt)
		elif self.jfw_running():
			self.jfw_say(text, interrupt)
		else:
			self.sapi_say(text, interrupt)

	def silence(self) -> None:
		if self.nvda_running():
			self.nvda_silence()
		elif self.sa_running():
			self.sa_silence()
		elif self.jfw_running():
			self.jfw_silence()
		else:
			self.sapi_silence()

	def speaking(self) -> bool:
		if self.nvda_running() or self.sa_running() or self.jfw_running():
			# None of the screen reader APIs support retrieving speaking status.
			return False
		if self.sapi is not None:
			return bool(self.sapi.Status.RunningState != 1)
		return False
