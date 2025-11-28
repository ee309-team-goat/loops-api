# GitHub Projects 세팅 가이드

백엔드 레포지토리를 GitHub Projects로 관리하기 위한 완벽한 가이드입니다.

## 📋 목차

- [프로젝트 보드 생성](#-프로젝트-보드-생성)
- [보드 구조 설정](#-보드-구조-설정)
- [이슈 생성 및 연결](#-이슈-생성-및-연결)
- [뷰(View) 설정](#-뷰view-설정)
- [자동화(Automation) 설정](#-자동화automation-설정)
- [FE-BE 협업 방법](#-fe-be-협업-방법)
- [워크플로우 예시](#-워크플로우-예시)

---

## 🎯 프로젝트 보드 생성

### 1. 새 프로젝트 생성

```
1. GitHub 레포지토리로 이동
2. "Projects" 탭 클릭
3. "New project" 버튼 클릭
4. 템플릿 선택:
   - "Board" 템플릿 선택 (Kanban 스타일)
   - 또는 "Table" 템플릿 선택 (스프레드시트 스타일)
5. 프로젝트 이름: "Loops API - Backend Development"
```

### 2. 프로젝트 설정

**Settings > General**:

- **Visibility**: Private (팀 내부용) 또는 Public (오픈소스)
- **Description**: "FSRS 기반 영어 학습 플랫폼 백엔드 API 개발 관리"
- **README**: 프로젝트 개요 및 현재 진행 상황 작성

---

## 🏗 보드 구조 설정

### 추천 컬럼 구조 (Board View)

```
📋 Backlog       → 아직 시작하지 않은 작업
🎯 Ready         → 작업 준비 완료, 우선순위 높음
🔨 In Progress   → 현재 진행 중
👀 In Review     → PR 리뷰 대기 중
✅ Done          → 완료된 작업
🚫 Blocked       → 블로킹된 작업 (의존성, 외부 요인)
```

### 컬럼 생성 방법

```
1. Board 뷰에서 "+ New column" 클릭
2. 컬럼 이름 입력 (예: "Backlog")
3. 각 컬럼에 대해 반복
```

### 커스텀 필드 추가

프로젝트에 유용한 메타데이터 필드를 추가하세요:

```
1. 프로젝트 설정 (⚙️) > "Custom fields" 클릭

추천 필드:

📊 Priority (우선순위)
   - Type: Single select
   - Options: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low

🏷️ Type (작업 타입)
   - Type: Single select
   - Options: ✨ Feature, 🐛 Bug, 🔧 Refactor, 📝 Docs, 🧪 Test

🎯 Area (작업 영역)
   - Type: Single select
   - Options: 🗄️ Database, 🌐 API, ⚙️ Service, 🤖 AI, 📊 Analytics

📅 Sprint (스프린트)
   - Type: Single select
   - Options: Sprint 1, Sprint 2, Sprint 3...

👤 Backend Owner (담당자)
   - Type: Single select
   - Options: 팀원 이름들

⏱️ Estimate (예상 시간)
   - Type: Number
   - Unit: Story Points or Hours

🔗 FE Dependency (프론트엔드 의존성)
   - Type: Single select
   - Options: None, Blocked by FE, Blocks FE

🎯 Milestone (마일스톤)
   - Type: Single select
   - Options: v0.1, v0.2, v1.0, v2.0
```

---

## 📝 이슈 생성 및 연결

### 이슈 템플릿 사용

이미 생성한 `docs/GITHUB_ISSUES_TEMPLATE.md`를 기반으로 이슈를 생성하세요.

**방법 1: 수동 생성**

```
1. 레포지토리 > "Issues" 탭
2. "New issue" 클릭
3. GITHUB_ISSUES_TEMPLATE.md의 각 이슈 내용 복사
4. 라벨, 마일스톤 할당
5. 프로젝트에 자동으로 추가됨
```

**방법 2: GitHub CLI로 일괄 생성 (추천)**

```bash
# gh CLI 설치
brew install gh

# 로그인
gh auth login

# 이슈 생성 스크립트 (예시)
gh issue create \
  --title "#1 데이터베이스 스키마 설계 및 마이그레이션 생성" \
  --body "$(cat issue_templates/issue_1.md)" \
  --label "priority:critical,type:feature,area:database" \
  --milestone "Core Infrastructure" \
  --project "Loops API - Backend Development"
```

### 이슈를 프로젝트에 연결

```
1. 프로젝트 보드에서 "+ Add item" 클릭
2. 레포지토리의 기존 이슈 검색 및 추가
3. 또는 이슈 생성 시 자동으로 프로젝트에 추가
```

### Epic 관리

Epic(대형 작업)을 관리하는 방법:

**방법 1: 이슈 라벨 사용**

```
라벨: epic:database-migration
관련 이슈들에 동일한 epic 라벨 추가
```

**방법 2: Milestones 사용**

```
Milestone: "Core Infrastructure"
관련 이슈들을 마일스톤에 할당
```

**방법 3: Tracking Issue (추천)**

```
타이틀: "[EPIC] 데이터베이스 마이그레이션"
본문에 체크리스트로 관련 이슈 링크:
- [ ] #1 데이터베이스 스키마 설계
- [ ] #2 초기 마이그레이션 실행
- [ ] #3 샘플 데이터 시드 생성
```

---

## 👁️ 뷰(View) 설정

GitHub Projects v2는 다양한 뷰를 지원합니다. 용도별로 여러 뷰를 생성하세요.

### 1. Board View (Kanban) - 기본

```
용도: 일일 작업 진행 상황 추적
설정:
  - Group by: Status
  - Filter: is:open
  - Sort: Priority (descending)
```

### 2. Table View (스프레드시트)

```
용도: 전체 이슈 목록 및 메타데이터 관리
설정:
  - Columns: Title, Status, Priority, Type, Area, Assignee, Milestone
  - Filter: is:open
  - Sort: Priority (descending), Created (ascending)
```

### 3. Sprint View

```
용도: 현재 스프린트 작업 관리
설정:
  - Group by: Status
  - Filter: Sprint = "Sprint 1" AND is:open
  - Sort: Priority (descending)
```

### 4. Roadmap View (타임라인)

```
용도: 장기 계획 및 마일스톤 추적
설정:
  - Layout: Roadmap
  - Group by: Milestone
  - Date field: Milestone due date
  - Filter: is:open OR closed:>2024-01-01
```

### 5. Priority View

```
용도: 우선순위별 작업 분류
설정:
  - Group by: Priority
  - Filter: is:open
  - Sort: Created (descending)
```

### 6. Team View

```
용도: 팀원별 작업 배분 확인
설정:
  - Group by: Backend Owner
  - Filter: is:open
  - Sort: Priority (descending)
```

### 7. FE Dependency View

```
용도: 프론트엔드 의존성 작업 추적
설정:
  - Filter: "FE Dependency" is not "None"
  - Group by: FE Dependency
  - Sort: Priority (descending)
```

### 뷰 생성 방법

```
1. 프로젝트에서 현재 뷰 이름 옆 "▼" 클릭
2. "New view" 선택
3. 뷰 타입 선택 (Board, Table, Roadmap)
4. 필터, 그룹, 정렬 설정
5. "Save changes" 클릭
```

---

## 🤖 자동화(Automation) 설정

GitHub Projects의 자동화 기능으로 반복 작업을 줄이세요.

### 기본 자동화 활성화

```
1. 프로젝트 설정 (⚙️) > "Workflows" 클릭
2. 다음 자동화 활성화:

✅ Auto-add to project
   - 새 이슈/PR이 생성되면 자동으로 프로젝트에 추가
   - Filter: repo:username/loops-api

✅ Item added to project
   - 새 아이템이 추가되면 "Backlog" 컬럼으로 이동

✅ Item closed
   - 이슈/PR이 닫히면 "Done" 컬럼으로 이동

✅ Pull request merged
   - PR이 머지되면 "Done" 컬럼으로 이동
   - 연결된 이슈도 자동으로 닫힘 (본문에 "Closes #123" 포함 시)

✅ Code changes requested
   - PR에 변경 요청이 있으면 "In Progress"로 이동

✅ Pull request approved
   - PR이 승인되면 "Ready to merge" 상태로 변경
```

### 커스텀 자동화 (GitHub Actions)

고급 자동화를 위해 GitHub Actions 사용:

**.github/workflows/project-automation.yml**

```yaml
name: Project Automation

on:
  issues:
    types: [opened, labeled, assigned]
  pull_request:
    types: [opened, review_requested, closed]

jobs:
  auto-assign-priority:
    runs-on: ubuntu-latest
    steps:
      - name: Auto-assign priority based on labels
        uses: actions/github-script@v6
        with:
          script: |
            const issue = context.payload.issue || context.payload.pull_request;
            const labels = issue.labels.map(l => l.name);

            // Critical 라벨이 있으면 높은 우선순위 할당
            if (labels.includes('priority:critical')) {
              // Project API를 통해 Priority 필드 업데이트
              // (GitHub Projects GraphQL API 사용)
            }

  notify-fe-dependencies:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'fe-dependency')
    steps:
      - name: Notify FE team
        uses: actions/github-script@v6
        with:
          script: |
            // FE 레포지토리에 이슈 생성 또는 코멘트 추가
            github.rest.issues.create({
              owner: 'your-org',
              repo: 'loops-fe',
              title: `[BE Dependency] ${context.payload.issue.title}`,
              body: `백엔드 작업이 완료되었습니다: ${context.payload.issue.html_url}`
            });
```

---

## 🤝 FE-BE 협업 방법

프론트엔드와 백엔드가 별도 레포지토리일 때 협업 전략:

### 방법 1: Cross-Repository Issues 링크

**백엔드 이슈에서 프론트엔드 이슈 참조:**

```markdown
# Backend Issue #15: User Authentication API

## Description

JWT 기반 사용자 인증 API 구현

## Frontend Dependencies

- 프론트엔드 이슈: username/loops-fe#23
- API 명세: [링크]

## API Endpoints

- POST /api/v1/auth/login
- POST /api/v1/auth/register
- GET /api/v1/auth/me
```

**프론트엔드 이슈에서 백엔드 이슈 참조:**

```markdown
# Frontend Issue #23: Login Page Implementation

## Description

로그인 페이지 UI 및 API 연동

## Backend Dependencies

- 백엔드 이슈: username/loops-api#15
- Blocked until: API 엔드포인트 완료
```

### 방법 2: 통합 GitHub Project (추천)

**Organization-level Project 생성:**

```
1. GitHub Organization에서 새 프로젝트 생성
2. 프로젝트 이름: "Loops - Full Stack Development"
3. 양쪽 레포지토리의 이슈를 모두 추가
4. 커스텀 필드로 "Repository" 추가 (Backend/Frontend 구분)

뷰 설정:
- Backend View: Filter by Repository = "loops-api"
- Frontend View: Filter by Repository = "loops-fe"
- Integration View: Filter by "fe-dependency" or "be-dependency" label
```

### 방법 3: API 명세 공유

**OpenAPI/Swagger 문서를 활용한 협업:**

```
1. 백엔드에서 API 명세 자동 생성
   - FastAPI는 자동으로 /docs 엔드포인트 제공
   - OpenAPI JSON: /openapi.json

2. API 변경사항을 이슈/PR에 명시
   - Breaking changes는 반드시 FE 팀에 알림
   - API 버전 관리 (/api/v1, /api/v2)

3. Mock Server 제공 (개발 초기)
   - Prism 또는 MSW 사용
   - FE가 BE 완료 전에 개발 가능
```

### 방법 4: Slack/Discord 통합

**GitHub 알림을 팀 채팅에 연동:**

```
Slack Integration:
1. Slack Workspace에 GitHub 앱 추가
2. 채널 생성: #loops-backend, #loops-frontend, #loops-integration
3. 구독 설정:
   /github subscribe username/loops-api issues,pulls,commits
   /github subscribe username/loops-fe issues,pulls,commits

Discord Integration:
- Webhooks를 사용하여 이슈/PR 알림 전송
```

### 방법 5: 정기 동기화 미팅

```
Weekly Sync Meeting:
- 백엔드 완료된 API 리뷰
- 프론트엔드 필요 API 요청
- 블로킹 이슈 해결
- 다음 주 계획 공유

도구:
- GitHub Projects의 Roadmap View 화면 공유
- API 문서 (/docs) 함께 보기
```

---

## 🔄 워크플로우 예시

### 일반적인 개발 워크플로우

```
1️⃣ 이슈 생성 및 계획
   - 새 기능/버그를 이슈로 생성
   - 라벨, 우선순위, 담당자 할당
   - 자동으로 "Backlog" 컬럼에 추가됨

2️⃣ 작업 시작
   - 이슈를 "Ready" 또는 "In Progress"로 이동
   - 브랜치 생성: git checkout -b feature/issue-15-auth-api
   - 이슈 번호를 브랜치명에 포함

3️⃣ 개발
   - 코드 작성 및 테스트
   - 커밋 메시지에 이슈 참조: "feat: add login endpoint #15"

4️⃣ Pull Request 생성
   - PR 생성 시 이슈 연결
   - PR 본문에 "Closes #15" 추가 (자동 닫힘)
   - PR이 자동으로 "In Review" 컬럼으로 이동

5️⃣ 코드 리뷰
   - 팀원이 리뷰
   - 변경 요청 시 "In Progress"로 자동 이동
   - 승인 시 "Ready to merge" 상태로 변경

6️⃣ 머지 및 배포
   - PR 머지
   - 연결된 이슈가 자동으로 닫힘
   - "Done" 컬럼으로 자동 이동

7️⃣ 배포 및 검증
   - CI/CD 파이프라인 실행
   - 스테이징 환경에서 테스트
   - 프로덕션 배포
```

### 긴급 버그 수정 워크플로우

```
1️⃣ 버그 이슈 생성
   - 라벨: bug, priority:critical
   - 자동으로 높은 우선순위로 표시

2️⃣ 핫픽스 브랜치 생성
   - git checkout -b hotfix/issue-42-fix-auth-bug main

3️⃣ 빠른 수정 및 테스트
   - 최소한의 변경으로 버그 수정
   - 테스트 추가

4️⃣ 긴급 PR 및 리뷰
   - PR 생성 및 즉시 리뷰 요청
   - 빠른 승인 후 머지

5️⃣ 즉시 배포
   - 프로덕션에 핫픽스 배포
   - 모니터링 강화
```

---

## 📊 프로젝트 인사이트 활용

GitHub Projects는 자동으로 차트와 인사이트를 제공합니다.

### 유용한 차트

```
1. Insights 탭 클릭

추천 차트:

📈 Burndown Chart
   - 스프린트 진행 상황 추적
   - 남은 작업량 시각화

📊 Velocity Chart
   - 완료된 작업의 속도 측정
   - 다음 스프린트 계획에 활용

🥧 Distribution by Priority
   - 우선순위별 이슈 분포
   - 리소스 배분 확인

📉 Cycle Time
   - 이슈 생성부터 완료까지 소요 시간
   - 병목 지점 파악

🔄 Cumulative Flow
   - 각 상태별 작업 누적량
   - 워크플로우 균형 확인
```

---

## 🎯 초기 세팅 체크리스트

백엔드 프로젝트를 시작하기 전에 확인하세요:

- [ ] GitHub Project 생성 완료
- [ ] 기본 컬럼 구조 설정 (Backlog, Ready, In Progress, In Review, Done, Blocked)
- [ ] 커스텀 필드 추가 (Priority, Type, Area, Sprint, Owner, Estimate)
- [ ] 기본 자동화 활성화
- [ ] GITHUB_ISSUES_TEMPLATE.md의 이슈들 생성 및 프로젝트에 연결
- [ ] 여러 뷰 생성 (Board, Table, Sprint, Roadmap, Priority, Team)
- [ ] 마일스톤 생성 (Core Infrastructure, Database Migration, Deck System, Analytics & AI)
- [ ] 라벨 체계 정리 (priority, type, area, epic)
- [ ] FE 팀과 협업 방법 합의
- [ ] (선택) Organization-level 통합 프로젝트 생성
- [ ] (선택) Slack/Discord 통합 설정
- [ ] 팀원 초대 및 권한 설정

---

## 📚 추가 리소스

- [GitHub Projects 공식 문서](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Projects Best Practices](https://github.blog/2022-07-27-planning-next-to-your-code-github-projects-is-now-generally-available/)
- [GitHub CLI로 프로젝트 관리](https://cli.github.com/manual/gh_project)
- [GitHub Actions로 프로젝트 자동화](https://github.com/actions/add-to-project)

---

## 🔗 관련 문서

- [GITHUB_ISSUES_TEMPLATE.md](./GITHUB_ISSUES_TEMPLATE.md) - 이슈 템플릿
- [DEVELOPMENT.md](./DEVELOPMENT.md) - 개발 가이드
- [API.md](./API.md) - API 문서
- [README.md](../README.md) - 프로젝트 개요
