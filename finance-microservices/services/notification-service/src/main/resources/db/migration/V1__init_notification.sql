CREATE TABLE notifications (
    id                      BIGSERIAL PRIMARY KEY,
    user_id                 BIGINT NOT NULL,
    type                    VARCHAR(50) NOT NULL,
    title                   VARCHAR(200) NOT NULL,
    message                 TEXT NOT NULL,
    is_read                 BOOLEAN NOT NULL DEFAULT FALSE,
    email_sent              BOOLEAN NOT NULL DEFAULT FALSE,
    related_transaction_id  BIGINT,
    related_budget_id       BIGINT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at                 TIMESTAMPTZ,
    CONSTRAINT chk_notif_type CHECK (type IN (
        'budget_exceeded',
        'large_transaction',
        'anomaly_detected',
        'report_ready',
        'system'
    ))
);

CREATE INDEX idx_notif_user_read ON notifications (user_id, is_read);
CREATE INDEX idx_notif_user_created ON notifications (user_id, created_at DESC);
