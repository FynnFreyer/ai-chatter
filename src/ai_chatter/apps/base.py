# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
This module defines the base class for ai_chatter applications.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from logging import DEBUG, basicConfig, getLogger
from typing import Optional

import openai  # type: ignore
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session as DBSession

from ai_chatter.__about__ import __app_name__
from ai_chatter.communication import CLICommunicator, Communicator
from ai_chatter.db import Base, Session
from ai_chatter.utils.config import Settings

_logger = getLogger(__name__)

__all__ = ["Application"]


@dataclass
class Application(ABC):
    """
    The base class for ai_chatter applications. Subclass this, override the :meth:`run` method and then start your
    application with the :meth:`start` method.
    """

    settings: Settings
    session: Session
    communicator: Communicator
    engine: Optional[Engine] = None

    def __init__(
        self,
        settings: Optional[Settings] = None,
        session: Optional[Session] = None,
        communicator: Optional[Communicator] = None,
        engine: Optional[Engine] = None,
    ):
        self.settings = settings or Settings.load()

        if self.settings.api_key is None:
            msg = "No api key provided in settings."
            _logger.error(msg)
            raise ValueError(msg)

        self.session = session or Session(
            self.settings.session_settings.model, self.settings.session_settings.context_size_messages
        )

        self.communicator = communicator or CLICommunicator()

        if self.settings.persist:
            _logger.info(f"Persisting data for {__app_name__} in {self.settings.data_dir}.")

            self.settings.data_dir.mkdir(parents=True, exist_ok=True)
            db = self.settings.data_dir / "session.db"

            echo = self.settings.verbosity == DEBUG
            self.engine = engine or create_engine(f"sqlite:///{db}", echo=echo)
            Base.metadata.create_all(self.engine)
        else:
            self.engine = None

    def start(self):
        """Start the application."""
        basicConfig(level=self.settings.verbosity)
        _logger.info(f"Starting {__app_name__}.{self.__class__.__name__}")
        openai.api_key = self.settings.api_key
        if self.engine is not None:
            with DBSession(self.engine) as db_session:
                self.run()
                db_session.add(self.session)
                db_session.commit()
        else:
            self.run()

    @abstractmethod
    def run(self):
        """The method providing the main functionality of the application."""
