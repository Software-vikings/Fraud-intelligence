CREATE TABLE customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    home_country CHAR(2),
    customer_avg_amount_30d NUMERIC(14,2)
);
CREATE TABLE cards (
    card_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL REFERENCES customers(customer_id)
);
CREATE TABLE transactions (
    transaction_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL REFERENCES customers(customer_id),
    card_id VARCHAR(32) NOT NULL REFERENCES cards(card_id),
    amount NUMERIC(14,2) NOT NULL CHECK (amount >= 0),
    currency CHAR(3) NOT NULL,
    merchant_id VARCHAR(32),
    merchant_category VARCHAR(64),
    country CHAR(2),
    transaction_timestamp TIMESTAMP NOT NULL,
    is_card_present BOOLEAN NOT NULL DEFAULT FALSE,
    failed_attempts_24h INTEGER NOT NULL DEFAULT 0,
    label_is_fraud BOOLEAN
);
CREATE INDEX idx_transactions_card_time ON transactions(card_id, transaction_timestamp);
CREATE INDEX idx_transactions_customer_time ON transactions(customer_id, transaction_timestamp);
CREATE INDEX idx_transactions_amount ON transactions(amount);
