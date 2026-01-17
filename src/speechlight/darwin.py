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

"""Darwin speech."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import sys
from typing import Any

# Local Modules:
from .base import BaseSpeech


if sys.platform == "darwin":  # pragma: no cover
	from Cocoa import NSSpeechSynthesizer


class Speech(BaseSpeech):
	"""Implements Speech for Darwin."""

	_darwin: Any | None = None

	def __init__(self) -> None:  # pragma: no cover
		"""Defines the constructor."""
		# Allocate and initialize the default TTS.
		if sys.platform == "darwin":
			self._darwin = NSSpeechSynthesizer.alloc().init()

	def braille(self, text: str) -> None:  # NOQA: D102
		pass

	def output(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
		self.say(text, interrupt=interrupt)
		self.braille(text)

	def say(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
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
