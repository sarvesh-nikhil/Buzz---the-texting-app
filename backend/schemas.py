from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Schema for creating a user
class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str

# Schema for the response model when retrieving user information
class User(BaseModel):
    username: str
    email: Optional[EmailStr] = None

    class Config:
        from_attributes = True

# Schema for sign-in (only username and password)
class UserSignIn(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    

class Conversation(BaseModel):
    conversation_id: int
    user1_id: int
    user2_id: int

    class Config:
        from_attributes = True


#  schema for messages
class Message(BaseModel):
    message_id: int
    conversation_id: int
    sender_id: int
    message_text: str

    class Config:
        from_attributes = True

class UserWithProfilePic(BaseModel):
    user_id: int
    username: str
    profile_image_url: str

    class Config:
        from_attributes = True
    
class EmailSchema(BaseModel):
    email: List[EmailStr]

class ResetPasswordSchema(BaseModel):
    reset_token: str
    new_password: str

