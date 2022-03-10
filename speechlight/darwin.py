# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
import sys
from typing import Optional

# Local Modules:
from .base import BaseSpeech


if sys.platform == "darwin":  # pragma: no cover
	from Cocoa import NSSpeechSynthesizer


class MockTTS(object):  # pragma: no cover
	def init(self) -> MockTTS:
		return self

	def startSpeakingString_(self, text: str) -> None:
		pass

	def stopSpeaking(self) -> None:
		pass

	def isSpeaking(self) -> bool:
		return False


class MockNSSpeechSynthesizer(object):  # pragma: no cover
	@staticmethod
	def alloc() -> MockTTS:
		return MockTTS()


class Speech(BaseSpeech):
	def __init__(self) -> None:  # pragma: no cover
		if sys.platform == "darwin":
			# Allocate and initialize the default TTS.
			self.darwin = NSSpeechSynthesizer.alloc().init()
		else:
			self.darwin = MockNSSpeechSynthesizer.alloc().init()

	def braille(self, text: str) -> None:
		pass

	def output(self, text: str, interrupt: Optional[bool] = None) -> None:
		self.say(text, interrupt)
		self.braille(text)

	def say(self, text: str, interrupt: Optional[bool] = None) -> None:
		if interrupt:
			self.silence()
		self.darwin.startSpeakingString_(text)

	def silence(self) -> None:
		self.darwin.stopSpeaking()

	def speaking(self) -> bool:
		return bool(self.darwin.isSpeaking())
