from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Comment, Post, CommentReaction, ReactionType, User
from app.schemas import CommentCreate, CommentResponse, ReactionTypeEnum
from app.routers.auth import get_current_user

router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.post("/{post_id}", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=comment_data.content
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(comment)
    db.commit()

@router.post("/{comment_id}/react/{reaction_type}", status_code=status.HTTP_201_CREATED)
async def react_to_comment(
    comment_id: int,
    reaction_type: ReactionTypeEnum,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    existing_reaction = db.query(CommentReaction).filter(
        CommentReaction.comment_id == comment_id,
        CommentReaction.user_id == current_user.id,
        CommentReaction.reaction_type == reaction_type
    ).first()
    
    if existing_reaction:
        db.delete(existing_reaction)
    else:
        reaction = CommentReaction(
            comment_id=comment_id,
            user_id=current_user.id,
            reaction_type=ReactionType[reaction_type.value.upper()]
        )
        db.add(reaction)
    
    db.commit()
    return {"status": "ok"}
