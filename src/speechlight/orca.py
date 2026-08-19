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

"""Orca."""

# Future Modules:
from __future__ import annotations

# Built-in Modules:
import logging
import sys
from contextlib import suppress
from typing import Any, Protocol, cast

# Third-party Modules:
from knickknacks.typedef import Self

# Local Modules:
from .base import BaseSpeech


if sys.platform == "linux":  # pragma: no cover
	from jeepney import DBusAddress, MessageFlag, MessageType, new_method_call
	from jeepney.io.blocking import open_dbus_connection
	from jeepney.wrappers import unwrap_msg
else:  # pragma: no cover

	class DBusAddress:
		def __init__(
			self,
			object_path: str,
			bus_name: str | None = None,
			interface: str | None = None,
		) -> None:
			pass

	class MessageType:
		error = object()

	class MessageFlag:
		no_reply_expected = 1
		no_auto_start = 2
		allow_interactive_authorization = 4

	def new_method_call(
		remote_obj: DBusAddress,
		method: str,
		signature: str = "",
		body: tuple[Any, ...] = (),
	) -> _DBusOutMessage:
		return cast(_DBusOutMessage, object())

	def open_dbus_connection(bus: str = "SESSION") -> _DBusConnection:
		raise RuntimeError("jeepney is only available on Linux")

	def unwrap_msg(msg: _DBusMessage) -> tuple[Any, ...]:
		return ()


# Constants:
BUS_NAME: str = "org.gnome.Orca.Service"
SERVICE_PATH: str = "/org/gnome/Orca/Service"
SERVICE_INTERFACE: str = "org.gnome.Orca.Service"
SPEECH_PATHS: tuple[str, ...] = (
	"/org/gnome/Orca/Service/SpeechAndVerbosityManager",
	"/org/gnome/Orca/Service/SpeechManager",
)
SPEECH_INTERFACE: str = "org.gnome.Orca.Module"

# Globals:
logger: logging.Logger = logging.getLogger(__name__)


class OrcaError(Exception):
	"""Base exception for the Orca wrapper."""


class OrcaNotAvailableError(OrcaError):
	"""Raised when the Orca D-Bus service cannot be found."""


class OrcaSpeakError(OrcaError):
	"""Raised when PresentMessage / InterruptSpeech fails."""


class _MessageHeader(Protocol):
	message_type: object


class _DBusMessage(Protocol):
	header: _MessageHeader
	body: object


class _OutMessageHeader(Protocol):
	flags: int


class _DBusOutMessage(Protocol):
	"""A method-call message we are about to send (needs writable header.flags)."""

	header: _OutMessageHeader


class _DBusConnection(Protocol):
	def close(self) -> None: ...
	def send(self, message: _DBusOutMessage, serial: int | None = None) -> None: ...
	def send_and_get_reply(
		self,
		message: _DBusOutMessage,
		*,
		timeout: float | None = None,
	) -> _DBusMessage: ...


class Orca:
	def __init__(self) -> None:
		self._conn: _DBusConnection | None = None
		self._speech_path: str | None = None

	def open_connection(self) -> None:
		try:
			self._conn = open_dbus_connection(bus="SESSION")
			self._detect()
		except Exception as e:  # NOQA: BLE001
			# Intentionally broad so missing jeepney/bus/Orca never crashes callers.
			logger.debug(f"Failed to open D-Bus connection or detect Orca: {e}")
			self.close()

	def close(self) -> None:
		"""Close the underlying D-Bus connection."""
		if self._conn is not None:
			with suppress(Exception):
				self._conn.close()
			self._conn = None
			self._speech_path = None

	def __enter__(self) -> Self:
		self.open_connection()
		return self

	def __exit__(self, *args: object) -> None:
		self.close()

	def __del__(self) -> None:
		self.close()

	def _call(  # NOQA: PLR0913
		self,
		*,
		path: str,
		interface: str,
		method: str,
		signature: str = "",
		body: tuple[Any, ...] = (),
		bus_name: str | None = None,
		timeout: float | None = 5.0,
	) -> Any:
		if self._conn is None:
			raise OrcaNotAvailableError("No D-Bus connection")
		addr = DBusAddress(path, bus_name=bus_name or BUS_NAME, interface=interface)
		msg = new_method_call(addr, method, signature, body)
		try:
			reply = self._conn.send_and_get_reply(msg, timeout=timeout)
		except Exception as e:
			raise OrcaError(f"D-Bus call {interface}.{method} failed: {e}") from e
		if reply.header.message_type == MessageType.error:
			raise OrcaError(f"D-Bus error: {reply.body}")
		result: tuple[Any, ...] = unwrap_msg(reply)
		if len(result) == 1:
			return result[0]
		return result

	def _call_noreply(  # NOQA: PLR0913
		self,
		*,
		path: str,
		interface: str,
		method: str,
		signature: str = "",
		body: tuple[Any, ...] = (),
		bus_name: str | None = None,
	) -> None:
		if self._conn is None:
			raise OrcaNotAvailableError("No D-Bus connection")
		addr = DBusAddress(path, bus_name=bus_name or BUS_NAME, interface=interface)
		msg = new_method_call(addr, method, signature, body)
		# Tell the peer not to send a method return / error reply.
		msg.header.flags |= MessageFlag.no_reply_expected
		try:
			self._conn.send(msg)
		except Exception as e:
			raise OrcaError(f"D-Bus send {interface}.{method} failed: {e}") from e

	def _name_has_owner(self, name: str) -> bool:
		try:
			result = self._call(
				path="/org/freedesktop/DBus",
				interface="org.freedesktop.DBus",
				method="NameHasOwner",
				signature="s",
				body=(name,),
				bus_name="org.freedesktop.DBus",
			)
			return bool(result)
		except OrcaError:
			return False

	def _detect(self) -> None:
		if self._name_has_owner(BUS_NAME):
			for path in SPEECH_PATHS:
				with suppress(OrcaError):
					self._call(
						path=path,
						interface=SPEECH_INTERFACE,
						method="ListCommands",
						bus_name=BUS_NAME,
					)
					self._speech_path = path
					logger.debug(f"Detected Orca at {path}")
					return
		logger.debug("No usable Orca service found")

	@property
	def available(self) -> bool:
		return self._conn is not None and self._speech_path is not None

	def say(self, text: str, *, interrupt: bool = False) -> None:
		if not self.available:
			raise OrcaNotAvailableError("Orca not found")
		if interrupt:
			with suppress(OrcaSpeakError):
				self.silence()
		try:
			self._call_noreply(
				path=SERVICE_PATH,
				interface=SERVICE_INTERFACE,
				method="PresentMessage",
				signature="s",
				body=(text,),
			)
		except OrcaError as e:
			raise OrcaSpeakError(str(e)) from e

	def silence(self) -> None:
		if not self.available:
			raise OrcaNotAvailableError("Orca not found")
		try:
			self._call_noreply(
				path=str(self._speech_path),
				interface=SPEECH_INTERFACE,
				method="ExecuteCommand",
				signature="sb",
				body=("InterruptSpeech", False),
			)
		except OrcaError as e:
			raise OrcaSpeakError(str(e)) from e

	def version(self) -> str:
		if not self.available:
			raise OrcaNotAvailableError("Orca not found")
		result = self._call(
			path=SERVICE_PATH,
			interface=SERVICE_INTERFACE,
			method="GetVersion",
		)
		return str(result)


class Speech(BaseSpeech):
	"""Implements Speech for Orca."""

	def __init__(self) -> None:  # pragma: no cover
		"""Defines the constructor."""
		self._orca: Orca | None = None

	@property
	def version(self) -> str:
		"""The version of Orca currently running."""
		o = self._get_orca()
		if o is not None:
			with suppress(OrcaError):
				return o.version()
		return ""

	def _get_orca(self) -> Orca | None:
		"""Return a connected Orca wrapper, opening one if needed."""
		if self._orca is not None:
			if self._orca.available:
				return self._orca
			with suppress(Exception):
				self._orca.close()
			self._orca = None
		o = Orca()
		o.open_connection()
		if o.available:
			self._orca = o
			return o
		with suppress(Exception):
			o.close()
		return None

	def __del__(self) -> None:  # pragma: no cover
		if self._orca is not None:
			with suppress(Exception):
				self._orca.close()
			self._orca = None

	def braille(self, text: str) -> None:
		pass

	def output(self, text: str, *, interrupt: bool = False) -> None:
		self.say(text, interrupt=interrupt)
		self.braille(text)

	def say(self, text: str, *, interrupt: bool = False) -> None:
		o = self._get_orca()
		if o is None:
			return
		with suppress(OrcaError):
			o.say(text, interrupt=interrupt)

	def silence(self) -> None:
		o = self._get_orca()
		if o is None:
			return
		with suppress(OrcaError):
			o.silence()

	@staticmethod
	def speaking() -> bool:
		return False
