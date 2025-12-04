--
-- PostgreSQL database dump
--

\restrict 6frJoQc1SsYYP6g6OxYrcoVYRzFxBvqbXgDeO5dF65HlCKyK1xctwZYGcmdtUaE

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: cardstate; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.cardstate AS ENUM (
    'NEW',
    'LEARNING',
    'REVIEW',
    'RELEARNING'
);


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: decks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.decks (
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    name character varying(255) NOT NULL,
    description character varying,
    category character varying(100),
    difficulty_level character varying(50),
    is_public boolean NOT NULL,
    is_official boolean NOT NULL,
    id integer NOT NULL,
    creator_id integer
);


--
-- Name: decks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.decks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: decks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.decks_id_seq OWNED BY public.decks.id;


--
-- Name: study_sessions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.study_sessions (
    user_id integer NOT NULL,
    deck_id integer,
    session_date date NOT NULL,
    duration_minutes integer NOT NULL,
    cards_studied integer NOT NULL,
    correct_answers integer NOT NULL,
    wrong_answers integer NOT NULL,
    accuracy_rate double precision NOT NULL,
    id integer NOT NULL,
    started_at timestamp without time zone NOT NULL,
    ended_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL
);


--
-- Name: study_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.study_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: study_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.study_sessions_id_seq OWNED BY public.study_sessions.id;


--
-- Name: user_card_progress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_card_progress (
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    card_id integer NOT NULL,
    "interval" integer NOT NULL,
    repetitions integer NOT NULL,
    total_reviews integer NOT NULL,
    correct_count integer NOT NULL,
    wrong_count integer NOT NULL,
    accuracy_rate double precision NOT NULL,
    stability double precision,
    difficulty double precision,
    scheduled_days integer NOT NULL,
    lapses integer NOT NULL,
    elapsed_days integer NOT NULL,
    id integer NOT NULL,
    next_review_date timestamp without time zone NOT NULL,
    last_review_date timestamp without time zone,
    card_state public.cardstate NOT NULL,
    first_studied_at timestamp without time zone,
    quality_history json
);


--
-- Name: user_card_progress_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_card_progress_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_card_progress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_card_progress_id_seq OWNED BY public.user_card_progress.id;


--
-- Name: user_decks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_decks (
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    user_id integer NOT NULL,
    deck_id integer NOT NULL,
    is_active boolean NOT NULL,
    id integer NOT NULL,
    started_at timestamp without time zone NOT NULL,
    last_studied_at timestamp without time zone
);


--
-- Name: user_decks_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_decks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_decks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_decks_id_seq OWNED BY public.user_decks.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    is_active boolean NOT NULL,
    id integer NOT NULL,
    hashed_password character varying(255) NOT NULL,
    current_streak integer NOT NULL,
    longest_streak integer NOT NULL,
    last_study_date date
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vocabulary_cards; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vocabulary_cards (
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    english_word character varying(255) NOT NULL,
    korean_meaning character varying(255) NOT NULL,
    part_of_speech character varying(50),
    pronunciation_ipa character varying(255),
    definition_en character varying,
    difficulty_level character varying(50),
    cefr_level character varying(10),
    deck_id integer,
    is_verified boolean NOT NULL,
    id integer NOT NULL,
    example_sentences json,
    tags json
);


--
-- Name: vocabulary_cards_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vocabulary_cards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vocabulary_cards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vocabulary_cards_id_seq OWNED BY public.vocabulary_cards.id;


--
-- Name: decks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.decks ALTER COLUMN id SET DEFAULT nextval('public.decks_id_seq'::regclass);


--
-- Name: study_sessions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_sessions ALTER COLUMN id SET DEFAULT nextval('public.study_sessions_id_seq'::regclass);


--
-- Name: user_card_progress id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_card_progress ALTER COLUMN id SET DEFAULT nextval('public.user_card_progress_id_seq'::regclass);


--
-- Name: user_decks id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_decks ALTER COLUMN id SET DEFAULT nextval('public.user_decks_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vocabulary_cards id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vocabulary_cards ALTER COLUMN id SET DEFAULT nextval('public.vocabulary_cards_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: decks decks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.decks
    ADD CONSTRAINT decks_pkey PRIMARY KEY (id);


--
-- Name: user_decks idx_user_decks_user_deck; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_decks
    ADD CONSTRAINT idx_user_decks_user_deck UNIQUE (user_id, deck_id);


--
-- Name: study_sessions study_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_pkey PRIMARY KEY (id);


--
-- Name: user_card_progress uq_user_card; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_card_progress
    ADD CONSTRAINT uq_user_card UNIQUE (user_id, card_id);


--
-- Name: user_card_progress user_card_progress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_card_progress
    ADD CONSTRAINT user_card_progress_pkey PRIMARY KEY (id);


--
-- Name: user_decks user_decks_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_decks
    ADD CONSTRAINT user_decks_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vocabulary_cards vocabulary_cards_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vocabulary_cards
    ADD CONSTRAINT vocabulary_cards_pkey PRIMARY KEY (id);


--
-- Name: ix_decks_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_decks_category ON public.decks USING btree (category);


--
-- Name: ix_decks_creator_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_decks_creator_id ON public.decks USING btree (creator_id);


--
-- Name: ix_decks_is_public; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_decks_is_public ON public.decks USING btree (is_public);


--
-- Name: ix_study_sessions_deck_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_sessions_deck_id ON public.study_sessions USING btree (deck_id);


--
-- Name: ix_study_sessions_session_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_sessions_session_date ON public.study_sessions USING btree (session_date);


--
-- Name: ix_study_sessions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_study_sessions_user_id ON public.study_sessions USING btree (user_id);


--
-- Name: ix_user_card_progress_card_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_card_progress_card_id ON public.user_card_progress USING btree (card_id);


--
-- Name: ix_user_card_progress_card_state; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_card_progress_card_state ON public.user_card_progress USING btree (card_state);


--
-- Name: ix_user_card_progress_next_review_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_card_progress_next_review_date ON public.user_card_progress USING btree (next_review_date);


--
-- Name: ix_user_card_progress_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_card_progress_user_id ON public.user_card_progress USING btree (user_id);


--
-- Name: ix_user_decks_deck_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_decks_deck_id ON public.user_decks USING btree (deck_id);


--
-- Name: ix_user_decks_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_decks_user_id ON public.user_decks USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_is_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_is_active ON public.users USING btree (is_active);


--
-- Name: ix_users_last_study_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_users_last_study_date ON public.users USING btree (last_study_date);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_vocabulary_cards_deck_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_vocabulary_cards_deck_id ON public.vocabulary_cards USING btree (deck_id);


--
-- Name: ix_vocabulary_cards_difficulty_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_vocabulary_cards_difficulty_level ON public.vocabulary_cards USING btree (difficulty_level);


--
-- Name: ix_vocabulary_cards_english_word; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_vocabulary_cards_english_word ON public.vocabulary_cards USING btree (english_word);


--
-- Name: decks decks_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.decks
    ADD CONSTRAINT decks_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id);


--
-- Name: study_sessions study_sessions_deck_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_deck_id_fkey FOREIGN KEY (deck_id) REFERENCES public.decks(id);


--
-- Name: study_sessions study_sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.study_sessions
    ADD CONSTRAINT study_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_card_progress user_card_progress_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_card_progress
    ADD CONSTRAINT user_card_progress_card_id_fkey FOREIGN KEY (card_id) REFERENCES public.vocabulary_cards(id);


--
-- Name: user_card_progress user_card_progress_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_card_progress
    ADD CONSTRAINT user_card_progress_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_decks user_decks_deck_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_decks
    ADD CONSTRAINT user_decks_deck_id_fkey FOREIGN KEY (deck_id) REFERENCES public.decks(id);


--
-- Name: user_decks user_decks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_decks
    ADD CONSTRAINT user_decks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: vocabulary_cards vocabulary_cards_deck_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vocabulary_cards
    ADD CONSTRAINT vocabulary_cards_deck_id_fkey FOREIGN KEY (deck_id) REFERENCES public.decks(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 6frJoQc1SsYYP6g6OxYrcoVYRzFxBvqbXgDeO5dF65HlCKyK1xctwZYGcmdtUaE
