# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Built-in modules
import ctypes
import os
import platform
import sys

PLATFORM_SYSTEM = platform.system()

# Platform specific third-party modules
if PLATFORM_SYSTEM == "Windows":
	import win32gui
	import win32com.client
	import pywintypes
elif PLATFORM_SYSTEM == "Darwin":
	# For Mac OS X, we need the NSSpeechSynthesizer class from the Cocoa module
	from Cocoa import NSSpeechSynthesizer

# Dolphin constants
DOLACCESS_NONE = 0 # Indicates no Dolphin products are running.
DOLACCESS_SPEAK = 1
DOLACCESS_MUTE = 141 # Cancel speech.

# SAPI constants
SPF_ASYNC = 1 # Specifies that the Speak call should be asynchronous.
SPF_PURGEBEFORESPEAK = 2 # Purges all pending speak requests prior to this speak call.
SPF_IS_NOT_XML = 16 # The input text will not be parsed for XML markup.


def where():
	"""Return the directory where the screen reader API DLL files are stored, even if Python is running through a frozen Py2EXE."""
	try:
		if sys.frozen or sys.importers:
			return os.path.join(os.path.dirname(sys.executable), "speech_libs")
	except AttributeError:
		return os.path.join(os.path.dirname(os.path.realpath(__file__)), "speech_libs")


class Speech(object):
	def __init__(self):
		if PLATFORM_SYSTEM == "Windows":
			lib_directory = where()
			if platform.architecture()[0] == "32bit":
				self.dolphin = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "dolapi32.dll"))
				self.dolphin.DolAccess_Command.argtypes = (ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int)
				self.dolphin.DolAccess_Action.argtypes = (ctypes.c_int,)
				self.nvda = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "nvdaControllerClient32.dll"))
				self.sa = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "SAAPI32.dll"))
			else:
				self.dolphin = None
				self.nvda = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "nvdaControllerClient64.dll"))
				self.sa = ctypes.windll.LoadLibrary(os.path.join(lib_directory, "SAAPI64.dll"))
			self.nvda.nvdaController_brailleMessage.argtypes = (ctypes.c_wchar_p,)
			self.nvda.nvdaController_speakText.argtypes = (ctypes.c_wchar_p,)
			self.sa.SA_BrlShowTextW.argtypes = (ctypes.c_wchar_p,)
			self.sa.SA_SayW.argtypes = (ctypes.c_wchar_p,)
			try:
				self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
			except pywintypes.com_error:
				self.sapi = None
		elif PLATFORM_SYSTEM == "Darwin":
			# Allocate and initialize the default TTS
			self.darwin = NSSpeechSynthesizer.alloc().init()

	def dolphin_running(self):
		return self.dolphin is not None and self.dolphin.DolAccess_GetSystem() != DOLACCESS_NONE

	def dolphin_say(self, text, interrupt=False):
		if interrupt:
			self.dolphin.DolAccess_Action(DOLACCESS_MUTE)
		self.dolphin.DolAccess_Command(text, len(text) * 2 + 2, DOLACCESS_SPEAK)

	def dolphin_silence(self):
		self.dolphin.DolAccess_Action(DOLACCESS_MUTE)

	def jfw_braille(self, text):
		try:
			jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
		except pywintypes.com_error:
			return
		jfw.RunFunction("BrailleString(\"{text}\")".format(text=text.replace('"', "'")))

	def jfw_running(self):
		return win32gui.FindWindow("JFWUI2", None)

	def jfw_say(self, text, interrupt=False):
		try:
			jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
		except pywintypes.com_error:
			return
		jfw.SayString(text, int(interrupt))

	def jfw_silence(self):
		try:
			jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
		except pywintypes.com_error:
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

	def we_braille(self, text):
		try:
			we = win32com.client.Dispatch("WindowEyes.Application")
		except pywintypes.com_error:
			return
		we.Braille.Display(text)

	def we_running(self):
		return win32gui.FindWindow("GWMExternalControl", "External Control")

	def we_say(self, text, interrupt=False):
		try:
			we = win32com.client.Dispatch("WindowEyes.Application")
		except pywintypes.com_error:
			return
		if interrupt:
			we.Speech.Silence()
		we.Speech.Speak(text)

	def we_silence(self):
		try:
			we = win32com.client.Dispatch("WindowEyes.Application")
		except pywintypes.com_error:
			return
		we.Speech.Silence()

	def output(self, text, interrupt=False, speak=True, braille=True):
		if PLATFORM_SYSTEM == "Darwin":
			if interrupt:
				self.darwin.stopSpeaking()
			self.darwin.startSpeakingString_(text)
		elif PLATFORM_SYSTEM == "Windows":
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
			elif self.dolphin_running():
				self.dolphin_say(text, interrupt)
			elif self.we_running():
				if speak:
					self.we_say(text, interrupt)
				if braille:
					self.we_braille(text)
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
		if PLATFORM_SYSTEM == "Darwin":
			self.darwin.stopSpeaking()
		elif PLATFORM_SYSTEM == "Windows":
			if self.nvda_running():
				self.nvda_silence()
			elif self.sa_running():
				self.sa_silence()
			elif self.dolphin_running():
				self.dolphin_silence()
			elif self.we_running():
				self.we_silence()
			elif self.jfw_running():
				self.jfw_silence()
			elif self.sapi_running():
				self.sapi_silence()

	def speaking(self):
		if PLATFORM_SYSTEM == "Darwin":
			return self.darwin.isSpeaking()
		elif PLATFORM_SYSTEM == "Windows":
			if self.nvda_running() or self.sa_running() or self.dolphin_running() or self.we_running() or self.jfw_running():
				# None of the screen reader APIs support retrieving speaking status.
				return False
			elif self.sapi_running():
				return self.sapi.Status.RunningState != 1


if __name__ == "__main__":
	from time import sleep
	tts = Speech()
	tts.say("hello world!")
	# Make sure the tts engine finishes speaking before terminating.
	while tts.speaking():
		sleep(0.1)
