-- USERS
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password_hash TEXT,
  role TEXT,
  team_id INTEGER
);

-- ENGINEERS
CREATE TABLE engineers (
  id INTEGER PRIMARY KEY,
  name TEXT,
  team_id INTEGER
);

-- JOBS (RAW)
CREATE TABLE jobs (
  id INTEGER PRIMARY KEY,
  engineer_id INTEGER,
  status TEXT,
  created_at DATE,
  completed_at DATE
);

-- FACT (TIME DIMENSION)
CREATE TABLE job_fact (
  job_id INTEGER,
  engineer_id INTEGER,
  date DATE,
  week TEXT,
  month TEXT,
  status TEXT
);

-- KPI WEEKLY
CREATE TABLE kpi_weekly (
  week TEXT,
  engineer_id INTEGER,
  completion_rate REAL
);

-- KPI MONTHLY
CREATE TABLE kpi_monthly (
  month TEXT,
  engineer_id INTEGER,
  completion_rate REAL
);
