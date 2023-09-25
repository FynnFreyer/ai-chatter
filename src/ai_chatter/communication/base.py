# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""

"""

from abc import ABC, abstractmethod
from typing import Optional

__all__ = ["Communicator"]


class Communicator(ABC):
    """Base class for getting prompts from a user, and displaying the responses."""

    @abstractmethod
    def get_prompt(self) -> Optional[str]:
        """Generate a prompt. Returning ``None`` indicates that the Session should end."""

    @abstractmethod
    def show_response(self, response: str):
        """Display the response."""
