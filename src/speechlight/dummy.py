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

"""Dummy speech."""

# Future Modules:
from __future__ import annotations

# Local Modules:
from .base import BaseSpeech


class Speech(BaseSpeech):
	"""Implements Speech for the dummy platform."""

	def braille(self, text: str) -> None:  # NOQA: D102
		pass

	def output(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
		self.say(text, interrupt=interrupt)
		self.braille(text)

	def say(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
		if interrupt:
			self.silence()

	def silence(self) -> None:  # NOQA: D102
		pass

	def speaking(self) -> bool:  # NOQA: D102, PLR6301
		return False
