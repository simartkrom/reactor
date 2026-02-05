"""Expert API endpoints."""

import json
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from clora.api.deps import DB, CurrentUser
from clora.models.expert import Expert, ExpertCategory, ExpertKnowledgeSource
from clora.schemas.expert import (
    ExpertCreate,
    ExpertListResponse,
    ExpertResponse,
    KnowledgeSourceCreate,
    KnowledgeSourceResponse,
)

router = APIRouter(prefix="/experts", tags=["experts"])


@router.get("", response_model=list[ExpertListResponse])
async def list_experts(
    db: DB,
    category: ExpertCategory | None = None,
    featured_only: bool = False,
    limit: int = Query(default=20, le=100),
    offset: int = 0,
) -> list[Expert]:
    """List all active experts."""
    query = select(Expert).where(Expert.is_active == True)

    if category:
        query = query.where(Expert.category == category)
    if featured_only:
        query = query.where(Expert.is_featured == True)

    query = query.order_by(Expert.is_featured.desc(), Expert.name).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{expert_id}", response_model=ExpertResponse)
async def get_expert(expert_id: int, db: DB) -> Expert:
    """Get expert by ID with knowledge sources."""
    result = await db.execute(
        select(Expert)
        .options(selectinload(Expert.knowledge_sources))
        .where(Expert.id == expert_id, Expert.is_active == True)
    )
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    return expert


@router.post("", response_model=ExpertResponse, status_code=status.HTTP_201_CREATED)
async def create_expert(
    expert_data: ExpertCreate,
    db: DB,
    current_user: CurrentUser,
) -> Expert:
    """Create a new expert (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create experts",
        )

    # Create expert
    expert = Expert(
        name=expert_data.name,
        title=expert_data.title,
        organization=expert_data.organization,
        category=expert_data.category,
        profile_image_url=expert_data.profile_image_url,
        bio=expert_data.bio,
        expertise=expert_data.expertise,
        speaking_style=expert_data.speaking_style,
        system_prompt=expert_data.system_prompt,
    )
    db.add(expert)
    await db.flush()

    # Add knowledge sources
    for source_data in expert_data.knowledge_sources:
        source = ExpertKnowledgeSource(
            expert_id=expert.id,
            source_type=source_data.source_type,
            source_url=source_data.source_url,
            source_name=source_data.source_name,
            is_auto_update=source_data.is_auto_update,
        )
        db.add(source)

    await db.flush()

    # Reload with relationships
    result = await db.execute(
        select(Expert).options(selectinload(Expert.knowledge_sources)).where(Expert.id == expert.id)
    )
    return result.scalar_one()


@router.put("/{expert_id}", response_model=ExpertResponse)
async def update_expert(
    expert_id: int,
    expert_data: ExpertCreate,
    db: DB,
    current_user: CurrentUser,
) -> Expert:
    """Update an expert (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update experts",
        )

    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    # Update fields
    expert.name = expert_data.name
    expert.title = expert_data.title
    expert.organization = expert_data.organization
    expert.category = expert_data.category
    expert.profile_image_url = expert_data.profile_image_url
    expert.bio = expert_data.bio
    expert.expertise = expert_data.expertise
    expert.speaking_style = expert_data.speaking_style
    expert.system_prompt = expert_data.system_prompt

    await db.flush()

    # Reload with relationships
    result = await db.execute(
        select(Expert).options(selectinload(Expert.knowledge_sources)).where(Expert.id == expert.id)
    )
    return result.scalar_one()


@router.delete("/{expert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expert(
    expert_id: int,
    db: DB,
    current_user: CurrentUser,
) -> None:
    """Delete an expert (admin only). Actually sets is_active to False."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete experts",
        )

    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    expert = result.scalar_one_or_none()

    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    expert.is_active = False
    await db.flush()


@router.post(
    "/{expert_id}/knowledge-sources",
    response_model=KnowledgeSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_knowledge_source(
    expert_id: int,
    source_data: KnowledgeSourceCreate,
    db: DB,
    current_user: CurrentUser,
) -> ExpertKnowledgeSource:
    """Add a knowledge source to an expert."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add knowledge sources",
        )

    # Check expert exists
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    source = ExpertKnowledgeSource(
        expert_id=expert_id,
        source_type=source_data.source_type,
        source_url=source_data.source_url,
        source_name=source_data.source_name,
        is_auto_update=source_data.is_auto_update,
    )
    db.add(source)
    await db.flush()

    return source
