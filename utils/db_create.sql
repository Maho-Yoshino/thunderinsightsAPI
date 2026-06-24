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

CREATE TABLE expired_tokens( -- Long term storage for expired tokens to keep track of usage patterns
    hash_token TEXT NOT NULL, 
    email TEXT,
    requests_count INTEGER NOT NULL,
    last_used INTEGER NOT NULL, -- UNIX Timestamp
    expired_at INTEGER NOT NULL DEFAULT (unixepoch()), -- UNIX Timestamp

    PRIMARY KEY (hash_token, email)
);

CREATE TABLE two_factor_tokens (
    email TEXT PRIMARY KEY, 
    client_id TEXT NOT NULL,
    trusted_at INTEGER NOT NULL -- UNIX Timestamp
);

CREATE INDEX idx_tokens_expires ON tokens(expires);
CREATE INDEX idx_two_factor_tokens_email ON two_factor_tokens(email);