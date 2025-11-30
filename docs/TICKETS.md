# Loops API - Backend Ticket List

> Generated from ROADMAP.md on 2025-11-30
> Backend-focused ticket list (Frontend tickets excluded)

## 🎫 Ticket Overview

**Total Backend Tickets:** 48

- ✅ Completed: 5
- 🚧 In Progress: 0
- 📋 To Do: 43

**Priority Distribution:**

- 🔴 High Priority: 14 tickets
- 🟡 Medium Priority: 15 tickets
- 🟢 Low Priority: 14 tickets

---

## 📑 Table of Contents

- [Backend API Tickets](#backend-api-tickets) (29 tickets)
- [Data Preparation Tickets](#data-preparation-tickets) (5 tickets)
- [Security & Infrastructure Tickets](#security--infrastructure-tickets) (7 tickets)
- [Testing Tickets](#testing-tickets) (7 tickets)
- [Sprint Assignments](#sprint-assignments)

---

## 🏗️ Backend API Tickets

### BE-H1: 일일 학습 목표 조회

**Endpoint:** `GET /api/v1/users/me/daily-goal`  
**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Labels:** `backend`, `api`, `home`, `user`

**Description:**

사용자의 일일 학습 목표와 오늘의 완료 수를 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/users.py`
- [ ] Return `{ "daily_goal": int, "completed_today": int }`
- [ ] Count today's reviews from UserCardProgress
- [ ] Require authentication (Depends(get_current_user))
- [ ] Add to API documentation

**Response Example:**

```json
{
  "daily_goal": 20,
  "completed_today": 12
}
```

---

### BE-H2: 오늘의 학습 진행률 조회

**Endpoint:** `GET /api/v1/users/me/today-progress`  
**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Labels:** `backend`, `api`, `home`, `progress`

**Description:**

오늘의 학습 진행 통계를 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/progress.py`
- [ ] Count today's reviews (all states)
- [ ] Count correct vs wrong reviews today
- [ ] Calculate accuracy rate for today
- [ ] Return daily goal progress percentage
- [ ] Add timezone handling (use server time or user.timezone if available)

**Response Example:**

```json
{
  "total_reviews": 12,
  "correct_count": 10,
  "wrong_count": 2,
  "accuracy_rate": 83.3,
  "daily_goal": 20,
  "goal_progress": 60.0
}
```

---

### BE-H3: 새 카드 개수 조회

**Endpoint:** `GET /api/v1/progress/new-cards-count`  
**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Dependencies:** BE-D2  
**Labels:** `backend`, `api`, `home`, `progress`

**Description:**

사용자가 선택한 덱을 기반으로 학습 가능한 새 카드의 개수를 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/progress.py`
- [ ] Query cards user hasn't seen yet (not in UserCardProgress)
- [ ] Filter by selected decks (respect user.select_all_decks flag)
- [ ] If select_all_decks=true, count from all public decks
- [ ] If select_all_decks=false, count from user_selected_decks only
- [ ] Return count only (not full card data)
- [ ] Also return review cards count for convenience

**Response Example:**

```json
{
  "new_cards_count": 320,
  "review_cards_count": 15
}
```

---

### BE-D1: 덱 목록 조회 (진행률 포함)

**Endpoint:** `GET /api/v1/decks`  
**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Dependencies:** BE-D6  
**Labels:** `backend`, `api`, `deck`

**Description:**

현재 사용자의 학습 진행 정보가 포함된 모든 덱 목록을 조회합니다.

**Acceptance Criteria:**

- [ ] Create new file `src/app/api/decks.py`
- [ ] Create endpoint GET /api/v1/decks
- [ ] Include total_cards, learned_cards, learning_cards, new_cards per deck
- [ ] Calculate progress_percent using DeckService (BE-D6)
- [ ] Support pagination (skip/limit parameters)
- [ ] Filter: show public decks + user's own decks
- [ ] Register router in `src/app/api/routes.py`

**Response Example:**

```json
{
  "decks": [
    {
      "id": 1,
      "name": "TOPIK 초급",
      "description": "Basic Korean vocabulary",
      "total_cards": 500,
      "learned_cards": 150,
      "learning_cards": 30,
      "new_cards": 320,
      "progress_percent": 30.0
    }
  ],
  "total": 5,
  "skip": 0,
  "limit": 10
}
```

---

### BE-D2: 선택한 덱 설정

**Endpoint:** `PUT /api/v1/users/me/selected-decks`  
**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `backend`, `api`, `deck`, `user`

**Description:**

사용자가 학습할 덱을 선택합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/decks.py`
- [ ] Accept `select_all` boolean + `deck_ids` array in request body
- [ ] Update user.select_all_decks field
- [ ] If select_all=false, sync user_selected_decks table
- [ ] Clear existing selections when updating (delete old records)
- [ ] Validate deck IDs exist and are accessible
- [ ] Return updated selection

**Request Example:**

```json
// Option 1: Select all
{ "select_all": true }

// Option 2: Select specific decks
{ "select_all": false, "deck_ids": [1, 3, 5] }
```

---

### BE-D3: 선택한 덱 조회

**Endpoint:** `GET /api/v1/users/me/selected-decks`  
**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `backend`, `api`, `deck`, `user`

**Description:**

사용자가 현재 선택한 덱을 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/decks.py`
- [ ] Return select_all status
- [ ] If select_all=false, return deck_ids array and deck details
- [ ] Include deck names and basic info (card_count, progress)

**Response Example:**

```json
{
  "select_all": false,
  "deck_ids": [1, 3, 5],
  "decks": [
    {
      "id": 1,
      "name": "TOPIK 초급",
      "total_cards": 500,
      "progress_percent": 30.0
    },
    {
      "id": 3,
      "name": "Business Korean",
      "total_cards": 200,
      "progress_percent": 10.0
    },
    {
      "id": 5,
      "name": "Travel Korean",
      "total_cards": 150,
      "progress_percent": 0.0
    }
  ]
}
```

---

### BE-D4: 특정 덱 상세 조회

**Endpoint:** `GET /api/v1/decks/{id}`  
**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `backend`, `api`, `deck`

**Description:**

사용자의 진행률을 포함한 특정 덱의 상세 정보를 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/decks.py`
- [ ] Return deck details (name, description, creator_id, etc.)
- [ ] Include user's progress if authenticated
- [ ] Include card count breakdown
- [ ] Return 404 if deck not found
- [ ] Return 403 if deck is private and user doesn't have access

---

### BE-D5: 덱의 단어 카드 목록 조회

**Endpoint:** `GET /api/v1/decks/{id}/cards`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `backend`, `api`, `deck`, `vocabulary`

**Description:**

특정 덱의 모든 단어 카드를 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/decks.py`
- [ ] Support pagination (skip/limit parameters)
- [ ] Include user's progress state for each card if authenticated (NEW/LEARNING/REVIEW)
- [ ] Support sorting by: difficulty, frequency, recently_added
- [ ] Support filtering by: cefr_level, difficulty_level
- [ ] Return 404 if deck not found

---

### BE-D6: 덱 진행률 계산 로직

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `backend`, `service`, `deck`

**Description:**

사용자의 덱 학습 진행률을 계산하는 서비스 메서드를 구현합니다.

**Acceptance Criteria:**

- [ ] Create `src/app/services/deck_service.py`
- [ ] Implement `calculate_deck_progress(session, user_id, deck_id)` method
- [ ] Count cards by state: NEW, LEARNING, REVIEW
- [ ] Calculate progress percentage = (learned / total) \* 100
- [ ] Optimize with single query (JOIN VocabularyCard with UserCardProgress)
- [ ] Handle case where user has no progress (all cards are NEW)

**Technical Notes:**

```python
@staticmethod
async def calculate_deck_progress(
    session: AsyncSession,
    user_id: int,
    deck_id: int
) -> dict:
    """
    Returns: {
        "total_cards": int,
        "learned_cards": int,  # REVIEW state
        "learning_cards": int,  # LEARNING/RELEARNING
        "new_cards": int,  # Not in UserCardProgress
        "progress_percent": float
    }
    """
```

---

### BE-S1: 연속 학습 일수 조회

**Endpoint:** `GET /api/v1/users/me/streak`  
**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `backend`, `api`, `statistics`, `user`

**Description:**

사용자의 연속 학습 일수 정보를 조회합니다 (User 모델에 필드 존재).

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/users.py`
- [ ] Return current_streak, longest_streak, last_study_date
- [ ] Calculate days_studied_this_month (count distinct study dates)
- [ ] Add streak_status: "active" if last_study_date is today or yesterday, "broken" otherwise
- [ ] Add helpful message based on streak status

**Response Example:**

```json
{
  "current_streak": 7,
  "longest_streak": 15,
  "last_study_date": "2025-11-30",
  "days_studied_this_month": 12,
  "streak_status": "active",
  "message": "🔥 7일 연속 학습 중!"
}
```

---

### BE-S2: 학습 완료 단어 수 조회

**Endpoint:** `GET /api/v1/stats/total-learned`  
**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `backend`, `api`, `statistics`

**Description:**

사용자가 학습 완료한 단어 수를 조회합니다 (REVIEW 상태 카드).

**Acceptance Criteria:**

- [ ] Create new file `src/app/api/stats.py`
- [ ] Count UserCardProgress records with card_state=REVIEW
- [ ] Include breakdown by CEFR level (join with VocabularyCard)
- [ ] Include total study time from User.total_study_time_minutes
- [ ] Register router in routes.py

**Response Example:**

```json
{
  "total_learned": 150,
  "by_level": {
    "A1": 50,
    "A2": 60,
    "B1": 40
  },
  "total_study_time_minutes": 450
}
```

---

### BE-S3: 학습 기록 조회

**Endpoint:** `GET /api/v1/stats/history`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `backend`, `api`, `statistics`

**Description:**

차트 시각화를 위한 학습 기록을 조회합니다 (일별/주별/월별).

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/stats.py`
- [ ] Support period parameter: 7d, 30d, 90d, 1y
- [ ] Group reviews by date
- [ ] Include cards_studied, correct_count, accuracy_rate per day
- [ ] Return data in format suitable for charting library

**Response Example:**

```json
{
  "period": "30d",
  "data": [
    {
      "date": "2025-11-01",
      "cards_studied": 20,
      "correct_count": 16,
      "accuracy_rate": 80.0
    }
  ]
}
```

---

### BE-S4: 정답률 통계 조회

**Endpoint:** `GET /api/v1/stats/accuracy`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `backend`, `api`, `statistics`

**Description:**

전체 및 기간별 정답률 통계를 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/stats.py`
- [ ] Overall accuracy rate (all time)
- [ ] Last 7/30/90 days accuracy
- [ ] Accuracy by CEFR level
- [ ] Accuracy trend (improving/stable/declining)

---

### BE-F1: 즐겨찾기 카드 목록 조회

**Endpoint:** `GET /api/v1/favorites`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `backend`, `api`, `favorites`

**Description:**

사용자가 즐겨찾기한 단어 카드 목록을 조회합니다.

**Acceptance Criteria:**

- [ ] Create new file `src/app/services/favorite_service.py`
- [ ] Create new file `src/app/api/favorites.py`
- [ ] Support pagination (skip/limit)
- [ ] Include full card details (VocabularyCard)
- [ ] Include learning progress (UserCardProgress if exists)
- [ ] Order by created_at DESC (most recently favorited first)
- [ ] Register router in routes.py

---

### BE-F2: 즐겨찾기 추가

**Endpoint:** `POST /api/v1/favorites/{card_id}`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `backend`, `api`, `favorites`

**Description:**

카드를 사용자의 즐겨찾기에 추가합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/favorites.py`
- [ ] Create favorite record with user_id and card_id
- [ ] Handle duplicate (idempotent - return 200 if already exists)
- [ ] Validate card_id exists (404 if not)
- [ ] Require authentication
- [ ] Return created favorite or existing favorite

---

### BE-F3: 즐겨찾기 제거

**Endpoint:** `DELETE /api/v1/favorites/{card_id}`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `backend`, `api`, `favorites`

**Description:**

카드를 사용자의 즐겨찾기에서 제거합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/favorites.py`
- [ ] Delete favorite record
- [ ] Return 204 No Content
- [ ] Idempotent (return 204 even if not found)
- [ ] Require authentication

---

### BE-SET1: 사용자 설정 조회

**Endpoint:** `GET /api/v1/users/me/config`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `backend`, `api`, `settings`, `user`

**Description:**

사용자의 앱 설정을 조회합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/users.py`
- [ ] Return timezone, theme, notification_enabled, daily_goal
- [ ] Include new_cards_order preference (if implemented)
- [ ] Include audio preferences (auto_play, speed)
- [ ] Require authentication

---

### BE-SET2: 사용자 설정 업데이트

**Endpoint:** `PUT /api/v1/users/me/config`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `backend`, `api`, `settings`, `user`

**Description:**

사용자의 앱 설정을 업데이트합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/users.py`
- [ ] Accept partial updates (PATCH-style with PUT)
- [ ] Validate timezone string (use pytz or zoneinfo)
- [ ] Validate theme enum (light/dark/auto)
- [ ] Validate daily_goal > 0
- [ ] Return updated config
- [ ] Require authentication

---

### BE-A1: 단어 발음 오디오 제공 (TTS)

**Endpoint:** `GET /api/v1/cards/{id}/audio`  
**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `backend`, `api`, `audio`, `vocabulary`, `tts`

**Description:**

TTS를 사용하여 단어 카드의 발음 오디오를 실시간으로 생성하여 제공합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/cards.py`
- [ ] Choose TTS provider (Google Cloud TTS, AWS Polly, or OpenAI TTS)
- [ ] Implement TTS service wrapper in `src/app/services/tts_service.py`
- [ ] Generate audio on-demand or cache in memory/Redis
- [ ] Return audio file (MP3/OGG) as streaming response
- [ ] Add caching headers (Cache-Control: max-age=86400 for 1 day)
- [ ] Add configuration for TTS API keys in .env
- [ ] Rate limiting to avoid excessive API calls
- [ ] Handle TTS API failures gracefully (return 503)

**Technical Notes:**

```python
# Example with OpenAI TTS
from openai import AsyncOpenAI

@staticmethod
async def generate_audio(text: str, language: str = "en") -> bytes:
    """Generate audio using TTS and return audio bytes"""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    return response.content
```

---

### BE-A2: 동적 예문 생성 API (AI)

**Endpoint:** `GET /api/v1/cards/{id}/examples`  
**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `backend`, `api`, `ai`, `examples`

**Description:**

AI를 사용하여 단어 카드의 예문을 동적으로 생성합니다. 매번 새로운 예문을 제공하여 학습 다양성을 높입니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/cards.py`
- [ ] Choose AI provider (OpenAI GPT-4, Claude, or Gemini)
- [ ] Implement AI service wrapper in `src/app/services/ai_service.py`
- [ ] Generate 2-3 contextual examples per request
- [ ] Include English sentence + Korean translation
- [ ] Consider user's CEFR level for difficulty adjustment
- [ ] Add caching (Redis/in-memory) to reduce API costs (24h TTL)
- [ ] Add configuration for AI API keys in .env
- [ ] Rate limiting to avoid excessive API calls
- [ ] Fallback to static examples from VocabularyCard if AI fails
- [ ] Log generation for quality monitoring

**Query Parameters:**

- `count`: Number of examples (default: 3, max: 5)
- `context`: Optional context hint (e.g., "formal", "casual", "business")
- `regenerate`: Force new generation (skip cache)

**Response Example:**

```json
{
  "card_id": 123,
  "word": "hello",
  "examples": [
    {
      "en": "Hello! Nice to meet you.",
      "ko": "안녕하세요! 만나서 반갑습니다.",
      "context": "greeting_formal"
    },
    {
      "en": "She said hello to everyone in the room.",
      "ko": "그녀는 방 안의 모든 사람에게 인사했다.",
      "context": "past_tense"
    },
    {
      "en": "Just wanted to say hello and see how you're doing.",
      "ko": "그냥 인사하고 어떻게 지내는지 보고 싶었어.",
      "context": "casual"
    }
  ],
  "generated_at": "2025-11-30T10:00:00Z",
  "cached": false
}
```

**Technical Notes:**

```python
# Example with OpenAI
from openai import AsyncOpenAI

@staticmethod
async def generate_examples(
    word: str,
    meaning: str,
    level: str,
    count: int = 3
) -> list[dict]:
    """Generate example sentences using AI"""
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    prompt = f"""Generate {count} natural example sentences for the English word "{word}" (meaning: {meaning}).
    
Requirements:
- CEFR level: {level}
- Include diverse contexts (formal, casual, past tense, etc.)
- Keep sentences simple and clear
- Provide Korean translations
- Return as JSON array

Format:
[
  {{"en": "sentence", "ko": "번역", "context": "type"}},
  ...
]
"""
    
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)
```

---

### BE-L2: 학습 세션 시작

**Endpoint:** `POST /api/v1/study/session/start`  
**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Dependencies:** BE-L4, BE-D3  
**Labels:** `backend`, `api`, `learning`, `session`

**Description:**

새로운 학습 세션을 시작하고 학습할 카드를 반환합니다.

**Acceptance Criteria:**

- [ ] Create new file `src/app/services/study_session_service.py`
- [ ] Create endpoint in `src/app/api/learning.py` (new file)
- [ ] Get user's selected decks (use BE-D3 logic)
- [ ] Fetch new cards using BE-L4 algorithm
- [ ] Fetch due review cards (next_review_date <= now)
- [ ] Mix new + review cards (e.g., interleave or new first)
- [ ] Return session_id (UUID), total_cards, cards array
- [ ] Store session metadata in StudySession table (optional for MVP)
- [ ] Register router in routes.py

**Response Example:**

```json
{
  "session_id": "uuid-123",
  "total_cards": 20,
  "new_cards": 10,
  "review_cards": 10,
  "cards": [
    {
      "id": 1,
      "english_word": "hello",
      "is_new": true
    }
  ]
}
```

---

### BE-L3: 학습 세션 완료

**Endpoint:** `POST /api/v1/study/session/complete`  
**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Dependencies:** BE-L6  
**Labels:** `backend`, `api`, `learning`, `session`

**Description:**

학습 세션을 완료하고 사용자 연속 학습 일수를 업데이트합니다.

**Acceptance Criteria:**

- [ ] Create endpoint in `src/app/api/learning.py`
- [ ] Accept session_id, cards_studied, cards_correct, duration_seconds
- [ ] Update user streak by calling BE-L6 logic
- [ ] Check daily goal completion
- [ ] Return session summary + streak info + daily goal status
- [ ] Update StudySession record if exists (add end_time, results)
- [ ] Update User.total_study_time_minutes

**Response Example:**

```json
{
  "session_summary": {
    "total_cards": 20,
    "correct": 16,
    "wrong": 4,
    "accuracy": 80.0,
    "duration_seconds": 300
  },
  "streak": {
    "current_streak": 7,
    "longest_streak": 12,
    "is_new_record": false,
    "streak_status": "continued",
    "message": "🔥 7일 연속 학습 중!"
  },
  "daily_goal": {
    "goal": 20,
    "completed": 20,
    "progress": 100.0,
    "is_completed": true
  }
}
```

---

### BE-L4: 새 카드 선택 알고리즘 구현

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Dependencies:** DATA-3  
**Labels:** `backend`, `service`, `learning`, `algorithm`

**Description:**

빈도 기반 새 카드 선택 알고리즘을 구현합니다.

**Acceptance Criteria:**

- [ ] Create method in `StudySessionService.get_new_cards_for_session()`
- [ ] Filter cards user hasn't seen (not in UserCardProgress)
- [ ] Filter by selected decks (from user's selection)
- [ ] Order by frequency_rank ASC (most common words first)
- [ ] Apply limit (default 10 new cards per session)
- [ ] Handle case where no new cards available

**Technical Reference:**

See CARD_SELECTION_ALGORITHM.md and ROADMAP.md lines 546-573.

**Implementation:**

```python
@staticmethod
async def get_new_cards_for_session(
    session: AsyncSession,
    user_id: int,
    selected_deck_ids: list[int] | None,
    limit: int = 10
) -> list[VocabularyCard]:
    """Get new cards user hasn't seen, ordered by frequency."""

    # Cards user has already seen
    seen_subquery = select(UserCardProgress.card_id).where(
        UserCardProgress.user_id == user_id
    )

    # Query for unseen cards
    query = select(VocabularyCard).where(
        VocabularyCard.id.not_in(seen_subquery)
    )

    # Filter by selected decks
    if selected_deck_ids:
        query = query.where(VocabularyCard.deck_id.in_(selected_deck_ids))

    # Order by frequency (lower rank = more common)
    query = query.order_by(VocabularyCard.frequency_rank.asc())

    result = await session.exec(query.limit(limit))
    return list(result.all())
```

---

### BE-L5: 사용자 레벨 계산 로직

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `backend`, `service`, `learning`, `algorithm`

**Description:**

최근 정답률을 기반으로 사용자의 현재 레벨을 계산합니다 (향후 i+1 필터링용).

**Acceptance Criteria:**

- [ ] Create method in `UserService` or `StudySessionService`
- [ ] Calculate from last 50 reviews
- [ ] Return estimated CEFR level (A1-C2) or numeric level (1-10)
- [ ] Use for future card selection filtering (i+1 principle)
- [ ] Consider difficulty of cards answered correctly

**Technical Notes:**

For v2 implementation:

```python
# Calculate user level
user_level = await calculate_user_level(session, user_id)
# Based on recent 50 reviews accuracy

# Filter cards by level ± 1
query = query.where(
    VocabularyCard.difficulty_level >= user_level - 0.5,
    VocabularyCard.difficulty_level <= user_level + 1.5
)
```

---

### BE-L6: 연속 학습 일수 계산 및 업데이트 로직

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Labels:** `backend`, `service`, `user`, `streak`

**Description:**

학습 세션이 완료될 때 연속 학습 일수를 계산하는 로직을 구현합니다.

**Acceptance Criteria:**

- [ ] Create `update_user_streak(session, user_id)` function in UserService
- [ ] Handle same-day multiple sessions (don't double-count)
- [ ] Check if yesterday was studied (continue streak: current_streak + 1)
- [ ] Reset streak to 1 if >1 day gap
- [ ] Update longest_streak if current > longest
- [ ] Update last_study_date to today
- [ ] Return streak status object with message

**Technical Reference:**

See ROADMAP.md lines 644-730 for detailed implementation spec.

**Implementation:**

```python
from datetime import date, timedelta

async def update_user_streak(session: AsyncSession, user_id: int) -> dict:
    """
    Update user streak when study session completes.

    Returns:
        dict: {
            "current_streak": int,
            "longest_streak": int,
            "is_new_record": bool,
            "streak_status": "continued" | "started" | "broken"
        }
    """
    user = await session.get(User, user_id)
    today = date.today()

    # 1. Check if already studied today (same day multiple sessions)
    if user.last_study_date == today:
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "is_new_record": False,
            "streak_status": "continued"
        }

    # 2. Calculate streak
    if user.last_study_date is None:
        # First time studying
        user.current_streak = 1
        streak_status = "started"

    elif user.last_study_date == today - timedelta(days=1):
        # Studied yesterday, continue streak
        user.current_streak += 1
        streak_status = "continued"

    elif user.last_study_date < today - timedelta(days=1):
        # Missed a day, reset streak
        user.current_streak = 1
        streak_status = "broken"

    else:
        # last_study_date is in the future (data error)
        user.current_streak = 1
        streak_status = "started"

    # 3. Update longest streak
    is_new_record = False
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
        is_new_record = True

    # 4. Update last study date
    user.last_study_date = today

    # 5. Save to database
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "is_new_record": is_new_record,
        "streak_status": streak_status
    }
```

---

## 📊 Data Preparation Tickets

### DATA-1: 영어 단어 빈도 데이터 수집

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Labels:** `data`, `research`

**Description:**

신뢰할 수 있는 출처에서 영어 단어 빈도 데이터를 조사하고 다운로드합니다.

**Acceptance Criteria:**

- [ ] Download COCA 60k word list or similar frequency data
- [ ] Consider Oxford 3000/5000 for CEFR mapping
- [ ] Document data source, license, and citation
- [ ] Store in `data/frequency/` directory
- [ ] Create README.md in data directory with source info

**Resources:**

- **COCA**: Corpus of Contemporary American English (60,000 words)
- **Oxford 3000/5000**: CEFR-mapped learning vocabulary
- **Google 1T Corpus**: Web-based frequency data

---

### DATA-2: 빈도 순위 매핑 스크립트 작성

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Dependencies:** DATA-1  
**Labels:** `data`, `script`

**Description:**

영어 단어를 빈도 순위에 매핑하는 Python 스크립트를 작성합니다.

**Acceptance Criteria:**

- [ ] Create script in `src/scripts/map_frequency.py`
- [ ] Read frequency data from DATA-1
- [ ] Match VocabularyCard.english_word to frequency data
- [ ] Handle case-insensitive matching
- [ ] Handle multi-word phrases
- [ ] Assign rank=999999 for unmatched words (rare/unknown)
- [ ] Output mapping results and statistics
- [ ] Support dry-run mode (preview without updating DB)

**Technical Notes:**

```python
# Example script structure
async def map_frequency_ranks(session: AsyncSession, dry_run: bool = False):
    # Load frequency data
    frequency_map = load_frequency_data("data/frequency/coca_60k.txt")

    # Get all cards
    cards = await session.exec(select(VocabularyCard))

    for card in cards:
        rank = frequency_map.get(card.english_word.lower(), 999999)
        card.frequency_rank = rank

    if not dry_run:
        await session.commit()
```

---

### DATA-3: 기존 카드에 빈도 순위 업데이트

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Dependencies:** DATA-2  
**Labels:** `data`, `migration`

**Description:**

데이터베이스의 모든 기존 카드에 빈도 순위를 채우는 스크립트를 실행합니다.

**Acceptance Criteria:**

- [ ] Run DATA-2 script against database
- [ ] Verify all cards have frequency_rank assigned
- [ ] Generate report of unmatched words
- [ ] Add frequency mapping to `seed_data.py` for future cards
- [ ] Document process in DATA-2 script README

---

### DATA-4: 샘플 덱 데이터 준비

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `data`, `content`

**Description:**

테스트 및 초기 출시를 위한 샘플 덱을 생성합니다.

**Acceptance Criteria:**

- [ ] **Basic 1000**: Most common 1000 English words
- [ ] **TOEFL vocabulary**: Common TOEFL test words
- [ ] **GRE vocabulary**: Advanced GRE words
- [ ] **Business English**: Professional/business vocabulary
- [ ] Add decks to `seed_data.py`
- [ ] Each deck should have description, difficulty, target CEFR level

**Technical Notes:**

```python
# Example deck creation
basic_1000_deck = Deck(
    name="Basic 1000",
    description="The 1000 most common English words",
    is_public=True,
    cefr_level="A1-A2"
)
```

---

### DATA-5: 카드에 CEFR 레벨 매핑

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 2  
**Labels:** `data`, `content`

**Description:**

단어 카드에 CEFR 레벨 (A1-C2)을 할당합니다.

**Acceptance Criteria:**

- [ ] Use Oxford 3000/5000 CEFR mapping if available
- [ ] Assign levels based on frequency + difficulty
- [ ] Assign CEFR levels to all existing cards
- [ ] Update seed_data.py with CEFR levels
- [ ] Document level assignment criteria

**CEFR Levels:**

- **A1**: Beginner (most common ~500 words)
- **A2**: Elementary (~1500 words)
- **B1**: Intermediate (~3000 words)
- **B2**: Upper-intermediate (~5000 words)
- **C1**: Advanced (~10000 words)
- **C2**: Proficient (rare/specialized words)

---

## 🔐 Security & Infrastructure Tickets

### SEC-1: Rate Limiting 구현

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `backend`, `security`, `infrastructure`

**Description:**

남용 방지를 위해 API 엔드포인트에 rate limiting을 추가합니다.

**Acceptance Criteria:**

- [ ] Install library like `slowapi` or `fastapi-limiter`
- [ ] Set limits per endpoint (e.g., 10 req/min for auth, 100 req/min for others)
- [ ] Return 429 Too Many Requests with Retry-After header
- [ ] Document rate limits in API documentation
- [ ] Consider IP-based and user-based limits

**Technical Notes:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(...):
    ...
```

---

### SEC-2: CORS 설정 검증

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Labels:** `backend`, `security`, `infrastructure`

**Description:**

프로덕션을 위한 CORS 설정을 검토하고 강화합니다.

**Acceptance Criteria:**

- [ ] Review current CORS settings in `src/app/main.py`
- [ ] Replace wildcard "\*" with specific allowed origins
- [ ] Add environment variable for ALLOWED_ORIGINS
- [ ] Test with frontend (ensure requests work)
- [ ] Document allowed origins in deployment guide

**Current Settings:**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Too permissive
    ...
)
```

**Recommended:**

```python
origins = settings.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    ...
)
```

---

### SEC-3: 에러 처리 표준화

**Priority:** 🟡 Medium  
**Status:** ✅ Completed  
**Sprint:** Sprint 3  
**Labels:** `backend`, `error-handling`

**Description:**

모든 엔드포인트에서 일관된 에러 응답 형식을 적용합니다.

**Acceptance Criteria:**

- [x] Create custom exception classes in `src/app/core/exceptions.py`
- [x] Add global exception handler in main.py
- [x] Standardize error response schema: `{ "error": "type", "message": "details" }`
- [x] Don't leak sensitive info in errors (no stack traces in production)
- [x] Log errors with context (user_id, endpoint, timestamp)

---

### SEC-4: 입력 검증 강화

**Priority:** 🟡 Medium  
**Status:** ✅ Completed  
**Sprint:** Sprint 3  
**Labels:** `backend`, `validation`

**Description:**

더 강력한 입력 검증을 위한 Pydantic validator를 추가합니다.

**Acceptance Criteria:**

- [x] Add validators to all request schemas
- [x] Validate email format (use EmailStr)
- [x] Validate ranges (daily_goal > 0, rating 1-4, etc.)
- [x] Sanitize string inputs (trim whitespace, max length)
- [x] Validate foreign key existence where needed

**Example:**

```python
from pydantic import validator, EmailStr

class UserCreate(UserBase):
    email: EmailStr

    @validator('daily_goal')
    def daily_goal_positive(cls, v):
        if v <= 0:
            raise ValueError('daily_goal must be positive')
        return v
```

---

### SEC-5: SQL Injection 방어 검증

**Priority:** 🔴 High  
**Status:** ✅ Completed  
**Sprint:** Sprint 1  
**Labels:** `backend`, `security`

**Description:**

모든 쿼리를 검사하여 SQL injection 방어를 확인합니다.

**Acceptance Criteria:**

- [x] Review all SQL queries in codebase
- [x] Ensure all queries use parameterized statements (SQLModel/SQLAlchemy handles this)
- [x] Check for any raw SQL strings (grep for `text(`)
- [x] Test with injection attempts (e.g., `' OR 1=1 --`)
- [x] Document findings and confirm no vulnerabilities (see docs/SECURITY_AUDIT.md)

---

### SEC-6: 구조화된 로깅 시스템

**Priority:** 🟡 Medium  
**Status:** ✅ Completed  
**Sprint:** Sprint 3  
**Labels:** `backend`, `infrastructure`, `logging`

**Description:**

`structlog` 또는 `loguru`를 사용한 구조화된 로깅을 구현합니다.

**Acceptance Criteria:**

- [x] Install and configure structlog or loguru (using loguru)
- [x] Log all API requests (method, path, status, duration)
- [x] Log errors with full context (user_id, traceback)
- [x] Add request ID tracking (correlation ID via X-Request-ID header)
- [x] Configure log levels per environment (DEBUG in dev, INFO in prod)
- [x] JSON format for production (easier parsing)

---

### SEC-8: Health Check 엔드포인트 개선

**Priority:** 🟡 Medium  
**Status:** ✅ Completed  
**Sprint:** Sprint 3  
**Labels:** `backend`, `infrastructure`, `monitoring`

**Description:**

DB 연결 및 버전 정보를 포함하도록 health check 엔드포인트를 개선합니다.

**Acceptance Criteria:**

- [x] Test database connection (execute simple query)
- [x] Return API version from settings
- [x] Include uptime duration
- [x] Include timestamp
- [x] Return 503 Service Unavailable if unhealthy (DB down)
- [x] Keep response time < 100ms

**Example Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 3600,
  "timestamp": "2025-11-30T10:00:00Z",
  "database": "connected"
}
```

---

## 🧪 Testing Tickets

### TEST-1: 서비스 레이어 단위 테스트

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `testing`, `backend`, `unit-test`

**Description:**

모든 서비스 메서드에 대한 단위 테스트를 작성합니다.

**Acceptance Criteria:**

- [ ] Test UserService methods (create, update, authenticate)
- [ ] Test VocabularyCardService methods (CRUD)
- [ ] Test UserCardProgressService methods (review, FSRS integration)
- [ ] Test DeckService methods (progress calculation)
- [ ] Achieve >80% code coverage on services
- [ ] Use pytest fixtures for DB setup
- [ ] Mock external dependencies

**Framework:**

- pytest
- pytest-asyncio
- pytest-cov

---

### TEST-2: API 엔드포인트 통합 테스트

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `testing`, `backend`, `integration-test`

**Description:**

API 엔드포인트에 대한 통합 테스트를 작성합니다.

**Acceptance Criteria:**

- [ ] Test auth endpoints (register, login, get current user)
- [ ] Test home endpoints (daily goal, progress)
- [ ] Test deck endpoints (list, select, get)
- [ ] Test progress/review endpoints (review submission, due cards)
- [ ] Use test database (separate from dev DB)
- [ ] Test authentication flow
- [ ] Test error cases (404, 401, 400)

**Framework:**

- pytest
- httpx or TestClient

---

### TEST-3: FSRS 로직 정확성 테스트

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Labels:** `testing`, `backend`, `fsrs`, `algorithm`

**Description:**

FSRS 통합이 올바른 스케줄링 결과를 생성하는지 검증합니다.

**Acceptance Criteria:**

- [ ] Test rating=1 (Again) produces short interval (< 1 day)
- [ ] Test rating=3 (Good) increases interval appropriately
- [ ] Test stability increases after correct reviews
- [ ] Test difficulty decreases after multiple correct reviews
- [ ] Test state transitions: NEW → LEARNING → REVIEW
- [ ] Test RELEARNING state after forgetting
- [ ] Compare with py-fsrs library expected behavior

---

### TEST-4: 연속 학습 일수 계산 엣지 케이스 테스트

**Priority:** 🔴 High  
**Status:** 📋 To Do  
**Sprint:** Sprint 1  
**Dependencies:** BE-L6  
**Labels:** `testing`, `backend`, `streak`, `algorithm`

**Description:**

연속 학습 일수 계산이 엣지 케이스를 올바르게 처리하는지 테스트합니다.

**Acceptance Criteria:**

- [ ] Test same-day multiple sessions (streak doesn't increase)
- [ ] Test yesterday study (streak continues, +1)
- [ ] Test gap >1 day (streak resets to 1)
- [ ] Test first study ever (streak = 1)
- [ ] Test longest_streak update (only when current > longest)
- [ ] Test timezone edge cases (study at 11:59pm vs 12:01am)
- [ ] Test last_study_date in future (data error handling)

---

### TEST-5: 데이터베이스 마이그레이션 테스트

**Priority:** 🟡 Medium  
**Status:** 📋 To Do  
**Sprint:** Sprint 3  
**Labels:** `testing`, `database`, `migration`

**Description:**

마이그레이션이 깔끔하게 적용되고 롤백되는지 테스트합니다.

**Acceptance Criteria:**

- [ ] Test `alembic upgrade head` on empty database
- [ ] Test `alembic downgrade -1` (rollback last migration)
- [ ] Test data integrity after migration (no data loss)
- [ ] Test migration on database with existing data
- [ ] Test multiple upgrades/downgrades in sequence
- [ ] Automate migration testing in CI

---

### TEST-6: 부하 테스트

**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `testing`, `performance`, `load-test`

**Description:**

100명의 동시 사용자로 API 부하 테스트를 수행합니다.

**Acceptance Criteria:**

- [ ] Use tool like Locust, k6, or Apache JMeter
- [ ] Test auth endpoints (login)
- [ ] Test session start/review endpoints
- [ ] Measure response times (p50, p95, p99)
- [ ] Identify bottlenecks (DB queries, CPU)
- [ ] Test database connection pool limits
- [ ] Document performance baseline

**Target Metrics:**

- p95 response time < 500ms
- No errors under 100 concurrent users
- Sustained throughput > 500 req/sec

---

### TEST-7: E2E 테스트

**Priority:** 🟢 Low  
**Status:** 📋 To Do  
**Sprint:** Sprint 4  
**Labels:** `testing`, `e2e`, `backend`

**Description:**

전체 사용자 플로우를 다루는 E2E 테스트 (API 레벨)를 작성합니다.

**Acceptance Criteria:**

- [ ] Test registration + login flow
- [ ] Test start session + review cards + complete session
- [ ] Test deck selection flow
- [ ] Test favorites (add/remove)
- [ ] Use pytest with httpx
- [ ] Run against test environment
- [ ] Automate in CI/CD pipeline

**Framework:**

- pytest
- httpx

---

## 📊 Summary by Category

| Category    | Total  | 🔴 High | 🟡 Medium | 🟢 Low | ✅ Completed |
| ----------- | ------ | ------- | --------- | ------ | ------------ |
| Backend API | 29     | 8       | 10        | 11     | 0 (0%)       |
| Data        | 5      | 3       | 2         | 0      | 0 (0%)       |
| Security    | 7      | 1       | 3         | 2      | 5 (71.4%)    |
| Testing     | 7      | 2       | 3         | 2      | 0 (0%)       |
| **Total**   | **48** | **14**  | **18**    | **15** | **5 (10.4%)** |

---

## 🚀 Sprint Assignments

### Sprint 1: MVP - Core Learning Flow

**Goal:** Get basic learning functionality working

**Duration:** 2-3 weeks

**Total Tickets:** 14 backend tickets

**Data (3):**

- DATA-1: Collect English frequency data
- DATA-2: Create frequency mapping script
- DATA-3: Update cards with frequency_rank

**Backend API (6):**

- BE-H1: GET /users/me/daily-goal
- BE-H2: GET /users/me/today-progress
- BE-H3: GET /progress/new-cards-count
- BE-L2: POST /study/session/start
- BE-L3: POST /study/session/complete
- BE-L4: New card selection algorithm
- BE-L6: Streak calculation logic

**Security (2):**

- SEC-2: CORS verification
- SEC-5: SQL injection check

**Testing (2):**

- TEST-3: FSRS accuracy tests
- TEST-4: Streak edge case tests

---

### Sprint 2: Decks Management & AI Examples

**Goal:** Enable deck management and AI-powered examples

**Duration:** 2 weeks

**Total Tickets:** 9 backend tickets

**Data (2):**

- DATA-4: Prepare sample decks
- DATA-5: Map cards to CEFR levels

**Backend API (7):**

- BE-D1: GET /decks (with progress)
- BE-D2: PUT /users/me/selected-decks
- BE-D3: GET /users/me/selected-decks
- BE-D4: GET /decks/{id}
- BE-D6: DeckService progress calculation
- BE-A2: GET /cards/{id}/examples (AI-generated)
- BE-L5: User level calculation

---

### Sprint 3: Statistics & Security & Tests

**Goal:** Add statistics, harden security, write tests

**Duration:** 2 weeks

**Total Tickets:** 10 backend tickets (5 completed - 50%)

**Backend API (4):**

- BE-S1: GET /users/me/streak
- BE-S2: GET /stats/total-learned
- BE-S3: GET /stats/history
- BE-S4: GET /stats/accuracy

**Security (5):**

- SEC-1: Rate limiting
- ~~SEC-3: Standardize error handling~~ ✅
- ~~SEC-4: Input validation~~ ✅
- ~~SEC-5: SQL injection review~~ ✅
- ~~SEC-6: Structured logging~~ ✅
- ~~SEC-8: Enhanced health check~~ ✅

**Testing (3):**

- TEST-1: Service layer unit tests
- TEST-2: API integration tests
- TEST-5: DB migration tests

---

### Sprint 4: Settings & Audio & Favorites (Optional)

**Goal:** Improve user experience and production readiness

**Duration:** 2 weeks

**Total Tickets:** 7 backend tickets

**Backend API (7):**

- BE-SET1: GET /users/me/config
- BE-SET2: PUT /users/me/config
- BE-A1: GET /cards/{id}/audio (TTS-based)
- BE-D5: GET /decks/{id}/cards (deck browsing)
- BE-F1: GET /favorites
- BE-F2: POST /favorites/{card_id}
- BE-F3: DELETE /favorites/{card_id}

**Testing (2):**

- TEST-6: Load testing
- TEST-7: E2E tests

---

## 📌 Next Steps

1. **Start Sprint 1 backend development:**
   - DATA-1, DATA-2, DATA-3 (frequency data)
   - BE-H1, BE-H2, BE-H3 (home endpoints)
   - BE-L2, BE-L3, BE-L4, BE-L6 (learning session & streak)
2. **Set up CI/CD pipeline** for automated testing
3. **Write tests** as you develop (TDD approach)

---

## 🔗 Related Documents

- [ROADMAP.md](./ROADMAP.md) - Original roadmap with detailed specifications
- [CARD_SELECTION_ALGORITHM.md](./CARD_SELECTION_ALGORITHM.md) - Card selection algorithm details
- [API.md](./API.md) - API documentation
- [DATABASE.md](./DATABASE.md) - Database schema documentation
- [DEVELOPMENT.md](./DEVELOPMENT.md) - Development setup guide
- [CLAUDE.md](../CLAUDE.md) - Project overview and commands

---

## 📝 Notes

- **Next Focus:** Sprint 1 backend API implementation
- **Testing Strategy:** Write tests alongside development (TDD)
- **Frontend:** Separate project - use this API

---

## 🎯 Quick Reference

**Sprint 1 Priority:**

1. DATA-1, DATA-2, DATA-3 - Get frequency data working
2. BE-L4, BE-L6 - Core learning algorithms
3. BE-H1, BE-H2, BE-H3 - Home screen data
4. BE-L2, BE-L3 - Session management
5. TEST-3, TEST-4 - Critical algorithm tests

**Current Status:**

- 📋 43 backend tickets to do (5 completed - 10.4%)
- ✅ All database migrations applied
- ✅ SEC-3: Error handling standardized
- ✅ SEC-4: Input validation added
- ✅ SEC-5: SQL injection review completed
- ✅ SEC-6: Structured logging implemented
- ✅ SEC-8: Health check endpoint improved
- 🎯 Sprint 1 ready to start!
