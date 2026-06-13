from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ReactionTypeEnum(str, Enum):
    HEART = "heart"
    STAR = "star"
    FIRE = "fire"
    LAUGH = "laugh"

# User Schemas
class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    bio: Optional[str] = None
    gender: str = Field(default="M")
    age: int = Field(default=18, ge=13, le=120)
    theme_color: str = Field(default="#00c853")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    theme_color: Optional[str] = None

class UserResponse(UserBase):
    id: int
    profile_pic: str
    is_verified: bool
    created_at: datetime
    followers_count: Optional[int] = 0
    following_count: Optional[int] = 0
    is_following: Optional[bool] = False
    
    class Config:
        from_attributes = True

class UserProfileResponse(UserResponse):
    posts_count: int = 0
    reactions_count: int = 0

# Post Schemas
class PostBase(BaseModel):
    content: Optional[str] = Field(None, max_length=2000)

class PostCreate(PostBase):
    pass

class ReactionResponse(BaseModel):
    id: int
    reaction_type: ReactionTypeEnum
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    content: str
    author: UserResponse
    reactions: List[ReactionResponse] = []
    created_at: datetime
    reactions_count: dict = {"heart": 0, "star": 0, "fire": 0, "laugh": 0}
    
    class Config:
        from_attributes = True

class PostResponse(PostBase):
    id: int
    author: UserResponse
    image_path: Optional[str] = None
    video_path: Optional[str] = None
    video_duration: Optional[float] = None
    voice_path: Optional[str] = None
    voice_duration: Optional[float] = None
    comments: List[CommentResponse] = []
    reactions: List[ReactionResponse] = []
    reactions_count: dict = {"heart": 0, "star": 0, "fire": 0, "laugh": 0}
    user_reaction: Optional[ReactionTypeEnum] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Comment Schemas
class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)

# Message Schemas
class MessageCreate(BaseModel):
    content: Optional[str] = None

class MessageResponse(BaseModel):
    id: int
    sender: UserResponse
    receiver: UserResponse
    content: Optional[str] = None
    file_path: Optional[str] = None
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None

# Pagination
class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    page_size: int
