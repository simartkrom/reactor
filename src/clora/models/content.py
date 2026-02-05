"""Content models - FAQ, 추천 질문, 태그 등."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from clora.models.base import Base, TimestampMixin


class FAQ(Base, TimestampMixin):
    """FAQ 모델."""

    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(primary_key=True)
    question: Mapped[str] = mapped_column(String(500))
    answer: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    order: Mapped[int] = mapped_column(default=0)  # 정렬 순서
    is_active: Mapped[bool] = mapped_column(default=True)


class Tag(Base, TimestampMixin):
    """태그 모델 - 전문가 분류용."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(100))  # 한글 표시명
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Hex color
    order: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)


class ExpertTag(Base):
    """전문가-태그 연결 테이블."""

    __tablename__ = "expert_tags"

    expert_id: Mapped[int] = mapped_column(ForeignKey("experts.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)


class SuggestedQuestion(Base, TimestampMixin):
    """추천 질문 모델."""

    __tablename__ = "suggested_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    expert_id: Mapped[int | None] = mapped_column(ForeignKey("experts.id"), nullable=True)
    tag_id: Mapped[int | None] = mapped_column(ForeignKey("tags.id"), nullable=True)

    # 질문 정보
    question: Mapped[str] = mapped_column(String(500))
    context: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g., "창업의 시작"
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Display
    order: Mapped[int] = mapped_column(default=0)
    is_featured: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)


class UsageStats(Base, TimestampMixin):
    """사용 통계 모델."""

    __tablename__ = "usage_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD

    # 일별 통계
    total_users: Mapped[int] = mapped_column(default=0)
    new_users: Mapped[int] = mapped_column(default=0)
    total_conversations: Mapped[int] = mapped_column(default=0)
    total_messages: Mapped[int] = mapped_column(default=0)
    active_experts: Mapped[int] = mapped_column(default=0)
