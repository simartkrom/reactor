"""Seed data script - 샘플 전문가 및 지식베이스 데이터 생성."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import select

from clora.db.database import AsyncSessionLocal, init_db
from clora.models.expert import Expert, ExpertCategory, ExpertKnowledgeSource, KnowledgeSourceType
from clora.models.user import User
from clora.models.content import FAQ, Tag, ExpertTag, SuggestedQuestion
from clora.models.feedback import Feedback, FeedbackType
from clora.services.knowledge_service import get_knowledge_service
from clora.api.auth import get_password_hash


# 샘플 전문가 데이터 (Clora 스타일)
SAMPLE_EXPERTS = [
    {
        "name": "권도균",
        "title": "프라이머 대표",
        "organization": "프라이머",
        "category": ExpertCategory.VENTURE,
        "bio": "국내 최초 엑셀러레이터 프라이머 창업자. 20년 이상 스타트업 생태계에서 활동하며 수백 개의 스타트업을 지원했습니다.",
        "expertise": '["스타트업 투자", "액셀러레이팅", "창업 멘토링", "벤처 생태계"]',
        "speaking_style": """
친근하고 따뜻한 말투로 대화합니다. 젊은 창업가들에게 마치 선배처럼 조언합니다.
- "~해보세요", "~하는 게 좋겠어요" 형태로 조언
- 본인의 실제 경험을 자주 언급
- 실패를 두려워하지 말라는 격려를 자주 함
- 핵심을 짧고 명확하게 전달
""",
        "system_prompt": """
당신은 스타트업 창업자들의 멘토입니다. 투자 유치, 팀 빌딩, 제품 개발, 시장 진입 전략 등에 대해
실제 경험을 바탕으로 조언해주세요. 이론보다는 실전 경험을 강조합니다.
""",
        "knowledge_sources": [
            {"source_type": KnowledgeSourceType.YOUTUBE, "source_name": "프라이머 유튜브"},
            {"source_type": KnowledgeSourceType.BLOG, "source_name": "블로그"},
            {"source_type": KnowledgeSourceType.LINKEDIN, "source_name": "LinkedIn"},
        ],
    },
    {
        "name": "김용훈",
        "title": "김용훈그로스연구소 대표",
        "organization": "김용훈그로스연구소",
        "category": ExpertCategory.GROWTH,
        "bio": "그로스 해킹 전문가. 다양한 스타트업의 성장 전략을 컨설팅하고 있습니다.",
        "expertise": '["그로스 해킹", "마케팅", "데이터 분석", "사용자 획득"]',
        "speaking_style": """
데이터와 수치를 기반으로 논리적으로 설명합니다.
- 구체적인 수치와 예시를 자주 사용
- "A/B 테스트 해보셨나요?", "데이터로 확인해보면..." 같은 표현
- 실험과 검증의 중요성을 강조
""",
        "system_prompt": """
당신은 그로스 해킹 전문가입니다. 스타트업의 성장 지표, 사용자 획득, 리텐션,
매출 증대 등에 대해 데이터 기반의 조언을 해주세요.
""",
        "knowledge_sources": [
            {"source_type": KnowledgeSourceType.YOUTUBE, "source_name": "그로스 유튜브"},
            {"source_type": KnowledgeSourceType.BLOG, "source_name": "그로스 블로그"},
        ],
    },
    {
        "name": "이진수",
        "title": "신한벤처투자 글로벌본부장",
        "organization": "신한벤처투자",
        "category": ExpertCategory.VENTURE,
        "bio": "글로벌 스타트업 투자 전문가. 해외 진출 및 글로벌 스케일업에 대한 깊은 인사이트를 보유하고 있습니다.",
        "expertise": '["글로벌 투자", "해외 진출", "크로스보더 M&A", "스케일업"]',
        "speaking_style": """
전문적이고 분석적인 어조로 대화합니다.
- 글로벌 트렌드와 해외 사례를 자주 언급
- 시장 분석과 경쟁 구도를 중시
- 체계적인 접근 방법을 제안
""",
        "system_prompt": """
당신은 글로벌 투자 전문가입니다. 해외 시장 진출, 글로벌 스케일업,
해외 투자자 유치 등에 대해 조언해주세요.
""",
        "knowledge_sources": [
            {"source_type": KnowledgeSourceType.LINKEDIN, "source_name": "LinkedIn"},
        ],
    },
    {
        "name": "장현희",
        "title": "QPS Advisory 대표",
        "organization": "QPS Advisory",
        "category": ExpertCategory.FINANCE,
        "bio": "스타트업 재무/회계 전문가. IR 자료 작성부터 투자 협상까지 스타트업의 재무 전반을 지원합니다.",
        "expertise": '["재무 관리", "IR", "투자 협상", "밸류에이션"]',
        "speaking_style": """
정확하고 신뢰감 있는 어조로 대화합니다.
- 재무 용어를 쉽게 풀어서 설명
- 구체적인 숫자와 비율을 제시
- 리스크와 주의사항을 명확히 언급
""",
        "system_prompt": """
당신은 스타트업 재무 전문가입니다. 재무제표 분석, IR 자료 작성,
밸류에이션, 투자 협상 등에 대해 조언해주세요.
""",
        "knowledge_sources": [
            {"source_type": KnowledgeSourceType.NOTE, "source_name": "재무 가이드"},
        ],
    },
    {
        "name": "박이안",
        "title": "벤처파트너",
        "organization": None,
        "category": ExpertCategory.STARTUP,
        "bio": "연쇄 창업가이자 벤처파트너. 여러 스타트업을 창업하고 엑싯한 경험을 바탕으로 초기 스타트업을 지원합니다.",
        "expertise": '["창업", "제품 개발", "팀 빌딩", "초기 투자"]',
        "speaking_style": """
솔직하고 직설적인 어조로 대화합니다.
- 자신의 실패 경험도 솔직하게 공유
- "저도 그랬는데요..." 형태로 공감을 표현
- 현실적인 조언을 강조
""",
        "system_prompt": """
당신은 연쇄 창업가입니다. 창업 초기의 고민들, 팀 빌딩, 제품-시장 적합성 찾기,
초기 투자 유치 등에 대해 실제 경험을 바탕으로 조언해주세요.
""",
        "knowledge_sources": [
            {"source_type": KnowledgeSourceType.TWITTER, "source_name": "Twitter/X"},
            {"source_type": KnowledgeSourceType.THREADS, "source_name": "Threads"},
        ],
    },
]

# 샘플 지식 데이터
SAMPLE_KNOWLEDGE = {
    "권도균": [
        {
            "title": "스타트업 창업 조언",
            "content": """
스타트업을 시작하려는 분들에게 드리는 조언입니다.

첫째, 문제를 먼저 찾으세요. 솔루션이 아니라 문제에서 시작해야 합니다.
고객이 진짜 겪고 있는 문제, 돈을 내고서라도 해결하고 싶은 문제를 찾아야 합니다.

둘째, 고객을 만나세요. 사무실에서 아이디어만 다듬지 말고, 당장 밖으로 나가서
100명의 잠재 고객을 만나보세요. 그들의 이야기를 들어보면 답이 보입니다.

셋째, 빠르게 실행하세요. 완벽한 제품을 만들려고 하지 마세요.
부끄러운 버전이라도 빨리 출시해서 피드백을 받는 것이 중요합니다.

넷째, 팀이 중요합니다. 혼자서는 할 수 없어요.
서로 다른 강점을 가진 공동창업자를 찾으세요.
""",
            "source_type": "blog",
        },
        {
            "title": "PMF(Product-Market Fit) 찾기",
            "content": """
PMF를 찾았는지 어떻게 알 수 있을까요?

가장 확실한 방법은 '고객의 지갑을 열게 하는 것'입니다.
무료 사용자 1만 명보다 유료 사용자 100명이 더 중요합니다.

PMF의 신호들:
1. 고객이 먼저 찾아온다 (입소문, 추천)
2. 해지율이 낮다 (계속 쓴다)
3. 고객이 제품 개선을 요청한다 (관심이 있다)
4. 가격을 올려도 떠나지 않는다

아직 PMF를 못 찾았다면, 더 좁은 세그먼트를 공략해보세요.
모든 사람을 위한 제품은 아무도 위한 제품이 아닙니다.
""",
            "source_type": "youtube",
        },
    ],
    "김용훈": [
        {
            "title": "그로스 해킹 기본",
            "content": """
그로스 해킹의 핵심은 '실험'입니다.

1. 가설을 세우세요
   - "랜딩 페이지 제목을 바꾸면 전환율이 10% 올라갈 것이다"

2. 실험을 설계하세요
   - A/B 테스트로 검증
   - 충분한 샘플 사이즈 확보

3. 데이터로 판단하세요
   - 감이 아니라 숫자로 결정
   - 통계적 유의성 확인

4. 반복하세요
   - 작은 개선의 복리 효과
   - 매주 2-3개의 실험 진행

그로스는 마법이 아닙니다.
끊임없는 실험과 개선의 과정입니다.
""",
            "source_type": "blog",
        },
    ],
}


async def seed_admin_user(session):
    """Create admin user."""
    result = await session.execute(select(User).where(User.email == "admin@clora.ai"))
    if result.scalar_one_or_none():
        print("Admin user already exists")
        return

    admin = User(
        email="admin@clora.ai",
        username="admin",
        hashed_password=get_password_hash("admin123!"),
        full_name="Clora Admin",
        is_superuser=True,
    )
    session.add(admin)
    await session.flush()
    print("Created admin user: admin@clora.ai / admin123!")


async def seed_experts(session):
    """Create sample experts."""
    knowledge_service = get_knowledge_service()

    for expert_data in SAMPLE_EXPERTS:
        # Check if expert exists
        result = await session.execute(select(Expert).where(Expert.name == expert_data["name"]))
        if result.scalar_one_or_none():
            print(f"Expert {expert_data['name']} already exists, skipping...")
            continue

        # Create expert
        knowledge_sources_data = expert_data.pop("knowledge_sources", [])

        expert = Expert(**expert_data, is_featured=True)
        session.add(expert)
        await session.flush()

        # Add knowledge sources
        for source_data in knowledge_sources_data:
            source = ExpertKnowledgeSource(
                expert_id=expert.id,
                **source_data,
            )
            session.add(source)

        print(f"Created expert: {expert.name}")

        # Add sample knowledge
        if expert.name in SAMPLE_KNOWLEDGE:
            for knowledge in SAMPLE_KNOWLEDGE[expert.name]:
                await knowledge_service.add_knowledge(
                    expert_id=expert.id,
                    content=knowledge["content"],
                    source_type=knowledge["source_type"],
                    source_title=knowledge["title"],
                )
            print(f"  Added {len(SAMPLE_KNOWLEDGE[expert.name])} knowledge items")

    await session.commit()


# 태그 데이터
SAMPLE_TAGS = [
    {"name": "startup", "display_name": "창업의 시작", "order": 1},
    {"name": "growth", "display_name": "성장 전략", "order": 2},
    {"name": "tech", "display_name": "기술 트렌드", "order": 3},
    {"name": "investment", "display_name": "투자 유치", "order": 4},
    {"name": "organization", "display_name": "조직 관리", "order": 5},
    {"name": "sales", "display_name": "마케팅/세일즈", "order": 6},
    {"name": "ai", "display_name": "AI 활용", "order": 7},
    {"name": "global", "display_name": "글로벌 진출", "order": 8},
]

# 전문가-태그 매핑
EXPERT_TAG_MAPPING = {
    "권도균": ["startup", "investment", "organization"],
    "김용훈": ["growth", "sales"],
    "이진수": ["investment", "global"],
    "장현희": ["investment", "organization"],
    "박이안": ["startup", "tech"],
}

# FAQ 데이터
SAMPLE_FAQS = [
    {
        "question": "로그인 없이도 쓸 수 있나요?",
        "answer": "네, 기본적인 대화는 로그인 없이도 가능합니다. 다만 대화 기록 저장, 메모리 기능 등 개인화된 서비스를 이용하시려면 로그인이 필요합니다.",
        "order": 1,
    },
    {
        "question": "무료인가요?",
        "answer": "기본 기능은 무료로 제공됩니다. 더 많은 대화량과 프리미엄 기능은 유료 플랜에서 이용하실 수 있습니다.",
        "order": 2,
    },
    {
        "question": "클론은 당사자에게 동의를 받고 제작됐나요?",
        "answer": "네, 모든 AI 클론은 해당 전문가의 동의를 받고 제작되었습니다. 전문가들이 직접 검수하고 승인한 콘텐츠만 학습에 사용됩니다.",
        "order": 3,
    },
    {
        "question": "어떤 정보를 학습했나요?",
        "answer": "각 전문가가 공개적으로 발표한 콘텐츠를 학습합니다. 유튜브 강연, 블로그 글, SNS 포스팅, 인터뷰 기사 등 공개된 자료만 사용합니다.",
        "order": 4,
    },
    {
        "question": "저도 클론을 만들 수 있나요?",
        "answer": "현재는 선별된 전문가만 클론을 만들 수 있습니다. 원하시는 전문가가 있다면 커뮤니티에서 요청해주세요. 많은 요청이 있는 전문가를 우선적으로 검토합니다.",
        "order": 5,
    },
]

# 추천 질문 데이터
SAMPLE_SUGGESTED_QUESTIONS = [
    {
        "expert_name": "권도균",
        "question": "제품부터 만들까요? 시장조사부터 할까요?",
        "context": "창업의 시작",
        "description": "아이디어는 있는데 뭐부터 해야 하죠?",
        "is_featured": True,
    },
    {
        "expert_name": "권도균",
        "question": "PMF를 찾았는지 어떻게 알 수 있나요?",
        "context": "창업의 시작",
        "is_featured": True,
    },
    {
        "expert_name": "박이안",
        "question": "새로운 아이디어를 검토할 때 무엇을 가장 먼저 보시나요?",
        "context": "창업의 시작",
        "is_featured": True,
    },
    {
        "expert_name": "김용훈",
        "question": "수익화는 언제부터 해야할까요?",
        "context": "성장 전략",
        "is_featured": True,
    },
    {
        "expert_name": "이진수",
        "question": "글로벌 사업 확장은 어떻게 준비하면 좋을까요?",
        "context": "글로벌 진출",
        "is_featured": True,
    },
    {
        "expert_name": "장현희",
        "question": "시드 투자 받을 때 밸류에이션은 어떻게 정하나요?",
        "context": "투자 유치",
        "is_featured": True,
    },
]

# 샘플 피드백/후기
SAMPLE_FEEDBACKS = [
    {
        "content": "내향인(?)이라 멘토님들께 다가가지 못하는 문제를 해결해주는거 같아요!",
        "is_featured": True,
        "is_anonymous": True,
    },
    {
        "content": "실제적이고, 현실적인 조언들을 주는것 같아요",
        "is_featured": True,
        "is_anonymous": True,
    },
    {
        "content": "저는 이제 비즈니스 고민은 제미나이 안 쓰고 클로라만 씁니다ㅋㅋ",
        "is_featured": True,
        "is_anonymous": True,
    },
    {
        "content": "클로라는 진짜 전문가랑 대화하고 소통하는 느낌이라 많이 도움되는거같아요.",
        "is_featured": True,
        "is_anonymous": True,
    },
    {
        "content": "클로라 너무 똑똑해요.. 진짜 권도균 대표님이랑 대화하는 것 같네요ㅠㅠ",
        "is_featured": True,
        "is_anonymous": True,
    },
]


async def seed_tags(session):
    """Create sample tags."""
    for tag_data in SAMPLE_TAGS:
        result = await session.execute(select(Tag).where(Tag.name == tag_data["name"]))
        if result.scalar_one_or_none():
            continue

        tag = Tag(**tag_data)
        session.add(tag)

    await session.flush()
    print(f"Created {len(SAMPLE_TAGS)} tags")


async def seed_expert_tags(session):
    """Link experts to tags."""
    for expert_name, tag_names in EXPERT_TAG_MAPPING.items():
        result = await session.execute(select(Expert).where(Expert.name == expert_name))
        expert = result.scalar_one_or_none()
        if not expert:
            continue

        for tag_name in tag_names:
            result = await session.execute(select(Tag).where(Tag.name == tag_name))
            tag = result.scalar_one_or_none()
            if not tag:
                continue

            # Check if already exists
            result = await session.execute(
                select(ExpertTag).where(
                    ExpertTag.expert_id == expert.id,
                    ExpertTag.tag_id == tag.id,
                )
            )
            if result.scalar_one_or_none():
                continue

            expert_tag = ExpertTag(expert_id=expert.id, tag_id=tag.id)
            session.add(expert_tag)

    await session.flush()
    print("Linked experts to tags")


async def seed_faqs(session):
    """Create sample FAQs."""
    for faq_data in SAMPLE_FAQS:
        result = await session.execute(select(FAQ).where(FAQ.question == faq_data["question"]))
        if result.scalar_one_or_none():
            continue

        faq = FAQ(**faq_data, is_active=True)
        session.add(faq)

    await session.flush()
    print(f"Created {len(SAMPLE_FAQS)} FAQs")


async def seed_suggested_questions(session):
    """Create sample suggested questions."""
    for q_data in SAMPLE_SUGGESTED_QUESTIONS:
        expert_name = q_data.pop("expert_name")

        result = await session.execute(select(Expert).where(Expert.name == expert_name))
        expert = result.scalar_one_or_none()
        if not expert:
            continue

        result = await session.execute(
            select(SuggestedQuestion).where(SuggestedQuestion.question == q_data["question"])
        )
        if result.scalar_one_or_none():
            continue

        question = SuggestedQuestion(expert_id=expert.id, **q_data, is_active=True)
        session.add(question)

    await session.flush()
    print(f"Created {len(SAMPLE_SUGGESTED_QUESTIONS)} suggested questions")


async def seed_feedbacks(session):
    """Create sample feedbacks/reviews."""
    for fb_data in SAMPLE_FEEDBACKS:
        result = await session.execute(select(Feedback).where(Feedback.content == fb_data["content"]))
        if result.scalar_one_or_none():
            continue

        feedback = Feedback(
            feedback_type=FeedbackType.REVIEW,
            is_approved=True,
            **fb_data,
        )
        session.add(feedback)

    await session.flush()
    print(f"Created {len(SAMPLE_FEEDBACKS)} feedbacks")


async def main():
    """Run seed script."""
    print("Initializing database...")
    await init_db()

    async with AsyncSessionLocal() as session:
        print("\nSeeding admin user...")
        await seed_admin_user(session)

        print("\nSeeding experts...")
        await seed_experts(session)

        print("\nSeeding tags...")
        await seed_tags(session)

        print("\nLinking experts to tags...")
        await seed_expert_tags(session)

        print("\nSeeding FAQs...")
        await seed_faqs(session)

        print("\nSeeding suggested questions...")
        await seed_suggested_questions(session)

        print("\nSeeding feedbacks...")
        await seed_feedbacks(session)

        await session.commit()

    print("\nDone!")


if __name__ == "__main__":
    asyncio.run(main())
