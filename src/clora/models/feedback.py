"""Feedback and Review models - 사용자 피드백 및 후기."""

from enum import Enum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from clora.models.base import Base, TimestampMixin


class FeedbackType(str, Enum):
    """피드백 타입."""

    REVIEW = "review"  # 후기
    SUGGESTION = "suggestion"  # 제안
    BUG = "bug"  # 버그 리포트
    FEATURE_REQUEST = "feature_request"  # 기능 요청


class Feedback(Base, TimestampMixin):
    """사용자 피드백/후기 모델."""

    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    expert_id: Mapped[int | None] = mapped_column(ForeignKey("experts.id"), nullable=True)

    feedback_type: Mapped[FeedbackType] = mapped_column(default=FeedbackType.REVIEW)
    content: Mapped[str] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(nullable=True)  # 1-5 별점

    # Display settings
    is_featured: Mapped[bool] = mapped_column(default=False)  # 메인 페이지 노출
    is_approved: Mapped[bool] = mapped_column(default=False)  # 관리자 승인
    is_anonymous: Mapped[bool] = mapped_column(default=False)  # 익명 표시

    # Optional display name for anonymous feedback
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)


class CloneRequest(Base, TimestampMixin):
    """커뮤니티 클론 요청 모델."""

    __tablename__ = "clone_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    # 요청 정보
    expert_name: Mapped[str] = mapped_column(String(100))  # 요청하는 전문가 이름
    expert_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str] = mapped_column(Text)  # 요청 이유
    reference_urls: Mapped[str | None] = mapped_column(Text, nullable=True)  # 참고 URL들 (JSON)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, approved, rejected, completed
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Vote count
    vote_count: Mapped[int] = mapped_column(default=0)


class CloneRequestVote(Base, TimestampMixin):
    """클론 요청 투표."""

    __tablename__ = "clone_request_votes"

    id: Mapped[int] = mapped_column(primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("clone_requests.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
