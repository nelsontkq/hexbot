import select
from typing import Optional

from sqlmodel import Field, SQLModel, Session, create_engine

from app.config import settings


class TwitterUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: str
    access_token: Optional[str]
    access_token_secret: Optional[str]
# Properties to receive via API on creation

engine = create_engine(settings.db_connection_string)

SQLModel.metadata.create_all(engine)


def init_db() -> None:
    with Session(engine) as session:
        user = session.exec(
            select(TwitterUser).where(TwitterUser.user == settings.default_user)
        ).first()
        if not user:
            session.add(TwitterUser(user=settings.default_user))
            session.commit()
