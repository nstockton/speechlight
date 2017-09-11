# speechlight
A lightweight Python library providing a common interface to multiple TTS and screen reader APIs

## License
This project is licensed under the terms of the [Mozilla Public License, version 2.0.](https://www.mozilla.org/en-US/MPL/2.0/ "MPL2 official Site")

## Credits
This project was written by Nick Stockton with assistance for Mac OS X support by Jacob Schmude.

## Installation
```
pip install -U git+https://github.com/nstockton/speechlight.git
```

## Example Usage
```
from speechlight import Speech

s = Speech()

# Say something.
s.say("Hello world!")

# Say something else, interrupting the currently speaking text.
s.say("I'm a rood computer!", interrupt=True)

# Cancel the currently speaking message.
s.silence()

# Braille something.
s.braille("Braille dots go bump in the night.")

# Speak and braille text at the same time.
s.output("Read along with me.")

# And to interrupt speech.
s.output("Rood!", interrupt=True)
```
