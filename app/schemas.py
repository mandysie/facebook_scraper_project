# schemas.py
from pydantic import BaseModel

class FacebookPostSchema(BaseModel):
    content: str
    video_link: str
    like_count: str
    comment_count: str

    class Config:
        orm_mode = True