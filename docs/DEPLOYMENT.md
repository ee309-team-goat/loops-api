# 배포 가이드 (Deployment Guide)

Loops API를 프로덕션 환경에 배포하는 방법을 설명합니다.

## 📋 목차

- [배포 전 체크리스트](#-배포-전-체크리스트)
- [환경 변수 설정](#-환경-변수-설정)
- [Docker로 배포](#-docker로-배포)
- [Supabase 연동](#-supabase-연동)
- [클라우드 플랫폼 배포](#-클라우드-플랫폼-배포)
- [보안 강화](#-보안-강화)
- [모니터링 & 로깅](#-모니터링--로깅)

---

## ✅ 배포 전 체크리스트

배포하기 전에 다음 항목들을 확인하세요:

### 필수 항목

- [ ] `.env` 파일의 `DEBUG=False` 설정
- [ ] `SECRET_KEY`를 안전한 랜덤 키로 변경
- [ ] `DATABASE_URL`을 프로덕션 DB로 설정
- [ ] `ALLOWED_ORIGINS`를 실제 도메인으로 제한
- [ ] 모든 테스트 통과 확인
- [ ] 마이그레이션 파일 검토 완료
- [ ] 데이터베이스 백업 완료

### 권장 항목

- [ ] HTTPS 설정
- [ ] 로그 수집 시스템 구축
- [ ] 에러 모니터링 (Sentry 등)
- [ ] Rate limiting 설정
- [ ] 헬스 체크 엔드포인트 확인
- [ ] 백업 & 복구 계획 수립

---

## 🔐 환경 변수 설정

### 프로덕션 .env 파일

```bash
# 애플리케이션
APP_NAME=Loops API
APP_VERSION=0.1.0
DEBUG=False                           # ⚠️ 프로덕션에서는 반드시 False

# API
API_V1_PREFIX=/api/v1

# CORS - 실제 도메인으로 제한
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 데이터베이스
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
DATABASE_ECHO=False                   # ⚠️ 프로덕션에서는 반드시 False

# JWT 보안
SECRET_KEY=생성된_안전한_랜덤_키      # ⚠️ 반드시 변경 필요!
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### SECRET_KEY 생성

```bash
# 안전한 랜덤 키 생성
openssl rand -hex 32

# 출력 예시:
# 8f9a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7

# .env 파일에 추가
SECRET_KEY=8f9a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7
```

### 환경별 설정 관리

```bash
# 개발 환경
.env

# 프로덕션 환경
.env.production

# 스테이징 환경
.env.staging

# 환경별로 로드
cp .env.production .env
```

---

## 🐳 Docker로 배포

### 기본 배포

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd loops-api

# 2. 프로덕션 환경 변수 설정
cp .env.example .env
# .env 파일 수정 (위의 프로덕션 설정 참고)

# 3. Docker 컨테이너 빌드 및 시작
docker-compose build
docker-compose up -d

# 4. 마이그레이션 적용
docker-compose exec api uv run alembic upgrade head

# 5. 헬스 체크
curl http://localhost:8000/health
```

### docker-compose.yaml (프로덕션 최적화)

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: loops-api
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    mem_limit: 1g
    cpus: 1.0

  db:
    image: postgres:16
    container_name: loops-db
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
      POSTGRES_DB: ${DB_NAME:-loops}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Docker 명령어

```bash
# 빌드
docker-compose build --no-cache

# 시작 (detached)
docker-compose up -d

# 중지
docker-compose down

# 로그 확인
docker-compose logs -f api
docker-compose logs -f db

# 컨테이너 재시작
docker-compose restart api

# 마이그레이션 실행
docker-compose exec api uv run alembic upgrade head

# 컨테이너 내부 접속
docker-compose exec api sh
```

---

## 🌐 Supabase 연동

### Supabase 프로젝트 생성

1. [Supabase](https://supabase.com) 접속
2. 새 프로젝트 생성
3. Project Settings > Database로 이동
4. Connection string 복사 (Session pooling)

### DATABASE_URL 설정

```bash
# .env 파일
DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# 예시:
DATABASE_URL=postgresql+asyncpg://postgres:your-super-secret-password@db.abcdefghijk.supabase.co:5432/postgres
```

### 마이그레이션 적용

```bash
# 로컬에서 Supabase로 마이그레이션 실행
uv run alembic upgrade head

# 또는 Docker에서
docker-compose exec api uv run alembic upgrade head
```

### Supabase 장점

- ✅ 관리형 PostgreSQL (백업, 업데이트 자동화)
- ✅ 무료 플랜 제공
- ✅ Row Level Security (RLS) 지원
- ✅ 실시간 데이터베이스 기능
- ✅ Storage, Auth 통합 가능

---

## ☁️ 클라우드 플랫폼 배포

### Fly.io 배포

```bash
# 1. Fly CLI 설치
curl -L https://fly.io/install.sh | sh

# 2. 로그인
fly auth login

# 3. 앱 생성
fly launch

# 4. 환경 변수 설정
fly secrets set SECRET_KEY=your-secret-key
fly secrets set DATABASE_URL=your-database-url

# 5. 배포
fly deploy

# 6. 마이그레이션
fly ssh console
uv run alembic upgrade head
exit

# 7. 로그 확인
fly logs
```

### Render 배포

1. [Render](https://render.com) 계정 생성
2. New > Web Service 선택
3. GitHub 저장소 연결
4. 설정:
   - **Build Command**: `uv sync`
   - **Start Command**: `uv run python src/main.py`
   - **Environment**: Python 3.12
5. 환경 변수 추가 (위의 프로덕션 .env 참고)
6. Deploy 클릭

### Railway 배포

```bash
# 1. Railway CLI 설치
npm install -g @railway/cli

# 2. 로그인
railway login

# 3. 프로젝트 초기화
railway init

# 4. 환경 변수 설정
railway variables set SECRET_KEY=your-secret-key
railway variables set DATABASE_URL=your-database-url

# 5. 배포
railway up
```

### AWS ECS 배포 (고급)

```bash
# 1. ECR에 이미지 푸시
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t loops-api .
docker tag loops-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/loops-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/loops-api:latest

# 2. ECS 작업 정의 생성
# 3. ECS 서비스 생성
# 4. 로드 밸런서 설정
# 5. Auto Scaling 설정
```

---

## 🔒 보안 강화

### HTTPS 설정

```bash
# Nginx 리버스 프록시 설정
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Rate Limiting

FastAPI에 SlowAPI 추가:

```python
# requirements에 추가
# slowapi

# src/app/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 엔드포인트에 적용
@app.get("/api/v1/cards")
@limiter.limit("100/minute")
async def get_cards():
    ...
```

### 보안 헤더

```python
# src/app/main.py
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS 강제
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
    )
```

---

## 📊 모니터링 & 로깅

### Sentry 통합 (에러 추적)

```bash
# 1. Sentry 패키지 설치
uv add sentry-sdk[fastapi]

# 2. src/app/main.py에 추가
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
    environment="production"
)
```

### 로깅 설정

```python
# src/app/main.py
import logging
from logging.handlers import RotatingFileHandler

# 파일 핸들러
handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10000000,
    backupCount=5
)
handler.setLevel(logging.INFO)

# 포맷
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# 로거 설정
logger = logging.getLogger("uvicorn")
logger.addHandler(handler)
```

### 헬스 체크 모니터링

```bash
# Uptime monitoring (UptimeRobot, Pingdom 등)
# 헬스 체크 URL: https://yourdomain.com/health

# Prometheus metrics
uv add prometheus-fastapi-instrumentator

# src/app/main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🔄 배포 프로세스

### CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest

      - name: Deploy to server
        run: |
          # SSH into server and deploy
          # Or use Docker image push
```

### 배포 체크리스트

배포 시 순서:

1. ✅ 코드 리뷰 완료
2. ✅ 테스트 통과
3. ✅ 데이터베이스 백업
4. ✅ 환경 변수 확인
5. ✅ 마이그레이션 테스트
6. ✅ 배포 실행
7. ✅ 마이그레이션 적용
8. ✅ 헬스 체크 확인
9. ✅ 모니터링 확인
10. ✅ 롤백 계획 준비

---

## 🔙 롤백 계획

### 빠른 롤백

```bash
# 1. 이전 Docker 이미지로 롤백
docker-compose down
docker-compose pull <previous-image-tag>
docker-compose up -d

# 2. 데이터베이스 마이그레이션 롤백
docker-compose exec api uv run alembic downgrade -1

# 3. 헬스 체크
curl https://yourdomain.com/health
```

### 데이터베이스 백업 & 복구

```bash
# 백업
pg_dump -U postgres -d loops > backup_$(date +%Y%m%d_%H%M%S).sql

# 복구
psql -U postgres -d loops < backup_20250120_120000.sql
```

---

## 📚 관련 문서

- [README.md](../README.md) - 프로젝트 개요
- [COMMANDS.md](./COMMANDS.md) - 명령어 레퍼런스
- [DATABASE.md](./DATABASE.md) - 데이터베이스 정보
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결 가이드
