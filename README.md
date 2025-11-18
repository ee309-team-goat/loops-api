# Loops API - AI 기반 영단어 학습 시스템

FSRS(Free Spaced Repetition Scheduler) 알고리즘을 활용한 AI 기반 영단어 학습 백엔드 API

## 📋 목차

- [프로젝트 소개](#-프로젝트-소개)
- [주요 기능](#-주요-기능)
- [기술 스택](#-기술-스택)
- [빠른 시작](#-빠른-시작)
- [프로젝트 구조](#-프로젝트-구조)
- [API 문서](#-api-문서)
- [개발 가이드](#-개발-가이드)
- [데이터베이스](#-데이터베이스)
- [배포](#-배포)

---

## 🎯 프로젝트 소개

Loops API는 과학적으로 검증된 FSRS 알고리즘을 활용하여 최적의 복습 주기를 제공하는 영단어 학습 플랫폼의 백엔드입니다.

### 핵심 특징

- 🧠 **FSRS 알고리즘**: 전통적인 SM-2를 넘어선 현대적 간격 반복 시스템
- 🔐 **JWT 인증**: 안전한 토큰 기반 사용자 인증
- 📊 **상세한 학습 분석**: 실시간 진도 추적 및 통계
- 🎴 **덱 시스템**: 주제별, 난이도별 단어장 관리
- 🤖 **AI 상호작용**: AI 기반 예문 생성 및 발음 체크
- 📱 **오프라인 동기화**: 동기화 큐를 통한 오프라인 학습 지원

---

## ✨ 주요 기능

### 사용자 관리

- 회원가입 / 로그인 (JWT)
- 구독 관리 (Free/Premium/Enterprise)
- 학습 연속 일수(Streak) 추적
- 학습 통계 및 진도 관리

### 단어 학습

- FSRS 기반 최적 복습 주기 계산
- 4단계 난이도 평가 (Again/Hard/Good/Easy)
- 학습 상태 추적 (New/Learning/Review/Relearning)
- 단어별 상세 정보 (발음, 예문, 유의어, 반의어, 어원)

### 덱(Deck) 시스템

- 공식 덱 / 사용자 생성 덱
- 덱별 학습 진행률 추적
- 공개 덱 공유 기능

### 학습 세션

- 세션별 학습 기록
- 정답률, 응답 시간 분석
- 일/주/월 학습 통계

### AI 기능

- 컨텍스트별 예문 생성
- 발음 체크 및 피드백
- 단어 설명 및 사용법 안내

---

## 🛠 기술 스택

### Core

- **FastAPI** 0.104+ - 고성능 비동기 웹 프레임워크
- **Python** 3.12+ - 최신 Python 기능 활용
- **UV** - 초고속 패키지 매니저

### Database

- **PostgreSQL** 16+ - 메인 데이터베이스
- **SQLModel** - SQLAlchemy + Pydantic 통합 ORM
- **Alembic** - 데이터베이스 마이그레이션
- **asyncpg** - 비동기 PostgreSQL 드라이버

### Authentication & Security

- **python-jose** - JWT 토큰 처리
- **passlib[bcrypt]** - 비밀번호 해싱

### Machine Learning

- **FSRS** 6.3.0 - 간격 반복 학습 알고리즘

### Development

- **Docker** & **Docker Compose** - 컨테이너화
- **Just** - 작업 러너
- **Pydantic Settings** - 환경 설정 관리

---

## 🚀 빠른 시작

### 1. 사전 요구사항

```bash
# UV 설치 (필수)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Just 설치 (권장)
brew install just  # macOS
```

### 2. 프로젝트 설정

```bash
# 저장소 클론
git clone <repository-url>
cd loops-api

# 의존성 설치
uv sync

# 환경 변수 설정
cp .env.example .env
# .env 파일에서 SECRET_KEY 설정 필요!
```

### 3. 데이터베이스 설정

**옵션 A: Docker Compose (권장)**

```bash
# PostgreSQL 포함 전체 스택 실행
docker-compose up -d

# 마이그레이션 실행
uv run alembic upgrade head

# 샘플 데이터 시딩
uv run python src/scripts/seed_data.py
```

**옵션 B: 로컬 PostgreSQL**

```bash
# PostgreSQL 설치 후 데이터베이스 생성
createdb loops

# .env에서 DATABASE_URL 수정
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loops

# 마이그레이션 실행
uv run alembic upgrade head
```

### 4. 애플리케이션 실행

```bash
# 개발 서버 시작 (auto-reload)
just dev
# 또는
uv run python src/main.py
```

### 5. API 테스트

```bash
# 브라우저에서 Swagger UI 접속
open http://localhost:8000/docs

# 또는 curl로 테스트
curl http://localhost:8000/health
```

---

## 📁 프로젝트 구조

```
loops-api/
├── src/
│   ├── alembic/                    # 데이터베이스 마이그레이션
│   │   ├── versions/               # 마이그레이션 파일들
│   │   └── env.py                  # Alembic 설정
│   │
│   ├── app/
│   │   ├── core/                   # 핵심 유틸리티
│   │   │   ├── security.py         # JWT, 비밀번호 해싱
│   │   │   └── dependencies.py     # FastAPI 의존성
│   │   │
│   │   ├── models/                 # 데이터베이스 모델 (8개)
│   │   │   ├── user.py             # 사용자
│   │   │   ├── vocabulary_card.py  # 단어 카드
│   │   │   ├── user_card_progress.py  # 학습 진도 (FSRS)
│   │   │   ├── deck.py             # 덱
│   │   │   ├── user_deck.py        # 사용자-덱 관계
│   │   │   ├── study_session.py    # 학습 세션
│   │   │   ├── ai_interaction.py   # AI 상호작용
│   │   │   └── sync_queue.py       # 동기화 큐
│   │   │
│   │   ├── services/               # 비즈니스 로직
│   │   │   ├── user_service.py
│   │   │   ├── vocabulary_card_service.py
│   │   │   ├── user_card_progress_service.py  # FSRS 통합
│   │   │   └── sync_queue_service.py
│   │   │
│   │   ├── api/                    # API 엔드포인트
│   │   │   ├── auth.py             # 인증 (회원가입/로그인)
│   │   │   └── routes.py           # 메인 라우터
│   │   │
│   │   ├── main.py                 # FastAPI 앱
│   │   ├── config.py               # 설정
│   │   └── database.py             # DB 연결
│   │
│   ├── scripts/                    # 유틸리티 스크립트
│   │   └── seed_data.py            # 샘플 데이터 시딩
│   │
│   └── main.py                     # 진입점
│
├── docs/
│   ├── ROADMAP_KR.md              # 개발 로드맵
│   └── ...
│
├── .env.example                    # 환경 변수 템플릿
├── docker-compose.yaml             # Docker 설정
├── pyproject.toml                  # 프로젝트 메타데이터
├── CLAUDE.md                       # AI 협업 가이드
└── README.md                       # 이 문서
```

---

## 📚 API 문서

### 기본 엔드포인트

```
GET  /              # API 루트
GET  /health        # 헬스 체크
GET  /docs          # Swagger UI
GET  /redoc         # ReDoc
```

### 인증 (Authentication)

```
POST /api/v1/auth/register    # 회원가입
POST /api/v1/auth/login       # 로그인 (JWT 토큰 반환)
GET  /api/v1/auth/me          # 현재 사용자 정보
```

### 사용자 (Users)

```
GET    /api/v1/users/me          # 내 프로필
GET    /api/v1/users             # 사용자 목록
GET    /api/v1/users/{id}        # 사용자 조회
PATCH  /api/v1/users/{id}        # 사용자 수정
DELETE /api/v1/users/{id}        # 사용자 삭제
```

### 단어 카드 (Vocabulary Cards)

```
POST   /api/v1/cards                 # 카드 생성
GET    /api/v1/cards                 # 카드 목록 (필터: difficulty, deck_id)
GET    /api/v1/cards/search?q=word   # 카드 검색
GET    /api/v1/cards/{id}            # 카드 조회
PATCH  /api/v1/cards/{id}            # 카드 수정
DELETE /api/v1/cards/{id}            # 카드 삭제
```

### 학습 & 복습 (FSRS)

```
POST /api/v1/progress/review      # 복습 제출 (rating: 1-4)
GET  /api/v1/progress/due         # 복습 예정 카드
GET  /api/v1/progress/new         # 새 카드
GET  /api/v1/progress/statistics  # 학습 통계
GET  /api/v1/progress/{card_id}   # 카드별 진도
```

**Rating 값:**

- `1` - Again (완전히 잊음)
- `2` - Hard (어렵게 기억)
- `3` - Good (적당히 기억)
- `4` - Easy (완벽히 기억)

### 동기화 큐 (Sync Queue)

```
POST   /api/v1/sync           # 동기화 작업 추가
GET    /api/v1/sync/pending   # 대기 중인 작업
GET    /api/v1/sync/failed    # 실패한 작업
PATCH  /api/v1/sync/{id}      # 작업 상태 업데이트
DELETE /api/v1/sync/{id}      # 작업 삭제
```

---

## 👨‍💻 개발 가이드

### 환경 변수 설정

`.env` 파일 필수 설정:

```bash
# 데이터베이스
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loops

# JWT (보안!)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 개발 설정
DEBUG=True
ALLOWED_ORIGINS=*
```

**🔐 중요**: `SECRET_KEY`는 반드시 변경하세요!

```bash
# 안전한 키 생성
openssl rand -hex 32
```

### Just 명령어

```bash
# 개발
just dev              # 개발 서버 시작
just health           # API 헬스 체크

# 데이터베이스
just migrate          # 마이그레이션 적용
just rollback         # 마이그레이션 롤백
just revision "msg"   # 새 마이그레이션 생성
just history          # 마이그레이션 히스토리

# Docker
just docker-up        # Docker 시작
just docker-down      # Docker 중지
just docker-logs      # 로그 보기

# 유틸리티
just clean            # 캐시 정리
just check            # 전체 헬스 체크
```

### 새 엔티티 추가하기

1. **모델 생성** (`src/app/models/your_entity.py`)

   ```python
   from sqlmodel import Field, SQLModel
   from app.models.base import TimestampMixin

   class YourEntityBase(SQLModel):
       name: str = Field(max_length=255)

   class YourEntity(YourEntityBase, TimestampMixin, table=True):
       __tablename__ = "your_entities"
       id: Optional[int] = Field(default=None, primary_key=True)

   class YourEntityCreate(YourEntityBase):
       pass

   class YourEntityRead(YourEntityBase):
       id: int
       created_at: datetime
   ```

2. **모델 등록** (`src/app/models/__init__.py`)

   ```python
   from app.models.your_entity import YourEntity, YourEntityCreate, YourEntityRead

   __all__ = [..., "YourEntity", "YourEntityCreate", "YourEntityRead"]
   ```

3. **서비스 생성** (`src/app/services/your_entity_service.py`)

   ```python
   class YourEntityService:
       @staticmethod
       async def create_entity(session: AsyncSession, data: YourEntityCreate):
           entity = YourEntity(**data.model_dump())
           session.add(entity)
           await session.commit()
           await session.refresh(entity)
           return entity
   ```

4. **라우트 추가** (`src/app/api/routes.py`)

   ```python
   @router.post("/entities", response_model=YourEntityRead)
   async def create_entity(
       data: YourEntityCreate,
       session: Annotated[AsyncSession, Depends(get_session)],
       current_user: CurrentActiveUser,
   ):
       return await YourEntityService.create_entity(session, data)
   ```

5. **마이그레이션**
   ```bash
   just revision "add your_entity"
   just migrate
   ```

### 테스트

```bash
# API 테스트
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","username":"testuser","password":"password123"}'

# 로그인
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=testuser&password=password123"

# 인증이 필요한 요청
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## 🗄 데이터베이스

### 스키마

현재 8개의 주요 테이블:

1. **users** - 사용자 정보, 구독, 학습 통계
2. **vocabulary_cards** - 단어 정보, 예문, 난이도
3. **user_card_progress** - FSRS 기반 학습 진도
4. **decks** - 덱(단어장) 관리
5. **user_decks** - 사용자-덱 관계
6. **study_sessions** - 학습 세션 기록
7. **ai_interactions** - AI 상호작용 로그
8. **sync_queue** - 오프라인 동기화 큐

### 마이그레이션

```bash
# 새 마이그레이션 생성 (모델 변경 후)
uv run alembic revision --autogenerate -m "description"

# 마이그레이션 적용
uv run alembic upgrade head

# 마이그레이션 롤백
uv run alembic downgrade -1

# 히스토리 확인
uv run alembic history
```

### Supabase 사용

```bash
# Supabase 프로젝트 생성 후
# Project Settings > Database에서 연결 문자열 복사

# .env에 설정
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres

# 마이그레이션 실행
uv run alembic upgrade head
```

---

## 🚢 배포

### Docker로 배포

```bash
# 이미지 빌드
docker-compose build

# 프로덕션 실행
docker-compose up -d

# 마이그레이션
docker-compose exec api uv run alembic upgrade head

# 로그 확인
docker-compose logs -f api
```

### 환경 변수 (프로덕션)

프로덕션 환경에서는 반드시:

```bash
DEBUG=False
SECRET_KEY=<안전한-랜덤-키>
DATABASE_URL=<프로덕션-DB-URL>
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 📖 추가 문서

- **[ROADMAP_KR.md](./ROADMAP_KR.md)** - 개발 로드맵 및 우선순위
- **[CLAUDE.md](./CLAUDE.md)** - AI 협업 가이드 및 코드 컨벤션
- **[src/scripts/README.md](./src/scripts/README.md)** - 스크립트 사용법

---

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 라이선스

MIT License

---

## 💬 문의

프로젝트 관련 문의사항은 이슈로 등록해주세요.

**Happy Coding! 🚀**
