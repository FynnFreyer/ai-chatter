# SPDX-FileCopyrightText: 2023-present Fynn Freyer <fynn.freyer@googlemail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
This submodule holds database-related classes and functions that are of cross-cutting concern.
"""

from datetime import datetime

from sqlalchemy import Engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates
from sqlalchemy.sql import func

__all__ = ["Base"]


class Base(DeclarativeBase):  # pylint: disable=not-callable
    """The declarative base for the ORM. Adds ``created_at`` and ``updated_at`` timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    """A :class:`datetime` object, that is set on creation."""

    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), server_onupdate=func.now())  # type: ignore
    """A :class:`datetime` object, that is updated on changes."""

    @validates("created_at")
    def _validate_created_at(self, key, created_at: datetime):
        """
        Make sure that ``created_at`` timestamp isn't modified.

        :param key: Name of the modified column.
        :param settings: A :class:`rki_hivclustering.utils.config.HIVTraceSettings` object or a JSON dump representing one.
        :raises ValueError:  If settings is not a valid :class:`rki_hivclustering.utils.config.HIVTraceSettings` object, or JSON representation thereof.
        :return: A JSON encoded :class:`rki_hivclustering.utils.config.HIVTraceSettings`
        """
        # TODO turn this into an immutable decorator
        # if the created_at field already exists, we want to throw
        if self.created_at is not None:
            msg = f'{self.__class__.__name__}: column "{key}" cannot be modified retroactively.'
            raise ValueError(msg)
        return created_at


@event.listens_for(Engine, "connect")
def sqlite_pragma_enforce_foreign_keys(dbapi_connection, connection_record):  # noqa: ARG001
    """
    This is necessary to enforce foreign key constraints on SQLite.
    Cf. `SQLAlchemy docs <https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support>`
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
