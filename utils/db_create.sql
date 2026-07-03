CREATE TABLE tokens (
    hash_token TEXT NOT NULL,
    email TEXT PRIMARY KEY ,
    session_token TEXT NOT NULL,
    user_token TEXT NOT NULL,
    expires INTEGER NOT NULL, -- UNIX Timestamp
    uidHint INTEGER NOT NULL,
    requests_count INTEGER DEFAULT 0,
    last_used INTEGER NOT NULL, -- UNIX Timestamp
    created_at INTEGER NOT NULL DEFAULT (unixepoch()) -- UNIX Timestamp
);

CREATE INDEX idx_tokens_expires ON tokens(expires);