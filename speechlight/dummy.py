# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


# Future Modules:
from __future__ import annotations

# Built-in Modules:
from typing import Optional

# Local Modules:
from .base import BaseSpeech


class Speech(BaseSpeech):
	def braille(self, text: str) -> None:
		pass

	def output(self, text: str, interrupt: Optional[bool] = None) -> None:
		self.say(text, interrupt)
		self.braille(text)

	def say(self, text: str, interrupt: Optional[bool] = None) -> None:
		if interrupt:
			self.silence()

	def silence(self) -> None:
		pass

	def speaking(self) -> bool:
		return False
