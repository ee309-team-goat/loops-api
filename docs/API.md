# API 문서 (API Documentation)

Loops API의 모든 엔드포인트와 사용법을 설명합니다.

## 📋 목차

- [기본 정보](#-기본-정보)
- [인증](#-인증)
- [사용자 (Users)](#-사용자-users)
- [단어 카드 (Vocabulary Cards)](#-단어-카드-vocabulary-cards)
- [학습 & 복습 (FSRS)](#-학습--복습-fsrs)
- [동기화 큐 (Sync Queue)](#-동기화-큐-sync-queue)
- [에러 응답](#-에러-응답)

---

## 📡 기본 정보

### Base URL

```
http://localhost:8000/api/v1
```

### 인터랙티브 문서

서버 실행 후 다음 URL에서 확인 가능:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 기본 엔드포인트

```http
GET  /              # API 루트
GET  /health        # 헬스 체크
```

---

## 🔐 인증

모든 API 엔드포인트는 JWT 토큰 기반 인증을 사용합니다 (회원가입/로그인 제외).

### 회원가입

```http
POST /api/v1/auth/register
```

**Request Body:**

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "subscription_type": "free",
  "total_cards_learned": 0,
  "total_study_time_minutes": 0,
  "current_streak": 0,
  "longest_streak": 0,
  "last_study_date": null,
  "created_at": "2025-01-20T12:00:00Z",
  "updated_at": "2025-01-20T12:00:00Z"
}
```

### 로그인

```http
POST /api/v1/auth/login
```

**Request Body (x-www-form-urlencoded):**

```
username=testuser
password=password123
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 현재 사용자 정보

```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "subscription_type": "free",
  "total_cards_learned": 10,
  "total_study_time_minutes": 120,
  "current_streak": 5,
  "longest_streak": 10,
  "last_study_date": "2025-01-20",
  "created_at": "2025-01-20T12:00:00Z",
  "updated_at": "2025-01-20T12:00:00Z"
}
```

### 인증 헤더 사용

모든 보호된 엔드포인트에는 다음 헤더를 추가해야 합니다:

```
Authorization: Bearer <your_jwt_token>
```

---

## 👤 사용자 (Users)

### 일일 학습 목표 조회

```http
GET /api/v1/users/me/daily-goal
Authorization: Bearer <token>
```

**Description:**

사용자의 일일 학습 목표와 오늘의 완료 수를 조회합니다.

**Response (200 OK):**

```json
{
  "daily_goal": 20,
  "completed_today": 12
}
```

**Response Fields:**

- `daily_goal` (int): 사용자가 설정한 하루 학습 목표 카드 수
- `completed_today` (int): 오늘 완료한 복습 카드 수

### 사용자 목록 조회

```http
GET /api/v1/users?skip=0&limit=100
Authorization: Bearer <token>
```

**Query Parameters:**

- `skip` (int, optional): 건너뛸 레코드 수 (기본값: 0)
- `limit` (int, optional): 반환할 최대 레코드 수 (기본값: 100)

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "subscription_type": "free",
    "total_cards_learned": 10,
    "current_streak": 5,
    "created_at": "2025-01-20T12:00:00Z"
  }
]
```

### 특정 사용자 조회

```http
GET /api/v1/users/{user_id}
Authorization: Bearer <token>
```

**Response (200 OK):** 사용자 객체
**Response (404 Not Found):** 사용자를 찾을 수 없음

### 사용자 정보 수정

```http
PATCH /api/v1/users/{user_id}
Authorization: Bearer <token>
```

**Request Body (선택적 필드):**

```json
{
  "email": "newemail@example.com",
  "subscription_type": "premium",
  "current_streak": 10
}
```

**Response (200 OK):** 수정된 사용자 객체

### 사용자 삭제

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <token>
```

**Response (204 No Content):** 삭제 성공

---

## 🎴 단어 카드 (Vocabulary Cards)

### 카드 생성

```http
POST /api/v1/cards
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "korean_word": "안녕하세요",
  "pronunciation": "annyeonghaseyo",
  "meaning": "Hello",
  "definition_en": "A polite greeting in Korean",
  "difficulty_level": 1,
  "cefr_level": "A1",
  "example_sentences": ["안녕하세요, 만나서 반갑습니다."],
  "synonyms": ["여보세요"],
  "usage_notes": "Formal greeting used in most situations"
}
```

**Response (201 Created):**

```json
{
  "id": 1,
  "korean_word": "안녕하세요",
  "pronunciation": "annyeonghaseyo",
  "meaning": "Hello",
  "definition_en": "A polite greeting in Korean",
  "difficulty_level": 1,
  "cefr_level": "A1",
  "example_sentences": ["안녕하세요, 만나서 반갑습니다."],
  "synonyms": ["여보세요"],
  "is_verified": false,
  "created_at": "2025-01-20T12:00:00Z",
  "updated_at": "2025-01-20T12:00:00Z"
}
```

### 카드 목록 조회

```http
GET /api/v1/cards?skip=0&limit=100&difficulty_level=1&deck_id=1
Authorization: Bearer <token>
```

**Query Parameters:**

- `skip` (int, optional): 건너뛸 레코드 수
- `limit` (int, optional): 최대 반환 레코드 수
- `difficulty_level` (int, optional): 난이도 필터 (1-10)
- `deck_id` (int, optional): 덱 ID 필터

**Response (200 OK):** 카드 배열

### 카드 검색

```http
GET /api/v1/cards/search?q=안녕
Authorization: Bearer <token>
```

**Query Parameters:**

- `q` (string, required): 검색어 (한국어 단어 또는 의미에서 검색)
- `limit` (int, optional): 최대 결과 수 (기본값: 20)

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "korean_word": "안녕하세요",
    "meaning": "Hello",
    "difficulty_level": 1
  }
]
```

### 특정 카드 조회

```http
GET /api/v1/cards/{card_id}
Authorization: Bearer <token>
```

**Response (200 OK):** 카드 객체
**Response (404 Not Found):** 카드를 찾을 수 없음

### 카드 수정

```http
PATCH /api/v1/cards/{card_id}
Authorization: Bearer <token>
```

**Request Body (선택적 필드):**

```json
{
  "meaning": "Hi, Hello",
  "difficulty_level": 2,
  "is_verified": true
}
```

**Response (200 OK):** 수정된 카드 객체

### 카드 삭제

```http
DELETE /api/v1/cards/{card_id}
Authorization: Bearer <token>
```

**Response (204 No Content):** 삭제 성공

---

## 📚 학습 & 복습 (FSRS)

### 복습 제출

```http
POST /api/v1/progress/review
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "card_id": 1,
  "rating": 3
}
```

**Rating 값:**

- `1` - Again (완전히 잊음)
- `2` - Hard (어렵게 기억)
- `3` - Good (적당히 기억)
- `4` - Easy (완벽히 기억)

**Response (200 OK):**

```json
{
  "id": 1,
  "user_id": 1,
  "card_id": 1,
  "card_state": "learning",
  "stability": 2.5,
  "difficulty": 5.0,
  "interval": 3,
  "next_review_date": "2025-01-23T12:00:00Z",
  "last_review_date": "2025-01-20T12:00:00Z",
  "total_reviews": 1,
  "correct_count": 1,
  "accuracy_rate": 100.0
}
```

### 사용자 진도 조회

```http
GET /api/v1/progress/user/{user_id}?skip=0&limit=100
Authorization: Bearer <token>
```

**Response (200 OK):** 진도 배열

### 복습 예정 카드 조회

```http
GET /api/v1/progress/user/{user_id}/due?limit=20
Authorization: Bearer <token>
```

**Query Parameters:**

- `limit` (int, optional): 최대 카드 수 (기본값: 20)

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "card_id": 1,
    "card_state": "review",
    "next_review_date": "2025-01-20T10:00:00Z",
    "interval": 5
  }
]
```

### 새 카드 조회

```http
GET /api/v1/progress/user/{user_id}/new?limit=20
Authorization: Bearer <token>
```

**Response (200 OK):** 새로운 카드 진도 배열

### 특정 진도 조회

```http
GET /api/v1/progress/{progress_id}
Authorization: Bearer <token>
```

**Response (200 OK):** 진도 객체

### 진도 수정

```http
PATCH /api/v1/progress/{progress_id}
Authorization: Bearer <token>
```

**Request Body (선택적 필드):**

```json
{
  "card_state": "review",
  "stability": 10.0
}
```

**Response (200 OK):** 수정된 진도 객체

### 진도 삭제

```http
DELETE /api/v1/progress/{progress_id}
Authorization: Bearer <token>
```

**Response (204 No Content):** 삭제 성공

---

## 🔄 동기화 큐 (Sync Queue)

### 동기화 작업 추가

```http
POST /api/v1/sync
Authorization: Bearer <token>
```

**Request Body:**

```json
{
  "user_id": 1,
  "entity_type": "card",
  "entity_id": 1,
  "operation": "update",
  "payload": {
    "field": "value"
  },
  "priority": 0
}
```

**Response (201 Created):** 동기화 큐 객체

### 대기 중인 작업 조회

```http
GET /api/v1/sync/user/{user_id}/pending
Authorization: Bearer <token>
```

**Response (200 OK):**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "entity_type": "card",
    "entity_id": 1,
    "operation": "update",
    "is_synced": false,
    "retry_count": 0,
    "created_at": "2025-01-20T12:00:00Z"
  }
]
```

### 작업 동기화 완료 표시

```http
PATCH /api/v1/sync/{queue_id}/synced
Authorization: Bearer <token>
```

**Response (200 OK):** 업데이트된 동기화 큐 객체

### 작업 삭제

```http
DELETE /api/v1/sync/{queue_id}
Authorization: Bearer <token>
```

**Response (204 No Content):** 삭제 성공

---

## ❌ 에러 응답

### 표준 에러 형식

```json
{
  "detail": "에러 메시지"
}
```

### HTTP 상태 코드

- `200 OK` - 요청 성공
- `201 Created` - 리소스 생성 성공
- `204 No Content` - 성공 (응답 본문 없음)
- `400 Bad Request` - 잘못된 요청
- `401 Unauthorized` - 인증 실패 또는 토큰 없음
- `403 Forbidden` - 권한 없음
- `404 Not Found` - 리소스를 찾을 수 없음
- `422 Unprocessable Entity` - 유효성 검증 실패
- `500 Internal Server Error` - 서버 오류

### 일반적인 에러 예시

**401 Unauthorized:**

```json
{
  "detail": "Could not validate credentials"
}
```

**404 Not Found:**

```json
{
  "detail": "User not found"
}
```

**422 Validation Error:**

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## 🧪 테스트 예제

### Curl 예제

```bash
# 회원가입
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"password123"}'

# 로그인 & 토큰 저장
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123" | jq -r .access_token)

# 현재 사용자 정보
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 카드 생성
curl -X POST http://localhost:8000/api/v1/cards \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "korean_word": "감사합니다",
    "pronunciation": "gamsahamnida",
    "meaning": "Thank you",
    "difficulty_level": 1,
    "cefr_level": "A1"
  }'

# 복습 제출
curl -X POST http://localhost:8000/api/v1/progress/review \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"card_id": 1, "rating": 3}'
```

### Python 예제

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 회원가입
response = requests.post(f"{BASE_URL}/auth/register", json={
    "username": "testuser",
    "email": "test@test.com",
    "password": "password123"
})
print(response.json())

# 로그인
response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": "testuser",
    "password": "password123"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 현재 사용자 정보
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
user = response.json()
print(user)

# 카드 목록
response = requests.get(f"{BASE_URL}/cards", headers=headers)
cards = response.json()
print(cards)

# 복습 제출
response = requests.post(
    f"{BASE_URL}/progress/review",
    headers=headers,
    json={"card_id": 1, "rating": 3}
)
result = response.json()
print(result)
```

---

## 📚 관련 문서

- [README.md](../README.md) - 프로젝트 개요
- [COMMANDS.md](./COMMANDS.md) - 명령어 레퍼런스
- [DATABASE.md](./DATABASE.md) - 데이터베이스 상세 정보
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결 가이드
