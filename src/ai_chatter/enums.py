# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
This module defines different enumerations for use as a controlled vocabulary.
"""

from enum import Enum
from functools import total_ordering

try:
    from enum import StrEnum  # type: ignore
except ImportError:

    class StrEnum(str, Enum):  # type: ignore
        """
        These can be used as drop-in for string based values, and can use normal formatting, etc.
        ``StrEnum`` is not part of the standard library in Python 3.8, so we roll our own.
        """


class SenderRole(StrEnum):
    """Attached to a :class:`ai_chatter.model.chat.Message`."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@total_ordering
class ChatGPTModel(StrEnum):
    """Specifies available standard models to use with ChatGPT."""

    GPT4 = "gpt-4"
    """The most current model."""

    GPT35_TURBO = "gpt-3.5-turbo"
    """The slightly older and cheaper model."""

    def __lt__(self, other):
        """Implement ordering via order of definitions."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        defined = list(self.__class__.__members__.values())
        return defined.index(self) > defined.index(other)

    def __repr__(self):
        return str(self)
