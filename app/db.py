import datetime
from enum import StrEnum
from typing import List, Optional, Tuple

from sqlmodel import Field, SQLModel, Session, create_engine, select

from app.config import settings


class PostScheduleTime(StrEnum):
    on_new_video = "new_video"
    on_scheduled = "scheduled"


class TwitterUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user: str
    access_token: Optional[str]
    access_token_secret: Optional[str]
    lease_date: Optional[datetime.datetime]
    hub_topic: Optional[str]


class PostText(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    user: str
    post_trigger: Optional[PostScheduleTime]
    # if post_trigger is on_scheduled
    post_time: Optional[datetime.datetime]


class YoutubeUpload(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    link: str


engine = create_engine(settings.db_connection_string, pool_pre_ping=True)


def get_session():
    with Session(engine) as session:
        yield session


def init_db() -> None:
    print("Creating tables")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        user = session.exec(
            select(TwitterUser).where(TwitterUser.user == settings.default_user)
        ).first()
        if not user:
            print("Creating default user")
            session.add(
                TwitterUser(user=settings.default_user, hub_topic=settings.hub_topic)
            )
            session.commit()

        default_post = session.exec(
            select(PostText).where(
                PostText.user == settings.default_user
                and PostText.post_trigger == PostScheduleTime.on_new_video
            )
        ).first()
        if not default_post:
            print("Creating default post")
            session.add(
                PostText(
                    text="🚨 New Video 🚨\n\nCheck out my latest video over on YouTube and whilst you're there, don't forget to like, comment and subscribe!\n\nHex 👋\n\n{link}\n#mtgmkm #mtgkarlovmanor #karlovmanor #mtg #mtgarena",
                    user=settings.default_user,
                    post_trigger=PostScheduleTime.on_new_video,
                )
            )
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


def create_update_on_youtube_post(session: Session, text: str, user_name: str):
    print(f"Updating user {user_name}")
    post = session.exec(
        select(PostText).where(
            PostText.user == user_name
            and PostText.post_trigger == PostScheduleTime.on_new_video
        )
    ).first()
    if not post:
        session.add(
            PostText(
                text=text,
                user=user_name,
                post_trigger=PostScheduleTime.on_new_video,
                post_time=None,
            )
        )
    else:
        post.text = text
    session.commit()
    print(f"User {user_name} updated")
    return session.exec(
        select(PostText).where(
            PostText.user == user_name
            and PostText.post_trigger == PostScheduleTime.on_new_video
        )
    ).first()


def get_on_youtube_post(
    session: Session, title: str, link: str, user_name: str
) -> Optional[str]:
    post = session.exec(
        select(PostText).where(
            PostText.user == user_name,
            PostText.post_trigger == PostScheduleTime.on_new_video,
        )
    ).first()
    if not post:
        return None
    return post.text.format(title=title, link=link)


def get_create_post(session: Session, link: str) -> Tuple[YoutubeUpload, bool]:

    post = session.exec(select(YoutubeUpload).where(YoutubeUpload.link == link)).first()
    is_not_found = post is None

    if is_not_found:
        session.add(YoutubeUpload(link=link))
        session.commit()
        post = session.exec(
            select(YoutubeUpload).where(YoutubeUpload.link == link)
        ).first()
    return post, is_not_found


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
