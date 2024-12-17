# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

# users table
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    
    # New column to store Cloudinary URL for profile picture
    profile_image_url = Column(String(500), nullable=True)  # URL to the profile picture
    
    # relationships
    conversations1 = relationship('Conversation', foreign_keys='Conversation.user1_id', back_populates='user1')
    conversations2 = relationship('Conversation', foreign_keys='Conversation.user2_id', back_populates='user2')
    messages = relationship('Message', back_populates='sender')



# conversations table
class Conversation(Base):
    __tablename__ = 'conversations'
    
    conversation_id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    user2_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)

    # Relationships
    user1 = relationship('User', foreign_keys=[user1_id], back_populates='conversations1')
    user2 = relationship('User', foreign_keys=[user2_id], back_populates='conversations2')
    messages = relationship('Message', back_populates='conversation')



# Messages table
class Message(Base):
    __tablename__ = 'messages'
    
    message_id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.conversation_id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    message_text = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    # is_read = Column(Boolean, default=False)

    # Relationships
    conversation = relationship('Conversation', back_populates='messages')
    sender = relationship('User', back_populates='messages')



