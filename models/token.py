from sqlalchemy import Column, String, DateTime, Boolean
from database.database import Base
import datetime


class Token(Base):
    __tablename__ = "token"

    user_id = Column(String)
    access_token = Column(String(450), primary_key=True)
    refresh_token = Column(String(450), nullable=False)
    status = Column(Boolean)
    created_date = Column(DateTime, default=datetime.datetime.now)
