# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
from abc import ABC, abstractmethod
from typing import Optional


class BaseSpeech(ABC):
	@abstractmethod
	def braille(self, text: str) -> None:
		"""
		Brailles text.

		Args:
			text: The text to be brailled.
		"""

	@abstractmethod
	def output(self, text: str, interrupt: Optional[bool] = None) -> None:
		"""
		Speaks and brailles text.

		Args:
			text: The output text.
			interrupt: True if the speech should be silenced before speaking.
		"""

	@abstractmethod
	def say(self, text: str, interrupt: Optional[bool] = None) -> None:
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
