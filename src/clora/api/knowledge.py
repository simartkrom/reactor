"""Knowledge API endpoints - 전문가 지식베이스 관리."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from clora.api.deps import DB, CurrentUser, Knowledge
from clora.models.expert import Expert
from clora.services.content_crawler import ContentCrawler, get_content_crawler

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class AddKnowledgeRequest(BaseModel):
    """Request to add knowledge to an expert."""

    expert_id: int
    content: str
    source_type: str = "note"
    source_url: str | None = None
    source_title: str | None = None


class CrawlKnowledgeRequest(BaseModel):
    """Request to crawl and add knowledge from URL."""

    expert_id: int
    url: str


class KnowledgeAddedResponse(BaseModel):
    """Response for knowledge added."""

    chunk_ids: list[str]
    chunks_count: int
    message: str


class KnowledgeQueryRequest(BaseModel):
    """Request to query knowledge."""

    expert_id: int
    query: str
    n_results: int = 5


class KnowledgeChunkResponse(BaseModel):
    """Response for a knowledge chunk."""

    id: str
    content: str
    source_type: str
    source_url: str | None
    source_title: str | None


class KnowledgeQueryResponse(BaseModel):
    """Response for knowledge query."""

    chunks: list[KnowledgeChunkResponse]
    query: str


@router.post("/add", response_model=KnowledgeAddedResponse)
async def add_knowledge(
    request: AddKnowledgeRequest,
    db: DB,
    current_user: CurrentUser,
    knowledge_service: Knowledge,
) -> KnowledgeAddedResponse:
    """Add knowledge content to an expert's knowledge base.

    Admin only. Used to manually add notes, articles, etc.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add knowledge",
        )

    # Check expert exists
    result = await db.execute(select(Expert).where(Expert.id == request.expert_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    chunk_ids = await knowledge_service.add_knowledge(
        expert_id=request.expert_id,
        content=request.content,
        source_type=request.source_type,
        source_url=request.source_url,
        source_title=request.source_title,
    )

    return KnowledgeAddedResponse(
        chunk_ids=chunk_ids,
        chunks_count=len(chunk_ids),
        message=f"Successfully added {len(chunk_ids)} knowledge chunks",
    )


@router.post("/crawl", response_model=KnowledgeAddedResponse)
async def crawl_and_add_knowledge(
    request: CrawlKnowledgeRequest,
    db: DB,
    current_user: CurrentUser,
    knowledge_service: Knowledge,
) -> KnowledgeAddedResponse:
    """Crawl content from URL and add to expert's knowledge base.

    Admin only. Supports YouTube, blogs, and general webpages.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can crawl knowledge",
        )

    # Check expert exists
    result = await db.execute(select(Expert).where(Expert.id == request.expert_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    # Crawl content
    crawler = get_content_crawler()
    content = await crawler.crawl(request.url)

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to crawl content from URL",
        )

    # Add to knowledge base
    chunk_ids = await knowledge_service.add_knowledge(
        expert_id=request.expert_id,
        content=content.content,
        source_type=content.source_type,
        source_url=content.source_url,
        source_title=content.title,
    )

    return KnowledgeAddedResponse(
        chunk_ids=chunk_ids,
        chunks_count=len(chunk_ids),
        message=f"Successfully crawled and added {len(chunk_ids)} knowledge chunks from '{content.title}'",
    )


@router.post("/query", response_model=KnowledgeQueryResponse)
async def query_knowledge(
    request: KnowledgeQueryRequest,
    db: DB,
    current_user: CurrentUser,
    knowledge_service: Knowledge,
) -> KnowledgeQueryResponse:
    """Query an expert's knowledge base.

    Returns relevant knowledge chunks based on semantic similarity.
    """
    # Check expert exists
    result = await db.execute(select(Expert).where(Expert.id == request.expert_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    chunks = await knowledge_service.query_knowledge(
        expert_id=request.expert_id,
        query=request.query,
        n_results=request.n_results,
    )

    return KnowledgeQueryResponse(
        chunks=[
            KnowledgeChunkResponse(
                id=chunk.id,
                content=chunk.content,
                source_type=chunk.source_type,
                source_url=chunk.source_url,
                source_title=chunk.source_title,
            )
            for chunk in chunks
        ],
        query=request.query,
    )


@router.delete("/{expert_id}/chunks")
async def delete_knowledge_chunks(
    expert_id: int,
    chunk_ids: list[str],
    db: DB,
    current_user: CurrentUser,
    knowledge_service: Knowledge,
) -> dict:
    """Delete specific knowledge chunks from an expert's knowledge base.

    Admin only.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete knowledge",
        )

    # Check expert exists
    result = await db.execute(select(Expert).where(Expert.id == expert_id))
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expert not found",
        )

    await knowledge_service.delete_knowledge(expert_id=expert_id, chunk_ids=chunk_ids)

    return {"message": f"Successfully deleted {len(chunk_ids)} chunks"}
