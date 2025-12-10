# Loops API 유저 스토리

> 최종 업데이트: 2025-12-10

## 도메인별 문서

| 도메인 | 파일 | 엔드포인트 |
|--------|------|-----------|
| 인증 | [01-authentication.md](./01-authentication.md) | `/auth/*` |
| 프로필 | [02-profile.md](./02-profile.md) | `/profiles/*` |
| 단어 카드 | [03-vocabulary-cards.md](./03-vocabulary-cards.md) | `/cards/*` |
| 덱 | [04-decks.md](./04-decks.md) | `/decks/*` |
| 통계 | [07-statistics.md](./07-statistics.md) | `/stats/*` |
| 학습 | [08-study-session.md](./08-study-session.md) | `/study/*` |

---

## 핵심 플로우: 학습 세션

```text
1. GET  /study/overview        → 오늘 학습할 카드 수 확인
2. POST /study/session/start   → session_id 발급
3. POST /study/session/card    → 퀴즈 조회 (반복)
4. POST /study/session/answer  → 정답 제출 + FSRS (반복)
5. POST /study/session/complete → XP/스트릭/일일목표 반영
```

---

## 빠른 참조

### 인증

- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인
- `GET /auth/me` - 현재 사용자

### 학습

- `GET /study/overview` - 학습 현황
- `GET /study/cards/{id}` - 카드 진행
- `POST /study/session/*` - 세션 관리

### 통계

- `GET /stats/total-learned` - 총 학습량
- `GET /stats/history` - 학습 기록
- `GET /profiles/me/streak` - 스트릭
