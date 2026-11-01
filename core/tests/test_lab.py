import importlib, os, sys, tempfile, unittest
from pathlib import Path

try:
    import numpy as np
    import pandas as pd
    import scipy  # noqa: F401
    HAVE_SCI = True
except ImportError:                     # system python without the science stack: the merge gate uses the sci venv
    HAVE_SCI = False

LAB = Path(__file__).resolve().parents[2] / "lab"


@unittest.skipUnless(HAVE_SCI, "needs numpy/pandas/scipy (kbrain sci venv)")
class Lab(unittest.TestCase):
    """The trusted evaluator against a tiny synthetic ProteinGym tree."""
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "dms" / "DMS").mkdir(parents=True)
        (self.root / "cv_folds" / "cv").mkdir(parents=True)
        (self.root / "zero_shot" / "scores" / "ESM2_35M").mkdir(parents=True)
        rng = np.random.default_rng(1)
        ref, lb = [], []
        for i, aid in enumerate(["P1_A", "P1_B", "P2_A"]):
            n = 200
            truth = rng.normal(size=n)
            df = pd.DataFrame({"mutant": [f"A{k + 1}G" for k in range(n)], "mutated_sequence": "M" * 10,
                               "DMS_score": truth, "DMS_score_bin": (truth > 0).astype(int)})
            df.to_csv(self.root / "dms" / "DMS" / f"{aid}.csv", index=False)
            folds = df.assign(fold_random_5=np.arange(n) % 5, fold_modulo_5=np.arange(n) % 5,
                              fold_contiguous_5=np.arange(n) * 5 // n)
            folds.to_csv(self.root / "cv_folds" / "cv" / f"{aid}.csv", index=False)
            pd.DataFrame({"mutant": df.mutant, "DMS_score": truth, "esm2_35M_score": truth + rng.normal(size=n)}) \
                .to_csv(self.root / "zero_shot" / "scores" / "ESM2_35M" / f"{aid}.csv", index=False)
            ref.append({"DMS_id": aid, "UniProt_ID": aid.split("_")[0], "selection_type": "Activity" if i < 2 else "Stability",
                        "target_seq": "M" * 10, "DMS_number_single_mutants": n})
            lb.append({"DMS ID": aid, "ESM2 (35M)": 0.3, "Site-Independent": 0.1})
        pd.DataFrame(ref).to_csv(self.root / "DMS_substitutions_reference.csv", index=False)
        pd.DataFrame(lb).to_csv(self.root / "leaderboard_spearman_DMS_level.csv", index=False)
        os.environ["KB_PG"] = str(self.root)
        sys.path.insert(0, str(LAB))
        import proteingym
        self.pg = importlib.reload(proteingym)

    def test_perfect_predictions_and_coverage_rule(self):
        df = self.pg.load_assay("P1_A")
        perfect = df.set_index("mutant")["DMS_score"]
        self.assertAlmostEqual(self.pg.spearman("P1_A", perfect), 1.0)
        with self.assertRaises(ValueError):                       # cherry-picking a subset is refused
            self.pg.spearman("P1_A", perfect.iloc[:100])

    def test_published_scores_and_units(self):
        s = self.pg.published_scores("P1_A", "ESM2 (35M)")         # name normalisation finds ESM2_35M
        self.assertEqual(len(s), 200)
        ours = {"P1_A": 0.5, "P1_B": 0.4, "P2_A": 0.2}
        units = self.pg.improvement_units(ours, "ESM2 (35M)")
        self.assertAlmostEqual(units["P1_A"], 0.2)
        by_protein = self.pg.improvement_units(ours, "ESM2 (35M)", by="protein")
        self.assertEqual(set(by_protein), {"P1", "P2"})
        self.assertAlmostEqual(by_protein["P1"], 0.15)
        self.assertAlmostEqual(self.pg.aggregate(ours), (0.45 + 0.2) / 2)
        self.assertEqual(self.pg.place_on_leaderboard(ours).index[0], "OURS")

    def test_cv_never_shows_test_labels_and_low_n_is_deterministic(self):
        seen = []
        def fit_predict(train, test):
            seen.append("DMS_score" in test.columns)
            return np.zeros(len(test)) + np.arange(len(test)) * 0.0
        self.pg.cross_validate("P1_A", fit_predict, scheme="contiguous")
        self.assertEqual(seen, [False] * 5)
        oracle = lambda tr, te: te.index.to_numpy()                  # no labels available: no signal
        a = self.pg.low_n("P1_A", oracle, n_train=24, reps=3)
        b = self.pg.low_n("P1_A", oracle, n_train=24, reps=3)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
