# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""

"""

from typing import Optional

from ai_chatter.communication.base import Communicator

__all__ = ["CLICommunicator"]


class CLICommunicator(Communicator):
    """Prompts the user for an input and prints responses to the screen."""

    def get_prompt(self) -> Optional[str]:
        prompt = input("> ")
        return prompt if prompt not in ["q", "quit"] else None

    def show_response(self, response: str) -> None:
        print(response, "\n")  # noqa: T201
