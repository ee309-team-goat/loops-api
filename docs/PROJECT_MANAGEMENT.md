# 프로젝트 관리 가이드

Loops API 프로젝트를 효율적으로 관리하기 위한 실전 가이드입니다.

## 📋 목차

- [빠른 시작](#-빠른-시작)
- [이슈 관리](#-이슈-관리)
- [Pull Request 워크플로우](#-pull-request-워크플로우)
- [프로젝트 보드 운영](#-프로젝트-보드-운영)
- [라벨 시스템](#-라벨-시스템)
- [마일스톤 관리](#-마일스톤-관리)
- [자동화 기능](#-자동화-기능)
- [팀 협업 규칙](#-팀-협업-규칙)
- [정기 점검 체크리스트](#-정기-점검-체크리스트)

---

## 🚀 빠른 시작

### 초기 설정 (최초 1회)

```bash
# 1. GitHub Projects 생성
# - GitHub 레포 > Projects 탭 > New project
# - 템플릿: Board 선택
# - 이름: "Loops API - Backend Development"

# 2. Personal Access Token (PAT) 생성
# - GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
# - 권한: repo, project
# - 생성된 토큰을 레포 Secrets에 ADD_TO_PROJECT_PAT로 저장

# 3. 워크플로우 파일 수정
# - .github/workflows/project-automation.yml 열기
# - YOUR_USERNAME과 YOUR_PROJECT_NUMBER를 실제 값으로 수정
```

**프로젝트 URL 찾는 방법:**
```
예: https://github.com/users/yourusername/projects/1
여기서 YOUR_USERNAME = yourusername
YOUR_PROJECT_NUMBER = 1
```

### 일상적인 작업 흐름

```
1. 이슈 생성 → 자동으로 프로젝트에 추가
2. 이슈를 "Ready"로 이동 → 작업 준비 완료
3. 브랜치 생성 및 개발 → feature/issue-123-description
4. PR 생성 → 자동으로 라벨 추가, 마이그레이션 체크
5. 리뷰 → 승인되면 머지
6. 머지 → 이슈 자동 닫힘, "Done"으로 이동
```

---

## 📝 이슈 관리

### 이슈 생성

**방법 1: GitHub 웹 인터페이스 (추천)**

```
1. Issues 탭 > New issue
2. 템플릿 선택:
   - Feature Request: 새로운 기능
   - Bug Report: 버그 수정
3. 템플릿 양식 작성
4. Submit new issue
```

**방법 2: GitHub CLI**

```bash
# 기능 요청 이슈 생성
gh issue create \
  --title "[FEATURE] User profile page" \
  --label "type:feature,priority:high,area:api" \
  --assignee @me

# 버그 리포트 이슈 생성
gh issue create \
  --title "[BUG] Login returns 500 error" \
  --label "type:bug,priority:critical,area:auth" \
  --assignee @me
```

### 이슈 제목 규칙

```
[TYPE] 간단하고 명확한 설명

좋은 예:
✅ [FEATURE] Add FSRS review scheduling endpoint
✅ [BUG] Fix JWT token expiration issue
✅ [REFACTOR] Optimize user card progress query

나쁜 예:
❌ fix bug
❌ update code
❌ 기능 추가
```

### 이슈 본문 작성 팁

```markdown
# 좋은 이슈 본문의 특징:

1. 명확한 설명
   - 무엇을 하려는지 한 문장으로 요약
   - 왜 필요한지 배경 설명

2. 구체적인 요구사항
   - 체크리스트 형태로 작업 항목 나열
   - [ ] 첫 번째 작업
   - [ ] 두 번째 작업

3. 기술적 세부사항
   - API 엔드포인트, 데이터베이스 스키마 등
   - 코드 블록 사용

4. 연관 정보
   - 관련 이슈: #123, #456
   - 참고 문서 링크
   - 프론트엔드 의존성 명시
```

### 이슈 할당

```bash
# 나에게 할당
gh issue edit 123 --add-assignee @me

# 특정 팀원에게 할당
gh issue edit 123 --add-assignee username

# 여러 명에게 할당 (페어 프로그래밍)
gh issue edit 123 --add-assignee user1,user2
```

### 이슈 상태 변경

```
Backlog     → 아직 시작 안 함, 우선순위 낮음
Ready       → 작업 준비 완료, 바로 시작 가능
In Progress → 현재 작업 중
In Review   → PR 생성됨, 리뷰 대기
Done        → 완료 (PR 머지됨)
Blocked     → 블로킹됨 (외부 의존성, FE 대기 등)
```

---

## 🔀 Pull Request 워크플로우

### PR 생성 전 체크리스트

```bash
# 1. 최신 main 브랜치 동기화
git checkout main
git pull origin main

# 2. 브랜치 생성 (이슈 번호 포함)
git checkout -b feature/issue-123-add-review-endpoint

# 3. 개발 및 테스트
just dev
# 코드 작성...
just db-test

# 4. 마이그레이션 필요 시 생성
just revision "add review_history table"
just migrate

# 5. 커밋 (의미 있는 메시지)
git add .
git commit -m "feat: add FSRS review scheduling endpoint #123"

# 6. 푸시
git push origin feature/issue-123-add-review-endpoint
```

### PR 생성

```bash
# GitHub CLI로 PR 생성
gh pr create \
  --title "[FEATURE] Add FSRS review scheduling endpoint" \
  --body "Closes #123" \
  --label "type:feature,area:api"

# 웹에서도 가능 (자동으로 PR 템플릿 로드됨)
```

### PR 본문 작성

**PR 템플릿이 자동으로 로드됩니다. 각 섹션을 채워주세요:**

```markdown
## 📝 변경 사항
FSRS 알고리즘 기반 카드 복습 스케줄링 API 추가

## 🔗 관련 이슈
Closes #123

## 🎯 변경 타입
- [x] ✨ Feature

## 🧪 테스트 방법
\`\`\`bash
curl -X POST http://localhost:8000/api/v1/progress/review \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"card_id": 1, "rating": 3}'
\`\`\`

## ✅ 체크리스트
- [x] 코드가 정상적으로 동작합니다
- [x] 새로운 테스트를 추가했습니다
- [x] API.md 문서를 업데이트했습니다
- [ ] 프론트엔드 팀에 알림이 필요합니다 ← FE에 알려야 할 경우 체크
```

### 커밋 메시지 규칙

```
<type>: <subject> #<issue-number>

Type:
- feat: 새로운 기능
- fix: 버그 수정
- refactor: 리팩토링
- docs: 문서 수정
- test: 테스트 추가/수정
- style: 코드 포맷팅
- chore: 빌드, 설정 등

예시:
✅ feat: add user profile endpoint #45
✅ fix: resolve JWT token expiration bug #78
✅ refactor: optimize database query in UserService #92
✅ docs: update API documentation for auth endpoints #103
```

### 코드 리뷰

**리뷰어 역할:**

```
1. 코드 품질 확인
   - 버그 가능성
   - 성능 이슈
   - 보안 취약점

2. 설계 검토
   - 아키텍처 일관성
   - 확장성
   - 유지보수성

3. 테스트 확인
   - 충분한 테스트 커버리지
   - 엣지 케이스 처리

4. 문서 확인
   - API 문서 업데이트
   - 코드 주석 (필요 시)
```

**리뷰 요청:**

```bash
# 특정 사람에게 리뷰 요청
gh pr review 123 --request @username

# 여러 명에게 요청
gh pr review 123 --request @user1,@user2
```

**리뷰 응답:**

```bash
# 승인
gh pr review 123 --approve --body "LGTM! 👍"

# 변경 요청
gh pr review 123 --request-changes --body "마이그레이션 파일 추가가 필요합니다"

# 코멘트만
gh pr review 123 --comment --body "질문: 이 부분은 왜 이렇게 구현하셨나요?"
```

### PR 머지

```bash
# PR 머지 (squash merge 권장)
gh pr merge 123 --squash --delete-branch

# 머지 후 자동으로:
# - 연결된 이슈 닫힘
# - 프로젝트 보드에서 "Done"으로 이동
# - 브랜치 삭제
```

---

## 📊 프로젝트 보드 운영

### 보드 뷰 활용

**1. Board View (Kanban) - 일일 스탠드업**

```
매일 아침 확인:
- In Progress: 어제 작업한 것, 오늘 할 것
- Ready: 다음에 시작할 작업
- Blocked: 블로킹 해결 필요
- In Review: 리뷰 독려
```

**2. Sprint View - 스프린트 계획**

```
스프린트 시작 시:
1. Sprint 필드를 "Sprint 1"로 설정
2. Ready에서 작업 선택
3. Sprint View에서 진행 상황 추적
4. 스프린트 종료 시 완료/미완료 확인
```

**3. Priority View - 우선순위 관리**

```
주간 계획 시:
1. Critical: 즉시 처리
2. High: 이번 주 내 처리
3. Medium: 다음 주 고려
4. Low: 백로그 유지
```

**4. Roadmap View - 장기 계획**

```
마일스톤별 진행 상황:
- Core Infrastructure (v0.1)
- Database Migration (v0.2)
- Deck System (v0.3)
- Analytics & AI (v1.0)
```

### 컬럼 이동 규칙

```
수동으로 이동해야 하는 경우:
- Backlog → Ready: 작업 준비됨
- Ready → In Progress: 작업 시작
- In Progress → Blocked: 블로킹 발생

자동으로 이동하는 경우:
- (any) → In Review: PR 생성 시
- In Review → Done: PR 머지 시
- In Review → In Progress: 변경 요청 시
```

### 정기 보드 정리 (주간)

```
매주 금요일:
1. Done 컬럼 정리
   - 오래된 항목 아카이브
   - 이번 주 완료 항목 리뷰

2. Blocked 컬럼 확인
   - 블로킹 이유 재확인
   - 해결 방안 논의
   - 오래 블록된 항목 우선순위 재조정

3. Backlog 우선순위 재조정
   - 새로운 이슈 검토
   - 우선순위 업데이트
   - 다음 주 Ready로 이동할 항목 선정

4. Sprint 회고
   - 완료된 작업 개수
   - 속도(Velocity) 측정
   - 다음 스프린트 계획
```

---

## 🏷️ 라벨 시스템

### 라벨 체계

**Priority (우선순위)**

```
priority:critical  🔴  즉시 처리 필요 (서비스 중단, 심각한 버그)
priority:high      🟠  빠른 시일 내 처리 (주요 기능)
priority:medium    🟡  보통 (일반 기능, 개선)
priority:low       🟢  나중에 (nice-to-have)
```

**Type (작업 타입)**

```
type:feature    ✨  새로운 기능
type:bug        🐛  버그 수정
type:refactor   🔧  리팩토링
type:docs       📝  문서
type:test       🧪  테스트
type:chore      🔨  빌드, 설정 등
```

**Area (작업 영역)**

```
area:database   🗄️  데이터베이스 (모델, 마이그레이션)
area:api        🌐  API 엔드포인트
area:service    ⚙️  비즈니스 로직
area:ai         🤖  AI 기능
area:analytics  📊  분석, 통계
area:auth       🔐  인증, 보안
```

**Status (상태)**

```
status:blocked       🚫  블로킹됨
status:help-wanted   🆘  도움 필요
status:good-first    👶  초보자 친화적
status:breaking      💥  Breaking change
```

**FE Dependency**

```
fe-blocks    ⬅️  FE가 이 작업을 기다려야 함
fe-blocked   ➡️  FE 작업이 먼저 필요함
fe-parallel  ↔️  동시 진행 가능
```

### 라벨 자동 추가

**GitHub Actions가 자동으로 라벨 추가:**

```
PR 생성 시:
- alembic/, models/ 변경 → area:database
- api/ 변경 → area:api
- services/ 변경 → area:service
- test 파일 변경 → type:test
- .md 파일 변경 → type:docs
```

### 라벨 수동 추가

```bash
# 라벨 추가
gh issue edit 123 --add-label "priority:high,area:api"

# 라벨 제거
gh issue edit 123 --remove-label "priority:low"

# 라벨로 이슈 검색
gh issue list --label "priority:critical"
gh issue list --label "type:bug,area:auth"
```

---

## 🎯 마일스톤 관리

### 마일스톤 목록

```
Milestone 1: Core Infrastructure (v0.1)
- 기간: 2주
- 목표: 기본 프로젝트 설정 완료
- 이슈: #1, #2, #3

Milestone 2: Database Migration (v0.2)
- 기간: 1주
- 목표: 모든 테이블 마이그레이션 완료
- 이슈: #4, #5, #6

Milestone 3: Deck System (v0.3)
- 기간: 2주
- 목표: 덱 관리 기능 완료
- 이슈: #7, #8, #9

Milestone 4: Analytics & AI (v1.0)
- 기간: 3주
- 목표: 분석 및 AI 기능 완료
- 이슈: #10, #11, #12
```

### 마일스톤 진행 상황 확인

```bash
# 마일스톤 목록 보기
gh api repos/:owner/:repo/milestones

# 특정 마일스톤의 이슈 보기
gh issue list --milestone "Core Infrastructure"

# 진행률 확인 (완료/전체)
# GitHub 웹에서 Milestones 탭에서 확인
```

### 마일스톤 변경

```bash
# 이슈에 마일스톤 할당
gh issue edit 123 --milestone "Core Infrastructure"

# 마일스톤 제거
gh issue edit 123 --milestone ""
```

---

## 🤖 자동화 기능

프로젝트에 적용된 자동화 기능들입니다.

### 1. 이슈/PR 자동 추가

```yaml
이슈 또는 PR 생성 시
→ 자동으로 프로젝트 보드에 추가
→ Backlog 컬럼으로 이동
```

### 2. 우선순위 자동 라벨링

```yaml
이슈 본문에 "Critical" 또는 "즉시 필요" 포함 시
→ priority:critical 라벨 자동 추가
```

### 3. FE 팀 알림

```yaml
이슈 본문에 "Blocks FE" 포함 시
→ 프론트엔드 팀에게 알림 코멘트 자동 생성
```

### 4. PR 자동 라벨링

```yaml
PR 생성 시
→ 변경된 파일 경로 분석
→ area:database, area:api 등 라벨 자동 추가
```

### 5. 마이그레이션 체크

```yaml
models/ 파일 변경 + alembic/versions/ 변경 없음
→ 마이그레이션 필요 여부 알림 코멘트
```

### 6. PR 머지 시 이슈 업데이트

```yaml
PR이 머지됨
→ "Closes #123" 형태의 이슈 자동 닫힘
→ 완료 코멘트 자동 추가
→ Done 컬럼으로 이동
```

### 7. 리뷰 변경 요청 알림

```yaml
PR 리뷰에서 변경 요청
→ PR 작성자에게 알림 코멘트
```

### 자동화 커스터마이징

`.github/workflows/project-automation.yml` 파일을 수정하여 자동화를 추가하거나 변경할 수 있습니다.

---

## 👥 팀 협업 규칙

### 코드 오너십

```
모든 PR은 최소 1명의 승인 필요
특정 영역은 전문가 리뷰 권장:
- Database: @db-expert
- AI: @ai-expert
- Security: @security-expert
```

### 리뷰 에티켓

```
리뷰어:
- 건설적인 피드백 제공
- 질문은 "왜?"로 시작
- 칭찬도 잊지 말기
- 24시간 내 리뷰 완료

작성자:
- 리뷰 코멘트에 신속히 응답
- 변경 사항 설명
- 동의하지 않을 땐 정중히 토론
```

### 커뮤니케이션 채널

```
GitHub Issues:
- 기능 요청, 버그 리포트
- 공식 기록이 필요한 논의

GitHub Discussions:
- 아이디어 브레인스토밍
- 기술적 질문
- 일반 토론

Slack/Discord:
- 긴급 이슈
- 빠른 질문
- 데일리 스탠드업

Weekly Sync:
- 진행 상황 공유
- 블로킹 이슈 해결
- 다음 주 계획
```

### FE-BE 협업 프로세스

```
1. API 설계 단계
   - 백엔드: API 명세 작성 (OpenAPI)
   - 프론트엔드: 명세 리뷰 및 피드백
   - 합의 후 이슈 생성

2. 개발 단계
   - 백엔드: API 구현, Mock 데이터 제공
   - 프론트엔드: Mock 서버로 병렬 개발
   - 서로 이슈에 진행 상황 코멘트

3. 통합 단계
   - 백엔드 PR 머지 후 FE에 알림
   - 프론트엔드: 실제 API 연동 테스트
   - 이슈 발견 시 버그 리포트

4. 배포 단계
   - 백엔드 먼저 배포 (하위 호환성 유지)
   - 프론트엔드 배포
   - 함께 검증
```

---

## 📅 정기 점검 체크리스트

### 일일 체크 (매일 아침)

```
[ ] 프로젝트 보드 확인
    - In Progress: 어제 작업, 오늘 할 일
    - Blocked: 블로킹 이슈 확인
    - In Review: 리뷰 필요한 PR 확인

[ ] 새 이슈/PR 확인
    - 할당된 이슈 확인
    - 리뷰 요청된 PR 확인
    - 알림 확인

[ ] 긴급 이슈 우선 처리
    - priority:critical 이슈 확인
    - 즉시 처리 가능한지 판단
```

### 주간 체크 (매주 금요일)

```
[ ] 이번 주 완료 항목 리뷰
    - Done 컬럼 확인
    - 완료한 이슈 개수 확인
    - 속도(Velocity) 측정

[ ] 프로젝트 보드 정리
    - Blocked 컬럼 검토
    - 오래된 Done 항목 아카이브
    - Backlog 우선순위 재조정

[ ] 다음 주 계획
    - Ready 컬럼에 작업 추가
    - Sprint 할당
    - 팀원 간 작업 분배

[ ] 문서 업데이트
    - API.md 최신화
    - README.md 확인
    - CHANGELOG 작성 (필요 시)
```

### 월간 체크 (매월 말)

```
[ ] 마일스톤 진행 상황
    - 각 마일스톤 완료율 확인
    - 지연된 마일스톤 조정
    - 다음 달 마일스톤 계획

[ ] 프로젝트 인사이트 확인
    - Burndown Chart 확인
    - Cycle Time 분석
    - 병목 지점 파악

[ ] 프로세스 개선
    - 자동화 추가 필요한 부분 확인
    - 라벨 체계 개선
    - 팀 피드백 수집

[ ] 기술 부채 관리
    - Refactor 필요 항목 이슈화
    - 테스트 커버리지 확인
    - 보안 업데이트 확인
```

### 릴리스 전 체크

```
[ ] 모든 마일스톤 이슈 완료
[ ] 테스트 통과
[ ] 문서 업데이트
[ ] CHANGELOG 작성
[ ] 마이그레이션 검증
[ ] 배포 계획 수립
[ ] 롤백 계획 준비
[ ] 팀 공지
```

---

## 📊 성과 측정

### 추적할 메트릭

```
속도 (Velocity):
- 주당 완료한 이슈 개수
- 스토리 포인트 (설정 시)

사이클 타임 (Cycle Time):
- 이슈 생성부터 완료까지 평균 시간
- 목표: 일주일 이내

리뷰 시간:
- PR 생성부터 머지까지 평균 시간
- 목표: 24시간 이내

품질:
- 버그 이슈 비율
- 재작업 필요 PR 비율
```

### GitHub Insights 활용

```
프로젝트 > Insights 탭에서 확인:
- Burndown Chart: 스프린트 진행
- Velocity: 완료 속도
- Cumulative Flow: 워크플로우 균형
- Cycle Time: 평균 소요 시간
```

---

## 🛠️ 트러블슈팅

### 자동화가 작동하지 않을 때

```
1. Workflow 실행 로그 확인
   - GitHub > Actions 탭
   - 실패한 workflow 클릭
   - 에러 메시지 확인

2. PAT 토큰 확인
   - Settings > Secrets > ADD_TO_PROJECT_PAT
   - 만료되지 않았는지 확인
   - 권한(repo, project) 확인

3. Workflow 파일 확인
   - .github/workflows/project-automation.yml
   - YOUR_USERNAME, YOUR_PROJECT_NUMBER 올바른지 확인
```

### 이슈가 프로젝트에 추가되지 않을 때

```
1. 프로젝트 URL 확인
2. PAT 권한 확인
3. 수동으로 추가 후 자동화 재설정
```

### PR이 머지되었는데 이슈가 안 닫힐 때

```
PR 본문에 다음 키워드 사용:
- Closes #123
- Fixes #123
- Resolves #123

(주의: "Close #123", "Fix #123"는 작동 안 함)
```

---

## 📚 추가 리소스

- **[GITHUB_PROJECTS_SETUP.md](./GITHUB_PROJECTS_SETUP.md)** - GitHub Projects 초기 설정
- **[GITHUB_ISSUES_TEMPLATE.md](./GITHUB_ISSUES_TEMPLATE.md)** - 이슈 템플릿 목록
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - 개발 가이드
- **[API.md](./API.md)** - API 문서

---

## 📞 도움이 필요할 때

```
1. 문서 먼저 확인
   - docs/ 폴더의 관련 문서 읽기
   - README.md의 FAQ 확인

2. GitHub Discussions 활용
   - 질문 올리기
   - 다른 사람의 질문 검색

3. 이슈 생성
   - 공식 기록이 필요한 경우
   - 버그나 기능 요청

4. 팀에 문의
   - Slack/Discord에서 빠른 질문
   - Weekly Sync에서 논의
```

---

**이 문서는 프로젝트가 진행되면서 계속 업데이트됩니다.**

마지막 업데이트: 2025-01-20
