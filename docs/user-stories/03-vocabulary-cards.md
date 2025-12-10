# 단어 카드 (Vocabulary Cards) 유저 스토리

> 영어 단어 카드 CRUD 및 검색
>
> 최종 업데이트: 2025-12-10

---

## 개요

단어 카드 도메인은 영어 학습의 핵심 콘텐츠인 단어 카드를 관리합니다.
각 카드는 영어 단어, 한국어 뜻, 발음, 예문, 빈칸 채우기 문장 등 풍부한 학습 자료를 포함합니다.

### 주요 특징

- **다양한 학습 정보**: 단어, 뜻, 발음(IPA), 품사, 예문, 빈칸 채우기 문장
- **난이도 시스템**: 1~10 단계 난이도 및 CEFR 레벨 (A1~C2)
- **덱 연결**: 각 카드는 특정 덱에 소속
- **검증 시스템**: 관리자 검증 완료 카드 표시

### 카드 데이터 구조

```
VocabularyCard
├── 기본 정보
│   ├── id (정수, 자동 증가)
│   ├── english_word (영어 단어)
│   ├── korean_meaning (한국어 뜻)
│   └── part_of_speech (품사)
├── 발음 및 정의
│   ├── ipa_pronunciation (IPA 발음 기호)
│   └── english_definition (영어 정의)
├── 예문
│   ├── example_sentence (예문)
│   ├── example_translation (예문 번역)
│   └── cloze_sentence (빈칸 채우기 문장)
├── 분류
│   ├── difficulty_level (1~10)
│   ├── cefr_level (A1~C2)
│   └── deck_id (덱 ID)
├── 메타데이터
│   ├── usage_frequency (사용 빈도)
│   ├── is_verified (검증 완료 여부)
│   └── audio_url (발음 오디오 URL)
└── 타임스탬프
    ├── created_at
    └── updated_at
```

---

## US-CARD-01: 단어 카드 생성

### 스토리

**관리자로서**, 새로운 영어 단어 카드를 생성할 수 있다.
**그래서** 학습 콘텐츠를 추가할 수 있다.

### 상세 정보

| 항목           | 내용                                                            |
| -------------- | --------------------------------------------------------------- |
| **엔드포인트** | `POST /api/v1/cards`                                            |
| **인증 필요**  | 예                                                              |
| **필수 입력**  | 영어 단어, 한국어 뜻                                            |
| **선택 입력**  | 품사, IPA 발음, 영어 정의, 예문, 난이도(1~10), CEFR 레벨, 덱 ID |
| **상태**       | ✅ 구현 완료                                                    |

### 입력 필드 상세

| 필드                  | 필수 | 타입    | 제약조건         | 설명                    |
| --------------------- | ---- | ------- | ---------------- | ----------------------- |
| `english_word`        | ✅   | string  | max 100자        | 영어 단어               |
| `korean_meaning`      | ✅   | string  | max 200자        | 한국어 뜻               |
| `part_of_speech`      | ❌   | string  | max 20자         | 품사 (noun, verb 등)    |
| `ipa_pronunciation`   | ❌   | string  | max 100자        | IPA 발음 기호           |
| `english_definition`  | ❌   | string  | max 500자        | 영어 정의               |
| `example_sentence`    | ❌   | string  | max 500자        | 예문                    |
| `example_translation` | ❌   | string  | max 500자        | 예문 한국어 번역        |
| `cloze_sentence`      | ❌   | string  | max 500자        | 빈칸 채우기 문장        |
| `difficulty_level`    | ❌   | integer | 1~10             | 난이도 (기본값: 5)      |
| `cefr_level`          | ❌   | string  | A1~C2            | CEFR 레벨               |
| `deck_id`             | ❌   | integer | 유효한 덱 ID     | 소속 덱                 |
| `usage_frequency`     | ❌   | integer | 양수             | 사용 빈도 순위          |

### 빈칸 채우기 문장 형식

빈칸 채우기 문장(`cloze_sentence`)은 정답 위치를 `{{word}}`로 표시합니다:

```
입력: "She {{decided}} to study abroad."
표시: "She _______ to study abroad."
정답: "decided"
```

### 요청/응답 예시

**요청:**

```json
{
  "english_word": "decide",
  "korean_meaning": "결정하다",
  "part_of_speech": "verb",
  "ipa_pronunciation": "/dɪˈsaɪd/",
  "english_definition": "to make a choice or come to a conclusion about something",
  "example_sentence": "She decided to study abroad.",
  "example_translation": "그녀는 유학을 가기로 결정했다.",
  "cloze_sentence": "She {{decided}} to study abroad.",
  "difficulty_level": 3,
  "cefr_level": "A2",
  "deck_id": 1,
  "usage_frequency": 450
}
```

**성공 응답 (201 Created):**

```json
{
  "id": 1234,
  "english_word": "decide",
  "korean_meaning": "결정하다",
  "part_of_speech": "verb",
  "ipa_pronunciation": "/dɪˈsaɪd/",
  "english_definition": "to make a choice or come to a conclusion about something",
  "example_sentence": "She decided to study abroad.",
  "example_translation": "그녀는 유학을 가기로 결정했다.",
  "cloze_sentence": "She {{decided}} to study abroad.",
  "difficulty_level": 3,
  "cefr_level": "A2",
  "deck_id": 1,
  "usage_frequency": 450,
  "is_verified": false,
  "audio_url": null,
  "created_at": "2025-12-10T10:00:00Z",
  "updated_at": "2025-12-10T10:00:00Z"
}
```

---

## US-CARD-02: 단어 카드 목록 조회

### 스토리

**사용자로서**, 단어 카드 목록을 조회할 수 있다.
**그래서** 학습할 단어들을 탐색할 수 있다.

### 상세 정보

| 항목              | 내용                                           |
| ----------------- | ---------------------------------------------- |
| **엔드포인트**    | `GET /api/v1/cards`                            |
| **인증 필요**     | 예                                             |
| **쿼리 파라미터** | `skip`, `limit`, `difficulty_level`, `deck_id` |
| **출력**          | 단어 카드 배열                                 |
| **상태**          | ✅ 구현 완료                                   |

### 쿼리 파라미터

| 파라미터           | 타입    | 기본값 | 최대값 | 설명                    |
| ------------------ | ------- | ------ | ------ | ----------------------- |
| `skip`             | integer | 0      | -      | 건너뛸 레코드 수        |
| `limit`            | integer | 100    | 100    | 반환할 최대 레코드 수   |
| `difficulty_level` | integer | -      | 10     | 특정 난이도만 필터      |
| `deck_id`          | integer | -      | -      | 특정 덱의 카드만 필터   |
| `cefr_level`       | string  | -      | -      | CEFR 레벨 필터          |

### 정렬 기준

기본적으로 `usage_frequency` (사용 빈도) 기준 내림차순 정렬됩니다.
자주 사용되는 단어가 먼저 표시됩니다.

### 요청/응답 예시

**요청:**

```
GET /api/v1/cards?deck_id=1&limit=10&skip=0
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
[
  {
    "id": 1,
    "english_word": "decide",
    "korean_meaning": "결정하다",
    "part_of_speech": "verb",
    "difficulty_level": 3,
    "cefr_level": "A2",
    "deck_id": 1,
    "is_verified": true
  },
  {
    "id": 2,
    "english_word": "important",
    "korean_meaning": "중요한",
    "part_of_speech": "adjective",
    "difficulty_level": 2,
    "cefr_level": "A1",
    "deck_id": 1,
    "is_verified": true
  }
]
```

### 페이지네이션 예시

```javascript
// 첫 페이지
GET /api/v1/cards?skip=0&limit=20

// 두 번째 페이지
GET /api/v1/cards?skip=20&limit=20

// 세 번째 페이지
GET /api/v1/cards?skip=40&limit=20
```

---

## US-CARD-03: 단어 카드 상세 조회

### 스토리

**사용자로서**, 특정 단어 카드의 상세 정보를 조회할 수 있다.
**그래서** 단어의 모든 정보를 확인할 수 있다.

### 상세 정보

| 항목           | 내용                                                            |
| -------------- | --------------------------------------------------------------- |
| **엔드포인트** | `GET /api/v1/cards/{card_id}`                                   |
| **인증 필요**  | 예                                                              |
| **출력**       | 영어 단어, 한국어 뜻, 발음, 품사, 정의, 예문, 난이도, CEFR 레벨 |
| **상태**       | ✅ 구현 완료                                                    |

### 사용 시나리오

1. **학습 중 상세 보기**: 카드 플립 후 추가 정보 확인
2. **복습 모드**: 틀린 단어의 상세 정보 학습
3. **검색 결과 상세**: 검색된 단어의 전체 정보 조회

### 요청/응답 예시

**요청:**

```
GET /api/v1/cards/1234
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "id": 1234,
  "english_word": "decide",
  "korean_meaning": "결정하다",
  "part_of_speech": "verb",
  "ipa_pronunciation": "/dɪˈsaɪd/",
  "english_definition": "to make a choice or come to a conclusion about something",
  "example_sentence": "She decided to study abroad.",
  "example_translation": "그녀는 유학을 가기로 결정했다.",
  "cloze_sentence": "She {{decided}} to study abroad.",
  "difficulty_level": 3,
  "cefr_level": "A2",
  "deck_id": 1,
  "usage_frequency": 450,
  "is_verified": true,
  "audio_url": "https://storage.example.com/audio/decide.mp3",
  "created_at": "2025-12-01T10:00:00Z",
  "updated_at": "2025-12-10T08:30:00Z"
}
```

**에러 응답:**

- `404 Not Found`: 해당 ID의 카드가 존재하지 않음

---

## US-CARD-04: 단어 카드 수정

### 스토리

**관리자로서**, 단어 카드 정보를 수정할 수 있다.
**그래서** 콘텐츠 오류를 수정할 수 있다.

### 상세 정보

| 항목           | 내용                            |
| -------------- | ------------------------------- |
| **엔드포인트** | `PATCH /api/v1/cards/{card_id}` |
| **인증 필요**  | 예                              |
| **입력**       | 수정할 필드 (부분 업데이트)     |
| **상태**       | ✅ 구현 완료                    |

### 수정 가능 필드

모든 카드 필드가 수정 가능합니다 (id, created_at 제외).

### 요청/응답 예시

**요청 (부분 업데이트):**

```json
PATCH /api/v1/cards/1234
{
  "korean_meaning": "결정하다, 결심하다",
  "example_sentence": "I decided to learn English.",
  "example_translation": "나는 영어를 배우기로 결심했다."
}
```

**성공 응답 (200 OK):** 업데이트된 전체 카드 정보 반환

---

## US-CARD-05: 단어 카드 삭제

### 스토리

**관리자로서**, 단어 카드를 삭제할 수 있다.
**그래서** 부적절한 콘텐츠를 제거할 수 있다.

### 상세 정보

| 항목           | 내용                             |
| -------------- | -------------------------------- |
| **엔드포인트** | `DELETE /api/v1/cards/{card_id}` |
| **인증 필요**  | 예                               |
| **상태**       | ✅ 구현 완료                     |

### 삭제 시 영향

1. **학습 진행 데이터**: 해당 카드의 모든 UserCardProgress 삭제
2. **즐겨찾기**: 해당 카드의 모든 Favorite 삭제
3. **덱 카드 수**: 소속 덱의 `card_count` 감소

### 요청/응답 예시

**요청:**

```
DELETE /api/v1/cards/1234
Authorization: Bearer {access_token}
```

**성공 응답 (204 No Content)**

**에러 응답:**

- `404 Not Found`: 해당 ID의 카드가 존재하지 않음

---

## 난이도 및 CEFR 레벨 가이드

### 난이도 레벨 (1~10)

| 레벨  | 설명                                      | 예시                    |
| ----- | ----------------------------------------- | ----------------------- |
| 1~2   | 매우 쉬운 기초 단어                       | the, is, have, go       |
| 3~4   | 기초 일상 단어                            | decide, important       |
| 5~6   | 중급 단어                                 | accomplish, significant |
| 7~8   | 고급 단어                                 | eloquent, meticulous    |
| 9~10  | 전문/학술 단어                            | epistemology, ubiquitous|

### CEFR 레벨

| 레벨 | 설명              | 어휘 수준                    |
| ---- | ----------------- | ---------------------------- |
| A1   | 입문              | 가장 기본적인 일상 표현      |
| A2   | 초급              | 간단한 일상 대화             |
| B1   | 중급              | 일반적인 주제의 명확한 표현  |
| B2   | 중상급            | 복잡한 텍스트의 주요 내용    |
| C1   | 고급              | 넓은 범위의 까다로운 텍스트  |
| C2   | 최고급            | 거의 모든 것을 쉽게 이해     |

---

## 관련 컴포넌트

### 서비스

- `src/app/services/vocabulary_card_service.py`: 카드 CRUD 로직

### 모델

- `src/app/models/tables/vocabulary_card.py`: VocabularyCard 테이블
- `src/app/models/schemas/vocabulary_card.py`: 카드 관련 스키마

### API

- `src/app/api/cards.py`: 카드 라우트 핸들러

---

## 테스트 예제

### Curl

```bash
# 토큰 발급 (로그인 후)
TOKEN="your_access_token_here"

# 카드 생성
curl -X POST http://localhost:8080/api/v1/cards \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "english_word": "decide",
    "korean_meaning": "결정하다",
    "part_of_speech": "verb",
    "ipa_pronunciation": "/dɪˈsaɪd/",
    "difficulty_level": 3,
    "cefr_level": "A2"
  }'

# 카드 목록 조회
curl -X GET "http://localhost:8080/api/v1/cards?limit=10&deck_id=1" \
  -H "Authorization: Bearer $TOKEN"

# 특정 카드 조회
curl -X GET http://localhost:8080/api/v1/cards/1234 \
  -H "Authorization: Bearer $TOKEN"

# 카드 수정
curl -X PATCH http://localhost:8080/api/v1/cards/1234 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"korean_meaning": "결정하다, 결심하다"}'

# 카드 삭제
curl -X DELETE http://localhost:8080/api/v1/cards/1234 \
  -H "Authorization: Bearer $TOKEN"
```

### Python

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"
headers = {"Authorization": "Bearer your_access_token_here"}

# 카드 생성
response = requests.post(f"{BASE_URL}/cards", headers=headers, json={
    "english_word": "decide",
    "korean_meaning": "결정하다",
    "part_of_speech": "verb",
    "difficulty_level": 3
})
card = response.json()
print(card)

# 카드 목록 조회
response = requests.get(f"{BASE_URL}/cards", headers=headers, params={
    "limit": 10,
    "deck_id": 1
})
cards = response.json()

# 카드 수정
response = requests.patch(
    f"{BASE_URL}/cards/{card['id']}",
    headers=headers,
    json={"korean_meaning": "결정하다, 결심하다"}
)

# 카드 삭제
response = requests.delete(f"{BASE_URL}/cards/{card['id']}", headers=headers)
```

---

## 관련 문서

- [덱 유저 스토리](./04-decks.md)
- [학습 진행 유저 스토리](./05-progress.md)
- [퀴즈 유저 스토리](./06-quiz.md)
