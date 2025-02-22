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

"""Contains the base class."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
from abc import ABC, abstractmethod


class BaseSpeech(ABC):
	"""The base interface that Speech inherits from."""

	@abstractmethod
	def braille(self, text: str) -> None:
		"""
		Brailles text.

		Args:
			text: The text to be brailled.
		"""

	@abstractmethod
	def output(self, text: str, *, interrupt: bool = False) -> None:
		"""
		Speaks and brailles text.

		Args:
			text: The output text.
			interrupt: True if the speech should be silenced before speaking.
		"""

	@abstractmethod
	def say(self, text: str, *, interrupt: bool = False) -> None:
		"""
		Speaks text.

		Args:
			text: The text to be spoken.
			interrupt: True if the speech should be silenced before speaking.
		"""

	@abstractmethod
	def silence(self) -> None:
		"""Cancels speech and flushes the speech buffer."""

	@abstractmethod
	def speaking(self) -> bool:
		"""
		Determines if text is currently being spoken.

		Returns:
			True if text is currently being spoken, False otherwise.
		"""
