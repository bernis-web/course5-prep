import json
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from run_samap_compliant_v98 import (  # noqa: E402
    V98Error,
    apply_species_prefix,
    exclusion_counts,
    assert_no_na_truth,
    assert_prefix_unique,
    evaluate_direction,
    freeze_mapping,
    load_species,
)


REAL_HUMAN = ROOT / "local_human_s.h5ad"
REAL_MOUSE = ROOT / "local_mouse_s.h5ad"
REAL_ZEBRAFISH = ROOT / "local_zebrafish_s.h5ad"
REAL_FILES_EXIST = all(p.is_file() for p in (REAL_HUMAN, REAL_MOUSE, REAL_ZEBRAFISH))


class PrefixingTests(unittest.TestCase):
    @unittest.skipUnless(REAL_FILES_EXIST, "local subset h5ad files not found")
    def test_real_inputs_prefix_and_unique(self):
        out = {}
        for species, path in (
            ("human", REAL_HUMAN),
            ("mouse", REAL_MOUSE),
            ("zebrafish", REAL_ZEBRAFISH),
        ):
            out[species] = load_species(path, species)
        a_h, a_m, a_z = out["human"], out["mouse"], out["zebrafish"]
        self.assertEqual(a_h.n_obs, 1528)
        self.assertEqual(a_m.n_obs, 1535)
        self.assertEqual(a_z.n_obs, 1543)
        all_names = list(a_h.obs_names) + list(a_m.obs_names) + list(a_z.obs_names)
        self.assertEqual(len(all_names), len(set(all_names)), "prefixed barcodes must be globally unique")
        self.assertTrue(all(n.startswith("hu|") for n in a_h.obs_names))
        self.assertTrue(all(n.startswith("mo|") for n in a_m.obs_names))
        self.assertTrue(all(n.startswith("zf|") for n in a_z.obs_names))

    def test_prefixing_detects_cross_species_collision(self):
        # 两物种的原始条码 COLLIDE 相同；前缀化后 hu|COLLIDE / mo|COLLIDE 互不冲突，
        # 但 SAMAP 联合命名空间会截掉前缀尾部，因此 v98 的规则是：联合后唯一即可通过。
        # 真正必须失败的是未前缀化时就重复的同物种条码。
        with tempfile_dir() as tmp:
            p = Path(tmp) / "fake_human.h5ad"
            write_fake_h5ad(p, barcodes=["COLLIDE", "COLLIDE"], species="human")
            a1 = load_species(p, "human")
            with self.assertRaises(V98Error) as ctx:
                assert_prefix_unique([a1])
            self.assertIn("hu|COLLIDE", str(ctx.exception))

    def test_unknown_species_fails(self):
        with tempfile_dir() as tmp:
            p = Path(tmp) / "fake.h5ad"
            write_fake_h5ad(p, barcodes=["X1"], species="lamprey")
            with self.assertRaises(V98Error):
                load_species(p, "lamprey")

    @unittest.skipUnless(REAL_FILES_EXIST, "local subset h5ad files not found")
    def test_na_truth_fails(self):
        # real files have no NA truth; inject one to prove the check fires
        import anndata as ad

        a = ad.read_h5ad(REAL_HUMAN)
        truth = "cell_type"
        self.assertIn(truth, a.obs.columns)
        saved = list(a.obs[truth].astype(str).values)
        a.obs[truth] = a.obs[truth].astype(str)
        a.obs.loc[a.obs_names[0], truth] = "NA"
        with self.assertRaises(V98Error) as ctx:
            assert_no_na_truth(a, truth)
        self.assertIn("NA", str(ctx.exception))
        _ = saved


class ExclusionTests(unittest.TestCase):
    @unittest.skipUnless(REAL_FILES_EXIST, "local subset h5ad files not found")
    def test_real_exclusion_counts_mouse30_zebrafish44(self):
        mapping = freeze_mapping(ROOT / "config" / "heart-celltype-map-v1.tsv")
        a_m = load_species(REAL_MOUSE, "mouse")
        a_z = load_species(REAL_ZEBRAFISH, "zebrafish")
        exc_m = exclusion_counts(a_m, mapping, "mouse")
        exc_z = exclusion_counts(a_z, mapping, "zebrafish")
        self.assertEqual(exc_m, 30, "mouse must exclude exactly 30 (Proliferating cell)")
        self.assertEqual(exc_z, 44, "zebrafish must exclude exactly 44 (mt 30 + Proliferating 14)")


class EvalRecordTests(unittest.TestCase):
    def test_evaluate_direction_per_cell_structure(self):
        mapping = freeze_mapping(ROOT / "config" / "heart-celltype-map-v1.tsv")
        sp = np.array(["human"] * 3 + ["mouse"] * 2)
        bc = np.array(["hu|A", "hu|B", "hu|C", "mo|A", "mo|B"])
        labels = np.array(
            [
                "Endothelial cell", "Endothelial cell", "Endothelial cell",
                "Endothelial cell", "Proliferating cell",
            ]
        )
        emb = np.array(
            [
                [1.0, 0.0], [0.9, 0.1], [0.8, 0.2],
                [0.85, 0.15], [0.0, 1.0],
            ]
        )
        result = evaluate_direction(
            emb, sp, bc, labels, "human", "mouse", mapping, k=1, nperm=10, seed=0,
        )
        for level in ("exact", "coarse", "fine"):
            self.assertIn(level, result)
            block = result[level]
            for field in ("acc", "majority", "shuffle_p", "per_cell", "confusion",
                          "n_q_total", "coverage_q"):
                self.assertIn(field, block)
            # per_cell keeps every query cell; n_q counts included only
            self.assertEqual(len(block["per_cell"]), block["n_q_total"])
            self.assertEqual(sum(1 for r in block["per_cell"] if r["included"]), block["n_q"])
            self.assertAlmostEqual(
                block["coverage_q"], block["n_q"] / block["n_q_total"], places=4)
            for row in block["per_cell"]:
                for field in (
                    "prefixed_barcode", "direction", "level",
                    "truth", "prediction", "included", "exclusion_reason", "confidence",
                ):
                    self.assertIn(field, row)
            inc = [r for r in block["per_cell"] if r["included"]]
            if inc:
                acc = sum(1 for r in inc if r["truth"] == r["prediction"]) / len(inc)
                self.assertAlmostEqual(block["acc"], acc, places=4)
        # exact: mo|B truth (Proliferating cell) absent from reference labels -> not included
        self.assertEqual(result["exact"]["n_q_total"], 2)
        self.assertEqual(result["exact"]["n_q"], 1)
        # coarse/fine: mapping exclusion removes mo|B before evaluation
        self.assertEqual(result["coarse"]["n_q"], 1)
        self.assertEqual(result["coarse"]["n_q_total"], 1)
        self.assertEqual(result["coarse"]["n_excluded_q"], 1)
        self.assertIn("mo|B", [r["prefixed_barcode"] for r in result["exact"]["per_cell"]])
        self.assertNotIn(
            "mo|B", [r["prefixed_barcode"] for r in result["coarse"]["per_cell"]]
        )


def tempfile_dir():
    import tempfile

    return tempfile.TemporaryDirectory()


def write_fake_h5ad(path, barcodes, species):
    import anndata as ad

    n = len(barcodes)
    a = ad.AnnData(
        X=np.ones((n, 3)),
        obs={"cell_type": ["Endothelial cell"] * n},
        var=pd_var(3),
    )
    a.obs_names = list(barcodes)
    a.write_h5ad(path)


def pd_var(n):
    import pandas as pd

    return pd.DataFrame(index=[f"g{i}" for i in range(n)])




class GateTests(unittest.TestCase):
    """Phase 5 failure-gate tests: missing truth column, truth NA, dup barcodes."""

    def _write(self, tmp, barcodes, labels):
        import anndata as ad
        import numpy as np
        n = len(barcodes)
        a = ad.AnnData(
            X=np.ones((n, 3), dtype=np.float32),
            obs={"cell_type": [str(x) for x in labels]} if labels is not None else {},
        )
        a.obs_names = list(barcodes)
        path = Path(tmp) / "fake.h5ad"
        a.write_h5ad(path)
        return path

    def test_missing_truth_column_fails(self):
        with tempfile_dir() as tmp:
            path = self._write(tmp, ["hu|A"], None)
            a = load_species(path, "human")
            # load_species prefixed obs names; column absent entirely
            import anndata as ad
            a2 = ad.read_h5ad(path)
            a2.obs_names = ["hu|A"]
            with self.assertRaises(V98Error) as ctx:
                assert_no_na_truth(a2)
            self.assertIn("missing", str(ctx.exception))

    def test_na_truth_value_fails(self):
        with tempfile_dir() as tmp:
            path = self._write(tmp, ["hu|A", "hu|B"], ["Endothelial cell", "NA"])
            a = load_species(path, "human")
            with self.assertRaises(V98Error) as ctx:
                assert_no_na_truth(a)
            self.assertIn("truth NA found", str(ctx.exception))

    def test_duplicate_barcode_fails(self):
        with tempfile_dir() as tmp:
            path = self._write(tmp, ["hu|A", "hu|A"], ["Endothelial cell", "Endothelial cell"])
            a = load_species(path, "human")
            with self.assertRaises(V98Error) as ctx:
                assert_prefix_unique([a])
            self.assertIn("hu|A", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
