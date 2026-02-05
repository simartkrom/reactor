"""Memory API endpoints - 사용자 메모리 관리."""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from clora.api.deps import DB, CurrentUser, Memory
from clora.models.conversation import Memory as MemoryModel
from clora.schemas.memory import MemoryCreate, MemoryResponse

router = APIRouter(prefix="/memories", tags=["memories"])


class MemorySearchRequest(BaseModel):
    """Request to search memories."""

    query: str
    n_results: int = 5
    min_importance: int = 1


class MemorySearchResult(BaseModel):
    """A memory search result."""

    id: int
    title: str
    content: str
    category: str | None
    importance: int
    relevance_score: float


class MemorySearchResponse(BaseModel):
    """Response for memory search."""

    results: list[MemorySearchResult]
    query: str


@router.get("", response_model=list[MemoryResponse])
async def list_memories(
    db: DB,
    current_user: CurrentUser,
    memory_service: Memory,
    limit: int = Query(default=50, le=100),
    offset: int = 0,
) -> list[MemoryModel]:
    """List user's memories."""
    memories = await memory_service.get_user_memories(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return memories


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    memory_data: MemoryCreate,
    db: DB,
    current_user: CurrentUser,
    memory_service: Memory,
) -> MemoryModel:
    """Create a new memory manually."""
    memory = await memory_service.save_memory(
        db=db,
        user_id=current_user.id,
        title=memory_data.title,
        content=memory_data.content,
        category=memory_data.category,
        expert_id=memory_data.expert_id,
        importance=memory_data.importance,
    )
    return memory


@router.post("/search", response_model=MemorySearchResponse)
async def search_memories(
    request: MemorySearchRequest,
    db: DB,
    current_user: CurrentUser,
    memory_service: Memory,
) -> MemorySearchResponse:
    """Search memories by semantic similarity."""
    results = await memory_service.search_memories(
        user_id=current_user.id,
        query=request.query,
        n_results=request.n_results,
        min_importance=request.min_importance,
    )

    return MemorySearchResponse(
        results=[
            MemorySearchResult(
                id=item.id,
                title=item.title,
                content=item.content,
                category=item.category,
                importance=item.importance,
                relevance_score=item.relevance_score,
            )
            for item in results
        ],
        query=request.query,
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: int,
    db: DB,
    current_user: CurrentUser,
    memory_service: Memory,
) -> MemoryModel:
    """Get a specific memory."""
    from sqlalchemy import select

    result = await db.execute(
        select(MemoryModel).where(
            MemoryModel.id == memory_id,
            MemoryModel.user_id == current_user.id,
        )
    )
    memory = result.scalar_one_or_none()

    if not memory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )

    return memory


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(
    memory_id: int,
    db: DB,
    current_user: CurrentUser,
    memory_service: Memory,
) -> None:
    """Delete a memory."""
    success = await memory_service.delete_memory(
        db=db,
        user_id=current_user.id,
        memory_id=memory_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Memory not found",
        )
