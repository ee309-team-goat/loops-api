# Loops API 유저 스토리

> 최종 업데이트: 2025-12-10

이 폴더는 Loops API의 모든 기능을 PM 유저스토리 형태로 정리한 문서들을 포함합니다.

---

## 📋 목차

| 번호 | 도메인                    | 파일                                           | 기능 수 | 설명                              |
| ---- | ------------------------- | ---------------------------------------------- | ------- | --------------------------------- |
| 01   | 인증 (Authentication)     | [01-authentication.md](./01-authentication.md) | 5       | 회원가입, 로그인, 토큰 관리       |
| 02   | 프로필 (Profile)          | [02-profile.md](./02-profile.md)               | 9       | 사용자 설정, 스트릭, 레벨         |
| 03   | 단어 카드 (Vocabulary)    | [03-vocabulary-cards.md](./03-vocabulary-cards.md) | 5   | 단어 카드 CRUD                    |
| 04   | 덱 (Decks)                | [04-decks.md](./04-decks.md)                   | 4       | 단어장 관리, 학습 덱 선택         |
| 05   | 학습 진행 (Progress)      | [05-progress.md](./05-progress.md)             | 4       | FSRS 기반 복습 관리               |
| 06   | 퀴즈 (Quiz)               | [06-quiz.md](./06-quiz.md)                     | 3       | 4가지 유형의 퀴즈                 |
| 07   | 통계 (Statistics)         | [07-statistics.md](./07-statistics.md)         | 3       | 학습량, 정확도, 추이 분석         |
| 08   | 학습 세션 (Study Session) | [08-study-session.md](./08-study-session.md)   | 2       | 세션 기반 학습 관리               |

**총 35개 기능** - 모두 구현 완료 ✅

---

## 📊 기능 요약 매트릭스

### 도메인별 기능 현황

```
인증          ████████████████████ 5개 ✅
프로필        ████████████████████████████████████ 9개 ✅
단어 카드     ████████████████████ 5개 ✅
덱            ████████████████ 4개 ✅
학습 진행     ████████████████ 4개 ✅
퀴즈          ████████████ 3개 ✅
통계          ████████████ 3개 ✅
학습 세션     ████████ 2개 ✅
```

### HTTP 메서드별 엔드포인트

| 메서드 | 개수 | 용도              |
| ------ | ---- | ----------------- |
| GET    | 20   | 조회              |
| POST   | 12   | 생성, 액션 실행   |
| PUT    | 2    | 전체 업데이트     |
| PATCH  | 3    | 부분 업데이트     |
| DELETE | 2    | 삭제              |

---

## 🔍 빠른 참조

### 인증 관련

- 회원가입: `POST /api/v1/auth/register` → [01-authentication.md#us-auth-01](./01-authentication.md#us-auth-01-회원가입)
- 로그인: `POST /api/v1/auth/login` → [01-authentication.md#us-auth-02](./01-authentication.md#us-auth-02-로그인)
- 현재 사용자: `GET /api/v1/auth/me` → [01-authentication.md#us-auth-05](./01-authentication.md#us-auth-05-현재-사용자-정보-조회)

### 학습 관련

- 세션 시작: `POST /api/v1/study/session/start` → [08-study-session.md#us-study-01](./08-study-session.md#us-study-01-학습-세션-시작)
- 복습 결과: `POST /api/v1/progress/review` → [05-progress.md#us-progress-01](./05-progress.md#us-progress-01-카드-복습-결과-제출)
- 퀴즈 시작: `POST /api/v1/quiz/start` → [06-quiz.md#us-quiz-01](./06-quiz.md#us-quiz-01-퀴즈-세션-시작)

### 통계 관련

- 총 학습량: `GET /api/v1/stats/total-learned` → [07-statistics.md#us-stats-01](./07-statistics.md#us-stats-01-총-학습량-통계-조회)
- 학습 기록: `GET /api/v1/stats/history` → [07-statistics.md#us-stats-02](./07-statistics.md#us-stats-02-학습-기록-조회)
- 스트릭: `GET /api/v1/profiles/me/streak` → [02-profile.md#us-profile-09](./02-profile.md#us-profile-09-스트릭-정보-조회)

---

## 📁 문서 구조

각 유저 스토리 문서는 다음 구조를 따릅니다:

```markdown
# 도메인명 유저 스토리

## 개요
- 도메인 설명
- 주요 특징
- 데이터 구조

## US-XXX-01: 기능명

### 스토리
사용자로서 / 관리자로서, ...

### 상세 정보
| 엔드포인트 | 인증 | 입력 | 출력 | 상태 |

### 비즈니스 규칙
(해당되는 경우)

### 요청/응답 예시

### 관련 컴포넌트
- 서비스, 모델, API 파일 위치
```

---

## 🔗 관련 문서

- [API 문서](../API.md) - Swagger/OpenAPI 상세
- [개발 가이드](../DEVELOPMENT.md) - 개발 환경 설정
- [데이터베이스](../DATABASE.md) - 스키마 및 마이그레이션
- [CLAUDE.md](../../CLAUDE.md) - AI 협업 가이드

---

## 📝 업데이트 이력

| 날짜       | 변경 내용                          |
| ---------- | ---------------------------------- |
| 2025-12-10 | 도메인별 파일 분리 및 상세 설명 추가 |
| 2025-12-10 | 초기 USER_STORIES.md 작성          |
