"""Deterministic gates. No LLM here: these encode kbrain/METHODOLOGY.md."""
import re
from pathlib import Path

# Section -> regexes; any match per section satisfies it.
PREREG_REQUIRED = {
    "hypothesis":  [r"hypothesis"],
    "universe":    [r"universe"],
    "dates":       [r"evaluation (window|dates)", r"\bdates?\b", r"holdout"],
    "rules":       [r"entry", r"exit"],
    "costs":       [r"fees?", r"slippage", r"costs?"],
    "unit":        [r"independent (sampling )?unit", r"cluster"],
    "endpoint":    [r"primary endpoint", r"endpoint"],
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
