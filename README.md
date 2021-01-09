# speechlight

A lightweight Python library providing a common interface to multiple TTS and screen reader APIs.


## License And Credits

Speechlight is licensed under the terms of the [Mozilla Public License, version 2.0.](license.md "License Page")
Speechlight was originally created and is actively maintained by Nick Stockton.
macOS support by Jacob Schmude.


## Installation

```
pip install -U git+https://github.com/nstockton/speechlight.git
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
