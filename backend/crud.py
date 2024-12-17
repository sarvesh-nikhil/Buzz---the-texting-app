#  crud.py 
from sqlalchemy.orm import Session
import models
from typing import List
from datetime import datetime
# from pydantic import EmailStr

# password hashing setup
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password:str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

def create_user(db: Session, username:str, email:str, password:str):
    password_hash = hash_password(password)
    db_user = models.User(username=username, email = email, password_hash=password_hash)
    db.add(db_user)
    db.commit() 
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username==username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id==user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email==email).first()

def authenticate_user(db: Session, username: str, password: str):
    hashed_password = hash_password(password)
    db_user = get_user_by_username(db, username=username)
    if not db_user:
        return False
    if not verify_password(password, db_user.password_hash):
        return False
    return db_user


#  sub-functions for new-conversation end point
def get_conversation_between_users(db: Session, user1_id: int, user2_id: int):
    return db.query(models.Conversation).filter(
        ((models.Conversation.user1_id==user1_id)&(models.Conversation.user2_id==user2_id))|
        ((models.Conversation.user1_id==user2_id)&(models.Conversation.user2_id==user1_id))
    ).first()


def create_conversation(db: Session, user1_id: int, user2_id: int):
    conversation = models.Conversation(user1_id=user1_id, user2_id=user2_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


# sub-functions for new-message end point 
def get_conversation_by_id(db: Session, conversation_id: int):
    return db.query(models.Conversation).filter(models.Conversation.conversation_id == conversation_id).first()

def create_message(db: Session, conversation_id: int, sender_id: int, message_text: str):
    new_message = models.Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        message_text=message_text
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

# displaying messages sub-fucntion
def get_messages_in_conversation(db: Session, conversation_id: int):
    return db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.message_id).all()

# fetch all conversations for the current user
def get_user_conversations(db: Session, user_id: int):
    return db.query(models.Conversation). filter(
        (models.Conversation.user1_id == user_id) | 
        (models.Conversation.user2_id == user_id)
    ).all()


# Fetch users based on user IDs(multiple users based on multiple IDs)
def get_users_by_ids(db: Session, user_ids: List[int]):
    return db.query(models.User).filter(models.User.user_id.in_(user_ids)).all()


# sub function for get-conversation-id
def get_conversation_by_usernames(db: Session, user1_id: int, user2_id: int):
    return db.query(models.Conversation).filter(
        ((models.Conversation.user1_id == user1_id) & (models.Conversation.user2_id == user2_id)) |
        ((models.Conversation.user1_id == user2_id) & (models.Conversation.user2_id == user1_id))
    ).first()

# sub function for profile image
def update_profile_image(db: Session, user_id: int, profile_image_url: str):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user:
        user.profile_image_url = profile_image_url
        db.commit()
        db.refresh(user)
        return user
    return None

def get_users_in_conversation(db: Session, current_user_id: int):
    # Fetch user details from conversations where current user is one of the participants
    return (
        db.query(models.User)
        .join(
            models.Conversation,
            (models.Conversation.user1_id == models.User.user_id) |
            (models.Conversation.user2_id == models.User.user_id)
        )
        .filter(
            (models.Conversation.user1_id == current_user_id) |
            (models.Conversation.user2_id == current_user_id)
        )
        .filter(models.User.user_id != current_user_id)  # Exclude current user
        .distinct()
        .all()
    )

# storing reset tokens
reset_tokens = {}
def store_reset_token(user_id: int, reset_token: str, expiration_time: datetime):
    reset_tokens[reset_token] = {
        "user_id": user_id,
        "expiration_time": expiration_time 
    }


def update_user_password(db: Session, user_id: int, new_password: str):
    # Hash the new password before storing it
    hashed_new_password = hash_password(new_password)
    
    # Fetch the user by their ID
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
    if user:
        # Update the user's password with the new hashed password
        user.password_hash = hashed_new_password
        db.commit()
        db.refresh(user)  # Refresh the user object to reflect the updated data in the session
        return user
    return None


    


