# Loops API 문서 센터

> 영어 단어 학습 앱 - 백엔드 API 문서 모음

---

## 📚 문서 목록

### 🚀 시작하기
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - 개발 환경 설정 및 시작 가이드
- **[COMMANDS.md](./COMMANDS.md)** - 자주 사용하는 명령어 모음

### 📋 기획 & 로드맵
- **[ROADMAP.md](./ROADMAP.md)** ⭐ - 전체 개발 로드맵 및 태스크 리스트
- **[CARD_SELECTION_ALGORITHM.md](./CARD_SELECTION_ALGORITHM.md)** - 단어 카드 선정 알고리즘 가이드

### 🔧 기술 문서
- **[API.md](./API.md)** - REST API 엔드포인트 명세
- **[DATABASE.md](./DATABASE.md)** - 데이터베이스 스키마 및 ERD
- **[schema.sql](./schema.sql)** - SQL 스키마 정의

### 🚢 배포 & 운영
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - 배포 가이드
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - 문제 해결 가이드

### 📊 프로젝트 관리
- **[PROJECT_MANAGEMENT.md](./PROJECT_MANAGEMENT.md)** - 프로젝트 관리 방법론
- **[GITHUB_PROJECTS_SETUP.md](./GITHUB_PROJECTS_SETUP.md)** - GitHub Projects 설정
- **[GITHUB_ISSUES_TEMPLATE.md](./GITHUB_ISSUES_TEMPLATE.md)** - 이슈 템플릿

---

## 🎯 목적별 문서 찾기

### 처음 시작하는 개발자
1. [DEVELOPMENT.md](./DEVELOPMENT.md) - 환경 설정
2. [COMMANDS.md](./COMMANDS.md) - 기본 명령어
3. [DATABASE.md](./DATABASE.md) - DB 구조 이해
4. [API.md](./API.md) - API 구조 이해

### 기능 개발자
1. [ROADMAP.md](./ROADMAP.md) - 개발 태스크 확인
2. [CARD_SELECTION_ALGORITHM.md](./CARD_SELECTION_ALGORITHM.md) - 알고리즘 설계
3. [API.md](./API.md) - 엔드포인트 명세
4. [DATABASE.md](./DATABASE.md) - 스키마 참조

### DevOps / 인프라
1. [DEPLOYMENT.md](./DEPLOYMENT.md) - 배포 절차
2. [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결
3. [DATABASE.md](./DATABASE.md) - DB 설정

### PM / 기획자
1. [ROADMAP.md](./ROADMAP.md) - 전체 로드맵
2. [PROJECT_MANAGEMENT.md](./PROJECT_MANAGEMENT.md) - 관리 방법
3. [GITHUB_PROJECTS_SETUP.md](./GITHUB_PROJECTS_SETUP.md) - 이슈 관리

---

## 📖 핵심 문서 요약

### ROADMAP.md ⭐ 가장 중요
```
📱 앱 구조 → 🗂️ 덱 선택 로직 → 📋 백엔드 태스크 →
🗄️ DB 스키마 → 📦 데이터 준비 → 📱 프론트 태스크 →
🚀 Sprint 계획 → 📊 진행 상황
```

**총 60개 태스크:**
- 백엔드 API: 22개 (2개 완료)
- DB 스키마: 7개
- 데이터 준비: 5개
- 프론트엔드: 26개

### CARD_SELECTION_ALGORITHM.md
```
7가지 알고리즘 비교 → 추천 전략 → 구현 예시 →
연구 기반 권장사항 → 실제 앱 사례 → A/B 테스트
```

**추천 구현:**
- MVP: 빈도 기반
- V2: 빈도 + i+1 필터 + Interleaving
- V3: ML 기반 예측

---

## 🏗️ 프로젝트 아키텍처

```
loops-api/
├── src/
│   ├── app/
│   │   ├── api/          # API 라우트
│   │   ├── models/       # SQLModel 모델
│   │   ├── services/     # 비즈니스 로직
│   │   └── core/         # 인증, 보안
│   └── alembic/          # DB 마이그레이션
├── docs/                 # 📚 여기!
└── tests/                # 테스트 코드
```

---

## 🔗 외부 리소스

### 기술 스택
- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **Alembic**: https://alembic.sqlalchemy.org/
- **FSRS**: https://github.com/open-spaced-repetition/py-fsrs

### 데이터 소스
- **COCA Frequency**: https://www.wordfrequency.info/samples.asp
- **Oxford 3000/5000**: https://www.oxfordlearnersdictionaries.com/wordlists/
- **Wiktionary**: https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists

### 연구 논문
- Krashen (1982) - Comprehensible Input
- Nation (2006) - Vocabulary Size
- Rohrer & Taylor (2007) - Interleaving Effect

---

## 🤝 기여하기

1. 새 기능 제안: [ROADMAP.md](./ROADMAP.md)의 해당 섹션에 추가
2. 버그 리포트: [GITHUB_ISSUES_TEMPLATE.md](./GITHUB_ISSUES_TEMPLATE.md) 참조
3. 문서 개선: 각 문서 하단에 수정 이력 추가

---

## 📝 문서 업데이트 히스토리

- **2025-11-28**: CARD_SELECTION_ALGORITHM.md 추가, ROADMAP.md 대폭 업데이트
- **이전**: 초기 문서 작성
