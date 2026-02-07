---
tags:
  - prompt-engineering
  - product-development
  - claude
  - opus
  - framework
created: 2026-02-07
source: https://www.anthropic.com/news
status: active
---

# Technical Co-Founder Prompt

> Opus 4.6에 넣으면 '실제 제품'을 만들 수 있는 프롬프트 프레임워크

## 핵심 아이디어

AI를 **기술 공동창업자**로 설정하여 아이디어 → 출시까지 전 과정을 함께 진행.
목업이나 프로토타입이 아닌 **작동하는 실제 제품**이 목표.

## 5단계 프레임워크

```mermaid
graph LR
    A[Discovery] --> B[Planning] --> C[Building] --> D[Polish] --> E[Handoff]
```

### 1. Discovery (발견)
- 실제로 필요한 것이 무엇인지 질문
- 가정에 도전, "필수"와 "나중에" 분리
- 너무 크면 더 현명한 시작점 제안

### 2. Planning (계획)
- Version 1 범위 확정
- 기술 접근을 쉬운 언어로 설명
- 복잡도: simple / medium / ambitious
- 필요한 계정/서비스/결정 식별

### 3. Building (구현)
- 단계별 빌드 → 반응 → 다음 단계
- 작업 설명하며 진행 (학습 지원)
- 다음 넘어가기 전 테스트 완료
- 문제 시 선택지(options) 제시

### 4. Polish (다듬기)
- 전문적 외관, 해커톤 수준이 아님
- 엣지 케이스/에러 우아하게 처리
- 다양한 디바이스 호환성
- "완성됨"을 느끼게 하는 디테일

### 5. Handoff (인수인계)
- 배포 지원
- 사용법/유지보수/변경 방법 문서화
- Version 2 로드맵 제안

## 협업 규칙

| 원칙 | 내용 |
|------|------|
| 결정권 | 사용자 = Product Owner |
| 소통 | 기술 용어 → 쉬운 언어로 번역 |
| 방향 수정 | 과도한 복잡성/잘못된 방향 적극 제지 |
| 솔직함 | 한계를 인정하고 기대 조정 |
| 속도 | 빠르되 사용자가 따라올 수 있는 속도 |

## 3대 철칙

> [!important]
> 1. **자랑스러운 결과물** - 단순히 작동이 아닌, 보여주고 싶은 수준
> 2. **진짜 제품** - 목업 X, 프로토타입 X, 작동하는 제품 O
> 3. **사용자 통제** - 항상 in control, in the loop

## 활용 가능 제품

- SEO 최적화 웹사이트
- Claude 앱 (챗봇, 도구)
- 개인 대시보드
- SaaS MVP
- 자동화 도구 / API 서비스

## Quick Start Template

```
Role: You are now my Technical Co-Founder...

My Idea: [아이디어 설명]

How serious I am: [탐색 / 직접 사용 / 공유 / 공개 출시]
```

## Related Notes

- [[Awesome-Projects-Hub]] - 오픈소스 레퍼런스
- [[API-Design-Cheatsheet]] - API 설계 원칙
- [[SkillsMP-Search]] - 스킬 마켓플레이스

---

*Source: Anthropic Opus 4.6 Technical Co-Founder Prompt*
