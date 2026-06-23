# Copyright (C) 2026 Nick Stockton
# SPDX-License-Identifier: MIT
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

"""Speech Dispatcher."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import sys
from collections.abc import Iterable
from contextlib import suppress
from typing import Protocol, TypeAlias

# Local Modules:
from .base import BaseSpeech


if sys.platform == "linux":  # pragma: no cover
	try:
		import speechd
	except ImportError:  # pragma: no cover
		print("ERROR: speechd Python module not found.", file=sys.stderr)
		print("Install python3-speechd or equivalent package.", file=sys.stderr)


SDListVoicesType: TypeAlias = tuple[tuple[str, str | None, str | None], ...]


class SDEventCallbackType(Protocol):
	"""Protocol for an event callback."""

	def __call__(self, event_type: str, *, index_mark: str | None = None) -> None: ...  # NOQA: D102


class SSIPClientType(Protocol):  # NOQA: PLR0904
	"""Protocol for the SSIPClient class."""

	def __init__(  # NOQA: D107, PLR0913, PLR0917
		self,
		name: str,
		component: str = "default",
		user: str = "unknown",
		address: str | None = None,
		autospawn: bool | None = None,  # NOQA: FBT001
		host: str | None = None,
		port: int | None = None,
		method: str | None = None,
		socket_path: str | None = None,
	) -> None: ...

	def set_priority(self, priority: str) -> None: ...  # NOQA: D102

	def set_data_mode(self, value: str) -> None: ...  # NOQA: D102

	def speak(  # NOQA: D102
		self,
		text: str,
		callback: SDEventCallbackType | None = None,
		event_types: Iterable[str] | None = None,
	) -> tuple[int, str, tuple[str, ...]]: ...

	def char(self, char: str) -> None: ...  # NOQA: D102

	def key(self, key: str) -> None: ...  # NOQA: D102

	def sound_icon(self, sound_icon: str) -> None: ...  # NOQA: D102

	def cancel(self, scope: str | int = "self") -> None: ...  # NOQA: D102

	def stop(self, scope: str | int = "self") -> None: ...  # NOQA: D102

	def pause(self, scope: str | int = "self") -> None: ...  # NOQA: D102

	def resume(self, scope: str | int = "self") -> None: ...  # NOQA: D102

	def list_output_modules(self) -> tuple[str, ...]: ...  # NOQA: D102

	def list_synthesis_voices(  # NOQA: D102
		self, language: str | None = None, variant: str | None = None
	) -> SDListVoicesType: ...

	def set_language(self, language: str, scope: str | int = "self") -> None: ...  # NOQA: D102

	def get_language(self) -> str | None: ...  # NOQA: D102

	def set_output_module(self, name: str, scope: str | int = "self") -> None: ...  # NOQA: D102

	def get_output_module(self) -> str | None: ...  # NOQA: D102

	def set_pitch(self, value: int, scope: str | int = "self") -> None: ...  # NOQA: D102

	def get_pitch(self) -> str | None: ...  # NOQA: D102

	def set_pitch_range(self, value: int, scope: str | int = "self") -> None: ...  # NOQA: D102

	def set_rate(self, value: int, scope: str | int = "self") -> None: ...  # NOQA: D102

	def get_rate(self) -> str | None: ...  # NOQA: D102

	def set_volume(self, value: int, scope: str | int = "self") -> None: ...  # NOQA: D102

	def get_volume(self) -> str | None: ...  # NOQA: D102

	def set_punctuation(self, value: str, scope: str | int = "self") -> None: ...  # NOQA: D102

	def get_punctuation(self) -> str | None: ...  # NOQA: D102

	def set_spelling(self, value: bool, scope: str | int = "self") -> None: ...  # NOQA: D102, FBT001

	def set_cap_let_recogn(self, value: str, scope: str | int = "self") -> None: ...  # NOQA: D102

	def set_voice(self, value: str, scope: str | int = "self") -> None: ...  # NOQA: D102

	def set_synthesis_voice(self, value: str, scope: str | int = "self") -> None: ...  # NOQA: D102

	def set_pause_context(self, value: int, scope: str | int = "self") -> None: ...  # NOQA: D102

	def set_debug(self, val: bool) -> None: ...  # NOQA: D102, FBT001

	def set_debug_destination(self, path: str) -> None: ...  # NOQA: D102

	def block_begin(self) -> None: ...  # NOQA: D102

	def block_end(self) -> None: ...  # NOQA: D102

	def close(self) -> None: ...  # NOQA: D102


class Speech(BaseSpeech):
	"""Implements Speech for Speech Dispatcher."""

	_sd: SSIPClientType | None = None

	def __init__(self) -> None:  # pragma: no cover
		"""Defines the constructor."""
		self._event_types: tuple[str, ...] = ()
		if sys.platform == "linux":  # pragma: no cover
			with suppress(NameError):
				self._sd = speechd.SSIPClient("speechlight")
				self._sd.set_data_mode(speechd.DataMode.TEXT)
				self._event_types = (
					speechd.CallbackType.BEGIN,
					speechd.CallbackType.CANCEL,
					speechd.CallbackType.END,
				)
		self._is_speaking: bool = False

	def _speak_callback(self, event_type: str, *, index_mark: str | None = None) -> None:
		"""
		Handle callbacks from Speech Dispatcher.

		Args:
			event_type: Event type from speechd.CallbackType.
			index_mark: Index mark for INDEX_MARK events.
		"""
		if sys.platform == "linux":  # pragma: no cover
			if event_type == speechd.CallbackType.BEGIN:
				self._is_speaking = True
			elif event_type in {speechd.CallbackType.END, speechd.CallbackType.CANCEL}:
				self._is_speaking = False

	def braille(self, text: str) -> None:  # NOQA: D102
		pass

	def output(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
		self.say(text, interrupt=interrupt)
		self.braille(text)

	def say(self, text: str, *, interrupt: bool = False) -> None:  # NOQA: D102
		if self._sd is not None:
			if interrupt:
				self.silence()
			self._sd.speak(text, callback=self._speak_callback, event_types=self._event_types)

	def silence(self) -> None:  # NOQA: D102
		if self._sd is not None:
			self._sd.cancel()

	def speaking(self) -> bool:  # NOQA: D102
		return self._is_speaking
