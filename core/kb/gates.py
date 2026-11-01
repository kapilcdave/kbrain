"""Deterministic gates. No LLM here: these encode kbrain/METHODOLOGY.md."""
import re
from pathlib import Path

# Section -> regexes; any match per section satisfies it.
PREREG_REQUIRED = {                                  # trading and experiment wording both accepted
    "hypothesis":  [r"hypothesis"],
    "universe":    [r"universe", r"\bdata(set)?s?\b", r"cohort", r"samples?"],
    "dates":       [r"evaluation (window|dates|split)", r"\bdates?\b", r"holdout", r"held[- ]out", r"test (set|split)"],
    "rules":       [r"entry", r"exit", r"\bmethods?\b", r"\bmodel\b", r"procedure"],
    "costs":       [r"fees?", r"slippage", r"costs?", r"compute", r"budget"],
    "unit":        [r"independent (sampling )?unit", r"cluster", r"\bfolds?\b"],
    "endpoint":    [r"primary endpoint", r"endpoint", r"primary metric"],
    "controls":    [r"controls?", r"baseline"],
    "outcomes":    [r"\bpass\b", r"\bfail\b", r"underpowered", r"blocked"],
}

def prereg_missing(path):
    p = Path(path)
    if not p.is_file():
        return ["<file missing>"]
    text = p.read_text(errors="replace").lower()
    return [k for k, pats in PREREG_REQUIRED.items()
            if not any(re.search(pt, text) for pt in pats)]
