import datetime
from typing import List, Optional, Tuple

from sqlmodel import Field, SQLModel, Session, create_engine, select

from app.config import settings


class TwitterUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: str
    access_token: Optional[str]
    access_token_secret: Optional[str]
    lease_date: Optional[datetime.datetime]
    hub_topic: Optional[str]
    # tweet_template: Optional[str]


class YoutubeUpload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    link: str


engine = create_engine(settings.db_connection_string)


def get_session():
    with Session(engine) as session:
        yield session


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = session.exec(
            select(TwitterUser).where(TwitterUser.user == settings.default_user)
        ).first()
        if not user:
            session.add(TwitterUser(user=settings.default_user))
            session.commit()


def create_update_user(
    session: Session, user_name: str, access_token: str, access_token_secret: str
) -> None:
    print(f"Updating user {user_name}")
    user = session.exec(
        select(TwitterUser).where(TwitterUser.user == user_name)
    ).first()
    if not user:
        session.add(
            TwitterUser(
                user=user_name,
                access_token=access_token,
                access_token_secret=access_token_secret,
            )
        )
    else:
        user.access_token = access_token
        user.access_token_secret = access_token_secret
    session.commit()
    print(f"User {user_name} updated")


def get_user(session: Session, user_name: str) -> Optional[TwitterUser]:
    user = session.exec(
        select(TwitterUser).where(TwitterUser.user == user_name)
    ).first()
    return user


def get_create_post(session: Session, link: str) -> Tuple[YoutubeUpload, bool]:

    post = session.exec(select(YoutubeUpload).where(YoutubeUpload.link == link)).first()
    new = post is None

    if new:
        session.add(YoutubeUpload(link=link))
        session.commit()
        post = session.exec(
            select(YoutubeUpload).where(YoutubeUpload.link == link)
        ).first()
    return post, new


def update_lease(session: Session, user_name: str, lease_seconds: int, hub_topic: str):
    user = session.exec(
        select(TwitterUser).where(TwitterUser.user == user_name)
    ).first()
    if user:
        user.lease_date = datetime.datetime.now() + datetime.timedelta(
            seconds=lease_seconds
        )
        user.hub_topic = hub_topic
        session.commit()
    else:
        print(f"User {user_name} not found")


def get_users_to_resub(session: Session) -> List[TwitterUser]:
    users = session.exec(
        select(TwitterUser).where(
            TwitterUser.lease_date
            < datetime.datetime.now() + datetime.timedelta(days=2)
        )
    ).all()
    return users
