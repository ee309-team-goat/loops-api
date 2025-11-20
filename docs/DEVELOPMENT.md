# 개발 가이드 (Development Guide)

Loops API 개발을 위한 상세 가이드입니다.

## 📋 목차

- [프로젝트 구조](#-프로젝트-구조)
- [개발 환경 설정](#-개발-환경-설정)
- [새 기능 추가하기](#-새-기능-추가하기)
- [코딩 컨벤션](#-코딩-컨벤션)
- [테스트](#-테스트)

---

## 🏗 프로젝트 구조

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
│   │   │   ├── base.py             # Base 모델 및 Mixin
│   │   │   ├── user.py             # 사용자
│   │   │   ├── vocabulary_card.py  # 단어 카드
│   │   │   ├── user_card_progress.py  # 학습 진도 (FSRS)
│   │   │   ├── deck.py             # 덱
│   │   │   ├── user_deck.py        # 사용자-덱 관계
│   │   │   ├── study_session.py    # 학습 세션
│   │   │   ├── ai_interaction.py   # AI 상호작용
│   │   │   ├── sync_queue.py       # 동기화 큐
│   │   │   └── __init__.py         # 모델 등록
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
│   │   ├── config.py               # 설정 (환경 변수)
│   │   └── database.py             # DB 연결 및 세션
│   │
│   ├── scripts/                    # 유틸리티 스크립트
│   │   └── seed_data.py            # 샘플 데이터 시딩
│   │
│   └── main.py                     # 진입점
│
├── docs/                           # 📚 프로젝트 문서
│   ├── API.md                      # API 문서
│   ├── COMMANDS.md                 # 명령어 레퍼런스
│   ├── DATABASE.md                 # 데이터베이스 가이드
│   ├── DEPLOYMENT.md               # 배포 가이드
│   ├── DEVELOPMENT.md              # 개발 가이드 (이 문서)
│   ├── TROUBLESHOOTING.md          # 문제 해결
│   └── GITHUB_ISSUES_TEMPLATE.md   # GitHub Issues 템플릿
│
├── .env.example                    # 환경 변수 템플릿
├── .gitignore                      # Git ignore 설정
├── docker-compose.yaml             # Docker 설정
├── Dockerfile                      # Docker 이미지 빌드
├── justfile                        # Just 명령어
├── pyproject.toml                  # 프로젝트 메타데이터
├── uv.lock                         # UV 의존성 잠금
├── CLAUDE.md                       # AI 협업 가이드
└── README.md                       # 프로젝트 개요
```

### 주요 디렉토리 설명

#### `src/app/models/`
- SQLModel 기반 데이터베이스 모델
- 각 모델은 Base, Table, Create, Read, Update 스키마로 구성
- `__init__.py`에 모든 모델을 등록해야 Alembic이 감지 가능

#### `src/app/services/`
- 비즈니스 로직을 담당하는 서비스 레이어
- Static 메서드 사용 (인스턴스 상태 없음)
- 각 모델에 대응하는 서비스 클래스

#### `src/app/api/`
- FastAPI 라우터 및 엔드포인트
- `auth.py`: 인증 관련 엔드포인트
- `routes.py`: 메인 라우터 (모든 엔드포인트 등록)

#### `src/alembic/`
- 데이터베이스 마이그레이션 파일
- `versions/`: 마이그레이션 파일들
- `env.py`: Alembic 설정 (비동기 지원)

---

## ⚙️ 개발 환경 설정

### 필수 도구 설치

```bash
# UV 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# Just 설치 (macOS)
brew install just

# Docker 설치
# https://docs.docker.com/get-docker/
```

### 프로젝트 설정

```bash
# 저장소 클론
git clone <repository-url>
cd loops-api

# 초기 설정
just setup

# .env 파일 수정
# - DATABASE_URL 설정
# - SECRET_KEY 생성 (openssl rand -hex 32)

# 데이터베이스 시작
just docker-up

# 마이그레이션 적용
just docker-migrate

# 샘플 데이터 추가
just docker-seed

# 개발 서버 시작
just dev
```

### IDE 설정

**VS Code 추천 확장:**
- Python
- Pylance
- SQLTools
- Thunder Client (API 테스트)

**설정 (.vscode/settings.json):**
```json
{
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

---

## ✨ 새 기능 추가하기

### 1. 새 모델 추가

**Step 1: 모델 파일 생성**

`src/app/models/your_entity.py`:
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# Base 스키마
class YourEntityBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None

# 테이블 모델
class YourEntity(YourEntityBase, table=True):
    __tablename__ = "your_entities"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Create 스키마 (POST용)
class YourEntityCreate(YourEntityBase):
    user_id: int

# Read 스키마 (응답용)
class YourEntityRead(YourEntityBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# Update 스키마 (PATCH용)
class YourEntityUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
```

**Step 2: 모델 등록**

`src/app/models/__init__.py`에 추가:
```python
from app.models.your_entity import (
    YourEntity,
    YourEntityCreate,
    YourEntityRead,
    YourEntityUpdate
)

__all__ = [
    # ... 기존 모델들
    "YourEntity",
    "YourEntityCreate",
    "YourEntityRead",
    "YourEntityUpdate",
]
```

**Step 3: 마이그레이션 생성**

```bash
just revision "Add your_entity model"
just migration-latest  # 검토
just migrate           # 적용
```

### 2. 서비스 레이어 추가

`src/app/services/your_entity_service.py`:
```python
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.your_entity import (
    YourEntity,
    YourEntityCreate,
    YourEntityUpdate
)

class YourEntityService:
    @staticmethod
    async def create(
        session: AsyncSession,
        data: YourEntityCreate
    ) -> YourEntity:
        entity = YourEntity(**data.model_dump())
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    @staticmethod
    async def get(
        session: AsyncSession,
        entity_id: int
    ) -> YourEntity | None:
        statement = select(YourEntity).where(YourEntity.id == entity_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> list[YourEntity]:
        statement = (
            select(YourEntity)
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def update(
        session: AsyncSession,
        entity_id: int,
        data: YourEntityUpdate
    ) -> YourEntity | None:
        entity = await YourEntityService.get(session, entity_id)
        if not entity:
            return None

        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(entity, key, value)

        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

    @staticmethod
    async def delete(
        session: AsyncSession,
        entity_id: int
    ) -> bool:
        entity = await YourEntityService.get(session, entity_id)
        if not entity:
            return False

        await session.delete(entity)
        await session.commit()
        return True
```

### 3. API 엔드포인트 추가

`src/app/api/routes.py`에 추가:
```python
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.your_entity import YourEntityCreate, YourEntityRead, YourEntityUpdate
from app.services.your_entity_service import YourEntityService

# 의존성 타입
CurrentUser = Annotated[User, Depends(get_current_user)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]

@router.post("/entities", response_model=YourEntityRead)
async def create_entity(
    data: YourEntityCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """엔티티 생성"""
    return await YourEntityService.create(session, data)

@router.get("/entities", response_model=list[YourEntityRead])
async def get_entities(
    current_user: CurrentUser,
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
):
    """엔티티 목록 조회"""
    return await YourEntityService.get_all(session, skip, limit)

@router.get("/entities/{entity_id}", response_model=YourEntityRead)
async def get_entity(
    entity_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    """엔티티 상세 조회"""
    entity = await YourEntityService.get(session, entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.patch("/entities/{entity_id}", response_model=YourEntityRead)
async def update_entity(
    entity_id: int,
    data: YourEntityUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """엔티티 수정"""
    entity = await YourEntityService.update(session, entity_id, data)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.delete("/entities/{entity_id}", status_code=204)
async def delete_entity(
    entity_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    """엔티티 삭제"""
    success = await YourEntityService.delete(session, entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
```

### 4. 테스트

```bash
# 서버 시작
just dev

# Swagger UI에서 테스트
open http://localhost:8000/docs

# 또는 curl
TOKEN="your-jwt-token"

curl -X POST http://localhost:8000/api/v1/entities \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","user_id":1}'
```

---

## 📏 코딩 컨벤션

### Python 스타일

- **PEP 8** 준수
- **Black** 포매터 사용
- **타입 힌트** 필수

### 네이밍

```python
# 클래스: PascalCase
class UserService:
    pass

# 함수/메서드: snake_case
def get_user_by_id():
    pass

# 상수: UPPER_SNAKE_CASE
MAX_RETRY_COUNT = 3

# 변수: snake_case
user_id = 1
```

### 파일 구조

```python
# 1. 임포트 (표준 라이브러리 → 서드파티 → 로컬)
from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from fastapi import Depends

from app.models.base import TimestampMixin

# 2. 타입 정의
UserID = int

# 3. 클래스/함수 정의
class User(SQLModel):
    ...

# 4. 상수
DEFAULT_LIMIT = 100
```

### 주석

```python
# 함수 docstring
async def create_user(session: AsyncSession, data: UserCreate) -> User:
    """
    새 사용자를 생성합니다.

    Args:
        session: 데이터베이스 세션
        data: 사용자 생성 데이터

    Returns:
        생성된 사용자 객체

    Raises:
        HTTPException: 이메일이 이미 존재하는 경우
    """
    pass
```

### 모델 패턴

```python
# Base → Table → Create → Read → Update 순서
class EntityBase(SQLModel):
    """공통 필드"""
    name: str

class Entity(EntityBase, table=True):
    """테이블 모델"""
    id: Optional[int] = Field(default=None, primary_key=True)

class EntityCreate(EntityBase):
    """생성용 (id 제외)"""
    pass

class EntityRead(EntityBase):
    """응답용 (id 포함)"""
    id: int

class EntityUpdate(SQLModel):
    """수정용 (모든 필드 optional)"""
    name: Optional[str] = None
```

---

## 🧪 테스트

### 수동 테스트

```bash
# Swagger UI
just dev
open http://localhost:8000/docs

# API 헬스 체크
just health

# DB 연결 테스트
just db-test
```

### API 테스트 (curl)

```bash
# 회원가입
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"pass123"}'

# 로그인 & 토큰 저장
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=pass123" | jq -r .access_token)

# 인증이 필요한 요청
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

자세한 테스트 예제는 [API.md](./API.md)를 참고하세요.

---

## 📚 관련 문서

- [README.md](../README.md) - 프로젝트 개요
- [COMMANDS.md](./COMMANDS.md) - 명령어 레퍼런스
- [API.md](./API.md) - API 문서
- [DATABASE.md](./DATABASE.md) - 데이터베이스 가이드
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 배포 가이드
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결
- [CLAUDE.md](../CLAUDE.md) - AI 협업 가이드
