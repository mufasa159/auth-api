--- https://www.exibit.me 
--- postgres database schema
--- created on 2022-08-02


--- To be used for creating UIDs in `unique_id()` function
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

--- Function `unique_id()` for generating short 8 digit UID
CREATE OR REPLACE FUNCTION unique_id()
RETURNS TRIGGER AS $$
DECLARE
	key VARCHAR(8);
	query TEXT;
	found VARCHAR(8);
BEGIN
	query := 'SELECT uid FROM ' || quote_ident(TG_TABLE_NAME) || ' WHERE uid=';
	LOOP
	    key := encode(gen_random_bytes(6), 'base64');
	    key := replace(key, '/', '6');
	    key := replace(key, '+', '9');
	    EXECUTE query || quote_literal(key) INTO found;
	    IF found IS NULL THEN
	      EXIT;
	    END IF;
	END LOOP;
	NEW.uid = lower(key);
	RETURN NEW;
END;
$$ language 'plpgsql';


--- Set timezone for Postgres server
SET timezone = 'America/New_York';

--- Enum to store role of account user
CREATE TYPE ROLE as ENUM ('admin', 'maintainer', 'user');

--- Table to store user data
CREATE TABLE "accounts" (
	"uid" VARCHAR(8) PRIMARY KEY NOT NULL UNIQUE,
	"name_first" VARCHAR(30) NOT NULL,
	"name_last" VARCHAR(30) NOT NULL,
	"image" TEXT NULL,
	"role" ROLE NOT NULL DEFAULT 'user',
	"username" VARCHAR(30) NOT NULL,
	"email" VARCHAR(60) NOT NULL UNIQUE,
	"hash" VARCHAR(255) NOT NULL,
	"bio" VARCHAR(500) NULL,
	"created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"last_login_at" TIMESTAMPTZ NULL,
	"last_login_ip" VARCHAR(300) NULL,
	"current_login_at" TIMESTAMPTZ NULL,
	"current_login_ip" VARCHAR(300) NULL,
	"login_count" INTEGER DEFAULT 0,
	"confirmed_email" BOOLEAN DEFAULT FALSE
);

--- Trigger for automatically generating and adding UIDs for new users whenever `INSERT` is performed
CREATE TRIGGER trigger_accounts_genid BEFORE INSERT ON accounts FOR EACH ROW EXECUTE PROCEDURE unique_id();


--- Table for managing authentication tokens
--- Mainly used for performing refresh token rotation
CREATE TABLE "token_management"(
	"id" SERIAL PRIMARY KEY NOT NULL UNIQUE,
	"uid" VARCHAR(8) NOT NULL,
	"access_token" TEXT NOT NULL,
	"refresh_token" TEXT NOT NULL,
	"created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"pair_count" INTEGER NOT NULL DEFAULT 0,
	"refresh_token_use_count" INTEGER DEFAULT 0 NOT NULL,
	"refresh_token_last_used_at" TIMESTAMPTZ NULL
);
