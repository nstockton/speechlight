# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import _imp
import ctypes
import os
import platform
import sys
import time


SYSTEM_PLATFORM = platform.system()

# SAPI constants
SPF_ASYNC = 1 # Specifies that the Speak call should be asynchronous.
SPF_PURGEBEFORESPEAK = 2 # Purges all pending speak requests prior to this speak call.
SPF_IS_NOT_XML = 16 # The input text will not be parsed for XML markup.


# Platform Specific Third-party Modules:
if SYSTEM_PLATFORM == "Windows":
	import win32com.client
	from pywintypes import com_error as ComError
	FindWindow = ctypes.WinDLL("user32").FindWindowW
	FindWindow.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p]
	FindWindow.restype = ctypes.c_void_p
elif SYSTEM_PLATFORM == "Darwin":
	# For Mac OS X, we need the NSSpeechSynthesizer class from the Cocoa module.
	from Cocoa import NSSpeechSynthesizer


def getFreezer():
	"""Return the name of the package used to freeze the code, or None."""
	# https://github.com/blackmagicgirl/ktools/blob/master/ktools/utils.py
	frozen = getattr(sys, "frozen", None)
	if frozen and hasattr(sys, "_MEIPASS"):
		return "pyinstaller"
	elif frozen is True:
		return "cx_freeze"
	elif frozen in ("windows_exe", "console_exe", "dll"):
		return "py2exe"
	elif frozen == "macosx_app":
		return "py2app"
	elif hasattr(sys, "importers"):
		return "old_py2exe"
	elif _imp.is_frozen("__main__"):
		return "tools/freeze"
	return frozen


def where():
	"""Return the directory where the screen reader API DLL files are stored."""
	if getFreezer():
		path = os.path.dirname(sys.executable)
	else:
		path = os.path.join(os.path.dirname(__file__))
	return os.path.realpath(os.path.join(path, "speech_libs"))


class Speech(object):
	def __init__(self):
		if SYSTEM_PLATFORM == "Darwin":
			# Allocate and initialize the default TTS.
			self.darwin = NSSpeechSynthesizer.alloc().init()
		elif SYSTEM_PLATFORM == "Windows":
			lib_directory = where()
			if platform.architecture()[0] == "32bit":
				self.nvda = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "nvdaControllerClient32.dll"))
				self.sa = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "SAAPI32.dll"))
			else:
				self.nvda = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "nvdaControllerClient64.dll"))
				self.sa = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "SAAPI64.dll"))
			self.nvda.nvdaController_brailleMessage.argtypes = (ctypes.c_wchar_p,)
			self.nvda.nvdaController_speakText.argtypes = (ctypes.c_wchar_p,)
			self.sa.SA_BrlShowTextW.argtypes = (ctypes.c_wchar_p,)
			self.sa.SA_SayW.argtypes = (ctypes.c_wchar_p,)
			try:
				self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
			except ComError:
				self.sapi = None

	def jfw_braille(self, text):
		try:
			jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
		except ComError:
			return
		jfw.RunFunction("BrailleString(\"{text}\")".format(text=text.replace('"', "'")))

	def jfw_running(self):
		return FindWindow("JFWUI2", None)

	def jfw_say(self, text, interrupt=False):
		try:
			jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
		except ComError:
			return
		jfw.SayString(text, int(interrupt))

	def jfw_silence(self):
		try:
			jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
		except ComError:
			return
		jfw.StopSpeech()

	def nvda_braille(self, text):
		self.nvda.nvdaController_brailleMessage(text)

	def nvda_running(self):
		return self.nvda.nvdaController_testIfRunning() == 0

	def nvda_say(self, text, interrupt=False):
		if interrupt:
			self.nvda.nvdaController_cancelSpeech()
		self.nvda.nvdaController_speakText(text)

	def nvda_silence(self):
		self.nvda.nvdaController_cancelSpeech()

	def sa_braille(self, text):
		self.sa.SA_BrlShowTextW(text)

	def sa_running(self):
		return self.sa.SA_IsRunning()

	def sa_say(self, text, interrupt=False):
		if interrupt:
			self.sa.SA_StopAudio()
		self.sa.SA_SayW(text)

	def sa_silence(self):
		self.sa.SA_StopAudio()

	def sapi_running(self):
		return self.sapi is not None

	def sapi_say(self, text, interrupt=False):
		self.sapi.Speak(text, SPF_ASYNC | SPF_PURGEBEFORESPEAK | SPF_IS_NOT_XML if interrupt else SPF_ASYNC | SPF_IS_NOT_XML)

	def sapi_silence(self):
		self.sapi.Speak("", SPF_ASYNC | SPF_PURGEBEFORESPEAK | SPF_IS_NOT_XML)

	def output(self, text, interrupt=False, speak=True, braille=True):
		if SYSTEM_PLATFORM == "Darwin":
			if interrupt:
				self.darwin.stopSpeaking()
			self.darwin.startSpeakingString_(text)
		elif SYSTEM_PLATFORM == "Windows":
			if self.nvda_running():
				if speak:
					self.nvda_say(text, interrupt)
				if braille:
					self.nvda_braille(text)
			elif self.sa_running():
				if speak:
					self.sa_say(text, interrupt)
				if braille:
					self.sa_braille(text, interrupt)
			elif self.jfw_running():
				if speak:
					self.jfw_say(text, interrupt)
				if braille:
					self.jfw_braille(text, interrupt)
			elif self.sapi_running():
				self.sapi_say(text, interrupt)

	def braille(self, text):
		self.output(text, speak=False, braille=True)

	def say(self, text, interrupt=False):
		self.output(text, interrupt, speak=True, braille=False)

	def silence(self):
		if SYSTEM_PLATFORM == "Darwin":
			self.darwin.stopSpeaking()
		elif SYSTEM_PLATFORM == "Windows":
			if self.nvda_running():
				self.nvda_silence()
			elif self.sa_running():
				self.sa_silence()
			elif self.jfw_running():
				self.jfw_silence()
			elif self.sapi_running():
				self.sapi_silence()

	def speaking(self):
		if SYSTEM_PLATFORM == "Darwin":
			return self.darwin.isSpeaking()
		elif SYSTEM_PLATFORM == "Windows":
			if self.nvda_running() or self.sa_running() or self.jfw_running():
				# None of the screen reader APIs support retrieving speaking status.
				return False
			elif self.sapi_running():
				return self.sapi.Status.RunningState != 1


if __name__ == "__main__":
	tts = Speech()
	tts.say("hello world!")
	# Make sure the tts engine finishes speaking before terminating.
	while tts.speaking():
		time.sleep(0.1)
