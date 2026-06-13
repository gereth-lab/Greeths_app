from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Post, Reaction, ReactionType, User, Follow
from app.schemas import PostCreate, PostResponse, ReactionTypeEnum
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/posts", tags=["posts"])

@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not post_data.content:
        raise HTTPException(status_code=400, detail="Post must have content or media")
    
    post = Post(
        author_id=current_user.id,
        content=post_data.content
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return post

@router.get("/feed", response_model=list[PostResponse])
async def get_feed(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    following_ids = db.query(Follow.following_id).filter(Follow.follower_id == current_user.id).all()
    following_ids = [f[0] for f in following_ids] + [current_user.id]
    
    posts = db.query(Post).filter(
        Post.author_id.in_(following_ids),
        Post.is_published == True
    ).order_by(desc(Post.created_at)).offset(skip).limit(limit).all()
    
    return posts

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(post)
    db.commit()

@router.post("/{post_id}/react/{reaction_type}", status_code=status.HTTP_201_CREATED)
async def react_to_post(
    post_id: int,
    reaction_type: ReactionTypeEnum,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_reaction = db.query(Reaction).filter(
        Reaction.post_id == post_id,
        Reaction.user_id == current_user.id,
        Reaction.reaction_type == reaction_type
    ).first()
    
    if existing_reaction:
        db.delete(existing_reaction)
    else:
        reaction = Reaction(
            post_id=post_id,
            user_id=current_user.id,
            reaction_type=ReactionType[reaction_type.value.upper()]
        )
        db.add(reaction)
    
    db.commit()
    return {"status": "ok"}

@router.get("/{post_id}/reactions", response_model=dict)
async def get_post_reactions(
    post_id: int,
    db: Session = Depends(get_db)
):
    reactions = db.query(Reaction).filter(Reaction.post_id == post_id).all()
    
    counts = {"heart": 0, "star": 0, "fire": 0, "laugh": 0}
    for r in reactions:
        counts[r.reaction_type.value] += 1
    
    return counts
