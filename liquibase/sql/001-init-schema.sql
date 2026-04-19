CREATE SCHEMA IF NOT EXISTS tink_invest_api;

CREATE TABLE IF NOT EXISTS tink_invest_api.money_amount_daily(
    report_dt date,
    active_type text,
    amount_rub numeric,
    amount_usd numeric,
    insert_tms timestamp DEFAULT current_timestamp
);