import time, tomllib
from .db import ROOT
from . import adapters

def load_config():
    with open(ROOT / "config" / "routing.toml", "rb") as f:
        return tomllib.load(f)

def family(model):          # "claude:claude-sonnet-5-5" -> "claude"; "api:groq/x" -> "api:groq"
    b, _, rest = model.partition(":")
    return f"api:{rest.split('/')[0]}" if b == "api" else b

def pick_model(c, cfg, task):
    """Pick an available model, skipping shared rate-limit cooldowns."""
    role = cfg["roles"][task["role"]]
    models = list(role["models"])
    indep = role.get("independent_of")
    if indep and task["hypothesis"]:
        row = c.execute(
            "SELECT r.model FROM runs r JOIN tasks t ON t.id=r.task_id "
            "WHERE t.hypothesis=? AND t.role=? AND r.outcome='ok' ORDER BY r.id DESC LIMIT 1",
            (task["hypothesis"], indep)).fetchone()
        if row:
            other = [m for m in models if family(m) != family(row["model"])]
            if other:
                models = other + [m for m in models if m not in other]
    now = time.time()
    cooldowns = {r["model"]: r["until_ts"] for r in c.execute(
        "SELECT model,until_ts FROM model_cooldowns WHERE until_ts>?", (now,))}
    start = min(task["model_idx"], len(models) - 1)
    for idx in range(start, len(models)):
        if models[idx] not in cooldowns and adapters.available(models[idx]):
            return models[idx], len(models), idx, None
    return None, len(models), None, min((cooldowns[m] for m in models[start:] if m in cooldowns), default=now + 300)
