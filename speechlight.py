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

# determine the directory where the screen reader API DLL files are stored, even if Python is running through a frozen Py2EXE.
try:
	if sys.frozen or sys.importers:
		LIB_DIRECTORY = os.path.join(os.path.dirname(sys.executable), "speech_libs")
except AttributeError:
	LIB_DIRECTORY = os.path.join(os.path.dirname(os.path.realpath(__file__)), "speech_libs")

# Dolphin constants
DOLACCESS_NONE = 0 # Indicates no Dolphin products are running.
DOLACCESS_SPEAK = 1
DOLACCESS_MUTE = 141 # Cancel speech.

# SAPI constants
SPF_ASYNC = 1 # Specifies that the Speak call should be asynchronous.
SPF_PURGEBEFORESPEAK = 2 # Purges all pending speak requests prior to this speak call.
SPF_IS_NOT_XML = 16 # The input text will not be parsed for XML markup.


class Speech(object):
	def __init__(self):
		if PLATFORM_SYSTEM == "Windows":
			if platform.architecture()[0] == "32bit":
				self.dolphin = ctypes.windll.LoadLibrary(os.path.join(LIB_DIRECTORY, "dolapi32.dll"))
				self.dolphin.DolAccess_Command.argtypes = (ctypes.c_wchar_p, ctypes.c_int, ctypes.c_int)
				self.dolphin.DolAccess_Action.argtypes = (ctypes.c_int,)
				self.nvda = ctypes.windll.LoadLibrary(os.path.join(LIB_DIRECTORY, "nvdaControllerClient32.dll"))
				self.sa = ctypes.windll.LoadLibrary(os.path.join(LIB_DIRECTORY, "SAAPI32.dll"))
			else:
				self.dolphin = None
				self.nvda = ctypes.windll.LoadLibrary(os.path.join(LIB_DIRECTORY, "nvdaControllerClient64.dll"))
				self.sa = ctypes.windll.LoadLibrary(os.path.join(LIB_DIRECTORY, "SAAPI64.dll"))
			self.nvda.nvdaController_speakText.argtypes = (ctypes.c_wchar_p,)
			self.sa.SA_SayW.argtypes = (ctypes.c_wchar_p,)
			try:
				self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
			except pywintypes.com_error:
				self.sapi = None
		elif PLATFORM_SYSTEM == "Darwin":
			# Allocate and initialize the default TTS
			self.darwin = NSSpeechSynthesizer.alloc().init()

	def say(self, text, interrupt=False):
		if PLATFORM_SYSTEM == "Darwin":
			if interrupt:
				self.darwin.stopSpeaking()
			self.darwin.startSpeakingString_(text)
		elif PLATFORM_SYSTEM == "Windows":
			if self.nvda.nvdaController_testIfRunning()==0:
				if interrupt:
					self.nvda.nvdaController_cancelSpeech()
				self.nvda.nvdaController_speakText(text)
			elif self.sa.SA_IsRunning():
				if interrupt:
					self.sa.SA_StopAudio()
				self.sa.SA_SayW(str(text))
			elif self.dolphin is not None and self.dolphin.DolAccess_GetSystem() != DOLACCESS_NONE:
				if interrupt:
					self.dolphin.DolAccess_Action(DOLACCESS_MUTE)
				self.dolphin.DolAccess_Command(text, len(text) * 2 + 2, DOLACCESS_SPEAK)
			elif win32gui.FindWindow("GWMExternalControl", "External Control"):
				try:
					we = win32com.client.Dispatch("GWSpeak.Speak")
				except pywintypes.com_error:
					return
				if interrupt:
					we.Silence()
				we.SpeakString(text)
			elif win32gui.FindWindow("JFWUI2", None):
				try:
					jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
				except pywintypes.com_error:
					return
				jfw.SayString(text, int(interrupt))
			elif self.sapi is not None:
				self.sapi.Speak(text, SPF_ASYNC | SPF_PURGEBEFORESPEAK | SPF_IS_NOT_XML if interrupt else SPF_ASYNC | SPF_IS_NOT_XML)

	def silence(self):
		if PLATFORM_SYSTEM == "Darwin":
			self.darwin.stopSpeaking()
		elif PLATFORM_SYSTEM == "Windows":
			if self.nvda.nvdaController_testIfRunning()==0:
				self.nvda.nvdaController_cancelSpeech()
			elif self.sa.SA_IsRunning():
				self.sa.SA_StopAudio()
			elif self.dolphin is not None and self.dolphin.DolAccess_GetSystem() != DOLACCESS_NONE:
				self.dolphin.DolAccess_Action(DOLACCESS_MUTE)
			elif win32gui.FindWindow("GWMExternalControl", "External Control"):
				try:
					we = win32com.client.Dispatch("GWSpeak.Speak")
				except pywintypes.com_error:
					return
				we.Silence()
			elif win32gui.FindWindow("JFWUI2", None):
				try:
					jfw = win32com.client.Dispatch("FreedomSci.JawsApi")
				except pywintypes.com_error:
					return
				jfw.StopSpeech()
			elif self.sapi is not None:
				self.sapi.Speak("", SPF_ASYNC | SPF_PURGEBEFORESPEAK | SPF_IS_NOT_XML)

	def speaking(self):
		if PLATFORM_SYSTEM == "Darwin":
			return self.darwin.isSpeaking()
		elif PLATFORM_SYSTEM == "Windows":
			if self.nvda.nvdaController_testIfRunning()==0 or self.sa.SA_IsRunning() or self.dolphin is not None and self.dolphin.DolAccess_GetSystem() != DOLACCESS_NONE or win32gui.FindWindow("GWMExternalControl", "External Control") or win32gui.FindWindow("JFWUI2", None):
				# None of the screen reader APIs support retrieving speaking status.
				return False
			elif self.sapi is not None:
				return self.sapi.Status.RunningState != 1


if __name__ == "__main__":
	from time import sleep
	tts = Speech()
	tts.say("hello world!")
	# Make sure the tts engine finishes speaking before terminating.
	while tts.speaking():
		sleep(0.1)
