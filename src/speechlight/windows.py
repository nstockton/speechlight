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

"""Windows speech."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import ctypes
import re
import shutil
import sys
from typing import Any, Optional

# Local Modules:
from . import LIB_DIRECTORY, SYSTEM_ARCHITECTURE
from .base import BaseSpeech


if sys.platform == "win32":  # pragma: no cover
	from pywintypes import com_error as ComError  # NOQA: N812


# SAPI constants
SPF_ASYNC: int = 1  # Specifies that the Speak call should be asynchronous.
SPF_PURGE_BEFORE_SPEAK: int = 2  # Purges all pending speak requests prior to this speak call.
SPF_IS_NOT_XML: int = 16  # The input text will not be parsed for XML markup.


def dispatch(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover
	"""
	Calls win32com.client.Dispatch with the supplied arguments.

	If the call fails, then an attempt is made to clear the cache and try again.

	Note:
		https://stackoverflow.com/questions/33267002/why-am-i-suddenly-getting-a-no-attribute-clsidtopackagemap-error-with-win32com

	Args:
			*args: Positional arguments to be passed to win32com.client.Dispatch.
			**kwargs: Key-word only arguments to be passed to win32com.client.Dispatch.

	Returns:
		The resulting COM reference.
	"""
	app = None
	if sys.platform == "win32":
		try:
			from win32com import client  # NOQA: PLC0415

			app = client.Dispatch(*args, **kwargs)
		except AttributeError:
			# Remove cache and try again.
			from win32com.client import gencache  # NOQA: PLC0415

			if not hasattr(gencache, "GetGeneratePath"):
				return None
			cache_location = gencache.GetGeneratePath()
			del gencache
			modules = [m.__name__ for m in sys.modules.values()]
			for module in modules:
				if re.match(r"win32com\.(?:gen_py|client)\..+", module):
					del sys.modules[module]
			if "gen_py" in cache_location:
				shutil.rmtree(cache_location, ignore_errors=True)
			from win32com import client  # NOQA: PLC0415

			app = client.Dispatch(*args, **kwargs)
		except ComError:
			return None
		del client
	return app


class Speech(BaseSpeech):  # NOQA: PLR0904
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
				str(LIB_DIRECTORY / f"nvdaControllerClient{arch}.dll")
			)
			self._sa: ctypes.WinDLL = ctypes.windll.LoadLibrary(str(LIB_DIRECTORY / f"SAAPI{arch}.dll"))
			self._nvda.nvdaController_brailleMessage.argtypes = (ctypes.c_wchar_p,)
			self._nvda.nvdaController_speakText.argtypes = (ctypes.c_wchar_p,)
			self._sa.SA_BrlShowTextW.argtypes = (ctypes.c_wchar_p,)
			self._sa.SA_SayW.argtypes = (ctypes.c_wchar_p,)

	@property
	def sapi(self) -> Any:  # type: ignore[misc] # pragma: no cover
		"""The SAPI COM object."""
		self._sapi = dispatch("SAPI.SpVoice")
		return self._sapi

	@property
	def jfw(self) -> Any:  # type: ignore[misc] # pragma: no cover
		"""The JFW COM object."""
		self._jfw = dispatch("FreedomSci.JawsApi")
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
		*,
		braille: bool = False,
		speak: bool = False,
		interrupt: bool = False,
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

	def jfw_say(self, text: str, *, interrupt: bool = False) -> None:
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

	def nvda_output(self, text: str, *, interrupt: bool = False) -> None:
		"""
		Outputs text using NVDA.

		Args:
			text: The output text.
			interrupt: True if the speech should be silenced before speaking.
		"""
		self.nvda_say(text, interrupt=interrupt)
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

	def nvda_say(self, text: str, *, interrupt: bool = False) -> None:
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

	def sa_output(self, text: str, *, interrupt: bool = False) -> None:
		"""
		Outputs text using System Access.

		Args:
			text: The output text.
			interrupt: True if the speech should be silenced before speaking.
		"""
		self.sa_say(text, interrupt=interrupt)
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

	def sa_say(self, text: str, *, interrupt: bool = False) -> None:
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

	def sapi_say(self, text: str, *, interrupt: bool = False) -> None:
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

	def output(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
		if self.nvda_running():
			self.nvda_output(text, interrupt=interrupt)
		elif self.sa_running():
			self.sa_output(text, interrupt=interrupt)
		elif self.jfw_running():
			self.jfw_output(text, braille=True, speak=True, interrupt=interrupt)
		else:
			self.sapi_say(text, interrupt=interrupt)

	def say(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
		if self.nvda_running():
			self.nvda_say(text, interrupt=interrupt)
		elif self.sa_running():
			self.sa_say(text, interrupt=interrupt)
		elif self.jfw_running():
			self.jfw_say(text, interrupt=interrupt)
		else:
			self.sapi_say(text, interrupt=interrupt)

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
