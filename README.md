# Loops API

FSRS 알고리즘 기반 AI 영어 학습 백엔드

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Coverage](https://img.shields.io/badge/Coverage-98%25-brightgreen)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 목차

- [소개](#-소개)
- [기술 스택](#-기술-스택)
- [시작하기](#-시작하기)
- [프로젝트 구조](#-프로젝트-구조)
- [개발 가이드](#-개발-가이드)
- [테스트](#-테스트)
- [API 문서](#-api-문서)
- [배포](#-배포)
- [기여하기](#-기여하기)

---

## 📖 소개

Loops API는 과학적으로 검증된 **FSRS(Free Spaced Repetition Scheduler)** 알고리즘을 활용하여 최적의 복습 주기를 제공하는 영어 학습 플랫폼입니다.

### 주요 기능

| 기능 | 설명 |
|------|------|
| **FSRS 학습** | 전통적인 SM-2를 넘어선 현대적 간격 반복 시스템 |
| **AI 튜터** | GPT 기반 실시간 단어 질의응답 |
| **이미지 생성** | Gemini로 단어 연상 이미지 자동 생성 |
| **덱 시스템** | 주제별, 난이도별 단어장 관리 |
| **학습 통계** | 정답률, 연속 학습일, 진도 추적 |

### 학습 흐름

```text
사용자 → 덱 선택 → 학습 세션 시작 → 카드 학습 → FSRS 평가 → 복습 일정 계산
                                        ↓
                                   AI 튜터 질문 (선택)
```

---

## 🛠 기술 스택

### 핵심 프레임워크

| 기술 | 버전 | 용도 |
|------|------|------|
| **FastAPI** | 0.121+ | 비동기 웹 프레임워크 |
| **Python** | 3.12+ | 런타임 |
| **UV** | latest | 패키지 매니저 |
| **Just** | latest | 태스크 러너 |

### 데이터베이스

| 기술 | 버전 | 용도 |
|------|------|------|
| **PostgreSQL** | 16+ | 메인 데이터베이스 |
| **SQLModel** | latest | ORM (SQLAlchemy + Pydantic) |
| **Alembic** | latest | 마이그레이션 |
| **asyncpg** | latest | 비동기 드라이버 |

### 인증 & 스토리지

| 기술 | 용도 |
|------|------|
| **Supabase Auth** | JWT 토큰 기반 인증 |
| **Supabase Storage** | 이미지 파일 저장 |

### AI & 학습

| 기술 | 용도 |
|------|------|
| **py-fsrs 6.3** | FSRS v5 간격 반복 알고리즘 |
| **LangChain + LangGraph** | AI 튜터 워크플로우 |
| **OpenAI GPT-4o-mini** | 대화 생성 |
| **Google Gemini** | 이미지 생성 |

### 개발 도구

| 도구 | 용도 |
|------|------|
| **pytest** | 테스트 프레임워크 |
| **ruff** | 린터 & 포매터 |
| **mypy** | 정적 타입 검사 |

---

## 🚀 시작하기

### 사전 요구사항

```bash
# UV 설치 (필수)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Just 설치 (권장)
brew install just  # macOS
```

### 빠른 설치

```bash
# 1. 저장소 클론
git clone <repository-url>
cd loops-api

# 2. 초기 설정 (의존성 설치 + .env 생성)
just setup

# 3. .env 파일 편집
# DATABASE_URL, SUPABASE_URL 등 설정
```

### 실행 방법

#### Docker 사용 (권장)

```bash
just docker-up        # PostgreSQL 컨테이너 시작
just docker-migrate   # 마이그레이션 적용
just dev              # 개발 서버 시작
```

#### 로컬 PostgreSQL 사용

```bash
createdb loops        # 데이터베이스 생성
just migrate          # 마이그레이션 적용
just dev              # 개발 서버 시작
```

### 실행 확인

- **API 문서**: <http://localhost:8080/docs>
- **헬스 체크**: <http://localhost:8080/health>

---

## 📁 프로젝트 구조

```text
loops-api/
├── src/app/
│   ├── main.py           # FastAPI 앱 진입점
│   ├── config.py         # 환경 설정
│   ├── database.py       # DB 세션 팩토리
│   ├── api/              # API 라우터
│   │   ├── auth.py       # 인증
│   │   ├── profiles.py   # 프로필
│   │   ├── cards.py      # 단어 카드
│   │   ├── decks.py      # 덱 관리
│   │   ├── study.py      # 학습 세션
│   │   ├── tutor.py      # AI 튜터
│   │   └── stats.py      # 통계
│   ├── core/             # 핵심 유틸리티
│   │   ├── security.py   # 인증 검증
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── models/
│   │   ├── tables/       # DB 테이블 정의
│   │   └── schemas/      # API 스키마
│   └── services/         # 비즈니스 로직
├── tests/                # 테스트 코드
├── alembic/              # DB 마이그레이션
├── docs/                 # 상세 문서
├── scripts/              # 유틸리티 스크립트
└── justfile              # 명령어 정의
```

### 레이어 구조

```text
HTTP 요청 → API Router → Service → Database
              ↓
         의존성 주입
         (인증, 세션)
```

| 레이어 | 위치 | 역할 |
|--------|------|------|
| **API** | `api/` | 요청/응답 처리, 검증 |
| **Service** | `services/` | 비즈니스 로직, FSRS 계산 |
| **Model** | `models/` | DB 스키마, DTO 정의 |
| **Core** | `core/` | 인증, 예외, 의존성 |

---

## 💻 개발 가이드

### 자주 쓰는 명령어

```bash
# 개발
just dev              # 개발 서버 시작 (port 8080)
just info             # 환경 상태 확인

# 마이그레이션
just migrate          # 마이그레이션 적용
just revision "설명"  # 새 마이그레이션 생성
just rollback         # 마지막 마이그레이션 롤백
just current          # 현재 리비전 확인

# 데이터베이스
just db-seed          # 샘플 데이터 추가
just db-test          # DB 연결 테스트

# Docker
just docker-up        # 컨테이너 시작
just docker-down      # 컨테이너 중지
just docker-logs      # 로그 확인

# 정리
just clean            # 캐시 정리
just --list           # 모든 명령어 보기
```

### 코드 품질 검사

```bash
# 린트 검사
uv run ruff check src/

# 자동 수정
uv run ruff check src/ --fix

# 포맷팅
uv run ruff format src/

# 타입 검사
uv run mypy src/

# 전체 검사 (CI와 동일)
uv run ruff check src/ && uv run ruff format src/ --check && uv run mypy src/
```

### 환경 설정 (.env)

**필수 설정**

```bash
# 애플리케이션
APP_NAME=Loops API
DEBUG=True
API_V1_PREFIX=/api/v1

# 데이터베이스
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/loops

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=eyJhbGciOiJIUzI1NiIs...
SUPABASE_SECRET_KEY=eyJhbGciOiJIUzI1NiIs...
```

#### AI 기능 (선택)

```bash
# OpenAI - AI 튜터
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Google Gemini - 이미지 생성
GEMINI_API_KEY=AIza...
```

---

## 🧪 테스트

### 기본 실행

```bash
# 전체 테스트
uv run pytest

# 상세 출력
uv run pytest -v

# 커버리지 포함
uv run pytest --cov=src/app --cov-report=term-missing
```

### 특정 테스트 실행

```bash
# 파일 단위
uv run pytest tests/unit/services/test_deck_service.py -v

# 클래스 단위
uv run pytest tests/unit/services/test_deck_service.py::TestDeckServiceCRUD -v

# 함수 단위
uv run pytest tests/unit/services/test_deck_service.py::TestDeckServiceCRUD::test_create_deck -v

# 키워드 필터
uv run pytest -k "deck" -v
```

### 커버리지 리포트

```bash
# 터미널 출력
uv run pytest --cov=src/app --cov-report=term-missing

# HTML 리포트
uv run pytest --cov=src/app --cov-report=html
open htmlcov/index.html

# XML 리포트 (CI용)
uv run pytest --cov=src/app --cov-report=xml
```

### 디버깅 옵션

```bash
uv run pytest -x              # 첫 실패에서 중단
uv run pytest --lf            # 마지막 실패한 테스트만
uv run pytest -s              # print 출력 표시
uv run pytest --pdb           # 실패 시 디버거
uv run pytest --durations=10  # 느린 테스트 표시
```

### 커버리지 현황

| 모듈 | 커버리지 |
|------|----------|
| API 레이어 | 96%+ |
| 서비스 레이어 | 95%+ |
| 스키마/모델 | 96%+ |
| **전체** | **98%+** |

---

## 📡 API 문서

모든 API는 `/api/v1` 접두사를 사용합니다.

### 주요 엔드포인트

| 그룹 | 경로 | 설명 |
|------|------|------|
| **인증** | `/auth/*` | 회원가입, 로그인, 토큰 갱신 |
| **프로필** | `/profiles/*` | 사용자 정보, 스트릭, 진도 |
| **카드** | `/cards/*` | 단어 카드 조회 |
| **덱** | `/decks/*` | 덱 목록, 선택, 관리 |
| **학습** | `/study/*` | 세션 시작, 카드 학습, 답변 제출 |
| **튜터** | `/study/.../tutor/*` | AI 튜터 대화 |
| **통계** | `/stats/*` | 학습량, 정답률, 히스토리 |

### 상세 문서

서버 실행 후 Swagger UI에서 확인:

- **Swagger UI**: <http://localhost:8080/docs>
- **ReDoc**: <http://localhost:8080/redoc>

---

## 🚢 배포

### 자동 배포

`main` 브랜치에 push하면 Cloud Run에 자동 배포됩니다.

```bash
git push origin main
```

### 수동 배포

```bash
# Docker 이미지 빌드 및 배포
gcloud builds submit --tag asia-northeast3-docker.pkg.dev/ee309-loops/cloud-run-source-deploy/loops-api

gcloud run deploy loops-api \
  --image asia-northeast3-docker.pkg.dev/ee309-loops/cloud-run-source-deploy/loops-api \
  --region asia-northeast3 \
  --platform managed
```

자세한 내용: [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)

---

## 🤝 기여하기

### 개발 워크플로우

1. 저장소 Fork
2. 기능 브랜치 생성: `git checkout -b feature/amazing-feature`
3. 변경사항 커밋: `git commit -m 'feat: add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Pull Request 생성

### 커밋 컨벤션

[Conventional Commits](https://www.conventionalcommits.org/) 사용:

| 타입 | 설명 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 변경 |
| `refactor` | 리팩토링 |
| `test` | 테스트 |
| `chore` | 빌드/설정 변경 |

### PR 체크리스트

- [ ] 테스트 통과: `uv run pytest`
- [ ] 린트 통과: `uv run ruff check src/`
- [ ] 타입 검사: `uv run mypy src/`

---

## 📚 문서

| 문서 | 설명 |
|------|------|
| [DEVELOPMENT.md](./docs/DEVELOPMENT.md) | 개발 가이드 |
| [COMMANDS.md](./docs/COMMANDS.md) | 명령어 레퍼런스 |
| [API.md](./docs/API.md) | API 상세 문서 |
| [DATABASE.md](./docs/DATABASE.md) | DB 스키마 & 마이그레이션 |
| [DEPLOYMENT.md](./docs/DEPLOYMENT.md) | 배포 가이드 |
| [TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md) | 문제 해결 |
| [CLAUDE.md](./CLAUDE.md) | AI 협업 가이드 |

---

## 📄 라이선스

MIT License - [LICENSE](LICENSE) 참고
