# main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, status, Query, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import schemas
import crud
import database
from sqlalchemy import create_engine
from database import Base
from fastapi.security import OAuth2PasswordRequestForm
import auth
import json
from typing import List
import uuid
import random
from datetime import datetime, timedelta
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from starlette.responses import JSONResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# cloudinary for storing profile images
import cloudinary
import cloudinary.uploader

load_dotenv()

# MySQL Database URL
DATABASE_URL = os.getenv("DATABASE_URL")

# Create a new engine instance
engine = create_engine(DATABASE_URL)

# Create the FastAPI app
app = FastAPI()

# Create all tables in the database if they don't exist
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Email configuration for sending emails
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS") == "True",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS") == "True",
    USE_CREDENTIALS=os.getenv("USE_CREDENTIALS") == "True",
    VALIDATE_CERTS=os.getenv("VALIDATE_CERTS") == "True"
)


# Initialize Cloudinary with credentials (using f******35@gmail.com)
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# Store messages in memory for simplicity
# messages = []

# @app.websocket("/ws/conversations/{conversation_id}")
# async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
#     await websocket.accept()
    
#     # Send existing messages to the new client
#     for message in messages:
#         await websocket.send_text(message)
    
#     while True:
#         data = await websocket.receive_text()
#         messages.append(data)
#         await websocket.send_text(data)  # Echo message back to the client


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}  # conversation_id -> [WebSockets]

    async def connect(self, websocket: WebSocket, conversation_id: int):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: int):
        self.active_connections[conversation_id].remove(websocket)
        if not self.active_connections[conversation_id]:
            del self.active_connections[conversation_id]

    async def send_message(self, message: str, conversation_id: int):
        if conversation_id in self.active_connections:
            for connection in self.active_connections[conversation_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/conversations/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: int):
    await manager.connect(websocket, conversation_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_message(data, conversation_id)
    except WebSocketDisconnect:
        await manager.disconnect(websocket, conversation_id)



@app.post('/create-user', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # check of any field is empty
    if not user.username or not user.email or not user.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Any field cannot be left empty"
        )
    # check if user already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user_email = crud.get_user_by_email(db, email = user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # else add the user to the database
    return crud.create_user(db=db, username=user.username, email=user.email, password=user.password)


@app.post('/token', response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Check if username or password is empty
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password cannot be empty",
        )
    
    # Authenticate the user
    db_user = crud.authenticate_user(db=db, username=form_data.username, password=form_data.password)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate an access token
    access_token = auth.create_access_token(data={"sub": db_user.username, "user_id": db_user.user_id})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: schemas.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/users/me/profile-image")
def upload_profile_image(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db), 
    current_user: schemas.User = Depends(auth.get_current_user)
):
    try:
        # Upload the file to Cloudinary
        result = cloudinary.uploader.upload(file.file)
        profile_image_url = result.get("secure_url")

        # Update the user's profile image in the database
        updated_user = crud.update_profile_image(db=db, user_id=current_user.user_id, profile_image_url=profile_image_url)
        return {"msg": "Profile image updated successfully", "profile_image_url": profile_image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to upload image")
    
@app.get("/users/profile-image")
async def get_profile_image(current_user: schemas.User = Depends(auth.get_current_user)):
    """
    Get the profile image URL for the logged-in user.
    If the user doesn't have a profile image, return a placeholder URL.
    """
    if current_user.profile_image_url:
        return {"profile_image_url": current_user.profile_image_url}
    else:
        # Placeholder URL if profile image is null
        placeholder_url = "/static/default-placeholder.png"
        return {"profile_image_url": placeholder_url}   


# Starting a new conversation
@app.post("/new-conversation", response_model=schemas.Conversation)
def new_conversation(recipient_username: str = Query(...), db: Session=Depends(database.get_db), curr_user: schemas.User=Depends(auth.get_current_user)):
    recipient = crud.get_user_by_username(db, username=recipient_username)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient user not found")
    
    existing_conversation = crud.get_conversation_between_users(db, user1_id=curr_user.user_id, user2_id=recipient.user_id)
    if existing_conversation:
        return existing_conversation
    
    # If conversation doesn't already exist
    new_conv = crud.create_conversation(db, user1_id=curr_user.user_id, user2_id=recipient.user_id)
    return new_conv


@app.post('/send-message', response_model=schemas.Message)
def send_message(conversation_id: int, message_text: str, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    conversation = crud.get_conversation_by_id(db, conversation_id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if current_user.user_id not in [conversation.user1_id, conversation.user2_id]:
        raise HTTPException(status_code=403, detail="You are not a participant in this conversation")
    
    # Store the message in the database
    message = crud.create_message(db, conversation_id=conversation_id, sender_id=current_user.user_id, message_text=message_text)
    
    # Send the message to WebSocket clients
    return message


@app.get("/conversations/{conversation_id}/messages", response_model=List[schemas.Message])
def get_conversation_messages(conversation_id: int, db: Session = Depends(database.get_db)):
    messages = crud.get_messages_in_conversation(db, conversation_id=conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="No messages found in this conversation")
    return messages



# all the users i have started a conversation with
# @app.get("/conversations/users", response_model=List[schemas.User])
# def get_users_in_conversations(db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
#     #  fetch all conversations for the current user
#     conversations = crud.get_user_conversations(db, current_user.user_id)

#     #  extract other user ids from the conversation
#     user_ids = set()
#     for conversation in conversations:
#         if conversation.user1_id != current_user.user_id:
#             user_ids.add(conversation.user1_id)
#         if conversation.user2_id != current_user.user_id:
#             user_ids.add(conversation.user2_id)
#     # Fetch the users with the extracted user IDs
#     users = crud.get_users_by_ids(db, list(user_ids))
#     return users

@app.get("/conversations/users", response_model=List[schemas.UserWithProfilePic])
async def get_users_in_conversations(
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(auth.get_current_user)
):
    users = crud.get_users_in_conversation(db=db, current_user_id=current_user.user_id)
    # print("hi")
    # print(users)
    users_with_pictures = []
    for user in users:
        profile_image_url = user.profile_image_url if user.profile_image_url else "https://w7.pngwing.com/pngs/177/551/png-transparent-user-interface-design-computer-icons-default-stephen-salazar-graphy-user-interface-design-computer-wallpaper-sphere-thumbnail.png"
        users_with_pictures.append({
            "user_id": user.user_id,
            "username": user.username,
            "profile_image_url": profile_image_url
        })
    # print(users_with_pictures)
    return users_with_pictures



# Get conversation-id for two users
@app.get("/conversations/get-conversation-id", response_model=int)
def get_conversation_id(recipient_username: str, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    recipient_user = crud.get_user_by_username(db, recipient_username)

    if not recipient_user:
        raise HTTPException(status_code=404, detail="Recipient user not found")

    # Check if a conversation exists between the current user and the recipient
    conversation = crud.get_conversation_by_usernames(db, user1_id=current_user.user_id, user2_id=recipient_user.user_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation.conversation_id

# Handling forgot passowrd request
background_tasks = BackgroundTasks()

async def send_email(message: MessageSchema):
    fm = FastMail(conf) 
    await fm.send_message(message)
 

# Background task to send the email
async def send_email(message: MessageSchema):
    fm = FastMail(conf)
    await fm.send_message(message)

def generate_otp():
    return f"{random.randint(100000, 999999)}"

@app.post("/forgot-password")
async def forgot_password(username: str, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    # Retrieve user from the database
    user = crud.get_user_by_username(db, username=username)

    # If user not found, return an error response
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a 6-digit OTP and set an expiration time (1 hour)
    otp = generate_otp()
    expiration_time = datetime.utcnow() + timedelta(hours=1)

    # Store the OTP and expiration time in the database for the user
    crud.store_reset_token(user.user_id, otp, expiration_time)

    # Prepare the email message with the OTP
    message = MessageSchema(
        subject="Your Password Reset OTP",
        recipients=[user.email],  # Send to the user's email
        body=f"Your OTP for resetting your password on BUZZ! is: {otp}\n\nThis OTP is valid for 1 hour.",
        subtype=MessageType.plain  # Plain text email
    )

    # Send the email in the background
    background_tasks.add_task(send_email, message)

    # Return success response
    return JSONResponse(status_code=200, content={"message": "OTP sent to your email address."})


# Define the request schema
class ResetPasswordSchema(BaseModel):
    reset_token: str
    new_password: str

# Define a response schema (optional, if you want structured response validation)
class MessageResponse(BaseModel):
    message: str

# Route for resetting password
@app.post("/reset-password", response_model=MessageResponse)
async def reset_password(password_change: ResetPasswordSchema, db: Session = Depends(database.get_db)):
    reset_token = password_change.reset_token
    new_password = password_change.new_password

    # Retrieve the reset request details from the stored tokens
    reset_request = crud.reset_tokens.get(reset_token)
    if not reset_request:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Check if the reset token is expired
    if reset_request["expiration_time"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Reset token expired")
    
    # Update the user's password
    crud.update_user_password(db, reset_request["user_id"], new_password)
    
    return {"message": "Password successfully reset"}


    



    

