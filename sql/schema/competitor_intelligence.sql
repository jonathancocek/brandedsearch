-- ============================================================================
-- Snowflake Schema - NO INDEXES VERSION (ARRAY FIX)
-- Database: BRANDEDSEARCH
-- Schema: PUBLIC
-- ============================================================================

USE DATABASE BRANDEDSEARCH;
USE SCHEMA PUBLIC;

-- Drop existing objects
DROP VIEW IF EXISTS VW_SHARE_OF_SEARCH;
DROP VIEW IF EXISTS VW_TOP_KEYWORDS_BY_SOLUTION;
DROP VIEW IF EXISTS VW_LATEST_COMPETITOR_PERFORMANCE;
DROP TABLE IF EXISTS PIPELINE_RUNS;
DROP TABLE IF EXISTS CATEGORY_METRICS;
DROP TABLE IF EXISTS COMPETITOR_METRICS;
DROP TABLE IF EXISTS KEYWORD_HISTORY;
DROP TABLE IF EXISTS COMPETITOR_KEYWORDS;
DROP TABLE IF EXISTS SOLUTION_CATEGORIES;
DROP TABLE IF EXISTS COMPETITORS;

-- ============================================================================
-- TABLES (NO INDEXES)
-- ============================================================================

CREATE TABLE COMPETITORS (
    competitor_id INT AUTOINCREMENT,
    competitor_name VARCHAR(100) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    is_client BOOLEAN DEFAULT FALSE,
    priority INT,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE SOLUTION_CATEGORIES (
    solution_id INT AUTOINCREMENT,
    solution_key VARCHAR(50) NOT NULL,
    solution_name VARCHAR(100) NOT NULL,
    display_order INT,
    semantic_indicators ARRAY,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE COMPETITOR_KEYWORDS (
    keyword_id INT AUTOINCREMENT,
    competitor_id INT NOT NULL,
    solution_id INT NOT NULL,
    keyword VARCHAR(500) NOT NULL,
    volume INT,
    position FLOAT,
    cpc FLOAT,
    competition FLOAT,
    trend VARCHAR(500),
    database VARCHAR(10),
    fetch_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE KEYWORD_HISTORY (
    history_id INT AUTOINCREMENT,
    keyword_id INT NOT NULL,
    date DATE NOT NULL,
    volume INT,
    position FLOAT,
    data_source VARCHAR(50) DEFAULT 'semrush',
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE COMPETITOR_METRICS (
    metric_id INT AUTOINCREMENT,
    competitor_id INT NOT NULL,
    solution_id INT NOT NULL,
    total_volume INT,
    avg_volume FLOAT,
    keyword_count INT,
    avg_position FLOAT,
    share_of_search FLOAT,
    recent_3m_avg INT,
    prior_3m_avg INT,
    momentum_pct FLOAT,
    momentum_status VARCHAR(50),
    calculation_date DATE NOT NULL,
    database VARCHAR(10),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE CATEGORY_METRICS (
    category_metric_id INT AUTOINCREMENT,
    solution_id INT NOT NULL,
    total_category_volume INT,
    category_growth_pct FLOAT,
    category_status VARCHAR(50),
    region_metrics VARIANT,
    seasonal_patterns VARIANT,
    calculation_date DATE NOT NULL,
    database VARCHAR(10),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE PIPELINE_RUNS (
    run_id INT AUTOINCREMENT,
    run_timestamp TIMESTAMP_NTZ NOT NULL,
    status VARCHAR(50) NOT NULL,
    database VARCHAR(10),
    keywords_fetched INT,
    competitors_processed INT,
    solutions_processed INT,
    duration_seconds INT,
    error_message VARCHAR(5000),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- VIEWS
-- ============================================================================

CREATE VIEW VW_LATEST_COMPETITOR_PERFORMANCE AS
SELECT 
    c.competitor_name,
    c.is_client,
    s.solution_name,
    m.total_volume,
    m.avg_volume,
    m.keyword_count,
    m.share_of_search,
    m.momentum_pct,
    m.momentum_status,
    m.calculation_date,
    m.database
FROM COMPETITOR_METRICS m
JOIN COMPETITORS c ON m.competitor_id = c.competitor_id
JOIN SOLUTION_CATEGORIES s ON m.solution_id = s.solution_id
WHERE m.calculation_date = (
    SELECT MAX(calculation_date) 
    FROM COMPETITOR_METRICS m2 
    WHERE m2.competitor_id = m.competitor_id 
    AND m2.solution_id = m.solution_id
);

CREATE VIEW VW_TOP_KEYWORDS_BY_SOLUTION AS
SELECT 
    s.solution_name,
    c.competitor_name,
    k.keyword,
    k.volume,
    k.position,
    k.fetch_date,
    ROW_NUMBER() OVER (
        PARTITION BY s.solution_id, c.competitor_id 
        ORDER BY k.volume DESC
    ) as keyword_rank
FROM COMPETITOR_KEYWORDS k
JOIN COMPETITORS c ON k.competitor_id = c.competitor_id
JOIN SOLUTION_CATEGORIES s ON k.solution_id = s.solution_id
WHERE k.is_active = TRUE
AND k.fetch_date = (SELECT MAX(fetch_date) FROM COMPETITOR_KEYWORDS)
QUALIFY keyword_rank <= 15;

CREATE VIEW VW_SHARE_OF_SEARCH AS
SELECT 
    s.solution_name,
    c.competitor_name,
    c.is_client,
    m.total_volume,
    m.share_of_search,
    m.calculation_date,
    m.database
FROM COMPETITOR_METRICS m
JOIN COMPETITORS c ON m.competitor_id = c.competitor_id
JOIN SOLUTION_CATEGORIES s ON m.solution_id = s.solution_id
WHERE m.calculation_date = (SELECT MAX(calculation_date) FROM COMPETITOR_METRICS)
ORDER BY s.solution_name, m.share_of_search DESC;

-- ============================================================================
-- SEED DATA - Solutions with ARRAY (using SELECT...UNION ALL)
-- ============================================================================

INSERT INTO SOLUTION_CATEGORIES (solution_key, solution_name, display_order, semantic_indicators) 
SELECT 'cloud', 'Cloud Security', 1, ARRAY_CONSTRUCT('cloud', 'cspm', 'cwpp', 'container', 'kubernetes', 'aws', 'azure', 'gcp')
UNION ALL
SELECT 'email', 'Email Security', 2, ARRAY_CONSTRUCT('email', 'phishing', 'spam', 'inbox', 'mailbox')
UNION ALL
SELECT 'network', 'Network Security', 3, ARRAY_CONSTRUCT('network', 'ndr', 'ids', 'ips', 'intrusion');

-- ============================================================================
-- SEED DATA - Competitors (regular INSERT works fine)
-- ============================================================================

INSERT INTO COMPETITORS (competitor_name, domain, is_client, priority) VALUES
('Darktrace', 'darktrace.com', TRUE, 1),
('Wiz', 'wiz.io', FALSE, 2),
('Orca', 'orca.security', FALSE, 3),
('Crowdstrike', 'crowdstrike.com', FALSE, 4),
('Palo Alto Cortex Cloud', 'paloaltonetworks.com', FALSE, 5),
('Abnormal', 'abnormalsecurity.com', FALSE, 6),
('ProofPoint', 'proofpoint.com', FALSE, 7),
('Mimecast', 'mimecast.com', FALSE, 8),
('VectraAI', 'vectra.ai', FALSE, 9),
('ExtraHop', 'extrahop.com', FALSE, 10),
('CoreLight', 'corelight.com', FALSE, 11);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '✓ Setup Complete!' AS status;

SELECT 'Competitors' AS table_name, COUNT(*) AS row_count FROM COMPETITORS
UNION ALL
SELECT 'Solutions' AS table_name, COUNT(*) AS row_count FROM SOLUTION_CATEGORIES;

SELECT * FROM COMPETITORS ORDER BY priority;
SELECT * FROM SOLUTION_CATEGORIES ORDER BY display_order;

-- ============================================================================
-- SUCCESS!
-- ============================================================================
