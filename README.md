# Loops API - AI 기반 영어 학습 시스템

FSRS(Free Spaced Repetition Scheduler) 알고리즘을 활용한 AI 기반 영어 학습 백엔드 API

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL 16+](https://img.shields.io/badge/PostgreSQL-16+-blue.svg)](https://www.postgresql.org/)

---

## 🎯 프로젝트 소개

Loops API는 과학적으로 검증된 FSRS 알고리즘을 활용하여 최적의 복습 주기를 제공하는 영어 학습 플랫폼의 백엔드입니다.

### 핵심 특징

- 🧠 **FSRS 알고리즘**: 전통적인 SM-2를 넘어선 현대적 간격 반복 시스템
- 🔐 **JWT 인증**: 안전한 토큰 기반 사용자 인증
- 📊 **상세한 학습 분석**: 실시간 진도 추적 및 통계
- 🎴 **덱 시스템**: 주제별, 난이도별 단어장 관리
- 🤖 **AI 상호작용**: AI 기반 예문 생성 및 발음 체크
- 📱 **오프라인 동기화**: 동기화 큐를 통한 오프라인 학습 지원

---

## 🛠 기술 스택

**Core**

- FastAPI 0.104+ - 고성능 비동기 웹 프레임워크
- Python 3.12+ - 최신 Python 기능 활용
- UV - 초고속 패키지 매니저

**Database**

- PostgreSQL 16+ - 메인 데이터베이스
- SQLModel - SQLAlchemy + Pydantic 통합 ORM
- Alembic - 데이터베이스 마이그레이션

**Security**

- python-jose - JWT 토큰 처리
- passlib[bcrypt] - 비밀번호 해싱

**ML & AI**

- FSRS 6.3.0 - 간격 반복 학습 알고리즘
- Upstage - LLM API (예문 생성)

---

## ⚡ 빠른 시작

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

# 초기 설정 (의존성 설치 + .env 생성)
just setup

# .env 파일 수정
# DATABASE_URL, SECRET_KEY 등 설정
```

### 3. 데이터베이스 설정 & 실행

**옵션 A: Docker (권장)**

```bash
# PostgreSQL 포함 전체 스택 실행
just docker-up

# 마이그레이션 적용
just docker-migrate

# 샘플 데이터 추가 (선택)
just docker-seed
```

**옵션 B: 로컬 PostgreSQL**

```bash
# PostgreSQL 데이터베이스 생성
createdb loops

# .env에서 DATABASE_URL 수정
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loops

# 마이그레이션 적용
just migrate

# 샘플 데이터 추가 (선택)
just db-seed
```

### 4. 개발 서버 시작

```bash
just dev
```

서버 실행 후:

- API 문서: http://localhost:8080/docs
- 헬스 체크: http://localhost:8080/health

---

## 📚 주요 기능

### 사용자 관리

- 회원가입 / 로그인 (JWT)
- 구독 관리 (Free/Premium/Enterprise)
- 학습 연속 일수(Streak) 추적

### 단어 학습

- FSRS 기반 최적 복습 주기 계산
- 4단계 난이도 평가 (Again/Hard/Good/Easy)
- 학습 상태 추적 (New/Learning/Review/Relearning)
- 단어별 상세 정보 (발음, 예문, 유의어, 반의어, 어원)

### 덱(Deck) 시스템

- 공식 덱 / 사용자 생성 덱
- 덱별 학습 진행률 추적
- 공개 덱 공유 기능

### AI 기능

- 컨텍스트별 예문 생성
- 발음 체크 및 피드백
- 단어 설명 및 사용법 안내

---

## 📖 문서

프로젝트 문서는 `docs/` 폴더에 정리되어 있습니다:

**개발 문서**

- **[DEVELOPMENT.md](./docs/DEVELOPMENT.md)** - 개발 가이드 및 프로젝트 구조
- **[COMMANDS.md](./docs/COMMANDS.md)** - 명령어 레퍼런스 (Just, UV)
- **[API.md](./docs/API.md)** - API 엔드포인트 문서 및 테스트 예제
- **[DATABASE.md](./docs/DATABASE.md)** - 데이터베이스 스키마 & 마이그레이션
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - 배포 가이드
- **[TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md)** - 문제 해결 가이드

**프로젝트 관리**

- **[PROJECT_MANAGEMENT.md](./docs/PROJECT_MANAGEMENT.md)** - 프로젝트 관리 및 워크플로우 가이드
- **[GITHUB_PROJECTS_SETUP.md](./docs/GITHUB_PROJECTS_SETUP.md)** - GitHub Projects 세팅 가이드
- **[GITHUB_ISSUES_TEMPLATE.md](./docs/GITHUB_ISSUES_TEMPLATE.md)** - 이슈 템플릿 및 에픽 목록

**기타**

- **[CLAUDE.md](./CLAUDE.md)** - AI 협업 가이드 (Claude Code용)

---

## 💡 자주 쓰는 명령어

```bash
# 개발
just dev                            # 개발 서버 시작
just info                           # 환경 상태 확인

# 마이그레이션
just revision "설명"                # 마이그레이션 생성
just migrate                        # 마이그레이션 적용
just rollback                       # 마지막 마이그레이션 롤백

# 데이터베이스
just db-seed                        # 샘플 데이터 추가
just db-test                        # DB 연결 테스트

# Docker
just docker-up                      # Docker 시작
just docker-logs                    # 로그 확인
just docker-down                    # Docker 중지

# 유틸리티
just clean                          # 캐시 정리
just --list                         # 모든 명령어 보기
```

**전체 명령어 목록**: [docs/COMMANDS.md](./docs/COMMANDS.md)

---

## 🔍 코드 품질 검사

### Linter (ruff)

```bash
# 코드 스타일 검사
uv run ruff check src/

# 자동 수정
uv run ruff check src/ --fix

# 포맷팅
uv run ruff format src/
```

### Type Checker (mypy)

```bash
# 타입 검사 실행
uv run mypy src/
```

---

## 🧪 테스트

```bash
# 전체 테스트 실행
uv run pytest

# 커버리지 리포트 포함
uv run pytest --cov=src/app --cov-report=term-missing

# 특정 테스트 파일 실행
uv run pytest tests/unit/services/test_deck_service.py -v

# 커버리지 HTML 리포트 생성
uv run pytest --cov=src/app --cov-report=html
```

테스트 커버리지 목표: **80% 이상**

---

## 🔐 환경 설정

`.env` 파일 필수 설정:

```bash
# 데이터베이스
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loops

# JWT 보안 (⚠️ 프로덕션에서 반드시 변경!)
SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 개발 설정
DEBUG=True
ALLOWED_ORIGINS=*
```

**안전한 SECRET_KEY 생성:**

```bash
openssl rand -hex 32
```
