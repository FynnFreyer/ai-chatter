# ai-chatter

[![PyPI - Version](https://img.shields.io/pypi/v/ai-chatter.svg)](https://pypi.org/project/ai-chatter)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ai-chatter.svg)](https://pypi.org/project/ai-chatter)

## About

AI is pretty cool, but a lot of fuss around it is just chatter.
This package tries to provide a toolkit to easily implement basic applications using ChatGPT,
so you can get your hands dirty, and see whether you can do something useful with it.

It automatically takes care of some issues around interacting with a chatbot,
like settings and session management, data persistence, communication, and gluing it together.

## Project Goals

Features für Sprachlehrer

- Individualisierter Unterricht
- Lernerfolgsübersicht
- Austauschbares Backend
  - online/lokal
  - verschiedene Anbieter
- Fehlerkorrektur
  - Was ist falsch?
  - Wie wäre es richtig?
- Vokabeln lernen
- Grammatik lernen

## Architektur

- Sprecher-Profile
  - Name
  - Level (A1-C2)
    - Angabe durch Nutzer
    - Einschätzung durch Programm
  - Hobbies (ggf. für Individualisierung?)
  - Lernerfolg
- Fehler
  - Verschiedene Arten von Fehlern, z.B.
    - Falsche Freunde,
    - Grammatik,
    - Orthographie,
    - ...
  - Fehlerhäufigkeiten (der verschiedenen Arten) könnten erhoben werden, um
    - das Sprecherlevel einzuschätzen, oder
    - den Unterricht zu individualisieren.
- Vokabeln lernen
- Knowledge-Base Artikel
  - Halten das "Gedächtnis" der AI
  - Werden genutzt, um Systemprompt zu generieren
  - Müssen geupdated werden

## Installation

```console
pip install ai-chatter
```

## License

`ai-chatter` is copyright (C) 2023 Fynn Freyer.

This program is free software: you can redistribute it and/or modify it under the terms of the [GNU Affero General Public License](https://spdx.org/licenses/AGPL-3.0-or-later.html) as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You can find a copy of the GNU Affero General Public License [along with this program](https://github.com/FynnFreyer/ai-chatter/blob/main/LICENSE.txt).
You can also get a copy online at <https://www.gnu.org/licenses/>.
