"""AI Service - GLM-4.7 API integration.

Based on the GLM-4.7 Deep Thinking mode guide.
"""

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import httpx

from clora.config import get_settings
from clora.models.expert import Expert

settings = get_settings()


@dataclass
class AIResponse:
    """AI response data."""

    content: str
    reasoning_content: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class AIService:
    """AI Service for GLM-4.7 API integration."""

    def __init__(self):
        """Initialize AI Service."""
        self.api_key = settings.glm_api_key
        self.base_url = settings.glm_api_base_url
        self.model = settings.glm_model
        self.timeout = 120.0  # 추론 모드는 느릴 수 있음 (7.9초 평균)

    def _build_system_prompt(
        self,
        expert: Expert,
        knowledge_context: str | None = None,
        memory_context: str | None = None,
    ) -> str:
        """Build system prompt for the expert."""
        # 기본 시스템 프롬프트
        base_prompt = f"""당신은 '{expert.name}'입니다. {expert.title}입니다.

## 페르소나
- 이름: {expert.name}
- 직함: {expert.title}
{f'- 소속: {expert.organization}' if expert.organization else ''}
{f'- 소개: {expert.bio}' if expert.bio else ''}
{f'- 전문 분야: {expert.expertise}' if expert.expertise else ''}

## 대화 스타일
{expert.speaking_style or '친근하고 전문적인 어조로 대화합니다. 실제 경험을 바탕으로 구체적인 조언을 제공합니다.'}

## 중요 지침
1. 당신은 실제 {expert.name}처럼 행동해야 합니다.
2. 1인칭으로 말하고, 자신의 경험과 관점에서 조언을 제공합니다.
3. "AI", "언어 모델", "프로그램" 등의 표현을 사용하지 않습니다.
4. 상대방의 상황을 이해하고 맞춤형 조언을 제공합니다.
5. 모르는 것은 솔직히 "그 부분은 잘 모르겠네요"라고 말합니다.
"""

        # 전문가의 커스텀 프롬프트가 있으면 추가
        if expert.system_prompt:
            base_prompt += f"\n## 추가 지침\n{expert.system_prompt}\n"

        # 지식베이스 컨텍스트
        if knowledge_context:
            base_prompt += f"""
## 참고 지식 (당신이 공개적으로 공유한 콘텐츠)
아래는 당신이 SNS, 블로그, 유튜브 등에서 공유한 내용입니다. 이 내용을 바탕으로 일관된 조언을 제공하세요.

{knowledge_context}
"""

        # 사용자 메모리 컨텍스트
        if memory_context:
            base_prompt += f"""
## 사용자 정보 (이전 대화에서 기억한 내용)
{memory_context}
"""

        return base_prompt

    def _build_messages(
        self,
        user_message: str,
        expert: Expert,
        conversation_history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        memory_context: str | None = None,
    ) -> list[dict[str, str]]:
        """Build messages array for API request."""
        messages = []

        # System prompt
        system_prompt = self._build_system_prompt(
            expert=expert,
            knowledge_context=knowledge_context,
            memory_context=memory_context,
        )
        messages.append({"role": "system", "content": system_prompt})

        # Conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    async def chat(
        self,
        message: str,
        expert: Expert,
        conversation_history: list[dict[str, str]] | None = None,
        knowledge_context: str | None = None,
        memory_context: str | None = None,
        thinking_mode: str = "enabled",
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        """Send chat request to GLM-4.7 API.

        Args:
            message: User's message
            expert: Expert model instance
            conversation_history: Previous messages in the conversation
            knowledge_context: Retrieved knowledge from RAG
            memory_context: User's memory context
            thinking_mode: "enabled" or "disabled"
            max_tokens: Maximum tokens for response
            temperature: Temperature for response generation

        Returns:
            AIResponse with content and optional reasoning
        """
        messages = self._build_messages(
            user_message=message,
            expert=expert,
            conversation_history=conversation_history,
            knowledge_context=knowledge_context,
            memory_context=memory_context,
        )

        # Build request payload
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens or settings.default_max_tokens,
            "temperature": temperature or settings.default_temperature,
            "stream": False,
        }

        # Add thinking config for GLM-4.7
        if self.model == "glm-4.7":
            payload["thinking"] = {"type": thinking_mode}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        # Parse response - handle both normal and reasoning modes
        # GLM-4.7 추론 모드: content는 빈 문자열, reasoning_content에 답변
        choice = data["choices"][0]
        msg = choice.get("message", {})

        content = msg.get("content", "")
        reasoning_content = msg.get("reasoning_content", "")

        # content가 비어있으면 reasoning_content 사용
        final_content = content if content else reasoning_content

        # Token usage
        usage = data.get("usage", {})

        return AIResponse(
            content=final_content,
            reasoning_content=reasoning_content if reasoning_content != final_content else None,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )

    async def analyze_for_memory(
        self,
        conversation_text: str,
    ) -> dict[str, Any] | None:
        """Analyze conversation to extract important information for memory.

        Returns memory data if important information found, None otherwise.
        """
        prompt = f"""다음 대화에서 사용자에 대한 중요한 정보를 추출해주세요.
중요한 정보란:
- 사용자가 하고 있는 일 (창업, 프로젝트 등)
- 사용자의 고민이나 목표
- 사용자의 배경 정보 (직업, 경험 등)
- 구체적인 계획이나 결정

중요한 정보가 없으면 "NONE"을 반환하세요.
중요한 정보가 있으면 아래 형식으로 반환하세요:

TITLE: [간단한 제목]
CATEGORY: [카테고리 - 창업/투자/기술/커리어/기타]
CONTENT: [핵심 내용 요약]
IMPORTANCE: [1-10 중요도]

대화:
{conversation_text}
"""

        # Use disabled thinking mode for quick analysis
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.3,
            "stream": False,
            "thinking": {"type": "disabled"},
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]

        if "NONE" in content.upper():
            return None

        # Parse the response
        try:
            lines = content.strip().split("\n")
            result = {}
            for line in lines:
                if line.startswith("TITLE:"):
                    result["title"] = line.replace("TITLE:", "").strip()
                elif line.startswith("CATEGORY:"):
                    result["category"] = line.replace("CATEGORY:", "").strip()
                elif line.startswith("CONTENT:"):
                    result["content"] = line.replace("CONTENT:", "").strip()
                elif line.startswith("IMPORTANCE:"):
                    try:
                        result["importance"] = int(line.replace("IMPORTANCE:", "").strip())
                    except ValueError:
                        result["importance"] = 5

            if "title" in result and "content" in result:
                return result
        except Exception:
            pass

        return None


@lru_cache
def get_ai_service() -> AIService:
    """Get cached AIService instance."""
    return AIService()
