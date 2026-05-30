CREATE TABLE IF NOT EXISTS users (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL,
    email   TEXT NOT NULL UNIQUE,         -- UNIQUE => the API returns 409 on duplicates
    age     INTEGER CHECK (age >= 0),     -- matches Pydantic's ge=0 validator
    created TIMESTAMPTZ NOT NULL DEFAULT now()
);
