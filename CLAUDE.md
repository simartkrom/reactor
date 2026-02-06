# Project Guidelines

## SkillsMP Search - Skill Installation Security Guidelines

> **Warning:** SkillsMP 마켓플레이스에는 약 12만 개 이상의 스킬이 등록되어 있습니다.
> 이는 사이트 운영자가 모든 스킬을 개별적으로 검증하지 못했을 가능성이 높다는 것을 의미합니다.
> 따라서 스킬 설치 시 아래 보안 지침을 **반드시** 준수해야 합니다.

When installing skills discovered through the SkillsMP search skill (`skillsmp-search`), the following guidelines **must** be strictly followed:

1. **격리 환경에서 사전 보안 검토 (Security Review in Isolated Environment)**
   - 특정 스킬 설치 시, 먼저 위험성 없는 격리 폴더에서 사전에 보안 검토를 수행할 것
   - 보안 검토 결과를 사용자에게 반드시 보고할 것
   - 악성 코드, 의심스러운 네트워크 요청, 민감 데이터 접근 여부 등을 확인할 것

2. **사용자 승인 필수 (User Approval Required)**
   - 1번의 보안 결과 보고와 더불어, 사용자의 승인을 **반드시** 받을 것
   - 사용자의 명시적 동의 없이 설치를 진행하지 말 것

3. **신규/저평점 스킬 주의 (Caution for New or Low-Star Skills)**
   - 신규 스킬 또는 스타 점수가 낮은 스킬은 **설치하지 말 것**
   - 사용자에게 해당 스킬의 보안 위험성을 알리고 주의를 권고할 것
   - 최종 판단은 사용자에게 맡기되, 위험성을 충분히 안내할 것
