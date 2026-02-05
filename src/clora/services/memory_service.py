"""Memory Service - 대화 맥락을 기억하는 시스템.

중요한 대화 내용을 자동으로 저장하고, 나중에 검색하여 컨텍스트로 활용합니다.
"""

import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from clora.db.vector_db import VectorDB, get_vector_db
from clora.models.conversation import Memory


@dataclass
class MemoryItem:
    """A memory item with relevance score."""

    id: int
    title: str
    content: str
    category: str | None
    importance: int
    relevance_score: float


class MemoryService:
    """Service for managing user memories."""

    def __init__(self, vector_db: VectorDB | None = None):
        """Initialize Memory Service."""
        self.vector_db = vector_db or get_vector_db()

    async def save_memory(
        self,
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str,
        category: str | None = None,
        expert_id: int | None = None,
        conversation_id: int | None = None,
        importance: int = 5,
    ) -> Memory:
        """Save a new memory.

        Args:
            db: Database session
            user_id: User's ID
            title: Memory title
            content: Memory content
            category: Category (창업, 투자, etc.)
            expert_id: Associated expert ID
            conversation_id: Source conversation ID
            importance: Importance score (1-10)

        Returns:
            Created Memory instance
        """
        # Save to database
        memory = Memory(
            user_id=user_id,
            title=title,
            content=content,
            category=category,
            expert_id=expert_id,
            source_conversation_id=conversation_id,
            importance=importance,
        )
        db.add(memory)
        await db.flush()

        # Save to vector DB for semantic search
        memory_text = f"{title}\n{content}"
        if category:
            memory_text += f"\n카테고리: {category}"

        self.vector_db.add_memory(
            user_id=user_id,
            documents=[memory_text],
            metadatas=[
                {
                    "memory_id": memory.id,
                    "title": title,
                    "category": category or "",
                    "importance": importance,
                    "expert_id": expert_id or 0,
                }
            ],
            ids=[f"memory_{memory.id}"],
        )

        return memory

    async def search_memories(
        self,
        user_id: int,
        query: str,
        n_results: int = 5,
        min_importance: int = 1,
    ) -> list[MemoryItem]:
        """Search user's memories by semantic similarity.

        Args:
            user_id: User's ID
            query: Search query
            n_results: Number of results
            min_importance: Minimum importance threshold

        Returns:
            List of relevant memory items with scores
        """
        results = self.vector_db.query_memory(
            user_id=user_id,
            query=query,
            n_results=n_results * 2,  # Get more to filter by importance
        )

        items = []
        if results and results.get("documents"):
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            distances = results["distances"][0] if results.get("distances") else []

            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else 1.0

                importance = metadata.get("importance", 5)
                if importance < min_importance:
                    continue

                # Convert distance to relevance score (0-1, higher is better)
                relevance_score = 1.0 - min(distance, 1.0)

                items.append(
                    MemoryItem(
                        id=metadata.get("memory_id", 0),
                        title=metadata.get("title", ""),
                        content=doc,
                        category=metadata.get("category"),
                        importance=importance,
                        relevance_score=relevance_score,
                    )
                )

        # Sort by relevance and limit
        items.sort(key=lambda x: x.relevance_score, reverse=True)
        return items[:n_results]

    async def get_context_for_chat(
        self,
        user_id: int,
        query: str,
        expert_id: int | None = None,
        n_results: int = 3,
    ) -> str | None:
        """Get formatted memory context for chat.

        Args:
            user_id: User's ID
            query: User's question/message
            expert_id: Filter by expert (optional)
            n_results: Number of memories to include

        Returns:
            Formatted context string or None if no relevant memories
        """
        memories = await self.search_memories(
            user_id=user_id,
            query=query,
            n_results=n_results,
        )

        if not memories:
            return None

        # Filter by expert if specified
        if expert_id:
            # Include both expert-specific and general memories
            memories = [m for m in memories if m.category]  # Has some categorization

        context_parts = []
        for memory in memories:
            category_info = f"[{memory.category}] " if memory.category else ""
            context_parts.append(f"- {category_info}{memory.title}: {memory.content}")

        return "\n".join(context_parts)

    async def get_user_memories(
        self,
        db: AsyncSession,
        user_id: int,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Memory]:
        """Get all memories for a user."""
        result = await db.execute(
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def delete_memory(
        self,
        db: AsyncSession,
        user_id: int,
        memory_id: int,
    ) -> bool:
        """Delete a memory."""
        result = await db.execute(
            select(Memory).where(Memory.id == memory_id, Memory.user_id == user_id)
        )
        memory = result.scalar_one_or_none()

        if not memory:
            return False

        # Delete from vector DB
        self.vector_db.delete_memory(user_id=user_id, ids=[f"memory_{memory_id}"])

        # Delete from database
        await db.delete(memory)

        return True


@lru_cache
def get_memory_service() -> MemoryService:
    """Get cached MemoryService instance."""
    return MemoryService()
