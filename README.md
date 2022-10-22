# Speechlight

A lightweight [Python][] library providing a common interface to multiple [TTS][] and [screen reader][] APIs. See the [API reference][] for more information.


## License And Credits

Speechlight is licensed under the terms of the [Mozilla Public License, version 2.0.][License]
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
pip install --upgrade "poetry==1.1.13"
poetry install --no-ansi
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

### Linux-specific Instructions

Execute the following commands from the root directory of this repository to install the virtual environment and project dependencies.
```
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade "poetry==1.1.13"
poetry install --no-ansi
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


[Python]: https://python.org (Python Main Page)
[TTS]: https://en.wikipedia.org/wiki/Speech_synthesis (Speech Synthesis Wikipedia Page)
[screen reader]: https://en.wikipedia.org/wiki/Screen_reader (Screen Reader Wikipedia Page)
[API reference]: https://nstockton.github.io/speechlight/api (Speechlight API reference Page)
[License]: https://nstockton.github.io/speechlight/license (License Page)
[Nick Stockton GitHub]: https://github.com/nstockton (My Profile On GitHub)
