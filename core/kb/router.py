import tomllib
from .db import ROOT

def load_config():
    with open(ROOT / "config" / "routing.toml", "rb") as f:
        return tomllib.load(f)

def family(model):          # "claude:claude-sonnet-5-5" -> "claude"; "api:groq/x" -> "api:groq"
    b, _, rest = model.partition(":")
    return f"api:{rest.split('/')[0]}" if b == "api" else b

def pick_model(c, cfg, task):
    """Fallback chain per role; `independent_of` role avoids the author's backend family."""
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
    idx = min(task["model_idx"], len(models) - 1)
    return models[idx], len(models)
