import json, os, sqlite3, time
from pathlib import Path

ROOT = Path(os.environ.get("KB_ROOT", Path(__file__).resolve().parent.parent))
STATE = Path(os.environ.get("KB_STATE", ROOT / "state"))
DB_PATH = STATE / "kb.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks(
  id INTEGER PRIMARY KEY, parent_id INTEGER, hypothesis TEXT,
  role TEXT NOT NULL, title TEXT NOT NULL, spec TEXT NOT NULL DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'queued',   -- queued|running|done|failed|blocked
  model_idx INTEGER NOT NULL DEFAULT 0, attempts INTEGER NOT NULL DEFAULT 0,
  max_attempts INTEGER NOT NULL DEFAULT 4, depth INTEGER NOT NULL DEFAULT 0,
  not_before REAL NOT NULL DEFAULT 0, created REAL NOT NULL, updated REAL NOT NULL,
  result TEXT, fingerprint TEXT);
CREATE INDEX IF NOT EXISTS tasks_pick ON tasks(status, not_before, id);
CREATE TABLE IF NOT EXISTS runs(
  id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, model TEXT NOT NULL,
  started REAL NOT NULL, ended REAL, rc INTEGER, outcome TEXT, log_path TEXT);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY, ts REAL NOT NULL, actor TEXT NOT NULL,
  kind TEXT NOT NULL, task_id INTEGER, data TEXT NOT NULL DEFAULT '{}');
CREATE INDEX IF NOT EXISTS events_task ON events(task_id, id);
CREATE INDEX IF NOT EXISTS events_kind ON events(kind, id);
-- idea -> prereg -> backtest (<-> data) -> review -> validated | rejected | parked
CREATE TABLE IF NOT EXISTS hypotheses(
  slug TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'idea',
  path TEXT, prereg_sha TEXT, reason TEXT, updated REAL NOT NULL, domain TEXT);
-- background collectors the harness runs for the data engineer (outside any agent)
CREATE TABLE IF NOT EXISTS jobs(
  id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, hypothesis TEXT, name TEXT NOT NULL,
  script TEXT NOT NULL, args TEXT NOT NULL DEFAULT '[]', cwd TEXT NOT NULL, dataset TEXT NOT NULL,
  blocking INTEGER NOT NULL DEFAULT 1, max_s INTEGER NOT NULL DEFAULT 3600,
  status TEXT NOT NULL DEFAULT 'queued',   -- queued|running|done|failed
  pid INTEGER, started REAL, ended REAL, rc INTEGER, log_path TEXT, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS datasets(
  name TEXT PRIMARY KEY, path TEXT NOT NULL, description TEXT, domain TEXT,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending|ready|failed
  validated INTEGER NOT NULL DEFAULT 0, notes TEXT, updated REAL NOT NULL);
-- ideas scouted by researchers, waiting for the chief to promote them
CREATE TABLE IF NOT EXISTS ideas(
  slug TEXT PRIMARY KEY, domain TEXT, idea TEXT, mechanism TEXT, data TEXT,
  status TEXT NOT NULL DEFAULT 'new', task_id INTEGER, created REAL NOT NULL);
"""
MIGRATIONS = [("tasks", "fingerprint", "TEXT"), ("hypotheses", "prereg_sha", "TEXT"), ("hypotheses", "reason", "TEXT"),
              ("hypotheses", "domain", "TEXT")]

def connect():
    STATE.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.executescript(SCHEMA)
    for table, col, typ in MIGRATIONS:
        if col not in {r[1] for r in c.execute(f"PRAGMA table_info({table})")}:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typ}")
    return c

def event(c, actor, kind, task_id=None, **data):
    c.execute("INSERT INTO events(ts,actor,kind,task_id,data) VALUES(?,?,?,?,?)",
              (time.time(), actor, kind, task_id, json.dumps(data, default=str)))

def add_task(c, role, title, spec=None, parent_id=None, hypothesis=None,
             depth=0, max_attempts=4, actor="user", fingerprint=None):
    now = time.time()
    if hypothesis:
        c.execute("INSERT OR IGNORE INTO hypotheses(slug,status,updated,domain) VALUES(?,'idea',?,?)",
                  (hypothesis, now, (spec or {}).get("domain")))
        c.execute("UPDATE ideas SET status='promoted' WHERE slug=?", (hypothesis,))
    cur = c.execute(
        "INSERT INTO tasks(parent_id,hypothesis,role,title,spec,depth,max_attempts,created,updated,fingerprint)"
        " VALUES(?,?,?,?,?,?,?,?,?,?)",
        (parent_id, hypothesis, role, title, json.dumps(spec or {}), depth, max_attempts, now, now, fingerprint))
    event(c, actor, "task.created", cur.lastrowid, role=role, title=title, hypothesis=hypothesis, parent=parent_id)
    return cur.lastrowid
