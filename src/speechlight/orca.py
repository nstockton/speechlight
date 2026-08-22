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
from dataclasses import dataclass, field
from typing import Any, Final, Protocol, cast

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
DBUS_NAME: Final[str] = "org.freedesktop.DBus"
DBUS_PATH: Final[str] = "/org/freedesktop/DBus"
DBUS_INTERFACE: Final[str] = "org.freedesktop.DBus"
ORCA_BUS_NAME: Final[str] = "org.gnome.Orca.Service"
ORCA_SERVICE_PATH: Final[str] = "/org/gnome/Orca/Service"
ORCA_SERVICE_INTERFACE: Final[str] = "org.gnome.Orca.Service"
ORCA_SPEECH_PATHS: Final[tuple[str, ...]] = (
	"/org/gnome/Orca/Service/SpeechAndVerbosityManager",
	"/org/gnome/Orca/Service/SpeechManager",
)
ORCA_MODULE_INTERFACE: Final[str] = "org.gnome.Orca.Module"

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


@dataclass(slots=True)
class _DBusCall:
	path: str
	bus_name: str
	interface: str
	method: str
	signature: str = ""
	body: tuple[Any, ...] = field(default_factory=tuple)
	no_reply: bool = False
	timeout: float | None = 5.0


class Orca:
	def __init__(self) -> None:
		self._conn: _DBusConnection | None = None
		self._speech_path: str | None = None

	def __enter__(self) -> Self:
		self.open_connection()
		return self

	def __exit__(self, *args: object) -> None:
		self.close()

	def __del__(self) -> None:
		self.close()

	def close(self) -> None:
		"""Close the underlying D-Bus connection."""
		if self._conn is not None:
			with suppress(Exception):
				self._conn.close()
		self._conn = None
		self._speech_path = None

	def open_connection(self) -> None:
		try:
			self._conn = open_dbus_connection(bus="SESSION")
			self._detect()
		except Exception as e:  # NOQA: BLE001
			# Intentionally broad so missing jeepney/bus/Orca never crashes callers.
			logger.debug(f"Failed to open D-Bus connection or detect Orca: {e}")
			self.close()

	def _detect(self) -> None:
		if self._has_owner(ORCA_BUS_NAME):
			for path in ORCA_SPEECH_PATHS:
				call = _DBusCall(
					path=path,
					bus_name=ORCA_BUS_NAME,
					interface=ORCA_MODULE_INTERFACE,
					method="ListCommands",
				)
				with suppress(OrcaError):
					self._call(call)
					self._speech_path = path
					logger.debug(f"Detected Orca at {path}")
					return
		logger.debug("No usable Orca service found")
		self.close()

	def _has_owner(self, name: str) -> bool:
		call = _DBusCall(
			path=DBUS_PATH,
			bus_name=DBUS_NAME,
			interface=DBUS_INTERFACE,
			method="NameHasOwner",
			signature="s",
			body=(name,),
		)
		with suppress(OrcaError):
			return bool(self._call(call))
		return False

	def _call(self, call: _DBusCall) -> Any:
		if self._conn is None:
			raise OrcaNotAvailableError("No D-Bus connection")
		addr = DBusAddress(call.path, bus_name=call.bus_name, interface=call.interface)
		msg = new_method_call(addr, call.method, call.signature, call.body)
		try:
			if call.no_reply:
				# Tell the peer not to send a method return / error reply.
				msg.header.flags |= MessageFlag.no_reply_expected
				self._conn.send(msg)
				return None
			reply = self._conn.send_and_get_reply(msg, timeout=call.timeout)
		except Exception as e:
			raise OrcaError(f"D-Bus call {call.interface}.{call.method} failed: {e}") from e
		if reply.header.message_type == MessageType.error:
			raise OrcaError(f"D-Bus error: {reply.body}")
		result: tuple[Any, ...] = unwrap_msg(reply)
		if len(result) == 1:
			return result[0]
		return result

	@property
	def available(self) -> bool:
		return self._conn is not None and self._speech_path is not None

	def present_message(self, text: str, *, interrupt: bool = False) -> None:
		if not self.available:
			raise OrcaNotAvailableError("Orca not found")
		if interrupt:
			with suppress(OrcaSpeakError):
				self.interrupt_speech()
		call = _DBusCall(
			path=ORCA_SERVICE_PATH,
			bus_name=ORCA_BUS_NAME,
			interface=ORCA_SERVICE_INTERFACE,
			method="PresentMessage",
			signature="s",
			body=(text,),
			no_reply=True,
		)
		try:
			self._call(call)
		except OrcaError as e:
			raise OrcaSpeakError(str(e)) from e

	def interrupt_speech(self) -> None:
		if not self.available:
			raise OrcaNotAvailableError("Orca not found")
		call = _DBusCall(
			path=str(self._speech_path),
			bus_name=ORCA_BUS_NAME,
			interface=ORCA_MODULE_INTERFACE,
			method="ExecuteCommand",
			signature="sb",
			body=("InterruptSpeech", False),
			no_reply=True,
		)
		try:
			self._call(call)
		except OrcaError as e:
			raise OrcaSpeakError(str(e)) from e

	def get_version(self) -> str:
		if not self.available:
			raise OrcaNotAvailableError("Orca not found")
		call = _DBusCall(
			path=ORCA_SERVICE_PATH,
			bus_name=ORCA_BUS_NAME,
			interface=ORCA_SERVICE_INTERFACE,
			method="GetVersion",
		)
		return str(self._call(call))


class Speech(BaseSpeech):
	"""Implements Speech for Orca."""

	def __init__(self) -> None:  # pragma: no cover
		"""Defines the constructor."""
		self._orca: Orca
		self._ensure_orca()

	def __del__(self) -> None:  # pragma: no cover
		if hasattr(self, "_orca"):
			self._orca.close()

	@property
	def version(self) -> str:
		"""The version of Orca currently running."""
		if self._ensure_orca():
			with suppress(OrcaError):
				return self._orca.get_version()
		return ""

	def _ensure_orca(self) -> bool:
		"""
		Ensures that Orca is available, establishing a new connection if necessary.

		Returns:
			True if Orca is available, False otherwise.
		"""
		if hasattr(self, "_orca"):
			if self._orca.available:
				return True
			self._orca.close()
		o = Orca()
		o.open_connection()
		if o.available:
			self._orca = o
			return True
		o.close()
		return False

	def braille(self, text: str) -> None:
		# Change this if Braille-only support is added to Orca.
		self.output(text)

	def output(self, text: str, *, interrupt: bool = False) -> None:
		if self._ensure_orca():
			with suppress(OrcaError):
				self._orca.present_message(text, interrupt=interrupt)

	def say(self, text: str, *, interrupt: bool = False) -> None:
		# Change this if speak-only support is added to Orca.
		self.output(text, interrupt=interrupt)

	def silence(self) -> None:
		if self._ensure_orca():
			with suppress(OrcaError):
				self._orca.interrupt_speech()

	@staticmethod
	def speaking() -> bool:
		return False
