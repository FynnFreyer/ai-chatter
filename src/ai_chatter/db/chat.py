# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Wrapper around the OpenAI API.
"""

# ruff: noqa: A003, RUF012

from __future__ import annotations

from itertools import chain
from json import dumps
from logging import getLogger
from typing import Optional

from openai import ChatCompletion
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.util import hybridproperty

from ai_chatter.db.base import Base
from ai_chatter.enums import ChatGPTModel, SenderRole
from ai_chatter.utils.config import SessionSettings

_logger = getLogger(__name__)


class Message(Base):
    """Represents a message to or from ChatGPT."""

    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    """The message id."""

    role: Mapped[SenderRole] = mapped_column(SQLEnum(SenderRole))
    """The role of the sender. Can be one of "user", "assistant" or "system"."""

    content: Mapped[str]
    """The message content."""

    tokens: Mapped[Optional[int]]
    """The amount of tokens this message used up."""

    def to_dict(self):
        return {
            "role": self.role,
            "content": self.content,
        }

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_abstract": True,
    }


class BehaviorDirective(Message):
    """Represents a message to ChatGPT containing a directive specifying wanted behavior."""

    __tablename__ = "behavior_directive"

    id: Mapped[int] = mapped_column(ForeignKey("message.id"), primary_key=True)
    """The :class:`Message` id."""

    # TODO make "unique" BehaviorDirectives via "upserts"

    __mapper_args__ = {
        "polymorphic_identity": SenderRole.SYSTEM,
    }


class Prompt(Message):
    """Represents a message to ChatGPT containing a prompt to complete."""

    __tablename__ = "prompt"

    id: Mapped[int] = mapped_column(ForeignKey("message.id"), primary_key=True)
    """The :class:`Message` id."""

    session_id: Mapped[int] = mapped_column(ForeignKey("session.id"))
    """The ID of the :class:`Session`, this prompt belongs to."""

    session: Mapped[Session] = relationship(back_populates="prompts")
    """The :class:`Session` this message belongs to."""

    response: Mapped[Optional[Response]] = relationship(foreign_keys="response.c.prompt_id")
    """The :class:`Response` that belongs to this prompt."""

    __mapper_args__ = {
        "polymorphic_identity": SenderRole.USER,
    }


class Response(Message):
    """Represents a message from ChatGPT, completing a prompt."""

    __tablename__ = "response"

    id: Mapped[int] = mapped_column(ForeignKey("message.id"), primary_key=True)
    """The :class:`Message` id."""

    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompt.id"))
    """Id of the :class:`Prompt` that was completed by this response."""

    prompt: Mapped[Prompt] = relationship(foreign_keys="response.c.prompt_id", back_populates="response")
    """The :class:`Prompt` that was completed by this response."""

    raw_json: Mapped[str]
    """The raw JSON response."""

    @hybridproperty
    def session_id(self):
        """The ID of the :class:`Session`, this response belongs to."""
        return self.prompt.session_id

    @hybridproperty
    def session(self):
        """The the :class:`Session`, this response belongs to."""
        return self.prompt.session

    __mapper_args__ = {
        "polymorphic_identity": SenderRole.ASSISTANT,
    }


class Session(Base):
    """Represents a set of interactions with ChatGPT, e.g., some prompts and answers."""

    __tablename__ = "session"

    id: Mapped[int] = mapped_column(primary_key=True)
    """The session id."""

    model: Mapped[ChatGPTModel] = mapped_column(SQLEnum(ChatGPTModel), default=ChatGPTModel.GPT4)
    """The model to use. Defaults to GPT-4."""

    behavior_id: Mapped[Optional[int]] = mapped_column(ForeignKey("behavior_directive.id"))
    """
    A directive to ChatGPT indicating desired behavior, e.g., "Only output Python code, compatible with version3.8".
    Will be included in requests regardless of :attr:`context` settings.
    """

    behavior: Mapped[Optional[BehaviorDirective]] = relationship()
    """
    A directive to ChatGPT indicating desired behavior, e.g., "Only output Python code, compatible with version3.8".
    Will be included in requests regardless of :attr:`context` settings.
    """

    context_size: Mapped[int] = mapped_column(default=-1)
    """
    How many message pairs of the history to include as context. Negative numbers send complete history. Defaults to -1.
    """

    prompts: Mapped[list[Prompt]] = relationship()
    """The history of :class:`Prompt` objects sent to ChatGPT."""

    @hybridproperty
    def responses(self) -> list[Response]:
        """The history of :class:`Response` objects sent by ChatGPT."""
        return [prompt.response for prompt in self.prompts if prompt.response is not None]

    # TODO auto summarize feature, where we use ChatGPT to summarize the conversation so far, to compress context.

    def __init__(
        self, model: ChatGPTModel = ChatGPTModel.GPT4, context: int = 0, behavior: Optional[str] = None, **kwargs
    ):
        """Get a prompt from the user, send it to ChatGPT, and display the response."""
        super().__init__(**kwargs)

        self.model = model
        self.context_size = context
        if behavior is not None:
            self.behavior = BehaviorDirective(content=behavior)

    def complete(self, prompt: str) -> str:
        """
        Get a prompt completion.

        :param prompt: The prompt to send to ChatGPT.
        :return: The answer.
        """
        message = Prompt(
            content=prompt,
            session=self,
        )

        completion = ChatCompletion.create(
            model=self.model,
            messages=[*self.context, message.to_dict()],
        )

        message.tokens = completion["usage"]["prompt_tokens"]

        response = Response(
            role="assistant",
            content=completion["choices"][0]["message"]["content"],
            raw_json=dumps(completion),
            tokens=completion["usage"]["completion_tokens"],
            prompt=message,
        )

        return response.content

    @hybridproperty
    def context(self) -> list[dict]:
        """The context to send to ChatGPT."""
        if 0 < self.context_size <= len(self.answered):
            history_ctx = self.answered[: -self.context_size]
        elif self.context_size != 0:
            history_ctx = self.answered[:]
        else:
            history_ctx = []

        context = [] if self.behavior is None else [self.behavior.to_dict()]
        context.extend(msg.to_dict() for msg in chain.from_iterable(history_ctx))

        return context

    @hybridproperty
    def messages(self) -> list[Message]:
        """A flat list of messages."""
        return [msg for msg in chain.from_iterable(self.history) if msg is not None]

    @hybridproperty
    def history(self) -> list[tuple[Prompt, Optional[Response]]]:
        """The message history. It consists of :class:`Prompt` and :class:`Response` message pairs."""
        return [(prompt, prompt.response) for prompt in self.prompts]

    @hybridproperty
    def answered(self) -> list[tuple[Prompt, Response]]:
        """The :class:`Prompt` and :class:`Response` message pairs, that already have a response."""
        return [(prompt, response) for prompt, response in self.history if response is not None]

    @hybridproperty
    def tokens(self) -> int:
        """Number of tokens used up by the messages in this :class:`Session`."""
        return sum(msg.tokens for msg in self.messages if msg.tokens is not None)

    @classmethod
    def from_settings(cls, settings: SessionSettings):
        """Instantiate a session from :class:`ai_chatter.utils.config.SessionSettings`."""
        return cls(settings.model, settings.context_size_messages, settings.behavior)
