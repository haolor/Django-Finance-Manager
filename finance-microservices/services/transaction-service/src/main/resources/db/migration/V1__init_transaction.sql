CREATE TABLE categories (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    icon        VARCHAR(50) NOT NULL DEFAULT '💰',
    color       VARCHAR(20) NOT NULL DEFAULT '#3B82F6',
    type        VARCHAR(10) NOT NULL DEFAULT 'expense',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_categories_name UNIQUE (name),
    CONSTRAINT chk_categories_type CHECK (type IN ('income', 'expense'))
);

CREATE TABLE transactions (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL,
    category_id         BIGINT,
    amount              NUMERIC(15, 2) NOT NULL CHECK (amount >= 0.01),
    description         TEXT,
    transaction_date    DATE NOT NULL,
    original_nlp_input  TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_tx_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

CREATE INDEX idx_tx_user_date ON transactions (user_id, transaction_date);
CREATE INDEX idx_tx_user_category ON transactions (user_id, category_id);

CREATE TABLE spending_patterns (
    id                      BIGSERIAL PRIMARY KEY,
    user_id                 BIGINT NOT NULL,
    category_id             BIGINT NOT NULL,
    average_amount          NUMERIC(15, 2),
    frequency               INTEGER NOT NULL DEFAULT 0,
    last_transaction_date   DATE,
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uk_pattern_user_category UNIQUE (user_id, category_id),
    CONSTRAINT fk_pattern_category FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

INSERT INTO categories (name, description, icon, color, type) VALUES
    ('Ăn uống', 'Chi phí ăn uống hàng ngày', '🍔', '#EF4444', 'expense'),
    ('Đi lại', 'Xăng xe, taxi, vé tàu', '🚗', '#F59E0B', 'expense'),
    ('Mua sắm', 'Mua sắm cá nhân', '🛍️', '#EC4899', 'expense'),
    ('Hóa đơn', 'Điện, nước, internet', '💡', '#3B82F6', 'expense'),
    ('Lương', 'Thu nhập từ lương', '💰', '#10B981', 'income'),
    ('Thưởng', 'Thưởng và phụ cấp', '🎁', '#22C55E', 'income');
