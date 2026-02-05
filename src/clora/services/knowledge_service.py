"""Knowledge Service - RAG (Retrieval Augmented Generation) system.

전문가의 지식베이스를 관리하고 검색합니다.
SNS, 유튜브, 블로그 등에서 수집한 콘텐츠를 저장하고 쿼리합니다.
"""

import hashlib
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from clora.db.vector_db import VectorDB, get_vector_db


@dataclass
class KnowledgeChunk:
    """A chunk of knowledge content."""

    id: str
    content: str
    source_type: str  # youtube, blog, twitter, etc.
    source_url: str | None
    source_title: str | None
    metadata: dict[str, Any]


class KnowledgeService:
    """Service for managing expert knowledge bases."""

    def __init__(self, vector_db: VectorDB | None = None):
        """Initialize Knowledge Service."""
        self.vector_db = vector_db or get_vector_db()
        self.chunk_size = 1000  # characters per chunk
        self.chunk_overlap = 200

    def _generate_chunk_id(self, expert_id: int, content: str, index: int) -> str:
        """Generate unique ID for a knowledge chunk."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"expert_{expert_id}_{content_hash}_{index}"

    def _split_into_chunks(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size

            # Try to find a good break point (sentence end or paragraph)
            if end < len(text):
                # Look for paragraph break
                para_break = text.rfind("\n\n", start, end)
                if para_break > start + self.chunk_size // 2:
                    end = para_break + 2
                else:
                    # Look for sentence end
                    for sep in ["。", ".", "!", "?", "\n"]:
                        sent_break = text.rfind(sep, start + self.chunk_size // 2, end)
                        if sent_break > start:
                            end = sent_break + 1
                            break

            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap

        return [c for c in chunks if c]  # Remove empty chunks

    async def add_knowledge(
        self,
        expert_id: int,
        content: str,
        source_type: str,
        source_url: str | None = None,
        source_title: str | None = None,
        additional_metadata: dict[str, Any] | None = None,
    ) -> list[str]:
        """Add knowledge content to expert's knowledge base.

        Args:
            expert_id: Expert's ID
            content: Text content to add
            source_type: Type of source (youtube, blog, twitter, etc.)
            source_url: URL of the source
            source_title: Title of the source
            additional_metadata: Additional metadata to store

        Returns:
            List of chunk IDs that were created
        """
        chunks = self._split_into_chunks(content)

        documents = []
        metadatas = []
        ids = []

        for i, chunk in enumerate(chunks):
            chunk_id = self._generate_chunk_id(expert_id, content, i)

            metadata = {
                "source_type": source_type,
                "source_url": source_url or "",
                "source_title": source_title or "",
                "chunk_index": i,
                "total_chunks": len(chunks),
            }

            if additional_metadata:
                metadata.update(additional_metadata)

            documents.append(chunk)
            metadatas.append(metadata)
            ids.append(chunk_id)

        self.vector_db.add_knowledge(
            expert_id=expert_id,
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

        return ids

    async def query_knowledge(
        self,
        expert_id: int,
        query: str,
        n_results: int = 5,
    ) -> list[KnowledgeChunk]:
        """Query expert's knowledge base.

        Args:
            expert_id: Expert's ID
            query: Search query
            n_results: Number of results to return

        Returns:
            List of relevant knowledge chunks
        """
        results = self.vector_db.query_knowledge(
            expert_id=expert_id,
            query=query,
            n_results=n_results,
        )

        chunks = []
        if results and results.get("documents"):
            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results.get("metadatas") else []
            ids = results["ids"][0] if results.get("ids") else []

            for i, doc in enumerate(documents):
                metadata = metadatas[i] if i < len(metadatas) else {}
                chunk_id = ids[i] if i < len(ids) else str(uuid.uuid4())

                chunks.append(
                    KnowledgeChunk(
                        id=chunk_id,
                        content=doc,
                        source_type=metadata.get("source_type", "unknown"),
                        source_url=metadata.get("source_url"),
                        source_title=metadata.get("source_title"),
                        metadata=metadata,
                    )
                )

        return chunks

    async def get_context_for_chat(
        self,
        expert_id: int,
        query: str,
        n_results: int = 3,
    ) -> str | None:
        """Get formatted knowledge context for chat.

        Args:
            expert_id: Expert's ID
            query: User's question/message
            n_results: Number of chunks to include

        Returns:
            Formatted context string or None if no relevant knowledge
        """
        chunks = await self.query_knowledge(
            expert_id=expert_id,
            query=query,
            n_results=n_results,
        )

        if not chunks:
            return None

        context_parts = []
        for chunk in chunks:
            source_info = ""
            if chunk.source_title:
                source_info = f"[출처: {chunk.source_title}]"
            elif chunk.source_type:
                source_info = f"[출처: {chunk.source_type}]"

            context_parts.append(f"{source_info}\n{chunk.content}")

        return "\n\n---\n\n".join(context_parts)

    async def delete_knowledge(
        self,
        expert_id: int,
        chunk_ids: list[str],
    ) -> None:
        """Delete knowledge chunks from expert's knowledge base."""
        self.vector_db.delete_knowledge(expert_id=expert_id, ids=chunk_ids)

    async def add_knowledge_from_source(
        self,
        expert_id: int,
        source_type: str,
        source_url: str,
        content: str,
        title: str | None = None,
    ) -> list[str]:
        """Convenience method to add knowledge from a specific source."""
        return await self.add_knowledge(
            expert_id=expert_id,
            content=content,
            source_type=source_type,
            source_url=source_url,
            source_title=title,
        )


@lru_cache
def get_knowledge_service() -> KnowledgeService:
    """Get cached KnowledgeService instance."""
    return KnowledgeService()
