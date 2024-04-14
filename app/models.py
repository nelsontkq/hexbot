import datetime
from typing import Optional
from pydantic import BaseModel

from app.db import PostScheduleTime

class Post(BaseModel):
    user_name: str
    text: str
    post_trigger: PostScheduleTime
    post_time: Optional[datetime.datetime] = None