"""Feedback API endpoints - 사용자 피드백 및 후기."""

import json

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from clora.api.deps import DB, CurrentUser
from clora.models.feedback import CloneRequest, CloneRequestVote, Feedback
from clora.schemas.feedback import (
    CloneRequestCreate,
    CloneRequestResponse,
    CloneRequestVoteResponse,
    FeedbackCreate,
    FeedbackResponse,
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


# ========== Feedback/Reviews ==========


@router.get("/reviews", response_model=list[FeedbackResponse])
async def list_reviews(
    db: DB,
    featured_only: bool = False,
    expert_id: int | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
) -> list[Feedback]:
    """List approved reviews/feedback."""
    query = select(Feedback).where(Feedback.is_approved == True)

    if featured_only:
        query = query.where(Feedback.is_featured == True)
    if expert_id:
        query = query.where(Feedback.expert_id == expert_id)

    query = query.order_by(Feedback.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/reviews", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    feedback_data: FeedbackCreate,
    db: DB,
    current_user: CurrentUser,
) -> Feedback:
    """Create a new review/feedback."""
    feedback = Feedback(
        user_id=current_user.id,
        expert_id=feedback_data.expert_id,
        feedback_type=feedback_data.feedback_type,
        content=feedback_data.content,
        rating=feedback_data.rating,
        is_anonymous=feedback_data.is_anonymous,
        display_name=feedback_data.display_name,
        is_approved=False,  # 관리자 승인 필요
    )
    db.add(feedback)
    await db.flush()

    return feedback


@router.put("/reviews/{feedback_id}/approve")
async def approve_review(
    feedback_id: int,
    db: DB,
    current_user: CurrentUser,
    is_featured: bool = False,
) -> dict:
    """Approve a review (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve reviews",
        )

    result = await db.execute(select(Feedback).where(Feedback.id == feedback_id))
    feedback = result.scalar_one_or_none()

    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found",
        )

    feedback.is_approved = True
    feedback.is_featured = is_featured
    await db.flush()

    return {"message": "Review approved", "is_featured": is_featured}


# ========== Clone Requests ==========


@router.get("/clone-requests", response_model=list[CloneRequestResponse])
async def list_clone_requests(
    db: DB,
    status_filter: str | None = None,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
) -> list[CloneRequest]:
    """List clone requests."""
    query = select(CloneRequest)

    if status_filter:
        query = query.where(CloneRequest.status == status_filter)

    query = query.order_by(CloneRequest.vote_count.desc(), CloneRequest.created_at.desc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post(
    "/clone-requests", response_model=CloneRequestResponse, status_code=status.HTTP_201_CREATED
)
async def create_clone_request(
    request_data: CloneRequestCreate,
    db: DB,
    current_user: CurrentUser,
) -> CloneRequest:
    """Create a new clone request."""
    reference_urls_json = None
    if request_data.reference_urls:
        reference_urls_json = json.dumps(request_data.reference_urls)

    clone_request = CloneRequest(
        user_id=current_user.id,
        expert_name=request_data.expert_name,
        expert_title=request_data.expert_title,
        reason=request_data.reason,
        reference_urls=reference_urls_json,
        status="pending",
        vote_count=1,  # 자동으로 자신의 투표 추가
    )
    db.add(clone_request)
    await db.flush()

    # 자신의 투표 추가
    vote = CloneRequestVote(
        request_id=clone_request.id,
        user_id=current_user.id,
    )
    db.add(vote)
    await db.flush()

    return clone_request


@router.post("/clone-requests/{request_id}/vote", response_model=CloneRequestVoteResponse)
async def vote_clone_request(
    request_id: int,
    db: DB,
    current_user: CurrentUser,
) -> CloneRequestVoteResponse:
    """Vote for a clone request (toggle)."""
    # Check request exists
    result = await db.execute(select(CloneRequest).where(CloneRequest.id == request_id))
    clone_request = result.scalar_one_or_none()

    if not clone_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clone request not found",
        )

    # Check if already voted
    result = await db.execute(
        select(CloneRequestVote).where(
            CloneRequestVote.request_id == request_id,
            CloneRequestVote.user_id == current_user.id,
        )
    )
    existing_vote = result.scalar_one_or_none()

    if existing_vote:
        # Remove vote
        await db.delete(existing_vote)
        clone_request.vote_count -= 1
        voted = False
    else:
        # Add vote
        vote = CloneRequestVote(
            request_id=request_id,
            user_id=current_user.id,
        )
        db.add(vote)
        clone_request.vote_count += 1
        voted = True

    await db.flush()

    return CloneRequestVoteResponse(
        request_id=request_id,
        new_vote_count=clone_request.vote_count,
        voted=voted,
    )


@router.put("/clone-requests/{request_id}/status")
async def update_clone_request_status(
    request_id: int,
    new_status: str,
    db: DB,
    current_user: CurrentUser,
    admin_note: str | None = None,
) -> dict:
    """Update clone request status (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update request status",
        )

    result = await db.execute(select(CloneRequest).where(CloneRequest.id == request_id))
    clone_request = result.scalar_one_or_none()

    if not clone_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clone request not found",
        )

    valid_statuses = ["pending", "approved", "rejected", "completed"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {valid_statuses}",
        )

    clone_request.status = new_status
    if admin_note:
        clone_request.admin_note = admin_note

    await db.flush()

    return {"message": f"Status updated to {new_status}"}
