"""Darwin speech."""


# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import sys
from typing import Any, Optional

# Local Modules:
from .base import BaseSpeech


if sys.platform == "darwin":  # pragma: no cover
	from Cocoa import NSSpeechSynthesizer


class Speech(BaseSpeech):
	"""Implements Speech for Darwin."""

	_darwin: Optional[Any] = None

	def __init__(self) -> None:  # pragma: no cover
		"""Defines the constructor."""
		# Allocate and initialize the default TTS.
		if sys.platform == "darwin":
			self._darwin = NSSpeechSynthesizer.alloc().init()

	def braille(self, text: str) -> None:  # NOQA: D102
		pass

	def output(self, text: str, interrupt: Optional[bool] = None) -> None:  # NOQA: D102
		self.say(text, interrupt)
		self.braille(text)

	def say(self, text: str, interrupt: Optional[bool] = None) -> None:  # NOQA: D102
		if self._darwin is not None:
			if interrupt:
				self.silence()
			self._darwin.startSpeakingString_(text)

	def silence(self) -> None:  # NOQA: D102
		if self._darwin is not None:
			self._darwin.stopSpeaking()

	def speaking(self) -> bool:  # NOQA: D102
		status = False
		if self._darwin is not None:
			status = bool(self._darwin.isSpeaking())
		return status
