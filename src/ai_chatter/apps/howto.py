# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""

"""

from __future__ import annotations

import platform
from dataclasses import dataclass

from ai_chatter.apps.base import Application
from ai_chatter.db import BehaviorDirective
from ai_chatter.utils.config import Settings

__all__ = ["ShellHowTo"]


@dataclass
class EnvData:
    shell: str
    platform: str


class ShellHowTo(Application):
    """An :class:`ai_chatter.apps.base.Application` to get a commando for the current shell."""

    def __init__(self, args: list[str]):
        super().__init__()
        system_info = self.find_env_data()
        self.session.behavior = BehaviorDirective(
            content=f"Only return a shell command, or a series of commands delineated by newlines. Don't give "
            f"explanations or further information. The commands should be runnable directly.\n"
            f"I'm running a {system_info} system."
        )
        self.prompt = " ".join(args)

    def find_env_data(self) -> str:
        """Find data on the current platform to provide context for ChatGPT."""
        # TODO find shell information
        system = platform.system()
        if system == "Linux" or "BSD" in system:
            try:
                with open("/etc/os-release") as release:
                    prefix = "PRETTY_NAME="
                    for line in release:
                        if line.upper().startswith(prefix):
                            return line[len(prefix) :].strip().strip('"')
            except FileNotFoundError:
                # /etc/os-release is not available
                return system

        return f"{system} {platform.version()}"

    def run(self):
        """Get a shell command from a question."""
        response = self.session.complete(self.prompt)
        self.communicator.show_response(response)


class LangHowTo(Application):
    """An :class:`ai_chatter.apps.base.Application` to solve a problem in a particular programming language."""

    def __init__(self, settings: Settings, lang: str):
        super().__init__(settings)
        self.lang = lang

    # def run(self):
    #     self.communicator
