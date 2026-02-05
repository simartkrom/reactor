"""Main FastAPI application for Clora service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from clora.api import (
    auth_router,
    chat_router,
    experts_router,
    knowledge_router,
    memories_router,
    feedback_router,
    content_router,
)
from clora.config import get_settings
from clora.db.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Clora API",
    description="""
# Clora - AI Expert Clone Service

전문가의 생각과 목소리를 담은 AI와 대화하세요.

## 주요 기능

### 전문가 시스템
- 실제 전문가(벤처파트너, 투자자, 대표 등)의 AI 클론
- 전문가의 SNS, 유튜브, 블로그 등에서 지식을 학습
- 전문가의 말투와 관점을 반영한 대화

### 지식베이스 (RAG)
- 전문가의 공개된 콘텐츠를 자동 수집
- 의미 기반 검색으로 관련 지식 검색
- 매일 자동 업데이트

### 메모리 시스템
- 중요한 대화 내용을 자동 저장
- 사용자의 맥락을 기억하여 맞춤형 조언 제공

### 사용 예시
- "PMF를 찾았는지 어떻게 알 수 있나요?"
- "글로벌 사업 확장은 어떻게 준비하면 좋을까요?"
- "국내 SaaS 세일즈는 어떻게 해야할까요?"
""",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(experts_router)
app.include_router(chat_router)
app.include_router(knowledge_router)
app.include_router(memories_router)
app.include_router(feedback_router)
app.include_router(content_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Clora",
        "tagline": "전문가의 생각과 목소리를 담은 AI와 대화하세요",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


def main():
    """Run the application."""
    import uvicorn

    uvicorn.run(
        "clora.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
