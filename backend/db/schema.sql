CREATE TABLE IF NOT EXISTS countries (
    code VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS commodities (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    unit VARCHAR
);

CREATE TABLE IF NOT EXISTS suppliers (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    country_code VARCHAR,
    commodities_json VARCHAR,
    cost_index DOUBLE,
    lead_time_days INTEGER,
    capability_flags_json VARCHAR
);

CREATE TABLE IF NOT EXISTS parts (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    criticality INTEGER,
    main_commodity VARCHAR,
    supplier_ids_json VARCHAR
);

CREATE TABLE IF NOT EXISTS plants (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    location VARCHAR,
    parts_used_json VARCHAR
);

CREATE TABLE IF NOT EXISTS news_events (
    id VARCHAR PRIMARY KEY,
    run_id VARCHAR,
    source VARCHAR,
    title VARCHAR,
    published_at TIMESTAMP,
    country_code VARCHAR,
    severity INTEGER,
    risk_type VARCHAR,
    url VARCHAR,
    raw_json VARCHAR
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    run_id VARCHAR PRIMARY KEY,
    started_at TIMESTAMP NOT NULL,
    finished_at TIMESTAMP,
    data_health_json VARCHAR
);

CREATE TABLE IF NOT EXISTS country_risk (
    run_id VARCHAR,
    country_code VARCHAR,
    score DOUBLE,
    components_json VARCHAR,
    PRIMARY KEY (run_id, country_code)
);

CREATE TABLE IF NOT EXISTS commodity_risk (
    run_id VARCHAR,
    commodity_id VARCHAR,
    score DOUBLE,
    components_json VARCHAR,
    PRIMARY KEY (run_id, commodity_id)
);

CREATE TABLE IF NOT EXISTS supplier_risk (
    run_id VARCHAR,
    supplier_id VARCHAR,
    score DOUBLE,
    components_json VARCHAR,
    PRIMARY KEY (run_id, supplier_id)
);

CREATE TABLE IF NOT EXISTS mcdm_scores (
    run_id VARCHAR,
    supplier_id VARCHAR,
    part_id VARCHAR,
    criterion VARCHAR,
    raw_value DOUBLE,
    normalized_value DOUBLE,
    weight DOUBLE,
    score DOUBLE,
    rank INTEGER,
    PRIMARY KEY (run_id, supplier_id, part_id, criterion)
);

CREATE TABLE IF NOT EXISTS scenarios (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description VARCHAR,
    shock_json VARCHAR
);

CREATE TABLE IF NOT EXISTS sim_results (
    run_id VARCHAR,
    scenario_id VARCHAR,
    strategy_id VARCHAR,
    metrics_json VARCHAR,
    PRIMARY KEY (run_id, scenario_id, strategy_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
    run_id VARCHAR,
    part_id VARCHAR,
    allocation_json VARCHAR,
    rationale_json VARCHAR,
    PRIMARY KEY (run_id, part_id)
);

CREATE TABLE IF NOT EXISTS data_source_health (
    provider VARCHAR PRIMARY KEY,
    last_ok TIMESTAMP,
    last_error VARCHAR,
    latency_ms INTEGER,
    status VARCHAR
);

CREATE TABLE IF NOT EXISTS macro_indicators (
    run_id VARCHAR,
    country_code VARCHAR,
    indicator_id VARCHAR,
    year INTEGER,
    value DOUBLE,
    PRIMARY KEY (run_id, country_code, indicator_id, year)
);

CREATE TABLE IF NOT EXISTS commodity_prices (
    run_id VARCHAR,
    series_id VARCHAR,
    date DATE,
    value DOUBLE,
    PRIMARY KEY (run_id, series_id, date)
);
