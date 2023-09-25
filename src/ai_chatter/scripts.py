# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
This module defines entry points for CLI scripts.
"""

import sys

from ai_chatter.apps.chat import Chatter
from ai_chatter.apps.howto import ShellHowTo
from ai_chatter.apps.web import SummarizePage
from ai_chatter.utils.config import Settings


def main():
    """The main entrypoint into the application."""
    settings = Settings.from_args()
    app = Chatter(settings)
    app.start()


def howto():
    """Entrypoint for the howto script."""
    app = ShellHowTo(sys.argv[1:])
    app.start()


def summarize():
    # parser = Settings.get_parser("summarize", "Summarize a webpage with ChatGPT.")
    # parser.add_argument("url", help="The URL of the webpage to summarize.")
    # args = Settings.parse_args(parser)
    # url = args.url

    app = SummarizePage(
        "https://stackoverflow.com/questions/3711856/how-to-remove-empty-lines-with-or-without-whitespace-in-python"
    )
    app.start()


if __name__ == "__main__":
    summarize()
    # main()
