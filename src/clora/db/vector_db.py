"""Vector database using ChromaDB for RAG."""

from functools import lru_cache
from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from clora.config import get_settings

settings = get_settings()


class VectorDB:
    """Vector database wrapper for ChromaDB."""

    def __init__(self):
        """Initialize ChromaDB client."""
        self.client = chromadb.Client(
            ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=settings.chroma_persist_dir,
                anonymized_telemetry=False,
            )
        )
        self._collections: dict[str, Any] = {}

    def get_expert_collection(self, expert_id: int) -> Any:
        """Get or create collection for an expert's knowledge base."""
        collection_name = f"expert_{expert_id}"
        if collection_name not in self._collections:
            self._collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[collection_name]

    def get_memory_collection(self, user_id: int) -> Any:
        """Get or create collection for a user's memories."""
        collection_name = f"memory_{user_id}"
        if collection_name not in self._collections:
            self._collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[collection_name]

    def add_knowledge(
        self,
        expert_id: int,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Add knowledge documents to expert's collection."""
        collection = self.get_expert_collection(expert_id)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query_knowledge(
        self,
        expert_id: int,
        query: str,
        n_results: int = 5,
    ) -> dict[str, Any]:
        """Query expert's knowledge base."""
        collection = self.get_expert_collection(expert_id)
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        return results

    def add_memory(
        self,
        user_id: int,
        documents: list[str],
        metadatas: list[dict[str, Any]],
        ids: list[str],
    ) -> None:
        """Add memory documents to user's collection."""
        collection = self.get_memory_collection(user_id)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query_memory(
        self,
        user_id: int,
        query: str,
        n_results: int = 5,
    ) -> dict[str, Any]:
        """Query user's memory collection."""
        collection = self.get_memory_collection(user_id)
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
        )
        return results

    def delete_knowledge(self, expert_id: int, ids: list[str]) -> None:
        """Delete knowledge documents from expert's collection."""
        collection = self.get_expert_collection(expert_id)
        collection.delete(ids=ids)

    def delete_memory(self, user_id: int, ids: list[str]) -> None:
        """Delete memory documents from user's collection."""
        collection = self.get_memory_collection(user_id)
        collection.delete(ids=ids)


@lru_cache
def get_vector_db() -> VectorDB:
    """Get cached VectorDB instance."""
    return VectorDB()
