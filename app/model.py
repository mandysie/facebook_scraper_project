from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class FacebookPost(Base):
    __tablename__ = 'facebook_posts'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    like_count = Column(String)
    comment_count = Column(String)
    video_link = Column(String)
    image_link = Column(String)