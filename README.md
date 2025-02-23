# Speechlight

[![Current Version on PyPi]][PyPi]
[![License]][License Page]
[![Supported Python Versions]][PyPi]
[![PyPi Downloads in Last 7 Days]][PyPi Download Stats]
[![PyPi Downloads in Last 30 Days]][PyPi Download Stats]
[![PyPi Total Downloads]][PyPi Download Stats]

A lightweight [Python][] library providing a common interface to multiple [TTS][] and [screen reader][] APIs. See the [API reference][] for more information.


## License And Credits

Speechlight is licensed under the terms of the [MIT License.][License Page]
Speechlight was originally created by [Nick Stockton.][Nick Stockton GitHub]
macOS support by Jacob Schmude.


## Installation

```
pip install --user speechlight
```


## Running From Source

### Windows-specific Instructions

Execute the following commands from the root directory of this repository to install the virtual environment and project dependencies.
```
py -3 -m venv .venv
.venv\Scripts\activate.bat
pip install --upgrade --require-hashes --requirement requirements-uv.txt
uv sync --frozen
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

### Linux-specific Instructions

Execute the following commands from the root directory of this repository to install the virtual environment and project dependencies.
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade --require-hashes --requirement requirements-uv.txt
uv sync --frozen
pre-commit install -t pre-commit
pre-commit install -t pre-push
```


## Example Usage

```
from speechlight import speech

# Say something.
speech.say("Hello world!")

# Say something else, interrupting the currently speaking text.
speech.say("I'm a rood computer!", interrupt=True)

# Cancel the currently speaking message.
speech.silence()

# Braille something.
speech.braille("Braille dots go bump in the night.")

# Speak and braille text at the same time.
speech.output("Read along with me.")

# And to interrupt speech.
speech.output("Rood!", interrupt=True)
```


[Current Version on PyPi]: https://img.shields.io/pypi/v/speechlight.svg
[License]: https://img.shields.io/github/license/nstockton/speechlight.svg
[License Page]: https://nstockton.github.io/speechlight/license (License Page)
[Supported Python Versions]: https://img.shields.io/pypi/pyversions/speechlight.svg
[PyPi]: https://pypi.org/project/speechlight (Speechlight on PyPi)
[PyPi Downloads in Last 7 Days]: https://pepy.tech/badge/speechlight/week
[PyPi Downloads in Last 30 Days]: https://pepy.tech/badge/speechlight/month
[PyPi Total Downloads]: https://pepy.tech/badge/speechlight
[PyPi Download Stats]: https://pepy.tech/project/speechlight (Download Statistics)
[Python]: https://python.org (Python Main Page)
[TTS]: https://en.wikipedia.org/wiki/Speech_synthesis (Speech Synthesis Wikipedia Page)
[screen reader]: https://en.wikipedia.org/wiki/Screen_reader (Screen Reader Wikipedia Page)
[API reference]: https://nstockton.github.io/speechlight/api (Speechlight API reference Page)
[Nick Stockton GitHub]: https://github.com/nstockton (My Profile On GitHub)
