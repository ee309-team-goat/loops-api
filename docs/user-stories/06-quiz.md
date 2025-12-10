# 퀴즈 (Quiz) 유저 스토리

> 4가지 퀴즈 모드 (word_to_meaning, meaning_to_word, cloze, listening)
>
> 최종 업데이트: 2025-12-10

---

## 개요

퀴즈 도메인은 다양한 형태의 퀴즈를 통해 단어 학습을 강화합니다.
단순 플래시카드 외에도 4지선다, 빈칸 채우기, 듣기 등 다양한 방식으로 학습할 수 있습니다.

### 주요 특징

- **4가지 퀴즈 유형**: 다양한 학습 방식 제공
- **세션 기반**: 퀴즈 시작부터 완료까지 세션으로 관리
- **즉시 피드백**: 답변 제출 시 즉시 정답/오답 확인
- **경험치 시스템**: 퀴즈 완료 시 XP 획득

### 퀴즈 유형

| 유형                | 설명                                    | 입력 방식    |
| ------------------- | --------------------------------------- | ------------ |
| `word_to_meaning`   | 영어 단어를 보고 뜻 맞추기              | 4지선다      |
| `meaning_to_word`   | 한국어 뜻을 보고 영어 단어 맞추기       | 4지선다      |
| `cloze`             | 문장에서 빈칸에 들어갈 단어 맞추기      | 직접 입력    |
| `listening`         | 발음을 듣고 단어 맞추기                 | 직접 입력    |

### 퀴즈 세션 흐름

```
┌────────────────┐     ┌────────────────┐     ┌────────────────┐
│   퀴즈 시작    │ ──▶ │   문제 풀이    │ ──▶ │   퀴즈 완료    │
│ POST /start    │     │ POST /answer   │     │ POST /complete │
└────────────────┘     └────────────────┘     └────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
  세션 ID 발급          즉시 채점 결과        최종 점수 + XP
  카드 목록 반환          피드백 제공           통계 업데이트
```

---

## US-QUIZ-01: 퀴즈 세션 시작

### 스토리

**사용자로서**, 특정 유형의 퀴즈 세션을 시작할 수 있다.
**그래서** 다양한 방식으로 단어를 학습할 수 있다.

### 상세 정보

| 항목           | 내용                                                            |
| -------------- | --------------------------------------------------------------- |
| **엔드포인트** | `POST /api/v1/quiz/start`                                       |
| **인증 필요**  | 예                                                              |
| **입력**       | 퀴즈 유형, 카드 수 제한, 새 카드 포함 여부, 복습 카드 포함 여부 |
| **출력**       | 세션 ID, 퀴즈 유형, 총 카드 수, 퀴즈 카드 목록, 시작 시간       |
| **상태**       | ✅ 구현 완료                                                    |

### 입력 파라미터

| 파라미터            | 타입    | 기본값 | 설명                           |
| ------------------- | ------- | ------ | ------------------------------ |
| `quiz_type`         | string  | 필수   | 퀴즈 유형                      |
| `limit`             | integer | 20     | 출제할 카드 수 (최대 50)       |
| `include_new`       | boolean | true   | 새 카드 포함 여부              |
| `include_review`    | boolean | true   | 복습 예정 카드 포함 여부       |

### 퀴즈 유형별 카드 데이터

#### word_to_meaning (영어 → 뜻)

```json
{
  "card_id": 1234,
  "question": "decide",
  "choices": [
    {"id": "A", "text": "결정하다"},
    {"id": "B", "text": "나누다"},
    {"id": "C", "text": "설명하다"},
    {"id": "D", "text": "요청하다"}
  ],
  "correct_answer": "A"
}
```

#### meaning_to_word (뜻 → 영어)

```json
{
  "card_id": 1234,
  "question": "결정하다",
  "choices": [
    {"id": "A", "text": "divide"},
    {"id": "B", "text": "decide"},
    {"id": "C", "text": "describe"},
    {"id": "D", "text": "demand"}
  ],
  "correct_answer": "B"
}
```

#### cloze (빈칸 채우기)

```json
{
  "card_id": 1234,
  "question": "She _______ to study abroad.",
  "hint": "d로 시작하는 7글자 단어",
  "correct_answer": "decided",
  "original_sentence": "She decided to study abroad."
}
```

#### listening (듣기)

```json
{
  "card_id": 1234,
  "audio_url": "https://storage.example.com/audio/decide.mp3",
  "hint": "동사, 7글자",
  "correct_answer": "decide"
}
```

### 요청/응답 예시

**요청:**

```json
POST /api/v1/quiz/start
{
  "quiz_type": "word_to_meaning",
  "limit": 10,
  "include_new": true,
  "include_review": true
}
```

**성공 응답 (200 OK):**

```json
{
  "session_id": "quiz_abc123def456",
  "quiz_type": "word_to_meaning",
  "total_cards": 10,
  "started_at": "2025-12-10T14:00:00Z",
  "cards": [
    {
      "card_id": 1234,
      "question": "decide",
      "choices": [
        {"id": "A", "text": "결정하다"},
        {"id": "B", "text": "나누다"},
        {"id": "C", "text": "설명하다"},
        {"id": "D", "text": "요청하다"}
      ]
    },
    {
      "card_id": 1235,
      "question": "important",
      "choices": [
        {"id": "A", "text": "가능한"},
        {"id": "B", "text": "중요한"},
        {"id": "C", "text": "다양한"},
        {"id": "D", "text": "특별한"}
      ]
    }
  ]
}
```

### 오답 선택지 생성 규칙

4지선다 퀴즈의 오답 선택지는 다음 기준으로 생성됩니다:

1. **같은 품사**: 정답과 같은 품사의 단어
2. **비슷한 난이도**: ±2 레벨 이내의 단어
3. **중복 방지**: 이미 출제된 단어 제외
4. **무작위 순서**: 정답 위치 랜덤화

---

## US-QUIZ-02: 퀴즈 정답 제출

### 스토리

**사용자로서**, 퀴즈 정답을 제출하고 채점 결과를 받을 수 있다.
**그래서** 즉시 학습 피드백을 받을 수 있다.

### 상세 정보

| 항목           | 내용                                        |
| -------------- | ------------------------------------------- |
| **엔드포인트** | `POST /api/v1/quiz/answer`                  |
| **인증 필요**  | 예                                          |
| **입력**       | 카드 ID, 사용자 정답, 퀴즈 유형, 응답 시간  |
| **출력**       | 정답 여부, 정답, 사용자 정답, 피드백 메시지 |
| **상태**       | ✅ 구현 완료                                |

### 입력 파라미터

| 파라미터        | 타입    | 설명                         |
| --------------- | ------- | ---------------------------- |
| `card_id`       | integer | 문제 카드 ID                 |
| `user_answer`   | string  | 사용자가 제출한 답           |
| `quiz_type`     | string  | 퀴즈 유형                    |
| `response_time` | integer | 응답 시간 (밀리초, 선택)     |

### 채점 규칙

#### 4지선다 (word_to_meaning, meaning_to_word)

```
정답: user_answer === correct_choice_id
예: user_answer: "A", correct: "A" → 정답
```

#### 빈칸 채우기 (cloze)

```
1. 소문자 변환 후 비교
2. 앞뒤 공백 제거
3. 정확히 일치해야 정답

예:
- 정답: "decided"
- "Decided" → 정답 (대소문자 무시)
- "decide" → 오답 (시제 다름)
- " decided " → 정답 (공백 제거)
```

#### 듣기 (listening)

```
1. 소문자 변환 후 비교
2. 앞뒤 공백 제거
3. 정확히 일치해야 정답
```

### 요청/응답 예시

**요청:**

```json
POST /api/v1/quiz/answer
{
  "card_id": 1234,
  "user_answer": "A",
  "quiz_type": "word_to_meaning",
  "response_time": 3500
}
```

**정답인 경우 (200 OK):**

```json
{
  "is_correct": true,
  "correct_answer": "A",
  "correct_text": "결정하다",
  "user_answer": "A",
  "feedback": "정답입니다! 🎉",
  "card_info": {
    "english_word": "decide",
    "korean_meaning": "결정하다",
    "example_sentence": "She decided to study abroad."
  }
}
```

**오답인 경우 (200 OK):**

```json
{
  "is_correct": false,
  "correct_answer": "A",
  "correct_text": "결정하다",
  "user_answer": "B",
  "user_answer_text": "나누다",
  "feedback": "아쉬워요! 정답은 '결정하다'입니다.",
  "card_info": {
    "english_word": "decide",
    "korean_meaning": "결정하다",
    "example_sentence": "She decided to study abroad.",
    "ipa_pronunciation": "/dɪˈsaɪd/"
  }
}
```

### FSRS 연동

퀴즈 답변 제출 시 자동으로 학습 진행(Progress)이 업데이트됩니다:

- **정답**: FSRS Good 등급으로 처리
- **오답**: FSRS Again 등급으로 처리

---

## US-QUIZ-03: 퀴즈 세션 완료

### 스토리

**사용자로서**, 퀴즈 세션을 완료하고 최종 결과를 확인할 수 있다.
**그래서** 퀴즈 성과를 파악할 수 있다.

### 상세 정보

| 항목           | 내용                                                |
| -------------- | --------------------------------------------------- |
| **엔드포인트** | `POST /api/v1/quiz/complete`                        |
| **인증 필요**  | 예                                                  |
| **입력**       | 세션 ID, 총 답변 수, 정답 수, 소요 시간             |
| **출력**       | 총 답변 수, 정답 수, 정확도, 소요 시간, 획득 경험치 |
| **상태**       | ✅ 구현 완료                                        |

### 경험치 (XP) 계산

```
기본 XP = 정답 수 × 10

보너스 XP:
- 정확도 80% 이상: +50 XP
- 정확도 100%: +100 XP (추가)
- 빠른 완료 (평균 5초 이내): +30 XP

총 XP = 기본 XP + 보너스 XP
```

### 요청/응답 예시

**요청:**

```json
POST /api/v1/quiz/complete
{
  "session_id": "quiz_abc123def456",
  "total_answered": 10,
  "correct_count": 8,
  "duration_seconds": 120
}
```

**성공 응답 (200 OK):**

```json
{
  "session_id": "quiz_abc123def456",
  "quiz_type": "word_to_meaning",
  "total_answered": 10,
  "correct_count": 8,
  "wrong_count": 2,
  "accuracy": 80.0,
  "duration_seconds": 120,
  "average_time_per_card": 12.0,
  "xp_earned": {
    "base": 80,
    "accuracy_bonus": 50,
    "speed_bonus": 0,
    "total": 130
  },
  "achievements": [
    {
      "type": "accuracy_streak",
      "message": "5문제 연속 정답! 🔥"
    }
  ]
}
```

### 세션 완료 시 처리

1. **통계 업데이트**: 오늘의 학습 통계에 반영
2. **스트릭 체크**: 오늘 첫 퀴즈면 스트릭 업데이트
3. **일일 목표**: 정답 수만큼 일일 목표 진행
4. **XP 적립**: 계산된 XP를 프로필에 추가

---

## 퀴즈 유형별 상세 가이드

### Word to Meaning (영어 → 뜻)

**목적**: 영어 단어를 보고 의미를 기억하는 능력 테스트

**화면 구성**:
```
┌─────────────────────────────────┐
│                                 │
│            decide               │
│           /dɪˈsaɪd/             │
│                                 │
├─────────────────────────────────┤
│  A. 결정하다                    │
│  B. 나누다                      │
│  C. 설명하다                    │
│  D. 요청하다                    │
└─────────────────────────────────┘
```

**학습 효과**: 수동적 어휘력 (읽기/듣기 시 이해력)

### Meaning to Word (뜻 → 영어)

**목적**: 한국어 의미에서 영어 단어를 떠올리는 능력 테스트

**화면 구성**:
```
┌─────────────────────────────────┐
│                                 │
│           결정하다              │
│                                 │
├─────────────────────────────────┤
│  A. divide                      │
│  B. decide                      │
│  C. describe                    │
│  D. demand                      │
└─────────────────────────────────┘
```

**학습 효과**: 능동적 어휘력 (말하기/쓰기 시 표현력)

### Cloze (빈칸 채우기)

**목적**: 문맥 속에서 단어를 사용하는 능력 테스트

**화면 구성**:
```
┌─────────────────────────────────┐
│                                 │
│  She _______ to study abroad.  │
│                                 │
│  힌트: d로 시작하는 7글자 동사  │
│                                 │
├─────────────────────────────────┤
│  [                            ] │
│            입력하세요           │
└─────────────────────────────────┘
```

**학습 효과**: 문맥 이해력, 활용형(시제/형태) 파악

### Listening (듣기)

**목적**: 발음을 듣고 단어를 인식하는 능력 테스트

**화면 구성**:
```
┌─────────────────────────────────┐
│                                 │
│         🔊 [재생 버튼]          │
│                                 │
│       힌트: 동사, 7글자         │
│                                 │
├─────────────────────────────────┤
│  [                            ] │
│          들은 단어 입력         │
└─────────────────────────────────┘
```

**학습 효과**: 듣기 이해력, 발음-철자 연결

---

## 관련 컴포넌트

### 서비스

- `src/app/services/quiz_service.py`: 퀴즈 세션 관리
- `src/app/services/cloze_service.py`: 빈칸 채우기 문장 처리

### 모델

- `src/app/models/schemas/quiz.py`: 퀴즈 관련 스키마

### API

- `src/app/api/quiz.py`: 퀴즈 라우트 핸들러

---

## 관련 문서

- [단어 카드 유저 스토리](./03-vocabulary-cards.md)
- [학습 진행 유저 스토리](./05-progress.md)
- [통계 유저 스토리](./07-statistics.md)
