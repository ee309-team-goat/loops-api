# Loops API 개발 로드맵

## ✅ 완료된 작업

### Phase 1: 데이터베이스 모델 구현 (100% 완료)

#### 기존 모델 업데이트
- [x] **User 모델** - 구독 타입, 학습 통계 필드 추가
  - `SubscriptionTypeEnum` (free/premium/enterprise)
  - `total_cards_learned`, `total_study_time_minutes`
  - `last_study_date` 타입 변경 (datetime → date)

- [x] **VocabularyCard 모델** - 상세 정보 필드 확장
  - 새 필드: `definition_en`, `cefr_level`, `usage_notes`, `etymology`, `is_verified`
  - 새 JSONB 필드: `synonyms`, `antonyms`, `collocations`
  - `deck_id` FK 연결

- [x] **UserCardProgress 모델** - FSRS 통계 강화
  - 새 필드: `scheduled_days`, `wrong_count`, `accuracy_rate`, `average_response_time`
  - 마일스톤: `first_studied_at`, `mastered_at`
  - `reps_since_lapse` 추가

- [x] **SyncQueue 모델** - 동기화 로직 개선
  - `is_synced` 타입 변경 (int → boolean)
  - 우선순위 시스템: `priority`, `last_retry_at`

#### 신규 모델 생성
- [x] **Deck** - 덱 관리 시스템
- [x] **UserDeck** - 사용자-덱 관계 테이블
- [x] **StudySession** - 학습 세션 추적
- [x] **AIInteraction** - AI 상호작용 로깅

#### 인프라
- [x] 모든 모델 `__init__.py`에 등록
- [x] ENUM 타입 정의 (SubscriptionType, CardState, OperationType)
- [x] Foreign Key 관계 설정
- [x] 인덱스 정의

---

## 📋 다음 단계

### Phase 2: 데이터베이스 마이그레이션 (우선순위: 🔴 높음)

#### 2.1 마이그레이션 준비
```bash
# 1. 데이터베이스 실행
docker-compose up -d

# 2. .env 파일 확인
# DATABASE_URL이 올바른지 확인
```

#### 2.2 마이그레이션 생성 및 실행
```bash
# 3. 마이그레이션 파일 자동 생성
uv run alembic revision --autogenerate -m "update schema to match loops.sql"

# 4. 생성된 마이그레이션 파일 검토
# src/alembic/versions/[timestamp]_update_schema_to_match_loops_sql.py 확인

# 5. 마이그레이션 적용
uv run alembic upgrade head

# 6. 데이터베이스 검증
# PostgreSQL 접속해서 테이블 구조 확인
```

#### 2.3 주의사항
- ⚠️ `User.last_study_date` 타입이 TIMESTAMP → DATE로 변경됨
- ⚠️ `SyncQueue.is_synced` 타입이 INTEGER → BOOLEAN으로 변경됨
- ⚠️ 기존 데이터가 있다면 데이터 마이그레이션 전략 필요

---

### Phase 3: 서비스 레이어 업데이트 (우선순위: 🔴 높음)

#### 3.1 기존 서비스 수정 필요

**SyncQueueService 수정** (`src/app/services/sync_queue_service.py`)
```python
# 변경 전: is_synced = 1
# 변경 후: is_synced = True

# 수정 필요한 메서드:
- mark_synced()      # is_synced = True
- mark_failed()      # is_synced = False + 별도 상태 관리 고려
- get_pending_operations()  # is_synced == False
```

**UserService 업데이트** (선택사항)
```python
# total_cards_learned 증가 로직
# total_study_time_minutes 업데이트 로직
```

#### 3.2 신규 서비스 생성 (우선순위: 🟡 중간)

다음 서비스들은 필요할 때 생성:

1. **DeckService** (`src/app/services/deck_service.py`)
   - CRUD 작업
   - 공개/비공개 덱 필터링
   - 인기 덱 조회

2. **UserDeckService** (`src/app/services/user_deck_service.py`)
   - 사용자의 활성 덱 관리
   - 진행률 계산
   - 덱별 카드 상태 집계

3. **StudySessionService** (`src/app/services/study_session_service.py`)
   - 세션 생성/종료
   - 통계 계산
   - 일일/주간/월간 리포트

4. **AIInteractionService** (`src/app/services/ai_interaction_service.py`)
   - 상호작용 로깅
   - 토큰 사용량 추적
   - 비용 분석

---

### Phase 4: API 엔드포인트 추가 (우선순위: 🟡 중간)

#### 4.1 신규 엔드포인트 구현

**Deck 관련** (`src/app/api/routes.py`)
```
POST   /api/v1/decks              # 덱 생성
GET    /api/v1/decks              # 덱 목록 (공개/비공개 필터)
GET    /api/v1/decks/{deck_id}    # 덱 상세
PATCH  /api/v1/decks/{deck_id}    # 덱 수정
DELETE /api/v1/decks/{deck_id}    # 덱 삭제
GET    /api/v1/decks/public       # 공개 덱 목록
GET    /api/v1/decks/official     # 공식 덱 목록
```

**UserDeck 관련**
```
POST   /api/v1/my/decks                    # 덱 구독
GET    /api/v1/my/decks                    # 내 덱 목록
GET    /api/v1/my/decks/{deck_id}/stats    # 덱별 통계
PATCH  /api/v1/my/decks/{deck_id}          # 덱 설정 변경
DELETE /api/v1/my/decks/{deck_id}          # 덱 구독 취소
```

**StudySession 관련**
```
POST   /api/v1/sessions/start    # 세션 시작
PATCH  /api/v1/sessions/{id}/end # 세션 종료
GET    /api/v1/sessions/today    # 오늘 세션 통계
GET    /api/v1/sessions/history  # 세션 히스토리
GET    /api/v1/sessions/stats    # 전체 통계
```

**AIInteraction 관련**
```
POST   /api/v1/ai/interact       # AI 상호작용
GET    /api/v1/ai/history        # 상호작용 기록
POST   /api/v1/ai/feedback       # 피드백 제출
GET    /api/v1/ai/usage          # 사용량 통계
```

---

### Phase 5: 데이터 시딩 업데이트 (우선순위: 🟢 낮음)

#### 5.1 시드 스크립트 확장 (`src/scripts/seed_data.py`)

추가할 샘플 데이터:
```python
# 덱 샘플 데이터
- 공식 덱: "TOEIC 필수 단어", "비즈니스 영어", "일상 회화"
- 난이도별 덱

# UserDeck 관계
- 테스트 유저들의 덱 구독 관계

# StudySession 샘플
- 최근 7일간의 학습 세션 데이터

# AIInteraction 샘플
- 예문 생성, 발음 체크 등 상호작용 예시
```

---

### Phase 6: 기능 개선 (우선순위: 🟢 낮음)

#### 6.1 덱 시스템 고도화
- [ ] 덱 공유 기능
- [ ] 덱 복사 기능
- [ ] 덱 병합 기능
- [ ] 커뮤니티 덱 랭킹

#### 6.2 학습 분석 강화
- [ ] 학습 패턴 분석
- [ ] 취약 단어 자동 감지
- [ ] 맞춤형 복습 제안
- [ ] 학습 시간대 분석

#### 6.3 AI 기능 확장
- [ ] 실시간 발음 평가
- [ ] 컨텍스트별 예문 생성
- [ ] 어려운 단어 설명
- [ ] 연어 표현 추천

#### 6.4 통계 대시보드
- [ ] 일일 학습 리포트
- [ ] 주간/월간 통계
- [ ] 목표 달성률 추적
- [ ] 다른 사용자와 비교

---

## 🎯 즉시 실행 가능한 다음 작업

### 1단계: 마이그레이션 (필수)
```bash
docker-compose up -d
uv run alembic revision --autogenerate -m "update schema to match loops.sql"
uv run alembic upgrade head
```

### 2단계: SyncQueueService 수정 (필수)
- `is_synced` 관련 로직 boolean으로 변경

### 3단계: 테스트 (필수)
```bash
# 기존 엔드포인트 동작 확인
curl http://localhost:8000/api/v1/auth/register
curl http://localhost:8000/api/v1/cards
```

### 4단계: 신규 기능 구현 (선택)
- 필요한 서비스부터 하나씩 구현
- 우선순위: Deck → UserDeck → StudySession → AIInteraction

---

## 📊 진행 상황 요약

| 단계 | 작업 | 상태 | 우선순위 |
|------|------|------|----------|
| Phase 1 | 모델 구현 | ✅ 100% | - |
| Phase 2 | DB 마이그레이션 | ⏳ 대기중 | 🔴 높음 |
| Phase 3 | 서비스 업데이트 | ⏳ 대기중 | 🔴 높음 |
| Phase 4 | API 엔드포인트 | ⏳ 대기중 | 🟡 중간 |
| Phase 5 | 데이터 시딩 | ⏳ 대기중 | 🟢 낮음 |
| Phase 6 | 기능 개선 | 📋 계획 | 🟢 낮음 |

---

## 💡 참고사항

### 기존 기능 유지
다음 기능들은 그대로 사용 가능:
- ✅ 사용자 인증 (JWT)
- ✅ 단어 카드 CRUD
- ✅ FSRS 기반 복습 시스템
- ✅ 학습 진도 추적
- ✅ 동기화 큐

### 호환성 주의
- `User.last_study_date` 사용 코드 확인 필요 (datetime → date)
- `SyncQueue.is_synced` 사용 코드 수정 필요 (int → bool)

### 개발 우선순위 제안
1. 🔴 마이그레이션 + SyncQueueService 수정 → **즉시 필요**
2. 🟡 Deck + UserDeck 시스템 → **핵심 기능**
3. 🟡 StudySession 추적 → **분석 기능**
4. 🟢 AIInteraction → **부가 기능**
