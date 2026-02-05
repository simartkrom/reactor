"""Content API endpoints - FAQ, Tags, Suggested Questions, Stats."""

from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from clora.api.deps import DB, CurrentUser
from clora.models.content import FAQ, ExpertTag, SuggestedQuestion, Tag, UsageStats
from clora.models.conversation import Conversation, Message
from clora.models.expert import Expert
from clora.models.user import User
from clora.schemas.content import (
    ExpertWithTagsResponse,
    FAQCreate,
    FAQResponse,
    StatsResponse,
    SuggestedQuestionCreate,
    SuggestedQuestionResponse,
    TagCreate,
    TagResponse,
)

router = APIRouter(prefix="/content", tags=["content"])


# ========== FAQ ==========


@router.get("/faq", response_model=list[FAQResponse])
async def list_faqs(
    db: DB,
    category: str | None = None,
) -> list[FAQ]:
    """List all active FAQs."""
    query = select(FAQ).where(FAQ.is_active == True)

    if category:
        query = query.where(FAQ.category == category)

    query = query.order_by(FAQ.order, FAQ.id)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/faq", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    faq_data: FAQCreate,
    db: DB,
    current_user: CurrentUser,
) -> FAQ:
    """Create a new FAQ (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create FAQs",
        )

    faq = FAQ(
        question=faq_data.question,
        answer=faq_data.answer,
        category=faq_data.category,
        order=faq_data.order,
    )
    db.add(faq)
    await db.flush()

    return faq


# ========== Tags ==========


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(db: DB) -> list[Tag]:
    """List all active tags."""
    result = await db.execute(
        select(Tag).where(Tag.is_active == True).order_by(Tag.order, Tag.id)
    )
    return list(result.scalars().all())


@router.post("/tags", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    db: DB,
    current_user: CurrentUser,
) -> Tag:
    """Create a new tag (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create tags",
        )

    tag = Tag(
        name=tag_data.name,
        display_name=tag_data.display_name,
        description=tag_data.description,
        color=tag_data.color,
        order=tag_data.order,
    )
    db.add(tag)
    await db.flush()

    return tag


@router.post("/experts/{expert_id}/tags/{tag_id}")
async def add_tag_to_expert(
    expert_id: int,
    tag_id: int,
    db: DB,
    current_user: CurrentUser,
) -> dict:
    """Add a tag to an expert (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can modify expert tags",
        )

    # Check if expert and tag exist
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Expert not found")

    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Tag not found")

    # Check if already exists
    result = await db.execute(
        select(ExpertTag).where(ExpertTag.expert_id == expert_id, ExpertTag.tag_id == tag_id)
    )
    if result.scalar_one_or_none():
        return {"message": "Tag already assigned"}

    expert_tag = ExpertTag(expert_id=expert_id, tag_id=tag_id)
    db.add(expert_tag)
    await db.flush()

    return {"message": "Tag added to expert"}


@router.get("/experts/by-tag/{tag_name}", response_model=list[ExpertWithTagsResponse])
async def get_experts_by_tag(
    tag_name: str,
    db: DB,
) -> list[dict]:
    """Get experts filtered by tag."""
    # Find tag
    result = await db.execute(select(Tag).where(Tag.name == tag_name))
    tag = result.scalar_one_or_none()

    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Get expert IDs with this tag
    result = await db.execute(select(ExpertTag.expert_id).where(ExpertTag.tag_id == tag.id))
    expert_ids = [row[0] for row in result.fetchall()]

    if not expert_ids:
        return []

    # Get experts
    result = await db.execute(
        select(Expert).where(Expert.id.in_(expert_ids), Expert.is_active == True)
    )
    experts = list(result.scalars().all())

    # Build response with tags
    response = []
    for expert in experts:
        # Get tags for this expert
        tag_result = await db.execute(
            select(Tag)
            .join(ExpertTag)
            .where(ExpertTag.expert_id == expert.id, Tag.is_active == True)
        )
        tags = list(tag_result.scalars().all())

        response.append(
            {
                "id": expert.id,
                "name": expert.name,
                "title": expert.title,
                "organization": expert.organization,
                "profile_image_url": expert.profile_image_url,
                "bio": expert.bio,
                "tags": tags,
            }
        )

    return response


# ========== Suggested Questions ==========


@router.get("/suggested-questions", response_model=list[SuggestedQuestionResponse])
async def list_suggested_questions(
    db: DB,
    expert_id: int | None = None,
    tag_id: int | None = None,
    featured_only: bool = False,
    limit: int = Query(default=10, le=50),
) -> list[dict]:
    """List suggested questions."""
    query = select(SuggestedQuestion).where(SuggestedQuestion.is_active == True)

    if expert_id:
        query = query.where(SuggestedQuestion.expert_id == expert_id)
    if tag_id:
        query = query.where(SuggestedQuestion.tag_id == tag_id)
    if featured_only:
        query = query.where(SuggestedQuestion.is_featured == True)

    query = query.order_by(SuggestedQuestion.order, SuggestedQuestion.id).limit(limit)

    result = await db.execute(query)
    questions = list(result.scalars().all())

    # Add expert names
    response = []
    for q in questions:
        expert_name = None
        if q.expert_id:
            expert_result = await db.execute(select(Expert.name).where(Expert.id == q.expert_id))
            expert_name = expert_result.scalar_one_or_none()

        response.append(
            {
                "id": q.id,
                "expert_id": q.expert_id,
                "expert_name": expert_name,
                "tag_id": q.tag_id,
                "question": q.question,
                "context": q.context,
                "description": q.description,
                "is_featured": q.is_featured,
            }
        )

    return response


@router.post(
    "/suggested-questions",
    response_model=SuggestedQuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_suggested_question(
    question_data: SuggestedQuestionCreate,
    db: DB,
    current_user: CurrentUser,
) -> dict:
    """Create a suggested question (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create suggested questions",
        )

    question = SuggestedQuestion(
        expert_id=question_data.expert_id,
        tag_id=question_data.tag_id,
        question=question_data.question,
        context=question_data.context,
        description=question_data.description,
        is_featured=question_data.is_featured,
    )
    db.add(question)
    await db.flush()

    expert_name = None
    if question.expert_id:
        expert_result = await db.execute(select(Expert.name).where(Expert.id == question.expert_id))
        expert_name = expert_result.scalar_one_or_none()

    return {
        "id": question.id,
        "expert_id": question.expert_id,
        "expert_name": expert_name,
        "tag_id": question.tag_id,
        "question": question.question,
        "context": question.context,
        "description": question.description,
        "is_featured": question.is_featured,
    }


# ========== Stats ==========


@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: DB) -> StatsResponse:
    """Get overall service statistics."""
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    # Total conversations
    result = await db.execute(select(func.count(Conversation.id)))
    total_conversations = result.scalar() or 0

    # Total messages
    result = await db.execute(select(func.count(Message.id)))
    total_messages = result.scalar() or 0

    # Active experts
    result = await db.execute(select(func.count(Expert.id)).where(Expert.is_active == True))
    active_experts = result.scalar() or 0

    return StatsResponse(
        total_users=total_users,
        total_conversations=total_conversations,
        total_messages=total_messages,
        active_experts=active_experts,
    )


@router.get("/stats/featured")
async def get_featured_stats(db: DB) -> dict:
    """Get featured stats for landing page (like '700+ users, 6000+ conversations')."""
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    result = await db.execute(select(func.count(Message.id)))
    total_messages = result.scalar() or 0

    return {
        "users_count": total_users,
        "users_display": f"{total_users}+" if total_users > 0 else "0",
        "messages_count": total_messages,
        "messages_display": f"{total_messages:,}+" if total_messages > 0 else "0",
    }
