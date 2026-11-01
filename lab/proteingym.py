"""kbrain lab: the ONE trusted evaluator for protein mutation-effect prediction on ProteinGym v1.3.

Operator-owned (agents may import it, never edit it; the merge gate refuses changes to lab/). Every result
kbrain reports is scored here, so nobody can bend the evaluation:

    import proteingym as pg
    ids = pg.assays()                              # 217 DMS substitution assays
    df = pg.load_assay(ids[0])                     # mutant, mutated_sequence, DMS_score (+ fold columns)
    esm = pg.published_scores(ids[0], "ESM2 (35M)")  # a leaderboard model's per-mutant scores
    rho = pg.spearman_by_assay({aid: my_series})   # per-assay Spearman; requires full coverage
    units = pg.improvement_units(rho, "ESM2 (35M)")  # {unit: ours - baseline} for kbstats.evaluate
    pg.place_on_leaderboard(rho)                   # where we would rank on the SAME assays

Supervised / low-N: the lab owns the split, so test labels can never leak into training:
    pg.cross_validate(aid, fit_predict, scheme="contiguous")   # official 5-fold folds
    pg.low_n(aid, fit_predict, n_train=48, reps=5)              # n labeled mutants, predict the rest
  where fit_predict(train_df, test_df) -> predictions for test_df (array-like, same order).
"""
import os
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

MIN_COVERAGE = 0.95          # a prediction set must cover >=95% of an assay's mutants (no cherry-picking)


def _root():
    for p in (os.environ.get("KB_PG"), "data/proteingym",
              Path(__file__).resolve().parent.parent / "core" / "state" / "data" / "proteingym"):
        if p and Path(p).is_dir():
            return Path(p)
    raise FileNotFoundError("ProteinGym data not found (set KB_PG or run from a workspace with data/proteingym)")


@lru_cache(maxsize=1)
def reference():
    """One row per assay: UniProt_ID, taxon, seq_len, selection_type, MSA_Neff_L_category, ..."""
    return pd.read_csv(_root() / "DMS_substitutions_reference.csv").set_index("DMS_id")


def assays(singles_only=False):
    ref = reference()
    if singles_only:
        ref = ref[ref["DMS_number_single_mutants"] > 0]
    return sorted(ref.index)


def _dms_file(aid):
    hits = list(_root().glob(f"dms/*/{aid}.csv"))
    if not hits:
        raise KeyError(f"unknown assay {aid}")
    return hits[0]


@lru_cache(maxsize=32)
def _load(aid, folds):
    if folds:
        hits = list(_root().glob(f"cv_folds/*/{aid}.csv"))
        if not hits:
            raise KeyError(f"no CV folds for {aid} (folds exist for single-substitution assays)")
        return pd.read_csv(hits[0])
    return pd.read_csv(_dms_file(aid))


def load_assay(aid, folds=False):
    """mutant, mutated_sequence, DMS_score, DMS_score_bin (+ fold_random_5, fold_modulo_5, fold_contiguous_5)."""
    return _load(aid, folds).copy()


def wild_type(aid):
    return reference().loc[aid, "target_seq"]


@lru_cache(maxsize=1)
def leaderboard():
    """Published per-assay zero-shot Spearman (rows: assays, columns: models)."""
    lb = pd.read_csv(_root() / "leaderboard_spearman_DMS_level.csv")
    key = "DMS ID" if "DMS ID" in lb.columns else "DMS_id"
    return lb.set_index(key)


_META = {"mutant", "mutated_sequence", "DMS_score", "DMS_score_bin"}


def _norm(name):
    return "".join(ch for ch in str(name).lower() if ch.isalnum())


@lru_cache(maxsize=8)
def _scores_table(aid):
    """ProteinGym v1.3 ships one file per assay with every published model as a column."""
    f = _root() / "zero_shot" / f"{aid}.csv"
    if not f.is_file():
        raise FileNotFoundError(f"no published zero-shot scores for {aid}")
    return pd.read_csv(f).set_index("mutant")


def published_models(aid=None):
    """Model columns available in the published score files (e.g. ESM2_35M, GEMME, Site_Independent)."""
    aid = aid or assays()[0]
    return [c for c in _scores_table(aid).columns if c not in _META]


def published_scores(aid, model):
    """A published model's per-mutant zero-shot score for one assay, as a Series indexed by mutant.
    Accepts the score-file name (ESM2_35M) or the leaderboard name (ESM2 (35M))."""
    t = _scores_table(aid)
    want = _norm(model)
    for c in t.columns:
        if c not in _META and _norm(c) == want:
            return t[c].rename(c)
    raise KeyError(f"no published model {model!r} for {aid}; see published_models()")


def _as_series(preds):
    if isinstance(preds, pd.Series):
        return preds
    if isinstance(preds, dict):
        return pd.Series(preds)
    raise TypeError("predictions must be a Series or dict indexed by mutant")


def spearman(aid, preds):
    """Spearman between predictions and DMS_score on one assay. Requires >=95% coverage of its mutants."""
    truth = load_assay(aid).set_index("mutant")["DMS_score"]
    p = _as_series(preds).reindex(truth.index)
    cov = p.notna().mean()
    if cov < MIN_COVERAGE:
        raise ValueError(f"{aid}: predictions cover {cov:.1%} of mutants (< {MIN_COVERAGE:.0%}); score the whole assay")
    m = p.notna()
    return float(spearmanr(p[m], truth[m]).correlation)


def spearman_by_assay(preds_by_assay):
    """{assay: predictions} -> {assay: Spearman}."""
    return {aid: spearman(aid, p) for aid, p in preds_by_assay.items()}


def aggregate(rho_by_assay):
    """ProteinGym's headline aggregation: mean within UniProt_ID, then within selection type, then across types."""
    ref = reference()
    col = "coarse_selection_type" if "coarse_selection_type" in ref.columns else "selection_type"
    s = pd.Series(rho_by_assay, dtype=float)
    df = pd.DataFrame({"rho": s, "uniprot": ref.loc[s.index, "UniProt_ID"], "type": ref.loc[s.index, col]})
    per_protein = df.groupby(["type", "uniprot"])["rho"].mean()
    return float(per_protein.groupby(level=0).mean().mean())


def improvement_units(ours, baseline, by="assay"):
    """{unit: our Spearman - baseline Spearman} for kbstats.evaluate. `baseline` is a leaderboard model name or
    a {assay: Spearman} dict. by="protein" averages assays of the same UniProt_ID first (stricter independence)."""
    ours = pd.Series(ours, dtype=float)
    if isinstance(baseline, str):
        base = leaderboard()[baseline].reindex(ours.index)
    else:
        base = pd.Series(baseline, dtype=float).reindex(ours.index)
    diff = (ours - base).dropna()
    if by == "protein":
        diff = diff.groupby(reference().loc[diff.index, "UniProt_ID"]).mean()
    return {str(k): float(v) for k, v in diff.items()}


def place_on_leaderboard(rho_by_assay):
    """Rank our method against every published model on the SAME assays (mean per-assay Spearman)."""
    lb = leaderboard().reindex(list(rho_by_assay)).apply(pd.to_numeric, errors="coerce")
    table = lb.mean().rename("mean_spearman").to_frame()
    table.loc["OURS", "mean_spearman"] = float(np.mean(list(rho_by_assay.values())))
    table = table.sort_values("mean_spearman", ascending=False)
    table["rank"] = range(1, len(table) + 1)
    return table


# ---------------------------------------------------------------- supervised / low-N (the lab owns the split)
SCHEMES = {"random": "fold_random_5", "modulo": "fold_modulo_5", "contiguous": "fold_contiguous_5"}


def cross_validate(aid, fit_predict, scheme="contiguous"):
    """ProteinGym's official 5-fold CV. fit_predict(train_df, test_df) only ever sees the training fold's labels.
    Returns the Spearman of the out-of-fold predictions over the whole assay."""
    df = load_assay(aid, folds=True)
    col = SCHEMES[scheme]
    oof = pd.Series(np.nan, index=df.index)
    for k in sorted(df[col].unique()):
        test = df[col] == k
        train_df = df.loc[~test].reset_index(drop=True)
        test_df = df.loc[test].drop(columns=["DMS_score", "DMS_score_bin"]).reset_index(drop=True)
        pred = np.asarray(fit_predict(train_df, test_df), dtype=float)
        if len(pred) != test.sum():
            raise ValueError("fit_predict must return one prediction per test row")
        oof[test] = pred
    return float(spearmanr(oof, df["DMS_score"]).correlation)


def low_n(aid, fit_predict, n_train=48, reps=5, seed=0):
    """n_train labeled mutants drawn at random (fixed seeds), predict all the others. Mean Spearman over reps."""
    df = load_assay(aid)
    if len(df) <= n_train + 10:
        raise ValueError(f"{aid} has too few mutants for n_train={n_train}")
    out = []
    for r in range(reps):
        rng = np.random.default_rng(seed + r)
        idx = rng.permutation(len(df))
        tr, te = df.iloc[idx[:n_train]].reset_index(drop=True), df.iloc[idx[n_train:]]
        test_df = te.drop(columns=["DMS_score", "DMS_score_bin"]).reset_index(drop=True)
        pred = np.asarray(fit_predict(tr, test_df), dtype=float)
        out.append(spearmanr(pred, te["DMS_score"].to_numpy()).correlation)
    return float(np.mean(out))
