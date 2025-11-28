# Loops API 개발 로드맵

> 최종 업데이트: 2025-11-28

## 📱 앱 구조 개요

### 탭 구성

1. **홈 (Home)** - 학습 시작 및 오늘의 진행도
2. **학습 통계 (Statistics)** - 학습 현황 및 분석
3. **즐겨찾기 (Favorites)** - 저장한 단어 목록

### 핵심 플로우

```
홈 화면
├── 오늘의 목표 (예: 20개)
├── 오늘의 진행도 (예: 12/20)
└── [학습 시작] 버튼
        │
        ▼
    학습 모달
    ├── 새로운 단어: X개
    ├── 복습할 단어: Y개
    └── [덱 변경] 버튼 ──→ 덱 선택 화면
                              ├── [전체 선택] (default)
                              └── 개별 덱 체크박스
                                  └── 덱별 진행도 표시
```

---

## 🗂️ 덱 선택 로직

### 요구사항

- 여러 덱 동시 선택 가능
- "전체 선택" 옵션 (default)
- 덱별 학습 진행도 표시

### 데이터 모델

```sql
-- User 테이블 수정
ALTER TABLE users ADD COLUMN select_all_decks BOOLEAN DEFAULT TRUE;
ALTER TABLE users ADD COLUMN daily_goal INT DEFAULT 20;

-- 새 Junction 테이블
CREATE TABLE user_selected_decks (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    deck_id INT REFERENCES decks(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, deck_id)
);
```

### 선택 로직

| `select_all_decks` | `user_selected_decks` | 결과                  |
| ------------------ | --------------------- | --------------------- |
| `true`             | (무시됨)              | 모든 공개 덱에서 학습 |
| `false`            | `[1, 3, 5]`           | 선택된 덱에서만 학습  |

---

## 📋 백엔드 개발 태스크

### 🏠 홈 관련 API (BE-H)

| ID    | 엔드포인트                             | 설명                                    | 상태    | 우선순위 |
| ----- | -------------------------------------- | --------------------------------------- | ------- | -------- |
| BE-H1 | `GET /api/v1/users/me/daily-goal`      | 일일 목표 조회                          | ❌      | 🔴 High  |
| BE-H2 | `GET /api/v1/users/me/today-progress`  | 오늘 학습 진행도                        | ❌      | 🔴 High  |
| BE-H3 | `GET /api/v1/progress/new-cards-count` | 오늘 학습할 새 카드 수 (선택된 덱 기준) | ❌      | 🔴 High  |
| BE-H4 | `GET /api/v1/progress/due`             | 복습할 카드 목록                        | ✅ 있음 | -        |

### 📚 덱 관련 API (BE-D)

| ID    | 엔드포인트                            | 설명                           | 상태 | 우선순위 |
| ----- | ------------------------------------- | ------------------------------ | ---- | -------- |
| BE-D1 | `GET /api/v1/decks`                   | 덱 목록 + 진행도 포함          | ❌   | 🟡 Med   |
| BE-D2 | `PUT /api/v1/users/me/selected-decks` | 선택 덱 설정                   | ❌   | 🟡 Med   |
| BE-D3 | `GET /api/v1/users/me/selected-decks` | 선택 덱 조회                   | ❌   | 🟡 Med   |
| BE-D4 | `GET /api/v1/decks/{id}`              | 덱 상세 + 진행도               | ❌   | 🟡 Med   |
| BE-D5 | `GET /api/v1/decks/{id}/cards`        | 덱의 카드 목록                 | ❌   | 🟡 Med   |
| BE-D6 | -                                     | DeckService progress 계산 로직 | ❌   | 🟡 Med   |

**덱 + 진행도 응답 스키마:**

```json
{
  "id": 1,
  "name": "TOPIK 초급",
  "description": "...",
  "total_cards": 500,
  "learned_cards": 150,
  "learning_cards": 30,
  "new_cards": 320,
  "progress_percent": 30.0
}
```

**선택 덱 설정 요청:**

```json
// 전체 선택
{ "select_all": true }

// 특정 덱만 선택
{ "select_all": false, "deck_ids": [1, 3, 5] }
```

### 📊 통계 관련 API (BE-S)

| ID    | 엔드포인트                        | 설명                   | 상태                     | 우선순위 |
| ----- | --------------------------------- | ---------------------- | ------------------------ | -------- |
| BE-S1 | `GET /api/v1/users/me/streak`     | 연속 학습 일수         | ✅ 모델에 있음, API 필요 | 🟡 Med   |
| BE-S2 | `GET /api/v1/stats/total-learned` | 총 학습 단어 수        | ❌                       | 🟡 Med   |
| BE-S3 | `GET /api/v1/stats/history`       | 학습 히스토리 (차트용) | ❌                       | 🟢 Low   |
| BE-S4 | `GET /api/v1/stats/accuracy`      | 정답률 통계            | ❌                       | 🟢 Low   |
| BE-S5 | `GET /api/v1/stats/by-level`      | CEFR 레벨별 진행도     | ❌                       | 🟢 Low   |

### ⭐ 즐겨찾기 관련 API (BE-F)

| ID    | 엔드포인트                           | 설명          | 상태               | 우선순위 |
| ----- | ------------------------------------ | ------------- | ------------------ | -------- |
| BE-F1 | `GET /api/v1/favorites`              | 즐겨찾기 목록 | ❌ (테이블도 없음) | 🟡 Med   |
| BE-F2 | `POST /api/v1/favorites/{card_id}`   | 즐겨찾기 추가 | ❌                 | 🟡 Med   |
| BE-F3 | `DELETE /api/v1/favorites/{card_id}` | 즐겨찾기 제거 | ❌                 | 🟡 Med   |

### 📖 학습 플로우 API (BE-L)

| ID    | 엔드포인트                                       | 설명                                      | 상태    | 우선순위 |
| ----- | ------------------------------------------------ | ----------------------------------------- | ------- | -------- |
| BE-L1 | `POST /api/v1/progress/review`                   | 리뷰 제출 (FSRS)                          | ✅      | -        |
| BE-L2 | `POST /api/v1/study/session/start`               | 학습 세션 시작 (카드 목록 + 총 갯수 반환) | ❌      | 🔴 High  |
| BE-L3 | `POST /api/v1/study/session/complete`            | 세션 완료 처리 (streak 저장 포함)         | ❌      | 🔴 High  |
| BE-L4 | StudySessionService - 새 카드 선택 알고리즘 구현 | ❌                                        | 🔴 High |
| BE-L5 | 사용자 레벨 계산 로직 (정답률 기반)              | ❌                                        | 🟡 Med  |
| BE-L6 | Streak 계산 및 업데이트 로직 구현                | ❌                                        | 🔴 High |

---

## 🗄️ DB 스키마 변경

| ID   | 변경 내용                                                        | 우선순위 |
| ---- | ---------------------------------------------------------------- | -------- |
| DB-1 | User 테이블에 `select_all_decks` (bool, default=true) 추가       | 🔴 High  |
| DB-2 | User 테이블에 `daily_goal` (int, default=20) 추가                | 🔴 High  |
| DB-3 | `UserSelectedDecks` 테이블 생성                                  | 🔴 High  |
| DB-4 | `Favorite` 테이블 생성 (user_id, card_id, created_at)            | 🟡 Med   |
| DB-5 | VocabularyCard에 `frequency_rank` 필드 추가 (영어 빈도 기준)     | 🔴 High  |
| DB-6 | VocabularyCard에 `category` 필드 추가 (학습 섹션 분류용)         | 🟡 Med   |
| DB-7 | VocabularyCard 필드명 확인/수정 (english_word, pronunciation 등) | 🔴 High  |

### 새 모델 정의

```python
# src/app/models/tables/user_selected_deck.py
class UserSelectedDeck(TimestampMixin, table=True):
    __tablename__ = "user_selected_decks"
    __table_args__ = (UniqueConstraint("user_id", "deck_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    deck_id: int = Field(foreign_key="decks.id", index=True)


# src/app/models/tables/favorite.py
class Favorite(TimestampMixin, table=True):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "card_id"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    card_id: int = Field(foreign_key="vocabulary_cards.id", index=True)
```

---

## 📦 데이터 준비 태스크

| ID     | 태스크                                          | 우선순위 |
| ------ | ----------------------------------------------- | -------- |
| DATA-1 | 영어 빈도 데이터 수집 (COCA/Oxford 3000 등)     | 🔴 High  |
| DATA-2 | frequency_rank 매핑 스크립트 작성               | 🔴 High  |
| DATA-3 | 기존 VocabularyCard에 frequency_rank 업데이트   | 🔴 High  |
| DATA-4 | 샘플 덱 데이터 준비 (Basic 1000, TOEFL, GRE 등) | 🟡 Med   |
| DATA-5 | 단어 카드에 CEFR 레벨 매핑 (A1-C2)              | 🟡 Med   |

---

## 📱 프론트엔드 개발 태스크

### 🏠 홈 탭 (F-H)

| ID   | 태스크                                  | 의존성       | 우선순위 |
| ---- | --------------------------------------- | ------------ | -------- |
| F-H1 | 홈 화면 레이아웃 구현                   | -            | 🔴 High  |
| F-H2 | 오늘의 목표 단어 갯수 표시              | BE-H1        | 🔴 High  |
| F-H3 | 오늘의 Progress Bar                     | BE-H2        | 🔴 High  |
| F-H4 | 학습 시작 버튼 (큰 CTA)                 | -            | 🔴 High  |
| F-H5 | 학습 시작 모달 UI                       | -            | 🔴 High  |
| F-H6 | 새로운 단어 X개 / 복습 단어 Y개 표시    | BE-H3, BE-H4 | 🔴 High  |
| F-H7 | 덱 변경 버튼 (모달 우측 상단)           | -            | 🟡 Med   |
| F-H8 | 덱 선택 화면 (체크박스 리스트 + 진행도) | BE-D1        | 🟡 Med   |
| F-H9 | 덱 선택 저장                            | BE-D2        | 🟡 Med   |

**덱 선택 UI 예시:**

```
┌─────────────────────────────────┐
│ ☑️ 전체 선택                     │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ ☑️ TOPIK 초급                    │
│ ████████░░░░░░░░░░░░ 30%        │
│ 150/500 학습 완료                │
└─────────────────────────────────┘
┌─────────────────────────────────┐
│ ☐ 비즈니스 한국어                │
│ ██░░░░░░░░░░░░░░░░░░ 10%        │
│ 20/200 학습 완료                 │
└─────────────────────────────────┘
```

### 📊 학습 통계 탭 (F-S)

| ID   | 태스크                       | 의존성 | 우선순위 |
| ---- | ---------------------------- | ------ | -------- |
| F-S1 | 통계 화면 레이아웃           | -      | 🟡 Med   |
| F-S2 | 연속 학습 일수 (Streak) 표시 | BE-S1  | 🟡 Med   |
| F-S3 | 총 학습 단어 수 표시         | BE-S2  | 🟡 Med   |
| F-S4 | 일별/주별/월별 학습 차트     | BE-S3  | 🟢 Low   |
| F-S5 | 정답률 통계                  | BE-S4  | 🟢 Low   |
| F-S6 | CEFR 레벨별 진행도           | BE-S5  | 🟢 Low   |

### ⭐ 즐겨찾기 탭 (F-F)

| ID   | 태스크                         | 의존성       | 우선순위 |
| ---- | ------------------------------ | ------------ | -------- |
| F-F1 | 즐겨찾기 화면 레이아웃         | -            | 🟡 Med   |
| F-F2 | 즐겨찾기 단어 리스트 표시      | BE-F1        | 🟡 Med   |
| F-F3 | 단어 카드에 즐겨찾기 토글 버튼 | BE-F2, BE-F3 | 🟡 Med   |
| F-F4 | 즐겨찾기 단어 검색/필터        | -            | 🟢 Low   |

### 📖 학습 플로우 (F-L)

| ID   | 태스크                                  | 의존성 | 우선순위 |
| ---- | --------------------------------------- | ------ | -------- |
| F-L1 | 플래시카드 UI (앞면: 영어 단어)         | -      | 🔴 High  |
| F-L2 | 플래시카드 UI (뒷면: 발음, 의미, 예문)  | -      | 🔴 High  |
| F-L3 | 카드 플립 애니메이션                    | -      | 🔴 High  |
| F-L4 | 정답/오답 버튼 (Binary rating)          | -      | 🔴 High  |
| F-L5 | 리뷰 제출 및 다음 카드 로딩             | BE-L1  | 🔴 High  |
| F-L6 | 학습 세션 완료 화면 (streak, 통계 표시) | BE-L3  | 🔴 High  |
| F-L7 | 학습 세션 중 Progress 표시 (N/M 카드)   | BE-L2  | 🔴 High  |
| F-L8 | Progress Bar (상단 고정)                | -      | 🔴 High  |

**학습 완료 화면 UI 예시:**

```
┌─────────────────────────────────┐
│      🎉 세션 완료!               │
├─────────────────────────────────┤
│  정답률: 16/20 (80%)             │
│  학습 시간: 5분                  │
├─────────────────────────────────┤
│  🔥 7일 연속 학습 중!            │
│  최장 기록: 12일                 │
├─────────────────────────────────┤
│  오늘의 목표: 20/20 ✅           │
│  ████████████████████ 100%      │
├─────────────────────────────────┤
│  [계속 학습하기]  [홈으로]       │
└─────────────────────────────────┘
```

---

## 🚀 Sprint 계획

### Sprint 1: MVP - 핵심 학습 플로우

**목표:** 기본 학습 기능 동작

**백엔드:**

- [ ] DB-1, DB-2, DB-3, DB-5, DB-7 (스키마 변경)
- [ ] DATA-1, DATA-2, DATA-3 (빈도 데이터 준비)
- [ ] BE-H1, BE-H2, BE-H3 (홈 화면 데이터)
- [ ] BE-L2, BE-L4 (학습 세션 + 새 카드 선택)
- [ ] BE-L3, BE-L6 (세션 완료 + Streak 저장)

**프론트엔드:**

- [ ] F-H1 ~ F-H6 (홈 화면)
- [ ] F-L1 ~ F-L6 (학습 플로우 + 완료 화면)
- [ ] F-L7, F-L8 (Progress 표시)

### Sprint 2: 덱 선택 & 즐겨찾기

**목표:** 덱 관리 및 즐겨찾기

**백엔드:**

- [ ] DB-4 (Favorite 테이블)
- [ ] DATA-4, DATA-5 (덱 및 레벨 데이터)
- [ ] BE-D1 ~ BE-D6 (덱 API)
- [ ] BE-F1 ~ BE-F3 (즐겨찾기 API)

**프론트엔드:**

- [ ] F-H7 ~ F-H9 (덱 선택)
- [ ] F-F1 ~ F-F3 (즐겨찾기)

### Sprint 3: 통계 & 폴리싱

**목표:** 학습 통계 및 UX 개선

**백엔드:**

- [ ] BE-S1 ~ BE-S5 (통계 API)
- [ ] BE-L3 (세션 완료 처리)

**프론트엔드:**

- [ ] F-S1 ~ F-S6 (통계 화면)
- [ ] F-F4 (즐겨찾기 검색)

---

## 📊 진행 상황 요약

| 카테고리   | 완료  | 진행중 | 대기   | 총     |
| ---------- | ----- | ------ | ------ | ------ |
| 백엔드 API | 2     | 0      | 21     | 23     |
| DB 스키마  | 0     | 0      | 7      | 7      |
| 데이터     | 0     | 0      | 5      | 5      |
| 프론트엔드 | 0     | 0      | 26     | 26     |
| **총합**   | **2** | **0**  | **59** | **61** |

---

## 📚 관련 문서

- [CARD_SELECTION_ALGORITHM.md](./CARD_SELECTION_ALGORITHM.md) - 단어 카드 선정 알고리즘 상세 가이드
- [API.md](./API.md) - API 명세
- [DATABASE.md](./DATABASE.md) - 데이터베이스 스키마
- [DEVELOPMENT.md](./DEVELOPMENT.md) - 개발 가이드

---

## 📝 참고사항

### 앱 정보

- **학습 언어:** 영어 단어 학습
- **CEFR 레벨:** A1/A2/B1/B2/C1/C2
- **플래시카드 형식:** 앞면(영어), 뒷면(발음, 의미, 예문)

### 기존 구현된 기능

- ✅ User CRUD + Supabase Auth 연동
- ✅ VocabularyCard CRUD
- ✅ UserCardProgress + FSRS 알고리즘 통합
- ✅ `POST /api/v1/progress/review` - 리뷰 제출
- ✅ `GET /api/v1/progress/due` - 복습 카드 조회
- ✅ Deck 모델 (API 미구현)

### FSRS Rating 시스템

- 정답 (is_correct: true) → FSRS Rating.Good (3)
- 오답 (is_correct: false) → FSRS Rating.Again (1)

### CardState 정의

```python
class CardState(str, Enum):
    NEW = "new"           # 아직 안 본 카드
    LEARNING = "learning" # 학습 중
    REVIEW = "review"     # 학습 완료 (복습 단계)
    RELEARNING = "relearning" # 다시 학습 중 (까먹음)
```

### 영어 빈도 데이터 소스

- **COCA (Corpus of Contemporary American English)**: 60,000단어 빈도 리스트
- **Oxford 3000/5000**: CEFR 레벨과 매핑된 학습용 단어
- **Google 1T Corpus**: 웹 기반 빈도

### 학습 세션 Progress

```json
// POST /api/v1/study/session/start 응답
{
  "session_id": "uuid-...",
  "total_cards": 20,
  "new_cards": 10,
  "review_cards": 10,
  "cards": [...]
}
```

프론트엔드에서 `current / total` 형태로 표시

### 새 카드 선택 알고리즘 (BE-L4)

> 📖 **상세 문서**: [CARD_SELECTION_ALGORITHM.md](./CARD_SELECTION_ALGORITHM.md)

**MVP 구현 (빈도 기반):**

```python
async def get_new_cards_for_session(
    session: AsyncSession,
    user_id: int,
    selected_deck_ids: list[int] | None,
    limit: int = 10
) -> list[VocabularyCard]:
    """Get new cards user hasn't seen, ordered by frequency."""

    # 이미 본 카드 제외
    seen_subquery = select(UserCardProgress.card_id).where(
        UserCardProgress.user_id == user_id
    )

    query = select(VocabularyCard).where(
        VocabularyCard.id.not_in(seen_subquery)
    )

    # 선택된 덱 필터
    if selected_deck_ids:
        query = query.where(VocabularyCard.deck_id.in_(selected_deck_ids))

    # 빈도순 정렬 (낮은 rank = 더 자주 쓰임)
    query = query.order_by(VocabularyCard.frequency_rank.asc())

    result = await session.exec(query.limit(limit))
    return list(result.all())
```

**v2 구현 (i+1 필터 추가):**

```python
# 사용자 현재 레벨 계산
user_level = await calculate_user_level(session, user_id)
# 최근 50개 리뷰의 정답률 기반

# 레벨 ± 1 범위 필터
query = query.where(
    VocabularyCard.difficulty_level >= user_level - 0.5,
    VocabularyCard.difficulty_level <= user_level + 1.5
)
```

### VocabularyCard 필드 정의 (영어 학습용)

```python
class VocabularyCard(VocabularyCardBase, TimestampMixin, table=True):
    """영어 단어 카드."""

    # 기본 정보
    english_word: str = Field(max_length=100, index=True)  # 영어 단어
    pronunciation: Optional[str]  # 발음 기호 (IPA)
    meaning: str  # 한글 의미
    definition_en: Optional[str]  # 영어 정의

    # 난이도 정보
    difficulty_level: int  # 1-10
    cefr_level: Optional[str]  # A1/A2/B1/B2/C1/C2
    frequency_rank: Optional[int] = Field(index=True)  # 빈도 순위 (1=가장 자주)

    # 학습 자료
    example_sentences: Optional[list] = Field(sa_column=Column(JSON))
    synonyms: Optional[list] = Field(sa_column=Column(JSON))
    antonyms: Optional[list] = Field(sa_column=Column(JSON))

    # 덱 연결
    deck_id: Optional[int] = Field(foreign_key="decks.id", index=True)
```

---

## 📖 학습 세션 전체 플로우

```
1. 세션 시작 (POST /session/start)
   ├─ 선택된 덱 확인 (select_all_decks)
   ├─ 새 카드 선정 (빈도 기반)
   ├─ 복습 카드 조회 (next_review_date <= now)
   └─ 응답: { session_id, total_cards, cards[] }

2. 카드 학습 반복
   ├─ 플래시카드 표시 (프론트)
   ├─ 사용자 응답 (정답/오답)
   └─ 리뷰 제출 (POST /progress/review)
       └─ FSRS 알고리즘으로 다음 복습 시점 계산

3. 세션 완료 (POST /session/complete)
   ├─ Streak 계산 및 업데이트
   │   ├─ 오늘 이미 학습? → 변경 없음
   │   ├─ 어제 학습함? → current_streak++
   │   └─ 하루 이상 놓침? → current_streak = 1
   ├─ longest_streak 갱신 확인
   ├─ 일일 목표 달성 여부 체크
   └─ 응답: { session_summary, streak, daily_goal }
```

---

## 🔥 Streak 계산 및 저장 로직 (BE-L3, BE-L6)

### User 모델의 Streak 필드

```python
class User(UserBase, TimestampMixin, table=True):
    """User database model."""

    # Streak tracking (이미 구현됨)
    current_streak: int = Field(default=0)      # 현재 연속 일수
    longest_streak: int = Field(default=0)      # 최장 연속 기록
    last_study_date: Optional[date] = Field(default=None, index=True)  # 마지막 학습 날짜
```

### Streak 계산 로직

**세션 완료 시 호출:** `POST /api/v1/study/session/complete`

```python
from datetime import date, timedelta

async def update_user_streak(session: AsyncSession, user_id: int) -> dict:
    """
    학습 세션 완료 시 streak 업데이트.

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

    # 1. 오늘 이미 학습했는지 체크 (같은 날 여러 세션)
    if user.last_study_date == today:
        return {
            "current_streak": user.current_streak,
            "longest_streak": user.longest_streak,
            "is_new_record": False,
            "streak_status": "continued"
        }

    # 2. Streak 계산
    if user.last_study_date is None:
        # 첫 학습
        user.current_streak = 1
        streak_status = "started"

    elif user.last_study_date == today - timedelta(days=1):
        # 연속 학습 (어제 학습함)
        user.current_streak += 1
        streak_status = "continued"

    elif user.last_study_date < today - timedelta(days=1):
        # Streak 끊김 (어제 학습 안 함)
        user.current_streak = 1
        streak_status = "broken"

    else:
        # last_study_date가 미래 (데이터 오류)
        user.current_streak = 1
        streak_status = "started"

    # 3. 최장 기록 갱신
    is_new_record = False
    if user.current_streak > user.longest_streak:
        user.longest_streak = user.current_streak
        is_new_record = True

    # 4. 마지막 학습 날짜 업데이트
    user.last_study_date = today

    # 5. DB 저장
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

### API 엔드포인트: POST /api/v1/study/session/complete

**요청:**

```json
{
  "session_id": "uuid-...",
  "cards_studied": 20,
  "cards_correct": 16,
  "duration_seconds": 300
}
```

**응답:**

```json
{
  "session_summary": {
    "total_cards": 20,
    "correct": 16,
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

### Streak 상태별 메시지

```python
def get_streak_message(current_streak: int, streak_status: str, is_new_record: bool) -> str:
    """Streak 상태에 따른 사용자 메시지 생성"""

    if is_new_record:
        return f"🎉 새 기록! {current_streak}일 연속 학습!"

    if streak_status == "started":
        return "🔥 학습 시작! 내일도 함께해요!"

    if streak_status == "continued":
        if current_streak >= 30:
            return f"🏆 대단해요! {current_streak}일 연속 학습 중!"
        elif current_streak >= 7:
            return f"🔥 일주일 돌파! {current_streak}일 연속!"
        else:
            return f"🔥 {current_streak}일 연속 학습 중!"

    if streak_status == "broken":
        return "💪 다시 시작! 오늘부터 새로운 기록을 만들어요!"

    return f"🔥 {current_streak}일 연속 학습 중!"
```

### 엣지 케이스 처리

| 케이스                 | 처리 방법                             |
| ---------------------- | ------------------------------------- |
| 같은 날 여러 세션      | streak 변경 없음, 첫 세션만 카운트    |
| 자정 넘어가는 세션     | 세션 완료 시각 기준 (시작X)           |
| 타임존 이슈            | 서버 시간 기준 (UTC 또는 사용자 설정) |
| 과거 날짜로 학습 기록  | 허용 안 함 (클라이언트 시간 무시)     |
| last_study_date가 미래 | 오늘부터 새로 시작 (데이터 보정)      |

### 타임존 고려사항

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

async def get_user_today(user_id: int) -> date:
    """사용자의 타임존에 맞는 오늘 날짜 반환"""

    # 옵션 1: 서버 시간 기준 (간단)
    return date.today()

    # 옵션 2: 사용자 타임존 기준 (추후 구현)
    user = await get_user(user_id)
    user_tz = ZoneInfo(user.timezone or "UTC")
    return datetime.now(user_tz).date()
```

### 추가 고려사항

**1. 일일 목표 달성 여부**

```python
async def check_daily_goal_completion(session: AsyncSession, user_id: int) -> dict:
    """오늘의 학습 목표 달성 여부 확인"""

    user = await session.get(User, user_id)
    today = date.today()

    # 오늘 완료한 리뷰 수 (is_correct 무관)
    today_reviews = await session.exec(
        select(func.count(UserCardProgress.id))
        .where(
            UserCardProgress.user_id == user_id,
            func.date(UserCardProgress.last_review_date) == today
        )
    )
    count = today_reviews.one()

    return {
        "goal": user.daily_goal,
        "completed": count,
        "progress": (count / user.daily_goal * 100) if user.daily_goal > 0 else 0,
        "is_completed": count >= user.daily_goal
    }
```

**2. Streak 복구 (선택적 기능)**

```python
# Streak이 끊긴 경우 1회 복구 기회 제공 (유료 기능)
async def restore_streak(session: AsyncSession, user_id: int) -> bool:
    """Streak 복구 (프리미엄 기능)"""

    user = await session.get(User, user_id)

    # 어제만 놓친 경우에만 복구 가능
    if user.last_study_date == date.today() - timedelta(days=2):
        # 복구 권한 확인 (프리미엄 사용자 등)
        if user.has_streak_restore_available():
            user.current_streak += 1  # 복구
            user.use_streak_restore()  # 복구 권한 소진
            await session.commit()
            return True

    return False
```

**3. Streak 통계 API**

```python
# GET /api/v1/users/me/streak-stats
{
  "current_streak": 7,
  "longest_streak": 15,
  "total_study_days": 45,
  "streak_history": [
    {"start_date": "2025-01-01", "end_date": "2025-01-15", "days": 15},
    {"start_date": "2025-02-01", "end_date": "2025-02-07", "days": 7}
  ],
  "monthly_calendar": {
    "2025-02": [1, 2, 3, 4, 5, 6, 7, 15, 16, 20]  # 학습한 날짜들
  }
}
```

### 구현 체크리스트

**Sprint 1 (MVP):**

- [ ] `update_user_streak()` 함수 구현
- [ ] `POST /session/complete` 엔드포인트에 streak 로직 통합
- [ ] 같은 날 중복 체크
- [ ] 연속/끊김 판단 로직
- [ ] longest_streak 갱신

**Sprint 2 (개선):**

- [ ] 타임존 지원
- [ ] Streak 메시지 다국어화
- [ ] 일일 목표 달성 체크
- [ ] Streak 통계 API

**Sprint 3 (고급):**

- [ ] Streak 복구 기능 (프리미엄)
- [ ] Streak 히스토리 조회
- [ ] 월별 캘린더 뷰
- [ ] Push 알림 (Streak 끊기기 전 리마인더)
