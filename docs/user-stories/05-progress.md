# 학습 진행 (Progress) 유저 스토리

> FSRS 알고리즘 기반 카드 복습 및 학습 진도 관리
>
> 최종 업데이트: 2025-12-10

---

## 개요

학습 진행 도메인은 FSRS(Free Spaced Repetition Scheduler) 알고리즘을 사용하여
각 사용자의 카드별 학습 상태를 관리하고 최적의 복습 일정을 계산합니다.

### 주요 특징

- **FSRS 알고리즘**: 과학적으로 검증된 간격 반복 학습 알고리즘
- **개인화된 일정**: 사용자의 학습 패턴에 맞춘 복습 일정
- **상태 추적**: 카드별 학습 상태 (신규/학습중/복습/재학습)
- **정확도 분석**: 카드별, 전체 정확도 추적

### FSRS 알고리즘 소개

FSRS는 기존 SM-2 알고리즘의 한계를 개선한 최신 간격 반복 알고리즘입니다:

```
핵심 파라미터:
├── Stability (안정성): 기억이 유지되는 정도
├── Difficulty (난이도): 카드를 기억하기 어려운 정도
├── State (상태): New → Learning → Review → Relearning
└── Scheduled Days: 다음 복습까지의 일수
```

### 학습 진행 데이터 구조

```
UserCardProgress
├── 관계
│   ├── profile_id (사용자 UUID)
│   └── card_id (카드 ID)
├── FSRS 파라미터
│   ├── stability (안정성)
│   ├── difficulty (난이도 1~10)
│   ├── scheduled_days (예정 간격)
│   ├── lapses (망각 횟수)
│   └── card_state (NEW/LEARNING/REVIEW/RELEARNING)
├── 통계
│   ├── total_reviews (총 복습 횟수)
│   ├── correct_count (정답 횟수)
│   ├── wrong_count (오답 횟수)
│   └── accuracy_rate (정확도)
├── 일정
│   ├── next_review_date (다음 복습일)
│   ├── last_review_date (마지막 복습일)
│   └── first_studied_at (첫 학습일)
└── 타임스탬프
    ├── created_at
    └── updated_at
```

---

## US-PROGRESS-01: 카드 복습 결과 제출

### 스토리

**사용자로서**, 카드 복습 결과를 제출할 수 있다.
**그래서** FSRS 알고리즘으로 최적의 다음 복습 일정을 계산받을 수 있다.

### 상세 정보

| 항목           | 내용                                                          |
| -------------- | ------------------------------------------------------------- |
| **엔드포인트** | `POST /api/v1/progress/review`                                |
| **인증 필요**  | 예                                                            |
| **입력**       | 카드 ID, 정답 여부 (`is_correct`)                             |
| **출력**       | 업데이트된 학습 진행 정보 (다음 복습일, 카드 상태, 정확도 등) |
| **상태**       | ✅ 구현 완료                                                  |

### FSRS 등급 매핑

| `is_correct` | FSRS Rating | 설명                              |
| ------------ | ----------- | --------------------------------- |
| `true`       | Good (3)    | 정답 - 적절한 간격으로 복습 예정  |
| `false`      | Again (1)   | 오답 - 짧은 간격으로 재복습 예정  |

### 비즈니스 규칙

1. **첫 복습**: 카드를 처음 학습하면 UserCardProgress 레코드 생성
2. **상태 전이**: FSRS 알고리즘에 따라 카드 상태 자동 변경
3. **통계 업데이트**: 복습 결과에 따라 정확도, 총 복습 횟수 등 업데이트
4. **스트릭 연동**: 오늘 첫 복습이면 학습 세션 시작으로 간주

### 카드 상태 전이도

```
                ┌──────────────────────────────────────┐
                │                                      │
                ▼                                      │
┌─────────┐   정답   ┌──────────┐   정답   ┌────────┐ │
│   NEW   │ ──────▶ │ LEARNING │ ──────▶ │ REVIEW │ │
└─────────┘         └──────────┘         └────────┘ │
                         │                    │      │
                         │ 오답               │ 오답 │
                         ▼                    ▼      │
                    ┌────────────────────────────┐   │
                    │        RELEARNING          │───┘
                    └────────────────────────────┘
                              │
                              │ 정답
                              ▼
                         REVIEW로 복귀
```

### 요청/응답 예시

**요청:**

```json
POST /api/v1/progress/review
{
  "card_id": 1234,
  "is_correct": true
}
```

**성공 응답 (200 OK):**

```json
{
  "id": 5678,
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "card_id": 1234,
  "card_state": "REVIEW",
  "stability": 15.2,
  "difficulty": 4.5,
  "scheduled_days": 7,
  "next_review_date": "2025-12-17T00:00:00Z",
  "last_review_date": "2025-12-10T14:30:00Z",
  "total_reviews": 5,
  "correct_count": 4,
  "wrong_count": 1,
  "accuracy_rate": 80.0,
  "lapses": 1,
  "first_studied_at": "2025-12-01T10:00:00Z"
}
```

### FSRS 파라미터 설명

| 파라미터         | 타입    | 범위    | 설명                              |
| ---------------- | ------- | ------- | --------------------------------- |
| `stability`      | float   | 0+      | 기억 안정성 (높을수록 오래 기억)  |
| `difficulty`     | float   | 1~10    | 카드 난이도 (높을수록 어려움)     |
| `scheduled_days` | integer | 0+      | 다음 복습까지의 일수              |
| `lapses`         | integer | 0+      | 망각 횟수 (REVIEW에서 오답 횟수)  |

---

## US-PROGRESS-02: 복습 예정 카드 조회

### 스토리

**사용자로서**, 오늘 복습해야 할 카드 목록을 조회할 수 있다.
**그래서** 효율적으로 복습 계획을 세울 수 있다.

### 상세 정보

| 항목              | 내용                            |
| ----------------- | ------------------------------- |
| **엔드포인트**    | `GET /api/v1/progress/due`      |
| **인증 필요**     | 예                              |
| **쿼리 파라미터** | `limit` (기본값: 20, 최대: 100) |
| **출력**          | 복습 예정 카드 목록             |
| **상태**          | ✅ 구현 완료                    |

### 조회 조건

1. **복습 예정일**: `next_review_date <= 현재 시간`
2. **선택 덱 필터**: 사용자가 선택한 덱의 카드만 포함
3. **정렬 순서**: 복습 예정일이 오래된 순서 (더 급한 것 먼저)

### 반환 데이터

각 카드에 대해 카드 정보와 학습 진행 정보가 함께 반환됩니다:

```json
{
  "card": {
    "id": 1234,
    "english_word": "decide",
    "korean_meaning": "결정하다",
    "example_sentence": "She decided to study abroad."
  },
  "progress": {
    "card_state": "REVIEW",
    "stability": 15.2,
    "next_review_date": "2025-12-10T00:00:00Z",
    "accuracy_rate": 80.0
  }
}
```

### 요청/응답 예시

**요청:**

```
GET /api/v1/progress/due?limit=10
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "due_cards": [
    {
      "card": {
        "id": 1234,
        "english_word": "decide",
        "korean_meaning": "결정하다",
        "ipa_pronunciation": "/dɪˈsaɪd/",
        "example_sentence": "She decided to study abroad.",
        "difficulty_level": 3
      },
      "progress": {
        "card_state": "REVIEW",
        "stability": 15.2,
        "difficulty": 4.5,
        "next_review_date": "2025-12-09T00:00:00Z",
        "total_reviews": 5,
        "accuracy_rate": 80.0,
        "overdue_days": 1
      }
    }
  ],
  "total_due": 45,
  "returned": 10
}
```

### `overdue_days` 계산

```
overdue_days = 오늘 - next_review_date

예시:
- next_review_date: 2025-12-09
- 오늘: 2025-12-10
- overdue_days: 1 (하루 지남)
```

---

## US-PROGRESS-03: 신규/복습 카드 수 조회

### 스토리

**사용자로서**, 학습 가능한 신규 카드와 복습 예정 카드 수를 확인할 수 있다.
**그래서** 오늘 학습해야 할 양을 파악할 수 있다.

### 상세 정보

| 항목           | 내용                                   |
| -------------- | -------------------------------------- |
| **엔드포인트** | `GET /api/v1/progress/new-cards-count` |
| **인증 필요**  | 예                                     |
| **출력**       | 신규 카드 수, 복습 카드 수             |
| **상태**       | ✅ 구현 완료                           |

### 카드 분류 기준

| 분류         | 조건                                                    |
| ------------ | ------------------------------------------------------- |
| **신규 카드**| UserCardProgress가 없는 카드 (아직 학습한 적 없음)      |
| **복습 카드**| `next_review_date <= 현재 시간`인 카드                  |

### 요청/응답 예시

**요청:**

```
GET /api/v1/progress/new-cards-count
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "new_cards": 150,
  "review_cards": 45,
  "total_available": 195
}
```

### UI 활용 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 오늘 학습할 카드
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🆕 신규 카드: 150개
🔄 복습 카드: 45개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
총 195개의 카드가 대기 중
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## US-PROGRESS-04: 특정 카드 학습 진행 조회

### 스토리

**사용자로서**, 특정 카드에 대한 내 학습 진행 상황을 조회할 수 있다.
**그래서** 개별 카드의 학습 이력을 확인할 수 있다.

### 상세 정보

| 항목           | 내용                                      |
| -------------- | ----------------------------------------- |
| **엔드포인트** | `GET /api/v1/progress/{card_id}`          |
| **인증 필요**  | 예                                        |
| **출력**       | FSRS 파라미터, 카드 상태, 통계, 복습 일정 |
| **상태**       | ✅ 구현 완료                              |

### 카드 상태 (CardState) 설명

| 상태         | 설명                                                |
| ------------ | --------------------------------------------------- |
| `NEW`        | 아직 학습하지 않은 카드                             |
| `LEARNING`   | 학습 중인 카드 (아직 장기 기억에 들어가지 않음)     |
| `REVIEW`     | 복습 단계 카드 (장기 기억에 들어감)                 |
| `RELEARNING` | 다시 학습 중 (복습 중 틀려서 재학습 필요)           |

### 요청/응답 예시

**요청:**

```
GET /api/v1/progress/1234
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "id": 5678,
  "profile_id": "550e8400-e29b-41d4-a716-446655440000",
  "card_id": 1234,
  "card_state": "REVIEW",
  "stability": 15.2,
  "difficulty": 4.5,
  "scheduled_days": 7,
  "lapses": 1,
  "next_review_date": "2025-12-17T00:00:00Z",
  "last_review_date": "2025-12-10T14:30:00Z",
  "first_studied_at": "2025-12-01T10:00:00Z",
  "total_reviews": 5,
  "correct_count": 4,
  "wrong_count": 1,
  "accuracy_rate": 80.0,
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-10T14:30:00Z"
}
```

**카드를 학습한 적 없는 경우 (404 또는 기본값):**

```json
{
  "card_id": 1234,
  "card_state": "NEW",
  "message": "이 카드를 아직 학습한 적이 없습니다."
}
```

---

## FSRS 알고리즘 상세

### 복습 간격 예시

#### 정답만 맞췄을 때 (이상적인 경우)

| 복습 횟수 | 간격      | 상태       |
| --------- | --------- | ---------- |
| 1         | 1일       | LEARNING   |
| 2         | 3일       | LEARNING   |
| 3         | 7일       | REVIEW     |
| 4         | 14일      | REVIEW     |
| 5         | 30일      | REVIEW     |
| 6         | 60일      | REVIEW     |

#### 중간에 틀렸을 때

```
복습 1: 정답 → 간격 1일 (LEARNING)
복습 2: 정답 → 간격 3일 (LEARNING)
복습 3: 정답 → 간격 7일 (REVIEW)
복습 4: 오답 → 간격 10분 (RELEARNING), lapses: 1
복습 5: 정답 → 간격 2일 (REVIEW) - 감소된 간격
```

### 난이도 조정

카드의 `difficulty`는 복습 결과에 따라 동적으로 조정됩니다:

- **계속 맞추면**: difficulty 감소 (더 쉬운 카드로 인식)
- **계속 틀리면**: difficulty 증가 (더 어려운 카드로 인식)

```
difficulty 범위: 1.0 (매우 쉬움) ~ 10.0 (매우 어려움)
기본값: 5.0
```

---

## 관련 컴포넌트

### 서비스

- `src/app/services/user_card_progress_service.py`: FSRS 통합 및 진행 관리

### 모델

- `src/app/models/tables/user_card_progress.py`: UserCardProgress 테이블
- `src/app/models/schemas/user_card_progress.py`: 진행 관련 스키마
- `src/app/models/enums.py`: CardState 열거형

### 외부 라이브러리

- `py-fsrs`: FSRS 알고리즘 구현체

### API

- `src/app/api/progress.py`: 진행 라우트 핸들러

---

## 테스트 예제

### Curl

```bash
# 토큰 발급 (로그인 후)
TOKEN="your_access_token_here"

# 복습 결과 제출
curl -X POST http://localhost:8080/api/v1/progress/review \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"card_id": 1234, "is_correct": true}'

# 복습 예정 카드 조회
curl -X GET "http://localhost:8080/api/v1/progress/due?limit=20" \
  -H "Authorization: Bearer $TOKEN"

# 신규/복습 카드 수 조회
curl -X GET http://localhost:8080/api/v1/progress/new-cards-count \
  -H "Authorization: Bearer $TOKEN"

# 특정 카드 학습 진행 조회
curl -X GET http://localhost:8080/api/v1/progress/1234 \
  -H "Authorization: Bearer $TOKEN"
```

### Python

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"
headers = {"Authorization": "Bearer your_access_token_here"}

# 복습 결과 제출
response = requests.post(
    f"{BASE_URL}/progress/review",
    headers=headers,
    json={"card_id": 1234, "is_correct": True}
)
progress = response.json()
print(f"다음 복습일: {progress['next_review_date']}")
print(f"정확도: {progress['accuracy_rate']}%")

# 복습 예정 카드 조회
response = requests.get(
    f"{BASE_URL}/progress/due",
    headers=headers,
    params={"limit": 20}
)
due_data = response.json()
print(f"오늘 복습할 카드: {due_data['total_due']}개")

# 신규/복습 카드 수 조회
response = requests.get(
    f"{BASE_URL}/progress/new-cards-count",
    headers=headers
)
counts = response.json()
print(f"신규: {counts['new_cards']}개, 복습: {counts['review_cards']}개")
```

---

## 관련 문서

- [단어 카드 유저 스토리](./03-vocabulary-cards.md)
- [퀴즈 유저 스토리](./06-quiz.md)
- [학습 세션 유저 스토리](./08-study-session.md)
