# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""

"""

from ai_chatter.apps.base import Application

__all__ = ["Chatter"]


class Chatter(Application):
    """A simple AI chatbot on your CLI."""

    def run(self):
        """Simple main loop, that takes a"""
        while (prompt := self.communicator.get_prompt()) is not None:
            response = self.session.complete(prompt)
            self.communicator.show_response(response)
