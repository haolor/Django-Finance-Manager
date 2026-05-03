CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    username        VARCHAR(150) NOT NULL,
    email           VARCHAR(255) NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    first_name      VARCHAR(100),
    last_name       VARCHAR(100),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_users_username UNIQUE (username),
    CONSTRAINT uk_users_email UNIQUE (email)
);

CREATE TABLE user_preferences (
    id                              BIGSERIAL PRIMARY KEY,
    user_id                         BIGINT NOT NULL,
    theme                           VARCHAR(20) NOT NULL DEFAULT 'light',
    primary_color                   VARCHAR(20) NOT NULL DEFAULT '#3B82F6',
    sidebar_collapsed               BOOLEAN NOT NULL DEFAULT FALSE,
    default_report_period           VARCHAR(20) NOT NULL DEFAULT 'month',
    report_categories               JSONB NOT NULL DEFAULT '[]'::jsonb,
    report_include_charts           BOOLEAN NOT NULL DEFAULT TRUE,
    report_include_tables           BOOLEAN NOT NULL DEFAULT TRUE,
    report_email_frequency          VARCHAR(20) NOT NULL DEFAULT 'never',
    notify_budget_exceeded          BOOLEAN NOT NULL DEFAULT TRUE,
    notify_large_transaction        BOOLEAN NOT NULL DEFAULT TRUE,
    notify_anomaly_detected         BOOLEAN NOT NULL DEFAULT TRUE,
    large_transaction_threshold     NUMERIC(15, 2) NOT NULL DEFAULT 1000000,
    dashboard_widgets               JSONB NOT NULL DEFAULT '[]'::jsonb,
    dashboard_chart_type            VARCHAR(20) NOT NULL DEFAULT 'line',
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_user_preferences_user UNIQUE (user_id),
    CONSTRAINT fk_user_preferences_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_users_email ON users (email);
