# GitHub Issues 템플릿

각 Issue를 복사해서 GitHub Projects에 붙여넣으세요.

---

## 🏷️ Labels 목록 (먼저 생성)

### Priority
- `priority: critical` 🔴
- `priority: high` 🟠
- `priority: medium` 🟡
- `priority: low` 🟢

### Type
- `type: feature` ✨
- `type: enhancement` 🔧
- `type: refactor` ♻️
- `type: testing` 🧪

### Area
- `area: database` 🗄️
- `area: api` 🌐
- `area: service` ⚙️
- `area: ai` 🤖
- `area: analytics` 📊

---

## 🎯 Milestones 목록 (먼저 생성)

### Milestone 1: Core Infrastructure
**Status**: ✅ 완료

### Milestone 2: Database Migration
**Due**: 최우선

### Milestone 3: Deck System
**Due**: TBD

### Milestone 4: Analytics & AI
**Due**: TBD

---

# 📝 Issues

## EPIC 1: Database Migration & Service Updates

---

### Issue #1

**Title:**
```
Database migration to new schema
```

**Labels:**
```
priority: critical, type: refactor, area: database
```

**Milestone:**
```
Database Migration
```

**Description:**
```markdown
## 개요
새로운 모델 스키마에 맞춰 데이터베이스 마이그레이션 수행

## 작업 내용
- [ ] Docker Compose로 PostgreSQL 실행 확인
- [ ] .env 파일의 DATABASE_URL 검증
- [ ] Alembic 마이그레이션 파일 자동 생성
  ```bash
  just revision "update schema to match new models"
  ```
- [ ] 생성된 마이그레이션 파일 검토
- [ ] 마이그레이션 적용
  ```bash
  just migrate
  ```
- [ ] 데이터베이스 스키마 검증

## ⚠️ Breaking Changes
- `User.last_study_date`: TIMESTAMP → DATE
- `SyncQueue.is_synced`: INTEGER → BOOLEAN

## 검증
- [ ] 모든 테이블 생성 확인
- [ ] Foreign key 관계 확인
- [ ] 인덱스 생성 확인

## 참고
- [DATABASE.md](./docs/DATABASE.md)
```

---

### Issue #2

**Title:**
```
Update SyncQueueService to use boolean for is_synced
```

**Labels:**
```
priority: critical, type: refactor, area: service
```

**Milestone:**
```
Database Migration
```

**Description:**
```markdown
## 개요
`SyncQueue.is_synced` 필드가 INTEGER → BOOLEAN으로 변경됨에 따라 서비스 로직 수정

## 변경 파일
`src/app/services/sync_queue_service.py`

## 작업 내용
- [ ] `mark_synced()` 메서드 수정
  - Before: `is_synced = 1`
  - After: `is_synced = True`

- [ ] `mark_failed()` 메서드 수정
  - `is_synced = False`

- [ ] `get_pending_operations()` 쿼리 수정
  - Before: `is_synced == 0`
  - After: `is_synced.is_(False)`

## 테스트
- [ ] 동기화 작업 생성 테스트
- [ ] 동기화 완료 처리 테스트
- [ ] 대기 중인 작업 조회 테스트

## 의존성
Depends on: #1
```

---

### Issue #3

**Title:**
```
Test all existing API endpoints after migration
```

**Labels:**
```
priority: high, type: testing, area: api
```

**Milestone:**
```
Database Migration
```

**Description:**
```markdown
## 개요
마이그레이션 후 기존 API 엔드포인트 정상 작동 확인

## 테스트 대상

### Authentication
- [ ] POST `/api/v1/auth/register`
- [ ] POST `/api/v1/auth/login`
- [ ] GET `/api/v1/auth/me`

### Users
- [ ] GET `/api/v1/users`
- [ ] GET `/api/v1/users/{id}`
- [ ] PATCH `/api/v1/users/{id}`

### Vocabulary Cards
- [ ] POST `/api/v1/cards`
- [ ] GET `/api/v1/cards`
- [ ] GET `/api/v1/cards/search?q=keyword`
- [ ] PATCH `/api/v1/cards/{id}`

### User Card Progress (FSRS)
- [ ] POST `/api/v1/progress/review`
- [ ] GET `/api/v1/progress/user/{user_id}`
- [ ] GET `/api/v1/progress/user/{user_id}/due`

### Sync Queue
- [ ] POST `/api/v1/sync`
- [ ] GET `/api/v1/sync/user/{user_id}/pending`
- [ ] PATCH `/api/v1/sync/{id}/synced`

## 테스트 방법
Swagger UI 사용: http://localhost:8000/docs

## 의존성
Depends on: #1, #2
```

---

## EPIC 2: Deck Management System

---

### Issue #4

**Title:**
```
Implement DeckService for deck CRUD operations
```

**Labels:**
```
priority: high, type: feature, area: service
```

**Milestone:**
```
Deck System
```

**Description:**
```markdown
## 개요
덱 관리를 위한 서비스 레이어 구현

## 파일
`src/app/services/deck_service.py` (신규 생성)

## 작업 내용

### CRUD 메서드
- [ ] `create_deck(session, data)`
- [ ] `get_deck(session, deck_id)`
- [ ] `get_decks(session, skip, limit, filters)`
- [ ] `update_deck(session, deck_id, data)`
- [ ] `delete_deck(session, deck_id)`

### 필터링
- [ ] 공개/비공개 덱 필터 (`is_public`)
- [ ] 생성자별 필터 (`creator_id`)
- [ ] 카드 수 기준 정렬

### 통계
- [ ] `get_deck_statistics(session, deck_id)`
  - 총 카드 수
  - 학습 중인 카드 수
  - 평균 난이도

## 참고
- `src/app/services/vocabulary_card_service.py`
- `src/app/services/user_service.py`

## 테스트
- [ ] CRUD 작업 테스트
- [ ] 필터링 로직 테스트
```

---

### Issue #5

**Title:**
```
Implement Deck API endpoints
```

**Labels:**
```
priority: high, type: feature, area: api
```

**Milestone:**
```
Deck System
```

**Description:**
```markdown
## 개요
덱 관리 REST API 엔드포인트 구현

## 파일
`src/app/api/routes.py` (수정)

## 엔드포인트

### 기본 CRUD
- [ ] `POST /api/v1/decks` - 덱 생성
- [ ] `GET /api/v1/decks` - 덱 목록
  - Query: `is_public`, `creator_id`, `skip`, `limit`
- [ ] `GET /api/v1/decks/{deck_id}` - 덱 상세
- [ ] `PATCH /api/v1/decks/{deck_id}` - 덱 수정 (생성자만)
- [ ] `DELETE /api/v1/decks/{deck_id}` - 덱 삭제 (생성자만)

### 추가 기능
- [ ] `GET /api/v1/decks/public` - 공개 덱 목록
- [ ] `GET /api/v1/decks/official` - 공식 덱 목록 (creator_id NULL)

## 요구사항
- JWT 인증 필수
- 권한 검증 (생성자만 수정/삭제)
- 페이지네이션 지원
- Response: `DeckRead` 스키마

## 의존성
Depends on: #4
```

---

### Issue #6

**Title:**
```
Implement UserDeckService for user-deck relationships
```

**Labels:**
```
priority: high, type: feature, area: service
```

**Milestone:**
```
Deck System
```

**Description:**
```markdown
## 개요
사용자-덱 관계 및 진행률 관리 서비스

## 파일
`src/app/services/user_deck_service.py` (신규 생성)

## 작업 내용

### 덱 구독 관리
- [ ] `subscribe_deck(session, user_id, deck_id)`
  - `is_active = True` 설정
- [ ] `unsubscribe_deck(session, user_id, deck_id)`
- [ ] `get_user_decks(session, user_id, is_active=None)`

### 진행률 계산
- [ ] `update_deck_progress(session, user_id, deck_id)`
- [ ] `calculate_progress_percentage(session, user_id, deck_id)`
  - 진행률 = (완료 카드 / 전체 카드) × 100

### 카드 상태 집계
- [ ] `get_deck_card_states(session, user_id, deck_id)`
  - NEW, LEARNING, REVIEW 카드 수 계산
  - `cards_new`, `cards_learning`, `cards_review` 업데이트

## 비즈니스 로직
- 덱 구독 시 자동으로 `is_active = True`
- 복습 완료 시 `last_studied_at` 자동 업데이트
- 진행률 자동 계산

## 의존성
Depends on: #4
```

---

### Issue #7

**Title:**
```
Implement UserDeck API endpoints
```

**Labels:**
```
priority: high, type: feature, area: api
```

**Milestone:**
```
Deck System
```

**Description:**
```markdown
## 개요
사용자의 덱 관리 API 엔드포인트

## 파일
`src/app/api/routes.py` (수정)

## 엔드포인트

### 내 덱 관리
- [ ] `POST /api/v1/my/decks`
  - Body: `{ "deck_id": 1 }`
  - 덱 구독

- [ ] `GET /api/v1/my/decks`
  - Query: `is_active` (optional)
  - 내 덱 목록

- [ ] `GET /api/v1/my/decks/{deck_id}/stats`
  - 덱별 통계
  - Response: 진행률, 카드 상태별 수, 마지막 학습

- [ ] `PATCH /api/v1/my/decks/{deck_id}`
  - Body: `{ "is_active": false }`
  - 덱 설정 변경

- [ ] `DELETE /api/v1/my/decks/{deck_id}`
  - 덱 구독 취소

## 권한
- 현재 로그인한 사용자만 자신의 덱 관리 가능

## 응답 예시
```json
{
  "deck_id": 1,
  "is_active": true,
  "cards_new": 50,
  "cards_learning": 30,
  "cards_review": 20,
  "progress_percentage": 33.3,
  "last_studied_at": "2025-01-20T12:00:00Z"
}
```

## 의존성
Depends on: #6
```

---

## EPIC 3: Study Session Tracking

---

### Issue #8

**Title:**
```
Implement StudySessionService for session tracking
```

**Labels:**
```
priority: medium, type: feature, area: service, area: analytics
```

**Milestone:**
```
Analytics & AI
```

**Description:**
```markdown
## 개요
학습 세션 추적 및 통계 서비스

## 파일
`src/app/services/study_session_service.py` (신규 생성)

## 작업 내용

### 세션 관리
- [ ] `start_session(session, user_id, deck_id=None)`
  - 세션 시작 시간 기록
  - session_id 반환

- [ ] `end_session(session, session_id, cards_studied, accuracy_rate)`
  - duration_minutes 자동 계산
  - 통계 업데이트

### 통계 계산
- [ ] `get_today_stats(session, user_id)`
- [ ] `get_weekly_stats(session, user_id)`
- [ ] `get_monthly_stats(session, user_id)`

### 리포트
- [ ] `generate_daily_report(session, user_id)`
  - 총 학습 시간
  - 총 카드 수
  - 평균 정답률

## 계산 로직
```python
duration_minutes = (end_time - start_time).total_seconds() / 60
accuracy_rate = (correct_count / total_count) * 100
```

## 집계 기간
- 일일: 오늘 (00:00 ~ 23:59)
- 주간: 최근 7일
- 월간: 최근 30일
```

---

### Issue #9

**Title:**
```
Implement StudySession API endpoints
```

**Labels:**
```
priority: medium, type: feature, area: api, area: analytics
```

**Milestone:**
```
Analytics & AI
```

**Description:**
```markdown
## 개요
학습 세션 추적 API

## 파일
`src/app/api/routes.py` (수정)

## 엔드포인트

### 세션 관리
- [ ] `POST /api/v1/sessions/start`
  - Body: `{ "deck_id": 1 }` (optional)
  - Response: `{ "session_id": 123 }`

- [ ] `PATCH /api/v1/sessions/{id}/end`
  - Body: `{ "cards_studied": 20, "accuracy_rate": 85.0 }`

### 통계 조회
- [ ] `GET /api/v1/sessions/today`
  - 오늘 세션 통계

- [ ] `GET /api/v1/sessions/history`
  - Query: `start_date`, `end_date`
  - 세션 히스토리 (페이지네이션)

- [ ] `GET /api/v1/sessions/stats`
  - Query: `period` (daily/weekly/monthly)
  - 통계 요약

## 응답 예시
```json
{
  "total_duration_minutes": 45,
  "total_cards_studied": 30,
  "average_accuracy_rate": 87.5,
  "session_count": 2
}
```

## 의존성
Depends on: #8
```

---

## EPIC 4: AI Integration

---

### Issue #10

**Title:**
```
Implement AIInteractionService for AI logging
```

**Labels:**
```
priority: low, type: feature, area: service, area: ai
```

**Milestone:**
```
Analytics & AI
```

**Description:**
```markdown
## 개요
AI 상호작용 로깅 및 분석 서비스

## 파일
`src/app/services/ai_interaction_service.py` (신규 생성)

## 작업 내용

### 상호작용 로깅
- [ ] `log_interaction(session, user_id, type, model, input, output)`
  - 토큰 수 자동 계산
  - 응답 시간 기록

### 사용량 추적
- [ ] `get_user_usage(session, user_id, start_date, end_date)`
  - 총 토큰 사용량
  - 예상 비용 계산

### 피드백
- [ ] `submit_feedback(session, interaction_id, rating)`
  - rating: 1~5

## Interaction Types
- `example_generation` - 예문 생성
- `pronunciation_check` - 발음 체크
- `explanation` - 단어 설명
- `collocation_suggestion` - 연어 추천

## 비용 계산 (예시)
```python
# GPT-3.5 Turbo
input_cost = (tokens / 1000) * 0.0015
output_cost = (tokens / 1000) * 0.002
total_cost = input_cost + output_cost
```
```

---

### Issue #11

**Title:**
```
Implement AI interaction API endpoints
```

**Labels:**
```
priority: low, type: feature, area: api, area: ai
```

**Milestone:**
```
Analytics & AI
```

**Description:**
```markdown
## 개요
AI 상호작용 API 엔드포인트

## 파일
`src/app/api/routes.py` (수정)

## 엔드포인트

### AI 상호작용
- [ ] `POST /api/v1/ai/interact`
  - Body: `{ "type": "example_generation", "input": "안녕하세요" }`
  - AI 호출 및 결과 반환

### 기록 및 통계
- [ ] `GET /api/v1/ai/history`
  - Query: `interaction_type`, `start_date`, `end_date`
  - 상호작용 기록

- [ ] `POST /api/v1/ai/feedback`
  - Body: `{ "interaction_id": 1, "rating": 5 }`
  - 피드백 제출

- [ ] `GET /api/v1/ai/usage`
  - 사용량 통계 (토큰, 비용, 요청 수)

## AI 통합 예시
```python
import openai

async def generate_example(word: str) -> str:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "한국어 예문 생성기"},
            {"role": "user", "content": f"'{word}' 예문"}
        ]
    )
    return response.choices[0].message.content
```

## 요구사항
- OpenAI API key 환경 변수 설정
- 토큰 제한 관리
- 에러 핸들링

## 의존성
Depends on: #10
```

---

## EPIC 5: Data Seeding

---

### Issue #12

**Title:**
```
Add sample deck data to seed script
```

**Labels:**
```
priority: low, type: enhancement, area: database
```

**Milestone:**
```
Analytics & AI
```

**Description:**
```markdown
## 개요
시드 스크립트에 덱 샘플 데이터 추가

## 파일
`src/scripts/seed_data.py` (수정)

## 작업 내용

### 공식 덱 생성
- [ ] "TOPIK 필수 단어 500"
- [ ] "일상 회화 표현"
- [ ] "비즈니스 한국어"
- [ ] "한국어 능력 시험 고급"

### 난이도별 덱
- [ ] 초급 덱 (CEFR A1-A2)
- [ ] 중급 덱 (CEFR B1-B2)
- [ ] 고급 덱 (CEFR C1-C2)

### 관계 데이터
- [ ] UserDeck 관계 생성 (테스트 유저 → 덱)
- [ ] 기존 카드를 덱에 할당
- [ ] 진행률 샘플 데이터

## 샘플 코드
```python
# 덱 생성
deck = Deck(
    name="TOPIK 필수 단어 500",
    description="TOPIK 시험 대비 필수 어휘",
    is_public=True,
    card_count=500
)
session.add(deck)

# UserDeck 관계
user_deck = UserDeck(
    user_id=1,
    deck_id=deck.id,
    is_active=True,
    cards_new=300,
    cards_learning=150,
    cards_review=50
)
session.add(user_deck)
```
```

---

## EPIC 6: Advanced Features (Future)

---

### Issue #13

**Title:**
```
Implement deck sharing and cloning features
```

**Labels:**
```
priority: low, type: feature, area: api
```

**Milestone:**
```
Future
```

**Description:**
```markdown
## 개요
덱 공유 및 복사 기능

## 기능

### 덱 공유
- [ ] 공유 링크 생성
- [ ] 공유 권한 관리
- [ ] 공유 링크 만료 설정

### 덱 복사
- [ ] 공개 덱 → 내 덱으로 복사
- [ ] 카드 포함 여부 선택
- [ ] 복사 시 진행률 초기화

### 덱 병합
- [ ] 여러 덱 → 하나의 덱으로 병합
- [ ] 중복 카드 제거 옵션

## API 설계
- `POST /api/v1/decks/{id}/share` - 공유 링크 생성
- `POST /api/v1/decks/{id}/clone` - 덱 복제
- `POST /api/v1/decks/merge` - 덱 병합
- `GET /api/v1/decks/popular` - 인기 덱 (공유 횟수순)
```

---

### Issue #14

**Title:**
```
Implement learning pattern analysis and recommendations
```

**Labels:**
```
priority: low, type: feature, area: analytics, area: ai
```

**Milestone:**
```
Future
```

**Description:**
```markdown
## 개요
학습 패턴 분석 및 AI 기반 추천

## 분석 기능

### 취약 단어 감지
- [ ] 정답률 낮은 카드 자동 필터링
- [ ] 반복해서 틀리는 카드 감지
- [ ] 취약 단어 목록 제공

### 학습 시간 분석
- [ ] 시간대별 학습 효율 분석
- [ ] 최적 학습 시간 추천
- [ ] 학습 패턴 인사이트

### AI 추천
- [ ] 복습 우선순위 제안
- [ ] 맞춤형 학습 계획 생성
- [ ] 유사 난이도 단어 추천

## API
- `GET /api/v1/insights/weak-cards`
- `GET /api/v1/insights/best-time`
- `GET /api/v1/insights/recommendations`
```

---

### Issue #15

**Title:**
```
Implement comprehensive statistics dashboard API
```

**Labels:**
```
priority: low, type: feature, area: analytics
```

**Milestone:**
```
Future
```

**Description:**
```markdown
## 개요
종합 학습 통계 대시보드 API

## 엔드포인트

### 개요
- [ ] `GET /api/v1/dashboard/overview`
  - 전체 학습 현황 요약
  - 오늘/이번 주/이번 달 통계

### 상세 통계
- [ ] `GET /api/v1/dashboard/daily` - 일일 리포트
- [ ] `GET /api/v1/dashboard/weekly` - 주간 통계
- [ ] `GET /api/v1/dashboard/monthly` - 월간 통계

### 목표 및 비교
- [ ] `GET /api/v1/dashboard/goals` - 목표 달성률
- [ ] `GET /api/v1/dashboard/compare` - 다른 사용자와 비교

## 포함 데이터
- 학습 시간 추이 (차트용)
- 카드 학습 진행률
- 정답률 변화
- 연속 학습 일수 (streak)
- 주간/월간 평균 비교

## 응답 예시
```json
{
  "overview": {
    "total_cards": 500,
    "cards_mastered": 150,
    "current_streak": 7,
    "study_time_today": 45
  },
  "weekly_trend": [
    { "date": "2025-01-14", "cards": 20, "time": 30 },
    { "date": "2025-01-15", "cards": 25, "time": 40 }
  ]
}
```
```

---

## 📊 우선순위 요약

### 🔴 Critical (지금 바로)
- Issue #1: Database migration
- Issue #2: SyncQueueService boolean 변경

### 🟠 High (다음 단계)
- Issue #3: API 테스트
- Issue #4-7: Deck System 전체

### 🟡 Medium (필요시)
- Issue #8-9: Study Session

### 🟢 Low (나중에)
- Issue #10-12: AI & Seeding
- Issue #13-15: Advanced Features

---

## ✅ GitHub Projects 설정 순서

1. **Labels 생성** (위의 목록 참고)
2. **Milestones 생성** (4개)
3. **Issues 생성** (이 템플릿 복사)
4. **Project Board 구성** (Backlog → To Do → In Progress → Review → Done)
5. **우선순위별로 To Do에 배치**

---

각 Issue를 복사해서 GitHub에 붙여넣으면 됩니다! 🚀
