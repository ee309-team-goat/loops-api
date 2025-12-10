# 덱 (Decks) 유저 스토리

> 단어장(덱) 관리 및 학습 덱 선택
>
> 최종 업데이트: 2025-12-10

---

## 개요

덱 도메인은 단어 카드를 그룹화하여 체계적인 학습을 가능하게 합니다.
사용자는 공개 덱을 선택하거나, 특정 덱만 골라서 학습할 수 있습니다.

### 주요 특징

- **주제별 분류**: 단어를 주제, 난이도, 목적별로 그룹화
- **공개/비공개**: 공식 공개 덱과 사용자 개인 덱 구분
- **선택적 학습**: 원하는 덱만 선택하여 맞춤 학습
- **진행률 추적**: 덱별 학습 진행 상황 확인

### 덱 데이터 구조

```
Deck
├── 기본 정보
│   ├── id (정수, 자동 증가)
│   ├── name (덱 이름)
│   ├── description (설명)
│   └── creator_id (생성자 프로필 ID)
├── 설정
│   ├── is_public (공개 여부)
│   └── is_official (공식 덱 여부)
├── 통계
│   ├── card_count (총 카드 수)
│   └── learning_count (학습 중인 사용자 수)
└── 타임스탬프
    ├── created_at
    └── updated_at
```

### 덱 접근 권한

| 덱 유형       | 조회 | 학습 | 수정 | 삭제 |
| ------------- | ---- | ---- | ---- | ---- |
| 공개 덱       | 모두 | 모두 | 생성자만 | 생성자만 |
| 비공개 덱     | 생성자만 | 생성자만 | 생성자만 | 생성자만 |
| 공식 덱       | 모두 | 모두 | 관리자만 | 관리자만 |

---

## US-DECK-01: 덱 목록 조회

### 스토리

**사용자로서**, 접근 가능한 덱 목록을 학습 진행 정보와 함께 조회할 수 있다.
**그래서** 학습할 덱을 선택할 수 있다.

### 상세 정보

| 항목              | 내용                                                        |
| ----------------- | ----------------------------------------------------------- |
| **엔드포인트**    | `GET /api/v1/decks`                                         |
| **인증 필요**     | 예                                                          |
| **쿼리 파라미터** | `skip`, `limit`                                             |
| **출력**          | 덱 목록 (이름, 설명, 총 카드 수, 진행률), 페이지네이션 정보 |
| **상태**          | ✅ 구현 완료                                                |

### 접근 가능한 덱 조건

사용자가 조회할 수 있는 덱:
1. **공개 덱** (`is_public: true`)
2. **본인이 생성한 덱** (비공개 포함)

### 반환 데이터 상세

| 필드                | 타입    | 설명                          |
| ------------------- | ------- | ----------------------------- |
| `id`                | integer | 덱 ID                         |
| `name`              | string  | 덱 이름                       |
| `description`       | string  | 덱 설명                       |
| `card_count`        | integer | 총 카드 수                    |
| `is_public`         | boolean | 공개 여부                     |
| `is_official`       | boolean | 공식 덱 여부                  |
| `progress`          | object  | 사용자의 학습 진행 정보       |
| `progress.total`    | integer | 덱의 총 카드 수               |
| `progress.learned`  | integer | 학습 완료한 카드 수           |
| `progress.learning` | integer | 학습 중인 카드 수             |
| `progress.new`      | integer | 아직 학습 안 한 카드 수       |
| `progress.percentage` | float | 진행률 (%)                   |

### 요청/응답 예시

**요청:**

```
GET /api/v1/decks?skip=0&limit=20
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "items": [
    {
      "id": 1,
      "name": "TOEIC 필수 단어 800",
      "description": "TOEIC 시험에 자주 출제되는 필수 단어 800개",
      "card_count": 800,
      "is_public": true,
      "is_official": true,
      "progress": {
        "total": 800,
        "learned": 150,
        "learning": 50,
        "new": 600,
        "percentage": 18.75
      }
    },
    {
      "id": 2,
      "name": "일상 회화 기초",
      "description": "일상생활에서 자주 사용하는 기초 표현",
      "card_count": 300,
      "is_public": true,
      "is_official": true,
      "progress": {
        "total": 300,
        "learned": 0,
        "learning": 0,
        "new": 300,
        "percentage": 0.0
      }
    }
  ],
  "total": 15,
  "skip": 0,
  "limit": 20
}
```

### UI 활용 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 TOEIC 필수 단어 800          [공식]
   TOEIC 시험에 자주 출제되는 필수 단어
   [██████░░░░░░░░░░░░░░] 18.75%
   800 단어 중 150개 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## US-DECK-02: 덱 상세 조회

### 스토리

**사용자로서**, 특정 덱의 상세 정보와 학습 진행 상황을 조회할 수 있다.
**그래서** 덱의 세부 내용을 파악할 수 있다.

### 상세 정보

| 항목           | 내용                                 |
| -------------- | ------------------------------------ |
| **엔드포인트** | `GET /api/v1/decks/{deck_id}`        |
| **인증 필요**  | 예                                   |
| **출력**       | 덱 기본 정보, 카드 정보, 학습 진행률 |
| **상태**       | ✅ 구현 완료                         |

### 반환 데이터 상세

목록 조회의 모든 필드에 추가:

| 필드                     | 타입     | 설명                      |
| ------------------------ | -------- | ------------------------- |
| `creator_id`             | UUID     | 생성자 프로필 ID          |
| `created_at`             | datetime | 생성일                    |
| `updated_at`             | datetime | 수정일                    |
| `cards_by_level`         | object   | CEFR 레벨별 카드 수       |
| `cards_by_difficulty`    | object   | 난이도별 카드 수          |

### 요청/응답 예시

**요청:**

```
GET /api/v1/decks/1
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "id": 1,
  "name": "TOEIC 필수 단어 800",
  "description": "TOEIC 시험에 자주 출제되는 필수 단어 800개. 파트별로 분류되어 있으며 최신 출제 경향을 반영했습니다.",
  "card_count": 800,
  "is_public": true,
  "is_official": true,
  "creator_id": null,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-12-01T10:00:00Z",
  "progress": {
    "total": 800,
    "learned": 150,
    "learning": 50,
    "new": 600,
    "percentage": 18.75
  },
  "cards_by_level": {
    "A1": 100,
    "A2": 200,
    "B1": 300,
    "B2": 150,
    "C1": 50,
    "C2": 0
  },
  "cards_by_difficulty": {
    "1-3": 200,
    "4-6": 400,
    "7-10": 200
  }
}
```

**에러 응답:**

- `403 Forbidden`: 비공개 덱에 접근 권한이 없음
- `404 Not Found`: 해당 ID의 덱이 존재하지 않음

---

## US-DECK-03: 학습 덱 선택 설정

### 스토리

**사용자로서**, 학습에 사용할 덱을 설정할 수 있다.
**그래서** 원하는 덱에서만 학습할 수 있다.

### 상세 정보

| 항목           | 내용                                                          |
| -------------- | ------------------------------------------------------------- |
| **엔드포인트** | `PUT /api/v1/decks/selected-decks`                            |
| **인증 필요**  | 예                                                            |
| **입력**       | `select_all` (전체 선택 여부), `deck_ids` (선택할 덱 ID 목록) |
| **상태**       | ✅ 구현 완료                                                  |

### 설정 모드

#### 1. 전체 덱 학습 모드

```json
{
  "select_all": true
}
```
- 모든 공개 덱에서 카드 학습
- `deck_ids`는 무시됨
- 새로운 공개 덱이 추가되면 자동으로 학습 범위에 포함

#### 2. 선택 덱 학습 모드

```json
{
  "select_all": false,
  "deck_ids": [1, 2, 5]
}
```
- 지정한 덱에서만 카드 학습
- 최소 1개 이상의 덱 선택 필요
- 비공개 덱은 본인 것만 선택 가능

### 비즈니스 규칙

1. **덱 유효성 검사**: 선택한 덱 ID가 모두 유효하고 접근 가능해야 함
2. **자동 프로필 업데이트**: `select_all` 값이 프로필에 반영
3. **기존 선택 대체**: 새 설정이 기존 설정을 완전히 대체

### 요청/응답 예시

**요청 (선택 모드):**

```json
PUT /api/v1/decks/selected-decks
{
  "select_all": false,
  "deck_ids": [1, 3, 5]
}
```

**성공 응답 (200 OK):**

```json
{
  "message": "Successfully updated selected decks",
  "select_all": false,
  "selected_deck_ids": [1, 3, 5],
  "total_cards": 1500
}
```

**에러 응답:**

- `400 Bad Request`: `select_all: false`인데 `deck_ids`가 비어있음
- `403 Forbidden`: 선택한 덱 중 접근 권한이 없는 덱 존재
- `404 Not Found`: 존재하지 않는 덱 ID 포함

---

## US-DECK-04: 선택된 덱 조회

### 스토리

**사용자로서**, 현재 학습에 사용하도록 설정된 덱 목록을 조회할 수 있다.
**그래서** 현재 학습 범위를 확인할 수 있다.

### 상세 정보

| 항목           | 내용                                            |
| -------------- | ----------------------------------------------- |
| **엔드포인트** | `GET /api/v1/decks/selected-decks`              |
| **인증 필요**  | 예                                              |
| **출력**       | 전체 선택 여부, 선택된 덱 ID 목록, 덱 상세 정보 |
| **상태**       | ✅ 구현 완료                                    |

### 반환 데이터

| 필드           | 타입      | 설명                                |
| -------------- | --------- | ----------------------------------- |
| `select_all`   | boolean   | 전체 덱 선택 여부                   |
| `deck_ids`     | integer[] | 선택된 덱 ID 목록                   |
| `decks`        | object[]  | 선택된 덱들의 상세 정보             |
| `total_cards`  | integer   | 선택된 덱들의 총 카드 수            |
| `total_due`    | integer   | 오늘 복습 예정인 카드 수            |
| `total_new`    | integer   | 새로 학습할 수 있는 카드 수         |

### 요청/응답 예시

**요청:**

```
GET /api/v1/decks/selected-decks
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "select_all": false,
  "deck_ids": [1, 3, 5],
  "decks": [
    {
      "id": 1,
      "name": "TOEIC 필수 단어 800",
      "card_count": 800,
      "progress_percentage": 18.75
    },
    {
      "id": 3,
      "name": "비즈니스 영어",
      "card_count": 400,
      "progress_percentage": 5.0
    },
    {
      "id": 5,
      "name": "일상 회화",
      "card_count": 300,
      "progress_percentage": 0.0
    }
  ],
  "total_cards": 1500,
  "total_due": 45,
  "total_new": 1200
}
```

---

## 덱 선택과 학습 흐름

### 시나리오 1: 처음 시작하는 사용자

```
1. 회원가입 완료 → select_all: true (기본값)
2. 덱 목록 조회 → 모든 공개 덱 표시
3. 학습 시작 → 모든 덱에서 카드 가져오기
```

### 시나리오 2: 특정 덱만 학습하고 싶은 사용자

```
1. 덱 목록 조회 → 관심있는 덱 확인
2. 덱 선택 설정 → select_all: false, deck_ids: [1, 5]
3. 학습 시작 → 선택한 덱에서만 카드 가져오기
```

### 시나리오 3: 새 덱 추가 후 학습 범위 변경

```
1. 현재 설정: deck_ids: [1, 5]
2. 새 덱 발견 → deck_id: 10
3. 덱 선택 설정 → deck_ids: [1, 5, 10]
4. 학습 시작 → 3개 덱에서 카드 가져오기
```

---

## 관련 컴포넌트

### 서비스

- `src/app/services/deck_service.py`: 덱 관련 비즈니스 로직

### 모델

- `src/app/models/tables/deck.py`: Deck 테이블
- `src/app/models/tables/user_selected_deck.py`: UserSelectedDeck 테이블
- `src/app/models/schemas/deck.py`: 덱 관련 스키마
- `src/app/models/schemas/user_selected_deck.py`: 덱 선택 스키마

### API

- `src/app/api/decks.py`: 덱 라우트 핸들러

---

## 관련 문서

- [단어 카드 유저 스토리](./03-vocabulary-cards.md)
- [학습 진행 유저 스토리](./05-progress.md)
- [학습 세션 유저 스토리](./08-study-session.md)
