import json
import sys
import unittest
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from dcs_provenance_v99 import (  # noqa: E402
    ALLOWED_OUTPUT_ROOT,
    EXPECTED_EMBEDDING_SHAPE,
    FINAL_ANNADATA_PATH,
    PROTOCOL_LABEL,
    candidate_hashes,
    check_embedding_shape,
    compact_summary,
    ensure_output_root,
    hash_tree,
    knn_eval,
    output_path,
    per_cell_records,
    resolve_mapping,
    self_header,
)


class SafetyTests(unittest.TestCase):
    def test_output_paths_must_stay_under_allowed_root(self):
        with self.assertRaises(ValueError):
            output_path("../escape.json")
        p = output_path("predictions/hu-mo.json")
        self.assertTrue(str(p).replace("\\", "/").startswith("/data/work/course5_v99/"))
        with self.assertRaises(ValueError):
            output_path("x", root="/elsewhere")

    def test_protocol_label_is_transductive_formal(self):
        self.assertEqual(PROTOCOL_LABEL, "transductive_formal_reassessment")

    def test_final_anndata_path_is_whitelisted(self):
        self.assertEqual(
            FINAL_ANNADATA_PATH,
            "/data/work/saturn_out_real3_h/saturn_results/"
            "test256_data_human_saturn_input_hvg_mouse_saturn_input_hvg_"
            "zebrafish_saturn_input_hvg_org_human_seed_0.h5ad",
        )


class HashTests(unittest.TestCase):
    def test_candidate_hashes_handles_missing_without_raising(self):
        with tempfile_dir() as tmp:
            existing = Path(tmp) / "exists.txt"
            existing.write_text("hello", encoding="utf-8")
            result = candidate_hashes(
                {
                    "exists": str(existing),
                    "missing": str(Path(tmp) / "nope.txt"),
                }
            )
        self.assertEqual(result["exists"]["sha256"], _sha("hello"))
        self.assertEqual(result["exists"]["bytes"], 5)
        self.assertTrue(result["missing"]["missing"])

    def test_hash_tree_covers_all_files(self):
        with tempfile_dir() as tmp:
            (Path(tmp) / "a.txt").write_text("a", encoding="utf-8")
            sub = Path(tmp) / "sub"
            sub.mkdir()
            (sub / "b.txt").write_text("bb", encoding="utf-8")
            result = hash_tree(tmp)
        self.assertEqual(set(result.keys()), {"a.txt", "sub/b.txt"})
        self.assertEqual(result["a.txt"], _sha("a"))


class ShapeTests(unittest.TestCase):
    def test_expected_shape_constant(self):
        self.assertEqual(EXPECTED_EMBEDDING_SHAPE, (4606, 1000))

    def test_check_embedding_shape(self):
        check_embedding_shape((4606, 1000))
        with self.assertRaises(ValueError):
            check_embedding_shape((4606, 256))


class EvalTests(unittest.TestCase):
    def _cells(self):
        # 2 mouse reference (one active, one unmapped-excluded) +
        # 2 mouse query + 2 human query
        sp = ["mouse", "mouse", "mouse", "mouse", "human", "human"]
        bc = ["mo|A", "mo|B", "mo|C", "mo|D", "hu|A", "hu|B"]
        lab = [
            "Endothelial cell",
            "Endothelial cell",
            "Proliferating cell",  # not in active mapping
            "Endothelial cell",
            "Endothelial cell",
            "Endothelial cell",
        ]
        return sp, bc, lab

    def _mapping(self):
        return {
            "mouse|Endothelial cell": [
                "endothelial",
                "endothelial cell",
                "active",
            ],
            "human|Endothelial cell": [
                "endothelial",
                "endothelial cell",
                "active",
            ],
        }

    def test_resolve_mapping_flags_inactive(self):
        from dcs_provenance_v99 import mapping_status
        mapping = resolve_mapping(self._mapping())
        self.assertEqual(mapping["mouse|Endothelial cell"][2], "active")
        # 未知 key 不在映射中 → 细胞级状态函数判 inactive
        self.assertEqual(mapping_status("mouse|Proliferating cell", mapping), "inactive")

    def test_knn_eval_excludes_inactive_on_both_sides(self):
        sp, bc, lab = self._cells()
        emb = np.array(
            [
                [1.0, 0.0],
                [0.9, 0.1],
                [0.0, 1.0],
                [0.1, 0.9],
                [0.95, 0.05],
                [0.05, 0.95],
            ]
        )
        spv = np.array(sp)
        bcv = np.array(bc)
        mapping = resolve_mapping(self._mapping())
        m_s = spv == "mouse"
        m_t = spv == "human"
        result = knn_eval(
            m_s, m_t, emb, lab,
            key_arr=np.array([s + "|" + l for s, l in zip(sp, lab)]),
            mapping=mapping, level="coarse", k=1, nperm=10, seed=0,
        )
        # inactive ref cell (mo|C) must be excluded; both human cells are active
        self.assertEqual(result["n_ref"], 3)
        self.assertEqual(result["n_q"], 2)
        self.assertEqual(result["n_excluded_ref"], 1)
        self.assertEqual(result["n_excluded_q"], 0)

    def test_per_cell_records_fields(self):
        sp, bc, lab = self._cells()
        emb = np.array(
            [
                [1.0, 0.0],
                [0.9, 0.1],
                [0.0, 1.0],
                [0.1, 0.9],
                [0.95, 0.05],
                [0.05, 0.95],
            ]
        )
        spv = np.array(sp)
        records = per_cell_records(
            sp,
            bc,
            lab,
            emb,
            src="mouse",
            tgt="human",
            level="exact",
            k=1,
            nperm=10,
            seed=0,
        )
        self.assertEqual(len(records), 2)
        for row in records:
            for field in (
                "prefixed_barcode",
                "direction",
                "level",
                "truth",
                "prediction",
                "included",
                "exclusion_reason",
            ):
                self.assertIn(field, row)
        self.assertTrue(all(r["included"] for r in records))

    def test_compact_summary_under_20kb(self):
        summary = compact_summary(
            {"mouse->human": {"exact": {"knn": {"acc": 1.0, "n_q": 2}}}},
            {"mouse->human": {"exact": [{"prefixed_barcode": "mo|A"}]}},
        )
        self.assertLess(len(summary), 20 * 1024)


class NotebookFallbackTests(unittest.TestCase):
    def test_notebook_text_is_valid_json_structure(self):
        from dcs_provenance_v99 import notebook_fallback_text

        text = notebook_fallback_text({"metrics": {"acc": 1.0}})
        parsed = json.loads(text)
        self.assertEqual(parsed["nbformat"], 4)
        cells = parsed["cells"]
        self.assertTrue(any("metrics" in json.dumps(c) for c in cells))


def _sha(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tempfile_dir():
    import tempfile

    return tempfile.TemporaryDirectory()


if __name__ == "__main__":
    unittest.main()
