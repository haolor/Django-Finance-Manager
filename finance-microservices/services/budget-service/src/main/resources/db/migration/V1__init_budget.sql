CREATE TABLE budgets (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    amount      NUMERIC(15, 2) NOT NULL CHECK (amount >= 0),
    period      VARCHAR(20) NOT NULL DEFAULT 'monthly',
    start_date  DATE NOT NULL,
    end_date    DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_budget_period CHECK (period IN ('daily', 'weekly', 'monthly', 'yearly'))
);

CREATE INDEX idx_budgets_user ON budgets (user_id, start_date DESC);
CREATE INDEX idx_budgets_user_category ON budgets (user_id, category_id);
