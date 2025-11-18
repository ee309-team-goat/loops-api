CREATE TYPE "card_state_enum" AS ENUM (
  'new',
  'learning',
  'review',
  'relearning'
);

CREATE TYPE "operation_type_enum" AS ENUM (
  'CREATE',
  'UPDATE',
  'DELETE'
);

CREATE TYPE "subscription_type_enum" AS ENUM (
  'free',
  'premium',
  'enterprise'
);

CREATE TABLE "users" (
  "id" SERIAL PRIMARY KEY,
  "email" "VARCHAR(255)" UNIQUE NOT NULL,
  "username" "VARCHAR(100)" UNIQUE NOT NULL,
  "hashed_password" "VARCHAR(255)" NOT NULL,
  "full_name" "VARCHAR(255)",
  "occupation" "VARCHAR(100)",
  "language_level" "VARCHAR(50)",
  "learning_goal" TEXT,
  "subscription_type" subscription_type_enum DEFAULT 'free',
  "is_active" BOOLEAN DEFAULT true,
  "is_verified" BOOLEAN DEFAULT false,
  "is_premium" BOOLEAN DEFAULT false,
  "current_streak" INTEGER DEFAULT 0,
  "longest_streak" INTEGER DEFAULT 0,
  "last_study_date" DATE,
  "total_cards_learned" INTEGER DEFAULT 0,
  "total_study_time_minutes" INTEGER DEFAULT 0,
  "created_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "updated_at" TIMESTAMP,
  "last_login_at" TIMESTAMP
);

CREATE TABLE "decks" (
  "id" SERIAL PRIMARY KEY,
  "name" "VARCHAR(255)" NOT NULL,
  "description" TEXT,
  "category" "VARCHAR(100)",
  "difficulty_level" "VARCHAR(50)",
  "is_public" BOOLEAN DEFAULT false,
  "is_official" BOOLEAN DEFAULT false,
  "creator_id" INTEGER,
  "card_count" INTEGER DEFAULT 0,
  "learning_count" INTEGER DEFAULT 0,
  "created_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "updated_at" TIMESTAMP
);

CREATE TABLE "user_decks" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "deck_id" INTEGER NOT NULL,
  "is_active" BOOLEAN DEFAULT true,
  "cards_new" INTEGER DEFAULT 0,
  "cards_learning" INTEGER DEFAULT 0,
  "cards_review" INTEGER DEFAULT 0,
  "progress_percentage" REAL DEFAULT 0,
  "started_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "last_studied_at" TIMESTAMP
);

CREATE TABLE "vocabulary_cards" (
  "id" SERIAL PRIMARY KEY,
  "word" "VARCHAR(255)" NOT NULL,
  "translation" "VARCHAR(255)" NOT NULL,
  "part_of_speech" "VARCHAR(50)",
  "pronunciation_ipa" "VARCHAR(255)",
  "pronunciation_kr" "VARCHAR(255)",
  "definition_en" TEXT,
  "synonyms" JSONB,
  "antonyms" JSONB,
  "example_sentences" JSONB,
  "collocations" JSONB,
  "audio_url" "VARCHAR(500)",
  "image_url" "VARCHAR(500)",
  "difficulty_level" "VARCHAR(50)",
  "frequency_rank" INTEGER,
  "cefr_level" "VARCHAR(10)",
  "tags" JSONB,
  "deck_id" INTEGER,
  "source" "VARCHAR(255)",
  "usage_notes" TEXT,
  "etymology" TEXT,
  "is_verified" BOOLEAN DEFAULT false,
  "created_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "updated_at" TIMESTAMP
);

CREATE TABLE "user_card_progress" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "card_id" INTEGER NOT NULL,
  "easiness_factor" REAL NOT NULL DEFAULT 2.5,
  "interval" INTEGER NOT NULL DEFAULT 0,
  "repetitions" INTEGER NOT NULL DEFAULT 0,
  "stability" REAL DEFAULT 0,
  "difficulty" REAL DEFAULT 5,
  "next_review_date" TIMESTAMP NOT NULL,
  "last_review_date" TIMESTAMP,
  "scheduled_days" INTEGER DEFAULT 0,
  "total_reviews" INTEGER NOT NULL DEFAULT 0,
  "correct_count" INTEGER NOT NULL DEFAULT 0,
  "wrong_count" INTEGER NOT NULL DEFAULT 0,
  "accuracy_rate" REAL DEFAULT 0,
  "average_response_time" INTEGER DEFAULT 0,
  "quality_history" JSONB,
  "card_state" card_state_enum NOT NULL DEFAULT 'new',
  "lapses" INTEGER DEFAULT 0,
  "reps_since_lapse" INTEGER DEFAULT 0,
  "first_studied_at" TIMESTAMP,
  "mastered_at" TIMESTAMP,
  "created_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "updated_at" TIMESTAMP
);

CREATE TABLE "study_sessions" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "deck_id" INTEGER,
  "session_date" DATE NOT NULL,
  "started_at" TIMESTAMP NOT NULL,
  "ended_at" TIMESTAMP,
  "duration_minutes" INTEGER DEFAULT 0,
  "cards_studied" INTEGER DEFAULT 0,
  "cards_new" INTEGER DEFAULT 0,
  "cards_reviewed" INTEGER DEFAULT 0,
  "correct_answers" INTEGER DEFAULT 0,
  "wrong_answers" INTEGER DEFAULT 0,
  "accuracy_rate" REAL DEFAULT 0,
  "average_response_time" INTEGER DEFAULT 0,
  "device_type" "VARCHAR(50)",
  "created_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE "ai_interactions" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "card_id" INTEGER,
  "interaction_type" "VARCHAR(50)" NOT NULL,
  "user_input" TEXT,
  "ai_response" TEXT,
  "model_used" "VARCHAR(100)",
  "tokens_used" INTEGER,
  "response_time_ms" INTEGER,
  "feedback_rating" INTEGER,
  "created_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TABLE "sync_queue" (
  "id" SERIAL PRIMARY KEY,
  "user_id" INTEGER NOT NULL,
  "entity_type" "VARCHAR(50)" NOT NULL,
  "entity_id" INTEGER NOT NULL,
  "operation" operation_type_enum NOT NULL,
  "payload" JSONB NOT NULL,
  "retry_count" INTEGER NOT NULL DEFAULT 0,
  "max_retries" INTEGER NOT NULL DEFAULT 3,
  "is_synced" BOOLEAN NOT NULL DEFAULT false,
  "error_message" TEXT,
  "priority" INTEGER DEFAULT 0,
  "created_at" TIMESTAMP DEFAULT (CURRENT_TIMESTAMP),
  "synced_at" TIMESTAMP,
  "last_retry_at" TIMESTAMP
);

CREATE INDEX "idx_users_email" ON "users" ("email");

CREATE INDEX "idx_users_username" ON "users" ("username");

CREATE INDEX "idx_users_is_active" ON "users" ("is_active");

CREATE INDEX "idx_users_last_study" ON "users" ("last_study_date");

CREATE INDEX "idx_decks_category" ON "decks" ("category");

CREATE INDEX "idx_decks_is_public" ON "decks" ("is_public");

CREATE INDEX "idx_decks_creator" ON "decks" ("creator_id");

CREATE INDEX "idx_decks_public_official" ON "decks" ("is_public", "is_official");

CREATE UNIQUE INDEX "idx_user_decks_user_deck" ON "user_decks" ("user_id", "deck_id");

CREATE INDEX "idx_user_decks_user" ON "user_decks" ("user_id");

CREATE INDEX "idx_user_decks_deck" ON "user_decks" ("deck_id");

CREATE INDEX "idx_user_decks_active" ON "user_decks" ("user_id", "is_active");

CREATE INDEX "idx_vocabulary_cards_word" ON "vocabulary_cards" ("word");

CREATE INDEX "idx_vocabulary_cards_deck_id" ON "vocabulary_cards" ("deck_id");

CREATE INDEX "idx_vocabulary_cards_difficulty" ON "vocabulary_cards" ("difficulty_level");

CREATE INDEX "idx_vocabulary_cards_deck_word" ON "vocabulary_cards" ("deck_id", "word");

CREATE INDEX "idx_vocabulary_cards_frequency" ON "vocabulary_cards" ("frequency_rank");

CREATE INDEX "idx_vocabulary_cards_tags" ON "vocabulary_cards" USING GIN ("tags");

CREATE INDEX "idx_vocabulary_cards_examples" ON "vocabulary_cards" USING GIN ("example_sentences");

CREATE UNIQUE INDEX "idx_user_card_progress_unique" ON "user_card_progress" ("user_id", "card_id");

CREATE INDEX "idx_user_card_progress_user" ON "user_card_progress" ("user_id");

CREATE INDEX "idx_user_card_progress_card" ON "user_card_progress" ("card_id");

CREATE INDEX "idx_user_card_progress_next_review" ON "user_card_progress" ("user_id", "next_review_date");

CREATE INDEX "idx_user_card_progress_state" ON "user_card_progress" ("user_id", "card_state");

CREATE INDEX "idx_user_card_progress_due_cards" ON "user_card_progress" ("user_id", "card_state", "next_review_date");

CREATE INDEX "idx_user_card_progress_quality_history" ON "user_card_progress" USING GIN ("quality_history");

CREATE INDEX "idx_study_sessions_user" ON "study_sessions" ("user_id");

CREATE INDEX "idx_study_sessions_user_date" ON "study_sessions" ("user_id", "session_date");

CREATE INDEX "idx_study_sessions_deck" ON "study_sessions" ("deck_id");

CREATE INDEX "idx_study_sessions_date" ON "study_sessions" ("session_date");

CREATE INDEX "idx_ai_interactions_user" ON "ai_interactions" ("user_id");

CREATE INDEX "idx_ai_interactions_card" ON "ai_interactions" ("card_id");

CREATE INDEX "idx_ai_interactions_type" ON "ai_interactions" ("interaction_type");

CREATE INDEX "idx_ai_interactions_created" ON "ai_interactions" ("created_at");

CREATE INDEX "idx_sync_queue_user" ON "sync_queue" ("user_id");

CREATE INDEX "idx_sync_queue_pending" ON "sync_queue" ("user_id", "is_synced", "created_at");

CREATE INDEX "idx_sync_queue_entity" ON "sync_queue" ("entity_type", "entity_id");

CREATE INDEX "idx_sync_queue_priority" ON "sync_queue" ("is_synced", "priority", "created_at");

COMMENT ON COLUMN "users"."id" IS '사용자 고유 ID';

COMMENT ON COLUMN "users"."email" IS '사용자 이메일 (로그인용)';

COMMENT ON COLUMN "users"."username" IS '사용자명 (표시용)';

COMMENT ON COLUMN "users"."hashed_password" IS '해시된 비밀번호';

COMMENT ON COLUMN "users"."full_name" IS '사용자 실명';

COMMENT ON COLUMN "users"."occupation" IS '직업/직군 (맞춤형 단어 추천용)';

COMMENT ON COLUMN "users"."language_level" IS '영어 수준 (beginner/intermediate/advanced)';

COMMENT ON COLUMN "users"."learning_goal" IS '학습 목표 (AI 추천 최적화용)';

COMMENT ON COLUMN "users"."subscription_type" IS '구독 유형';

COMMENT ON COLUMN "users"."is_active" IS '계정 활성화 상태';

COMMENT ON COLUMN "users"."is_verified" IS '이메일 인증 여부';

COMMENT ON COLUMN "users"."is_premium" IS '프리미엄 사용자 여부';

COMMENT ON COLUMN "users"."current_streak" IS '현재 연속 학습 일수';

COMMENT ON COLUMN "users"."longest_streak" IS '최장 연속 학습 일수';

COMMENT ON COLUMN "users"."last_study_date" IS '마지막 학습 날짜 (streak 계산용)';

COMMENT ON COLUMN "users"."total_cards_learned" IS '총 학습한 카드 수';

COMMENT ON COLUMN "users"."total_study_time_minutes" IS '총 학습 시간 (분)';

COMMENT ON COLUMN "users"."created_at" IS '계정 생성 일시';

COMMENT ON COLUMN "users"."updated_at" IS '정보 수정 일시';

COMMENT ON COLUMN "users"."last_login_at" IS '마지막 로그인 일시';

COMMENT ON COLUMN "decks"."id" IS '덱 고유 ID';

COMMENT ON COLUMN "decks"."name" IS '덱 이름';

COMMENT ON COLUMN "decks"."description" IS '덱 설명';

COMMENT ON COLUMN "decks"."category" IS '카테고리 (business/toeic/academic/daily 등)';

COMMENT ON COLUMN "decks"."difficulty_level" IS '난이도 (beginner/intermediate/advanced)';

COMMENT ON COLUMN "decks"."is_public" IS '공개 덱 여부';

COMMENT ON COLUMN "decks"."is_official" IS '공식 제공 덱 여부';

COMMENT ON COLUMN "decks"."creator_id" IS '덱 생성자 ID (사용자 생성 덱의 경우)';

COMMENT ON COLUMN "decks"."card_count" IS '포함된 카드 수';

COMMENT ON COLUMN "decks"."learning_count" IS '이 덱을 학습 중인 사용자 수';

COMMENT ON COLUMN "decks"."created_at" IS '덱 생성 일시';

COMMENT ON COLUMN "decks"."updated_at" IS '덱 수정 일시';

COMMENT ON COLUMN "user_decks"."id" IS '사용자-덱 관계 고유 ID';

COMMENT ON COLUMN "user_decks"."user_id" IS '사용자 ID';

COMMENT ON COLUMN "user_decks"."deck_id" IS '덱 ID';

COMMENT ON COLUMN "user_decks"."is_active" IS '활성 학습 중인 덱 여부';

COMMENT ON COLUMN "user_decks"."cards_new" IS '새 카드 수';

COMMENT ON COLUMN "user_decks"."cards_learning" IS '학습 중인 카드 수';

COMMENT ON COLUMN "user_decks"."cards_review" IS '복습할 카드 수';

COMMENT ON COLUMN "user_decks"."progress_percentage" IS '학습 진행률 (%)';

COMMENT ON COLUMN "user_decks"."started_at" IS '덱 학습 시작 일시';

COMMENT ON COLUMN "user_decks"."last_studied_at" IS '이 덱을 마지막으로 학습한 일시';

COMMENT ON COLUMN "vocabulary_cards"."id" IS '단어 카드 고유 ID';

COMMENT ON COLUMN "vocabulary_cards"."word" IS '영단어';

COMMENT ON COLUMN "vocabulary_cards"."translation" IS '한글 뜻';

COMMENT ON COLUMN "vocabulary_cards"."part_of_speech" IS '품사 (noun/verb/adjective 등)';

COMMENT ON COLUMN "vocabulary_cards"."pronunciation_ipa" IS 'IPA 발음 기호';

COMMENT ON COLUMN "vocabulary_cards"."pronunciation_kr" IS '한글 발음 표기';

COMMENT ON COLUMN "vocabulary_cards"."definition_en" IS '영어 정의';

COMMENT ON COLUMN "vocabulary_cards"."synonyms" IS '유의어 배열';

COMMENT ON COLUMN "vocabulary_cards"."antonyms" IS '반의어 배열';

COMMENT ON COLUMN "vocabulary_cards"."example_sentences" IS 'AI 생성 예문 배열 [{sentence, translation, context}]';

COMMENT ON COLUMN "vocabulary_cards"."collocations" IS '자주 쓰이는 연어 표현';

COMMENT ON COLUMN "vocabulary_cards"."audio_url" IS '발음 오디오 파일 URL';

COMMENT ON COLUMN "vocabulary_cards"."image_url" IS '이미지 URL (시각적 학습 보조)';

COMMENT ON COLUMN "vocabulary_cards"."difficulty_level" IS '난이도 (A1/A2/B1/B2/C1/C2)';

COMMENT ON COLUMN "vocabulary_cards"."frequency_rank" IS '빈도 순위 (낮을수록 자주 사용)';

COMMENT ON COLUMN "vocabulary_cards"."cefr_level" IS 'CEFR 레벨 (A1-C2)';

COMMENT ON COLUMN "vocabulary_cards"."tags" IS '태그 배열 (business/toeic/academic 등)';

COMMENT ON COLUMN "vocabulary_cards"."deck_id" IS '소속 덱 ID';

COMMENT ON COLUMN "vocabulary_cards"."source" IS '출처 (AI 생성/사용자 추가/공식 등)';

COMMENT ON COLUMN "vocabulary_cards"."usage_notes" IS '사용법 노트 (AI 생성 설명)';

COMMENT ON COLUMN "vocabulary_cards"."etymology" IS '어원 정보';

COMMENT ON COLUMN "vocabulary_cards"."is_verified" IS '검증된 카드 여부';

COMMENT ON COLUMN "vocabulary_cards"."created_at" IS '카드 생성 일시';

COMMENT ON COLUMN "vocabulary_cards"."updated_at" IS '카드 수정 일시';

COMMENT ON COLUMN "user_card_progress"."id" IS '진행상황 고유 ID';

COMMENT ON COLUMN "user_card_progress"."user_id" IS '사용자 ID';

COMMENT ON COLUMN "user_card_progress"."card_id" IS '단어 카드 ID';

COMMENT ON COLUMN "user_card_progress"."easiness_factor" IS 'SM-2 기반 난이도 계수 (1.3~2.5)';

COMMENT ON COLUMN "user_card_progress"."interval" IS '복습 간격 (일 단위)';

COMMENT ON COLUMN "user_card_progress"."repetitions" IS '성공적인 복습 횟수';

COMMENT ON COLUMN "user_card_progress"."stability" IS 'FSRS 안정성 파라미터 (기억 유지 강도)';

COMMENT ON COLUMN "user_card_progress"."difficulty" IS 'FSRS 난이도 파라미터 (1~10)';

COMMENT ON COLUMN "user_card_progress"."next_review_date" IS '다음 복습 예정 일시';

COMMENT ON COLUMN "user_card_progress"."last_review_date" IS '마지막 복습 일시';

COMMENT ON COLUMN "user_card_progress"."scheduled_days" IS '예정된 복습 간격 (일)';

COMMENT ON COLUMN "user_card_progress"."total_reviews" IS '총 복습 횟수';

COMMENT ON COLUMN "user_card_progress"."correct_count" IS '정답 횟수';

COMMENT ON COLUMN "user_card_progress"."wrong_count" IS '오답 횟수';

COMMENT ON COLUMN "user_card_progress"."accuracy_rate" IS '정답률 (%)';

COMMENT ON COLUMN "user_card_progress"."average_response_time" IS '평균 응답 시간 (초)';

COMMENT ON COLUMN "user_card_progress"."quality_history" IS '학습 품질 기록 배열 [{date, rating, response_time}]';

COMMENT ON COLUMN "user_card_progress"."card_state" IS '카드 상태';

COMMENT ON COLUMN "user_card_progress"."lapses" IS '망각 횟수 (틀린 횟수)';

COMMENT ON COLUMN "user_card_progress"."reps_since_lapse" IS '마지막 실수 이후 성공 횟수';

COMMENT ON COLUMN "user_card_progress"."first_studied_at" IS '최초 학습 일시';

COMMENT ON COLUMN "user_card_progress"."mastered_at" IS '숙달 완료 일시';

COMMENT ON COLUMN "user_card_progress"."created_at" IS '진행상황 생성 일시';

COMMENT ON COLUMN "user_card_progress"."updated_at" IS '진행상황 수정 일시';

COMMENT ON COLUMN "study_sessions"."id" IS '학습 세션 고유 ID';

COMMENT ON COLUMN "study_sessions"."user_id" IS '사용자 ID';

COMMENT ON COLUMN "study_sessions"."deck_id" IS '학습한 덱 ID';

COMMENT ON COLUMN "study_sessions"."session_date" IS '학습 날짜';

COMMENT ON COLUMN "study_sessions"."started_at" IS '세션 시작 일시';

COMMENT ON COLUMN "study_sessions"."ended_at" IS '세션 종료 일시';

COMMENT ON COLUMN "study_sessions"."duration_minutes" IS '학습 시간 (분)';

COMMENT ON COLUMN "study_sessions"."cards_studied" IS '학습한 카드 수';

COMMENT ON COLUMN "study_sessions"."cards_new" IS '새로 학습한 카드 수';

COMMENT ON COLUMN "study_sessions"."cards_reviewed" IS '복습한 카드 수';

COMMENT ON COLUMN "study_sessions"."correct_answers" IS '정답 수';

COMMENT ON COLUMN "study_sessions"."wrong_answers" IS '오답 수';

COMMENT ON COLUMN "study_sessions"."accuracy_rate" IS '정답률 (%)';

COMMENT ON COLUMN "study_sessions"."average_response_time" IS '평균 응답 시간 (초)';

COMMENT ON COLUMN "study_sessions"."device_type" IS '사용 기기 (mobile/tablet/desktop)';

COMMENT ON COLUMN "study_sessions"."created_at" IS '기록 생성 일시';

COMMENT ON COLUMN "ai_interactions"."id" IS 'AI 상호작용 고유 ID';

COMMENT ON COLUMN "ai_interactions"."user_id" IS '사용자 ID';

COMMENT ON COLUMN "ai_interactions"."card_id" IS '관련 카드 ID';

COMMENT ON COLUMN "ai_interactions"."interaction_type" IS '상호작용 유형 (example_generation/pronunciation_check/explanation 등)';

COMMENT ON COLUMN "ai_interactions"."user_input" IS '사용자 입력 (발음 체크 등)';

COMMENT ON COLUMN "ai_interactions"."ai_response" IS 'AI 응답';

COMMENT ON COLUMN "ai_interactions"."model_used" IS '사용된 AI 모델 (gpt-4/claude-3.5 등)';

COMMENT ON COLUMN "ai_interactions"."tokens_used" IS '사용된 토큰 수 (비용 추적)';

COMMENT ON COLUMN "ai_interactions"."response_time_ms" IS '응답 시간 (밀리초)';

COMMENT ON COLUMN "ai_interactions"."feedback_rating" IS '사용자 피드백 (1-5)';

COMMENT ON COLUMN "ai_interactions"."created_at" IS '상호작용 일시';

COMMENT ON COLUMN "sync_queue"."id" IS '동기화 큐 고유 ID';

COMMENT ON COLUMN "sync_queue"."user_id" IS '사용자 ID';

COMMENT ON COLUMN "sync_queue"."entity_type" IS '엔티티 타입 (user_card_progress/study_session 등)';

COMMENT ON COLUMN "sync_queue"."entity_id" IS '엔티티 ID';

COMMENT ON COLUMN "sync_queue"."operation" IS '작업 유형';

COMMENT ON COLUMN "sync_queue"."payload" IS '동기화할 데이터';

COMMENT ON COLUMN "sync_queue"."retry_count" IS '재시도 횟수';

COMMENT ON COLUMN "sync_queue"."max_retries" IS '최대 재시도 횟수';

COMMENT ON COLUMN "sync_queue"."is_synced" IS '동기화 완료 여부';

COMMENT ON COLUMN "sync_queue"."error_message" IS '에러 메시지 (동기화 실패 시)';

COMMENT ON COLUMN "sync_queue"."priority" IS '우선순위 (높을수록 먼저 처리)';

COMMENT ON COLUMN "sync_queue"."created_at" IS '큐 생성 일시';

COMMENT ON COLUMN "sync_queue"."synced_at" IS '동기화 완료 일시';

COMMENT ON COLUMN "sync_queue"."last_retry_at" IS '마지막 재시도 일시';

ALTER TABLE "decks" ADD FOREIGN KEY ("creator_id") REFERENCES "users" ("id") ON DELETE SET NULL;

ALTER TABLE "user_decks" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;

ALTER TABLE "user_decks" ADD FOREIGN KEY ("deck_id") REFERENCES "decks" ("id") ON DELETE CASCADE;

ALTER TABLE "vocabulary_cards" ADD FOREIGN KEY ("deck_id") REFERENCES "decks" ("id") ON DELETE SET NULL;

ALTER TABLE "user_card_progress" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;

ALTER TABLE "user_card_progress" ADD FOREIGN KEY ("card_id") REFERENCES "vocabulary_cards" ("id") ON DELETE CASCADE;

ALTER TABLE "study_sessions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;

ALTER TABLE "study_sessions" ADD FOREIGN KEY ("deck_id") REFERENCES "decks" ("id") ON DELETE SET NULL;

ALTER TABLE "ai_interactions" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;

ALTER TABLE "ai_interactions" ADD FOREIGN KEY ("card_id") REFERENCES "vocabulary_cards" ("id") ON DELETE SET NULL;

ALTER TABLE "sync_queue" ADD FOREIGN KEY ("user_id") REFERENCES "users" ("id") ON DELETE CASCADE;
