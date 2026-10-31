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
  result TEXT);
CREATE INDEX IF NOT EXISTS tasks_pick ON tasks(status, not_before, id);
CREATE TABLE IF NOT EXISTS runs(
  id INTEGER PRIMARY KEY, task_id INTEGER NOT NULL, model TEXT NOT NULL,
  started REAL NOT NULL, ended REAL, rc INTEGER, outcome TEXT, log_path TEXT);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY, ts REAL NOT NULL, actor TEXT NOT NULL,
  kind TEXT NOT NULL, task_id INTEGER, data TEXT NOT NULL DEFAULT '{}');
CREATE INDEX IF NOT EXISTS events_task ON events(task_id, id);
CREATE TABLE IF NOT EXISTS hypotheses(
  slug TEXT PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'idea',  -- idea|prereg|backtest|rejected|validated|paper|live
  path TEXT, updated REAL NOT NULL);
"""

def connect():
    STATE.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH, timeout=30, isolation_level=None)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    c.executescript(SCHEMA)
    return c

def event(c, actor, kind, task_id=None, **data):
    c.execute("INSERT INTO events(ts,actor,kind,task_id,data) VALUES(?,?,?,?,?)",
              (time.time(), actor, kind, task_id, json.dumps(data, default=str)))

def add_task(c, role, title, spec=None, parent_id=None, hypothesis=None,
             depth=0, max_attempts=4, actor="user"):
    now = time.time()
    cur = c.execute(
        "INSERT INTO tasks(parent_id,hypothesis,role,title,spec,depth,max_attempts,created,updated)"
        " VALUES(?,?,?,?,?,?,?,?,?)",
        (parent_id, hypothesis, role, title, json.dumps(spec or {}), depth, max_attempts, now, now))
    event(c, actor, "task.created", cur.lastrowid, role=role, title=title)
    return cur.lastrowid
