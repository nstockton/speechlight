"""Windows speech."""


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import ctypes
import os
import sys
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


class Speech(BaseSpeech):
	"""Implements Speech for Windows."""

	_find_window: Optional[Any] = None
	_nvda: Optional[Any] = None
	_sa: Optional[Any] = None
	_sapi: Optional[Any] = None
	_jfw: Optional[Any] = None

	def __init__(self) -> None:  # pragma: no cover
		"""Defines the constructor."""
		if sys.platform == "win32":
			self._find_window: ctypes._NamedFuncPointer = ctypes.WinDLL("user32").FindWindowW
			self._find_window.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
			self._find_window.restype = ctypes.c_void_p
			arch: str = "32" if SYSTEM_ARCHITECTURE == "32bit" else "64"
			self._nvda: ctypes.WinDLL = ctypes.windll.LoadLibrary(
				os.path.join(LIB_DIRECTORY, f"nvdaControllerClient{arch}.dll")
			)
			self._sa: ctypes.WinDLL = ctypes.windll.LoadLibrary(
				os.path.join(LIB_DIRECTORY, f"SAAPI{arch}.dll")
			)
			self._nvda.nvdaController_brailleMessage.argtypes = (ctypes.c_wchar_p,)
			self._nvda.nvdaController_speakText.argtypes = (ctypes.c_wchar_p,)
			self._sa.SA_BrlShowTextW.argtypes = (ctypes.c_wchar_p,)
			self._sa.SA_SayW.argtypes = (ctypes.c_wchar_p,)

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
		status: bool = False
		if self._find_window is not None:
			status = bool(self._find_window("JFWUI2", None))
		return status

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
		if self._nvda is not None:
			self._nvda.nvdaController_brailleMessage(text)

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
		status: bool = False
		if self._nvda is not None:
			status = bool(self._nvda.nvdaController_testIfRunning() == 0)
		return status

	def nvda_say(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Speak text using NVDA.

		Args:
			text: The text to be spoken.
			interrupt: True if the speech should be silenced before speaking.
		"""
		if self._nvda is not None:
			if interrupt:
				self.nvda_silence()
			self._nvda.nvdaController_speakText(text)

	def nvda_silence(self) -> None:
		"""Cancels NVDA speech and flushes the speech buffer."""
		if self._nvda is not None:
			self._nvda.nvdaController_cancelSpeech()

	def sa_braille(self, text: str) -> None:
		"""
		Brailles text using System Access.

		Args:
			text: The text to braille.
		"""
		if self._sa is not None:
			self._sa.SA_BrlShowTextW(text)

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
		status: bool = False
		if self._sa is not None:
			status = bool(self._sa.SA_IsRunning())
		return status

	def sa_say(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Speak text using System Access.

		Args:
			text: The text to be spoken.
			interrupt: True if the speech should be silenced before speaking.
		"""
		if self._sa is not None:
			if interrupt:
				self.sa_silence()
			self._sa.SA_SayW(text)

	def sa_silence(self) -> None:
		"""Cancels System Access speech and flushes the speech buffer."""
		if self._sa is not None:
			self._sa.SA_StopAudio()

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

	def braille(self, text: str) -> None:  # NOQA: D102
		if self.nvda_running():
			self.nvda_braille(text)
		elif self.sa_running():
			self.sa_braille(text)
		elif self.jfw_running():
			self.jfw_braille(text)

	def output(self, text: str, interrupt: Optional[bool] = None) -> None:  # NOQA: D102
		if self.nvda_running():
			self.nvda_output(text, interrupt)
		elif self.sa_running():
			self.sa_output(text, interrupt)
		elif self.jfw_running():
			self.jfw_output(text, braille=True, speak=True, interrupt=interrupt)
		else:
			self.sapi_say(text, interrupt)

	def say(self, text: str, interrupt: Optional[bool] = None) -> None:  # NOQA: D102
		if self.nvda_running():
			self.nvda_say(text, interrupt)
		elif self.sa_running():
			self.sa_say(text, interrupt)
		elif self.jfw_running():
			self.jfw_say(text, interrupt)
		else:
			self.sapi_say(text, interrupt)

	def silence(self) -> None:  # NOQA: D102
		if self.nvda_running():
			self.nvda_silence()
		elif self.sa_running():
			self.sa_silence()
		elif self.jfw_running():
			self.jfw_silence()
		else:
			self.sapi_silence()

	def speaking(self) -> bool:  # NOQA: D102
		if self.nvda_running() or self.sa_running() or self.jfw_running():
			# None of the screen reader APIs support retrieving speaking status.
			return False
		if self.sapi is not None:
			return bool(self.sapi.Status.RunningState != 1)
		return False
