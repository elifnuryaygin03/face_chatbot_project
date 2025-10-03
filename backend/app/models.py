from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    is_student = Column(Boolean, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, age={self.age}, gender={self.gender}, is_student={self.is_student})>"

class ChatHistory(Base):
    __tablename__ = "chat_histories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    message = Column(Text)
    is_user = Column(Boolean)  # True=user, False=bot
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="chat_histories")

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, user_id={self.user_id}, is_user={self.is_user})>"