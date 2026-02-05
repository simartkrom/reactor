# AI Video Generator

주제를 입력하면 자동으로 AI가 영상을 생성하는 웹 애플리케이션입니다.

## 기능

- **스크립트 자동 생성**: Gemini가 주제에 맞는 대본을 작성
- **이미지 병렬 생성**: 4장의 관련 이미지를 동시에 생성 (Fal.ai FLUX)
- **음성 합성**: Gemini TTS로 대본을 자연스럽게 읽음
- **영상 합성**: FFmpeg로 부드러운 전환 효과(fade)와 함께 최종 영상 제작
- **진행 상황 표시**: 각 단계별 진행 상태를 실시간으로 확인
- **오류 복구**: 실패 시 완료된 단계를 건너뛰고 재시도 가능

## 기술 스택

- **Frontend**: Next.js 14, React, TypeScript
- **Database**: SQLite with Prisma ORM
- **AI Services**:
  - Gemini 2.0 Flash (스크립트 생성)
  - Gemini TTS (음성 합성)
  - Fal.ai FLUX Schnell (이미지 생성)
- **Video Processing**: FFmpeg

## 설치

### 요구 사항

- Node.js 18+
- FFmpeg (시스템에 설치되어 있어야 함)

### 설정

1. 의존성 설치:
```bash
npm install
```

2. 환경 변수 설정:
```bash
cp .env.example .env
```

`.env` 파일을 열고 API 키를 설정:
```
GEMINI_API_KEY=your_gemini_api_key
FAL_API_KEY=your_fal_api_key
```

3. 데이터베이스 초기화:
```bash
npx prisma generate
npx prisma db push
```

4. 개발 서버 실행:
```bash
npm run dev
```

5. 브라우저에서 http://localhost:3000 접속

## 사용 방법

1. 영상 주제를 입력 (예: "우주의 신비", "고양이의 일상")
2. "영상 생성" 버튼 클릭
3. 4단계 생성 과정 확인:
   - 스크립트 생성
   - 이미지 생성 (4장 병렬)
   - 음성 합성
   - 영상 합성
4. 완료 후 영상 미리보기 및 다운로드

## 오류 처리

- 각 단계에서 오류 발생 시 구체적인 에러 메시지 표시
- "재시도" 버튼으로 이미 완료된 단계를 건너뛰고 실패한 단계부터 재개

## 저장 위치

- **이미지**: `public/storage/images/{projectId}/`
- **오디오**: `public/storage/audio/{projectId}/`
- **비디오**: `public/storage/videos/{projectId}/`
- **데이터베이스**: `prisma/dev.db`

## API 키 발급

- **Gemini API**: https://makersuite.google.com/app/apikey
- **Fal.ai API**: https://fal.ai/
