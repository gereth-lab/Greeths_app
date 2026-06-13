from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, Float, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import enum

class ReactionType(str, enum.Enum):
    HEART = "heart"
    STAR = "star"
    FIRE = "fire"
    LAUGH = "laugh"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    profile_pic = Column(String(500), default="default.png")
    bio = Column(Text, default="")
    theme_color = Column(String(7), default="#00c853")
    gender = Column(String(1), default="M")
    age = Column(Integer, default=18)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="user", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")
    following = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following_user")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    
    __table_args__ = (Index('ix_users_email', 'email'), Index('ix_users_username', 'username'))

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=True)
    image_path = Column(String(500), nullable=True)
    video_path = Column(String(500), nullable=True)
    video_duration = Column(Float, nullable=True)
    voice_path = Column(String(500), nullable=True)
    voice_duration = Column(Float, nullable=True)
    is_published = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    reactions = relationship("Reaction", back_populates="post", cascade="all, delete-orphan")
    
    __table_args__ = (Index('ix_posts_author_id', 'author_id'), Index('ix_posts_created_at', 'created_at'))

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
    reactions = relationship("CommentReaction", back_populates="comment", cascade="all, delete-orphan")
    
    __table_args__ = (Index('ix_comments_post_id', 'post_id'), Index('ix_comments_author_id', 'author_id'))

class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reaction_type = Column(Enum(ReactionType), default=ReactionType.HEART)
    created_at = Column(DateTime, server_default=func.now())
    
    post = relationship("Post", back_populates="reactions")
    user = relationship("User", back_populates="reactions")
    
    __table_args__ = (
        Index('ix_reactions_post_id', 'post_id'),
        Index('ix_reactions_user_id', 'user_id'),
        UniqueConstraint('post_id', 'user_id', 'reaction_type', name='uq_post_user_reaction')
    )

class CommentReaction(Base):
    __tablename__ = "comment_reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reaction_type = Column(Enum(ReactionType), default=ReactionType.HEART)
    created_at = Column(DateTime, server_default=func.now())
    
    comment = relationship("Comment", back_populates="reactions")
    user = relationship("User")
    
    __table_args__ = (
        Index('ix_comment_reactions_comment_id', 'comment_id'),
        Index('ix_comment_reactions_user_id', 'user_id'),
        UniqueConstraint('comment_id', 'user_id', 'reaction_type', name='uq_comment_user_reaction')
    )

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    receiver_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=True)
    file_path = Column(String(500), nullable=True)
    is_read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")
    
    __table_args__ = (
        Index('ix_messages_sender_id', 'sender_id'),
        Index('ix_messages_receiver_id', 'receiver_id'),
        Index('ix_messages_created_at', 'created_at')
    )

class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    
    follower = relationship("User", foreign_keys=[follower_id], back_populates="followers")
    following_user = relationship("User", foreign_keys=[following_id], back_populates="following")
    
    __table_args__ = (
        Index('ix_follows_follower_id', 'follower_id'),
        Index('ix_follows_following_id', 'following_id'),
        UniqueConstraint('follower_id', 'following_id', name='uq_follower_following')
    )
