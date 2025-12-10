# 학습 (Study) API

> FSRS 기반 학습 세션 + 퀴즈 + 스트릭/XP 통합
>
> 최종 업데이트: 2025-12-10

---

## 엔드포인트 요약

| 분류 | 메서드 | 엔드포인트 | 설명 |
|------|--------|-----------|------|
| 조회 | GET | `/overview` | 신규/복습 카드 수 + 복습 예정 목록 |
| 조회 | GET | `/cards/{card_id}` | 개별 카드 FSRS 진행 상세 |
| 세션 | POST | `/session/start` | 세션 시작 |
| 세션 | POST | `/session/card` | 다음 카드 조회 (퀴즈 유형 지정) |
| 세션 | POST | `/session/answer` | 정답 제출 + FSRS 업데이트 |
| 세션 | POST | `/session/complete` | 세션 완료 + XP/스트릭 반영 |

---

## 학습 플로우

```text
1. GET /overview → 오늘 학습할 카드 수 확인
2. POST /session/start → session_id 발급
3. POST /session/card → 문제 조회 (반복)
4. POST /session/answer → 정답 제출 (반복)
5. POST /session/complete → XP/스트릭 반영
```

---

## 조회 API

### GET /overview

학습 현황 개요 조회

**쿼리**: `?limit=50` (복습 카드 최대 수, 1~100)

**응답**:

```json
{
  "new_cards_count": 150,
  "review_cards_count": 45,
  "total_available": 195,
  "due_cards": [
    {
      "card_id": 1234,
      "english_word": "decide",
      "korean_meaning": "결정하다",
      "next_review_date": "2025-12-09T00:00:00Z",
      "card_state": "REVIEW"
    }
  ]
}
```

### GET /cards/{card_id}

개별 카드 FSRS 진행 조회

**응답**:

```json
{
  "card_id": 1234,
  "card_state": "REVIEW",
  "stability": 15.2,
  "difficulty": 4.5,
  "scheduled_days": 7,
  "next_review_date": "2025-12-17T00:00:00Z",
  "accuracy_rate": 80.0
}
```

---

## 세션 API

### POST /session/start

**요청**:

```json
{
  "new_cards_limit": 30,
  "review_cards_limit": 30
}
```

**응답**:

```json
{
  "session_id": "uuid",
  "total_cards": 25,
  "new_cards_count": 8,
  "review_cards_count": 17
}
```

### POST /session/card

**요청**:

```json
{
  "session_id": "uuid",
  "quiz_type": "word_to_meaning"
}
```

**퀴즈 유형**: `word_to_meaning`, `meaning_to_word`, `cloze`, `listening`

**응답**:

```json
{
  "card": {
    "id": 1234,
    "question": "decide",
    "options": ["결정하다", "나누다", "설명하다", "요청하다"]
  },
  "cards_remaining": 19,
  "cards_completed": 5
}
```

### POST /session/answer

**요청**:

```json
{
  "session_id": "uuid",
  "card_id": 1234,
  "answer": "결정하다"
}
```

**응답**:

```json
{
  "is_correct": true,
  "correct_answer": "결정하다",
  "next_review_date": "2025-12-17T00:00:00Z",
  "card_state": "review"
}
```

### POST /session/complete

**요청**:

```json
{
  "session_id": "uuid",
  "duration_seconds": 300
}
```

**응답**:

```json
{
  "session_summary": {
    "total_cards": 20,
    "correct_count": 16,
    "accuracy_rate": 80.0
  },
  "streak": {
    "current_streak": 7,
    "is_new_record": false
  },
  "daily_goal": {
    "goal": 20,
    "completed": 21,
    "is_achieved": true
  },
  "xp": {
    "base_xp": 160,
    "bonus_xp": 50,
    "total_xp": 210
  }
}
```

---

## 핵심 개념

### 카드 상태 (FSRS)

| 상태 | 설명 |
|------|------|
| `NEW` | 미학습 카드 |
| `LEARNING` | 학습 중 (단기 기억) |
| `REVIEW` | 복습 단계 (장기 기억) |
| `RELEARNING` | 재학습 (복습 중 오답) |

### XP 계산

- 기본: 정답당 10XP
- 보너스: 정확도 80%+ 시 +50XP

### 스트릭

- 어제 학습 → 연속일 +1
- 어제 미학습 → 1로 리셋

---

## 관련 파일

- `src/app/api/study.py`
- `src/app/services/study_session_service.py`
- `src/app/models/schemas/study.py`
