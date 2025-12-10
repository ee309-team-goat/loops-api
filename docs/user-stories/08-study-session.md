# 학습 세션 (Study Session) 유저 스토리

> 학습 세션 시작/완료, 스트릭 업데이트
>
> 최종 업데이트: 2025-12-10

---

## 개요

학습 세션 도메인은 사용자의 학습 단위를 관리합니다.
세션을 시작하면 학습할 카드 목록을 받고, 완료 시 결과를 저장하고 스트릭을 업데이트합니다.

### 주요 특징

- **세션 기반 학습**: 명확한 시작과 종료가 있는 학습 단위
- **카드 자동 선택**: 신규 카드와 복습 카드의 균형 잡힌 구성
- **스트릭 관리**: 세션 완료 시 자동으로 스트릭 업데이트
- **일일 목표 연동**: 세션 결과가 일일 목표 진행에 반영

### 학습 세션 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                        학습 세션 흐름                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  세션 시작   │ ──▶ │   카드 학습   │ ──▶ │  세션 완료   │ │
│  │ POST /start  │     │ (클라이언트)  │     │POST /complete│ │
│  └──────────────┘     └──────────────┘     └──────────────┘ │
│         │                    │                    │         │
│         ▼                    ▼                    ▼         │
│  • 카드 목록 생성     • 각 카드 복습      • 결과 저장       │
│  • 세션 ID 발급       • 정답/오답 처리    • 스트릭 업데이트  │
│  • 시작 시간 기록     • Progress 업데이트 • 일일 목표 반영  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 세션 vs 퀴즈 차이점

| 특성         | 학습 세션                    | 퀴즈                         |
| ------------ | ---------------------------- | ---------------------------- |
| 목적         | 플래시카드 기반 일반 학습    | 게이미피케이션 요소의 테스트 |
| 카드 형태    | 앞면/뒷면 플립               | 4지선다, 빈칸 채우기 등      |
| 평가 방식    | 자기 평가 (정답/오답)        | 시스템 자동 채점             |
| XP 시스템    | 없음                         | 있음                         |
| FSRS 연동    | 직접 연동                    | 간접 연동 (답변 시)          |

---

## US-STUDY-01: 학습 세션 시작

### 스토리

**사용자로서**, 새로운 학습 세션을 시작하고 학습할 카드 목록을 받을 수 있다.
**그래서** 체계적으로 학습을 시작할 수 있다.

### 상세 정보

| 항목           | 내용                                                         |
| -------------- | ------------------------------------------------------------ |
| **엔드포인트** | `POST /api/v1/study/session/start`                           |
| **인증 필요**  | 예                                                           |
| **입력**       | 신규 카드 최대 수 (기본: 10), 복습 카드 최대 수 (기본: 20)   |
| **출력**       | 세션 ID, 총 카드 수, 신규/복습 카드 수, 카드 목록, 시작 시간 |
| **상태**       | ✅ 구현 완료                                                 |

### 입력 파라미터

| 파라미터          | 타입    | 기본값 | 최대값 | 설명                    |
| ----------------- | ------- | ------ | ------ | ----------------------- |
| `max_new_cards`   | integer | 10     | 50     | 신규 카드 최대 수       |
| `max_review_cards`| integer | 20     | 100    | 복습 카드 최대 수       |

### 카드 선택 알고리즘

#### 1. 복습 카드 선택 (우선)

```
조건:
1. 사용자가 선택한 덱에 속한 카드
2. next_review_date <= 현재 시간 (복습 예정)
3. card_state가 LEARNING, REVIEW, RELEARNING 중 하나

정렬 기준:
1. 오버듀 일수 (많이 밀린 것 우선)
2. card_state 우선순위: RELEARNING > LEARNING > REVIEW
```

#### 2. 신규 카드 선택

```
조건:
1. 사용자가 선택한 덱에 속한 카드
2. UserCardProgress가 없거나 card_state가 NEW
3. is_verified = true (검증된 카드만)

정렬 기준:
1. usage_frequency (사용 빈도 높은 것 우선)
2. difficulty_level (쉬운 것 우선)
```

### 반환 카드 데이터

각 카드에는 학습에 필요한 정보가 포함됩니다:

```json
{
  "card_id": 1234,
  "card_type": "new",
  "front": {
    "english_word": "decide",
    "ipa_pronunciation": "/dɪˈsaɪd/",
    "part_of_speech": "verb"
  },
  "back": {
    "korean_meaning": "결정하다",
    "english_definition": "to make a choice",
    "example_sentence": "She decided to study abroad.",
    "example_translation": "그녀는 유학을 가기로 결정했다."
  },
  "difficulty_level": 3,
  "cefr_level": "A2"
}
```

### 요청/응답 예시

**요청:**

```json
POST /api/v1/study/session/start
{
  "max_new_cards": 10,
  "max_review_cards": 20
}
```

**성공 응답 (200 OK):**

```json
{
  "session_id": "session_abc123def456",
  "started_at": "2025-12-10T14:00:00Z",
  "total_cards": 25,
  "new_cards_count": 8,
  "review_cards_count": 17,
  "cards": [
    {
      "card_id": 1234,
      "card_type": "review",
      "overdue_days": 2,
      "front": {
        "english_word": "decide",
        "ipa_pronunciation": "/dɪˈsaɪd/",
        "part_of_speech": "verb"
      },
      "back": {
        "korean_meaning": "결정하다",
        "english_definition": "to make a choice or come to a conclusion",
        "example_sentence": "She decided to study abroad.",
        "example_translation": "그녀는 유학을 가기로 결정했다."
      },
      "difficulty_level": 3,
      "cefr_level": "A2",
      "audio_url": "https://storage.example.com/audio/decide.mp3"
    },
    {
      "card_id": 1235,
      "card_type": "new",
      "front": {
        "english_word": "accomplish",
        "ipa_pronunciation": "/əˈkɑːmplɪʃ/",
        "part_of_speech": "verb"
      },
      "back": {
        "korean_meaning": "성취하다, 달성하다",
        "english_definition": "to succeed in doing something",
        "example_sentence": "We accomplished our goal.",
        "example_translation": "우리는 목표를 달성했다."
      },
      "difficulty_level": 5,
      "cefr_level": "B1",
      "audio_url": null
    }
  ],
  "daily_goal_info": {
    "goal": 20,
    "completed_before_session": 5,
    "remaining": 15
  }
}
```

### 카드가 없는 경우

사용자가 선택한 덱에 학습할 카드가 없으면:

```json
{
  "session_id": null,
  "message": "현재 학습할 카드가 없습니다.",
  "reason": "all_cards_reviewed",
  "next_review_at": "2025-12-11T10:00:00Z",
  "suggestion": "내일 다시 확인하거나 새로운 덱을 추가해보세요."
}
```

---

## US-STUDY-02: 학습 세션 완료

### 스토리

**사용자로서**, 학습 세션을 완료하고 통계 및 스트릭을 업데이트할 수 있다.
**그래서** 학습 성과를 기록하고 연속 학습일을 유지할 수 있다.

### 상세 정보

| 항목           | 내용                                   |
| -------------- | -------------------------------------- |
| **엔드포인트** | `POST /api/v1/study/session/complete`  |
| **인증 필요**  | 예                                     |
| **입력**       | 학습 카드 수, 정답 수, 학습 시간 (초)  |
| **출력**       | 세션 요약, 스트릭 정보, 일일 목표 상태 |
| **상태**       | ✅ 구현 완료                           |

### 입력 파라미터

| 파라미터           | 타입    | 설명                      |
| ------------------ | ------- | ------------------------- |
| `cards_studied`    | integer | 학습한 카드 수            |
| `correct_count`    | integer | 정답으로 평가한 카드 수   |
| `duration_seconds` | integer | 총 학습 시간 (초)         |

### 처리 과정

#### 1. 세션 결과 저장

```
- 학습한 카드 수
- 정답/오답 수
- 정확도 계산
- 평균 카드당 소요 시간
```

#### 2. 스트릭 업데이트

```
오늘 첫 세션인 경우:
  └─ last_study_date가 어제이면:
       └─ current_streak += 1
       └─ longest_streak = max(current_streak, longest_streak)
  └─ last_study_date가 어제가 아니면:
       └─ current_streak = 1 (리셋)
  └─ last_study_date = 오늘

오늘 이미 학습한 경우:
  └─ 스트릭 변경 없음
```

#### 3. 프로필 통계 업데이트

```
- total_study_time_minutes += duration_seconds / 60
- last_study_date = 오늘
```

#### 4. 일일 목표 진행

```
- 정답 수만큼 일일 목표 진행
- goal_progress = (completed / daily_goal) * 100
```

### 반환 데이터 상세

#### session_summary

| 필드               | 타입    | 설명                      |
| ------------------ | ------- | ------------------------- |
| `total_cards`      | integer | 학습한 총 카드 수         |
| `correct`          | integer | 정답 수                   |
| `wrong`            | integer | 오답 수                   |
| `accuracy`         | float   | 정확도 (%)                |
| `duration_seconds` | integer | 소요 시간 (초)            |
| `avg_time_per_card`| float   | 카드당 평균 시간 (초)     |

#### streak

| 필드            | 타입    | 설명                           |
| --------------- | ------- | ------------------------------ |
| `current_streak`| integer | 현재 연속 학습일               |
| `longest_streak`| integer | 최장 연속 학습일               |
| `is_new_record` | boolean | 최장 기록 갱신 여부            |
| `streak_status` | string  | continued/started/maintained   |
| `message`       | string  | 스트릭 관련 메시지             |

#### daily_goal

| 필드          | 타입    | 설명                    |
| ------------- | ------- | ----------------------- |
| `goal`        | integer | 일일 목표               |
| `completed`   | integer | 완료한 카드 수          |
| `progress`    | float   | 진행률 (%)              |
| `is_completed`| boolean | 목표 달성 여부          |

### 요청/응답 예시

**요청:**

```json
POST /api/v1/study/session/complete
{
  "cards_studied": 20,
  "correct_count": 16,
  "duration_seconds": 300
}
```

**성공 응답 (200 OK):**

```json
{
  "session_summary": {
    "total_cards": 20,
    "correct": 16,
    "wrong": 4,
    "accuracy": 80.0,
    "duration_seconds": 300,
    "avg_time_per_card": 15.0
  },
  "streak": {
    "current_streak": 7,
    "longest_streak": 12,
    "is_new_record": false,
    "streak_status": "continued",
    "message": "🔥 7일 연속 학습 중! 최장 기록까지 5일 남았어요!"
  },
  "daily_goal": {
    "goal": 20,
    "completed": 21,
    "progress": 105.0,
    "is_completed": true,
    "message": "🎉 오늘의 목표를 달성했습니다!"
  },
  "achievements": [
    {
      "type": "daily_goal_complete",
      "message": "오늘의 학습 목표 달성! 🎯"
    }
  ]
}
```

### 스트릭 상태 메시지 예시

| streak_status | is_new_record | 메시지 예시                                    |
| ------------- | ------------- | ---------------------------------------------- |
| `started`     | false         | "🌱 새로운 스트릭을 시작했어요!"               |
| `continued`   | false         | "🔥 7일 연속 학습 중!"                         |
| `continued`   | true          | "🏆 새로운 기록! 8일 연속 학습 달성!"          |
| `maintained`  | false         | "✨ 오늘도 학습을 완료했어요!"                 |

---

## 학습 세션 시나리오

### 시나리오 1: 신규 사용자 첫 학습

```
세션 시작:
- 신규 카드: 10개 (사용 빈도 높은 순)
- 복습 카드: 0개 (아직 없음)
- 총: 10개

세션 완료:
- 정답: 7개, 오답: 3개
- 스트릭: 0 → 1 (새 스트릭 시작)
- 일일 목표: 7/20 (35%)
```

### 시나리오 2: 일주일째 학습 중인 사용자

```
세션 시작:
- 신규 카드: 5개
- 복습 카드: 15개 (밀린 복습 포함)
- 총: 20개

세션 완료:
- 정답: 18개, 오답: 2개
- 스트릭: 6 → 7 (연속 학습 유지)
- 일일 목표: 23/20 (115% - 초과 달성!)
```

### 시나리오 3: 하루 쉬고 복귀한 사용자

```
세션 시작:
- 신규 카드: 3개
- 복습 카드: 25개 (하루 밀림)
- 총: 28개

세션 완료:
- 정답: 20개, 오답: 8개
- 스트릭: 5 → 1 (리셋 후 새 시작)
- 메시지: "아쉽지만 괜찮아요! 새로운 스트릭을 시작했어요 🌱"
```

---

## 클라이언트 구현 가이드

### 학습 화면 흐름

```
1. 세션 시작 API 호출
2. 카드 목록 수신
3. 각 카드 표시:
   - 앞면 표시 (영어 단어, 발음)
   - 사용자가 답을 생각
   - 뒷면 표시 (뜻, 예문)
   - 정답/오답 버튼 표시
   - 선택에 따라 Progress API 호출 (선택적)
4. 모든 카드 완료 후 세션 완료 API 호출
5. 결과 화면 표시
```

### 정답/오답 처리

학습 세션 중 각 카드의 정답/오답은 두 가지 방식으로 처리할 수 있습니다:

#### 방식 1: 실시간 Progress 업데이트

```javascript
// 각 카드 복습 시
async function reviewCard(cardId, isCorrect) {
  await api.post('/progress/review', {
    card_id: cardId,
    is_correct: isCorrect
  });
  // 다음 카드로 이동
}
```

#### 방식 2: 세션 완료 시 일괄 처리

```javascript
// 클라이언트에서 결과 누적
const results = [];

function markCard(cardId, isCorrect) {
  results.push({ card_id: cardId, is_correct: isCorrect });
}

// 세션 완료 시 한번에 전송
async function completeSession() {
  await api.post('/study/session/complete', {
    cards_studied: results.length,
    correct_count: results.filter(r => r.is_correct).length,
    duration_seconds: totalDuration
  });
}
```

---

## 관련 컴포넌트

### 서비스

- `src/app/services/study_session_service.py`: 세션 관리 및 카드 선택
- `src/app/services/profile_service.py`: 스트릭 업데이트

### 모델

- `src/app/models/schemas/study.py`: 세션 관련 스키마

### API

- `src/app/api/study.py`: 세션 라우트 핸들러

---

## 관련 문서

- [학습 진행 유저 스토리](./05-progress.md)
- [프로필 유저 스토리](./02-profile.md)
- [통계 유저 스토리](./07-statistics.md)
