# PyRope - Rocket League Replay Parser

Decodes Rocket League replay headers

# Installation

## Requirements
* Bitstring (https://pypi.python.org/pypi/bitstring)
* Python 3+ (Developed on python 3.4 but any 3+ version should work)

## Setup
```
git+https://github.com/rocket-league-replays/pyrope.git
```

# Usage

## Getting Started:
```python
from pyrope import Replay

replay = Replay('FILEPATH')
# or
replay = Replay(open('FILEPATH', 'rb').read())
```

# Tests

You can run the tests with

```
python -W ignore -m unittest discover
```

# License
This Project is published under GNU GPL v3.0
It would also be nice if you drop me a notice (Mail or Github) if you made something publicly available using this package.

# Credits and Sources
Existing Parsers which this is partly based on https://github.com/rocket-league-replays/rocket-league-replays/wiki/Rocket-League-Replay-Parsers

Thread with people working hard on understanding the replay structure http://www.psyonix.com/forum/viewtopic.php?f=33&t=13656

The awesome game Rocket League http://store.steampowered.com/app/252950 owned by Psyonix
