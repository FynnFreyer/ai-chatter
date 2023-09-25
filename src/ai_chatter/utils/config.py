# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Module for classes and functions related to configuration.
"""

from __future__ import annotations

import sys
from argparse import ArgumentParser, Namespace
from json import JSONDecodeError, load
from logging import DEBUG, ERROR, INFO, WARNING, getLogger
from pathlib import Path
from typing import Literal, Optional

import platformdirs
from platformdirs import PlatformDirs
from pydantic import DirectoryPath, Field, NewPath
from pydantic_settings import BaseSettings, SettingsConfigDict

from ai_chatter.__about__ import __app_name__, __author__, __description__, __version__

__all__ = ["Settings", "SessionSettings"]

from ai_chatter.enums import ChatGPTModel

_logger = getLogger(__name__)


class SessionSettings(BaseSettings):
    """Settings of a :class:`ai_chatter.chat.Session`."""

    model: ChatGPTModel = ChatGPTModel.GPT4
    """The model to use. Defaults to GPT-4."""

    context_size_tokens: int = 8000
    """
    Maximum amount of (estimated) tokens of the message history to include as context. Negative numbers send complete
    history. Defaults to 8000.
    """

    context_size_messages: int = -1
    """
    How many message pairs of the history to include as context. Negative numbers send complete history. Defaults to -1.
    """

    session_warn_size: int = -1
    """
    After how many tokens should a warning message be printed out to the user. Negative numbers don't send warnings.
    Defaults to -1.
    """

    behavior: Optional[str] = None
    """A behavior directive to pass to ChatGPT."""


class Settings(BaseSettings):
    """Settings for the application. Can be set via env-vars or a config file."""

    model_config = SettingsConfigDict(env_prefix=f"{__app_name__}_")

    api_key: str = ""
    """The API key to use."""

    data_dir: DirectoryPath | NewPath = Path(platformdirs.user_data_dir(__app_name__, __author__))
    """The data directory of the application. E.g., "~/.local/share/ai_chatter"."""

    session_settings: SessionSettings = Field(default_factory=SessionSettings)
    """Settings concerning the session."""

    verbosity: Literal[ERROR, WARNING, INFO, DEBUG] = ERROR
    """How much information to print to screen."""

    persist: bool = True
    """Whether the conversation should be saved."""

    @classmethod
    def load(cls, file: Optional[str | Path] = None):
        """
        Load settings from the standard location or env vars. Location depends on the platform, e.g.,
        "${XDG_CONFIG_HOME}/ai_chatter/config.json" on Linux.

        :param file: Optionally, a configuration file to read from. Defaults to "config.json" in the current directory.
        :raise JSONDecodeError: If a config file contains invalid JSON.
        :raise RuntimeError: If no API key was provided.
        :return: A settings instance.
        """

        file = Path(file).resolve() if file is not None else Path("config.json").resolve()

        dirs = PlatformDirs(appname=__app_name__, appauthor=__author__)
        config_paths = [dirs.site_config_path / "config.json", dirs.user_config_path / "config.json", file]

        data_dir = dirs.user_data_path
        config = Settings(data_dir=data_dir).model_dump()

        for config_path in config_paths:
            _logger.info(f"{cls.__name__}: Trying to load config from {config_path}.")
            if config_path.exists():
                _logger.info(f"{cls.__name__}: Found file at {config_path}.")
                try:
                    with config_path.open() as config_file:
                        config |= load(config_file)
                except JSONDecodeError as e:
                    msg = f"{cls.__name__}: Invalid JSON in config file at {config_path}."
                    _logger.error(msg)
                    raise JSONDecodeError(msg, e.doc, e.pos) from e

        return cls(**config)

    @staticmethod
    def get_parser(name: str = __app_name__, description: str = __description__) -> ArgumentParser:
        """Get an ArgumentParser."""
        parser = ArgumentParser(name, description=description)

        parser.add_argument("-a", "--api-key", default=None, help="The API key to use.")
        parser.add_argument("-c", "--config", type=Path, default=None, help="Path to a config file.")
        parser.add_argument(
            "-e",
            "--ephemeral",
            dest="persist",
            action="store_false",
            default=True,
            help="Don't persist the conversation.",
        )
        parser.add_argument("-l", "--log", type=Path, default=None, help="Path to a log file.")

        parser.add_argument(
            "-v", "--verbose", dest="verbosity", action="count", default=0, help="Increase the level of verbosity."
        )
        parser.add_argument(
            "-V", "--version", action="version", version=__version__, help="Print version information and exit"
        )

        return parser

    @classmethod
    def parse_args(cls, parser: Optional[ArgumentParser] = None, args: Optional[tuple[str, ...]] = None) -> Namespace:
        """Parse arguments."""
        if args is None:
            args = tuple(sys.argv[1:])
        if parser is None:
            parser = cls.get_parser()

        parsed_args = parser.parse_args(args)
        verbosity = [ERROR, WARNING, INFO, DEBUG][min(parsed_args.verbosity, 3)]
        parsed_args.verbosity = verbosity

        return parsed_args

    @classmethod
    def from_args(cls, args: Optional[Namespace] = None):
        """Augment the settings object provided by :meth:`load` with command line parameters."""
        if args is None:
            args = cls.parse_args()
        settings = cls.load(args.config)

        settings.verbosity = args.verbosity
        if args.api_key is not None:
            settings.api_key = args.api_key

        return settings
