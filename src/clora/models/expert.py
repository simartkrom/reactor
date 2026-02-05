"""Expert model - 전문가 프로필 및 지식 소스."""

from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from clora.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from clora.models.conversation import Conversation


class ExpertCategory(str, Enum):
    """전문가 카테고리."""

    VENTURE = "venture"  # 벤처/투자
    STARTUP = "startup"  # 스타트업/창업
    TECH = "tech"  # 기술/개발
    SALES = "sales"  # 세일즈/마케팅
    FINANCE = "finance"  # 금융/재무
    LEADERSHIP = "leadership"  # 리더십/경영
    GROWTH = "growth"  # 그로스/성장
    OTHER = "other"


class KnowledgeSourceType(str, Enum):
    """지식 소스 타입."""

    YOUTUBE = "youtube"
    BLOG = "blog"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    THREADS = "threads"
    NOTE = "note"  # 직접 입력한 노트
    ARTICLE = "article"
    PODCAST = "podcast"
    BOOK = "book"


class Expert(Base, TimestampMixin):
    """전문가 프로필 모델."""

    __tablename__ = "experts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))  # e.g., "벤처파트너", "프라이머 대표"
    organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category: Mapped[ExpertCategory] = mapped_column(default=ExpertCategory.OTHER)

    # Profile
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    expertise: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of expertise

    # AI Personality
    speaking_style: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # 말투 스타일 설명
    system_prompt: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # 커스텀 시스템 프롬프트

    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    is_featured: Mapped[bool] = mapped_column(default=False)

    # Relationships
    knowledge_sources: Mapped[list["ExpertKnowledgeSource"]] = relationship(
        "ExpertKnowledgeSource", back_populates="expert", cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="expert", cascade="all, delete-orphan"
    )


class ExpertKnowledgeSource(Base, TimestampMixin):
    """전문가의 지식 소스 (SNS, 유튜브, 블로그 등)."""

    __tablename__ = "expert_knowledge_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    expert_id: Mapped[int] = mapped_column(ForeignKey("experts.id"), index=True)
    source_type: Mapped[KnowledgeSourceType]
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_name: Mapped[str] = mapped_column(String(255))  # e.g., "YouTube 채널", "블로그"

    # Crawling settings
    is_auto_update: Mapped[bool] = mapped_column(default=True)  # 매일 자동 업데이트
    last_crawled_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationship
    expert: Mapped["Expert"] = relationship("Expert", back_populates="knowledge_sources")
