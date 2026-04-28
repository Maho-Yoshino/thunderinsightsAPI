from logging import getLogger, Logger
from pathlib import Path
from contextlib import contextmanager
from sqlmodel import SQLModel, Field, BigInteger, DateTime, SmallInteger, VARCHAR, INTEGER, create_engine, Session
from enum import Enum

class clanRoles(Enum):
    COMMANDER = 1
    OFFICER = 2
    PRIVATE = 3
    DEPUTY = 4
    SERGEANT = 5
class clans(SQLModel, table=True):
    id:BigInteger = Field(primary_key=True)
    name:VARCHAR = VARCHAR(255)
    tag:VARCHAR = VARCHAR(255)
    type:INTEGER = INTEGER(4)
class user(SQLModel, table=True):
    id:BigInteger = Field(primary_key=True)
    clan_id:int = Field(nullable=True, default=None)
    nickname:str = Field(nullable=True, default=None)
    clan_member_role_id: SmallInteger = Field(nullable=True, default=None)
    last_day: DateTime = Field(nullable=True, default=None)
    register_day: DateTime = Field(nullable=True, default=None)
    selected_title_id: SmallInteger = Field(nullable=True, default=None)
    icon_id: SmallInteger = Field(nullable=True, default=None)
    frame_id: SmallInteger = Field(nullable=True, default=None)
    background_id: SmallInteger = Field(nullable=True, default=None)
    showcase_type_id: SmallInteger = Field(nullable=True, default=None)
    datetime: DateTime = Field(nullable=True, default=None)

class database:
    _db_path = Path() / "database.db"
    _logger:Logger
    def __init__(self):
        self._logger = getLogger(__name__)
        self._logger.debug("database class initialized")
        self._engine = create_engine(self._db_path)
    @contextmanager
    def con(self):
        with Session(self._engine) as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise