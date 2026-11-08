import importlib.util
import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "dcs_provenance_v96_readout.py"


class DcsProvenanceV96ReadoutTests(unittest.TestCase):
    def test_readout_is_readonly_and_redacts_sensitive_lines(self):
        with tempfile.TemporaryDirectory(dir=str(REPO_ROOT)) as temp_dir:
            root = Path(temp_dir)
            v95_data = {
                "schema_version": "g5-provenance-v95-readonly/1",
                "generated_at_utc": "2026-09-27T09:30:00+00:00",
                "purpose": "test",
                "self_record": {"script_sha256": "a" * 64},
                "scope": {"walked_file_count": 1},
                "negative_findings": {"root_exists": True},
                "files": [
                    {
                        "relative_path": "prep_real_v60.py",
                        "size_bytes": 12,
                        "sha256": "b" * 64,
                    }
                ],
                "text_and_log_excerpts": [
                    {
                        "path": "/data/work/prep_real_v60.py",
                        "matches": [
                            {"line_number": 2, "line": "--in_label_col cell_type"},
                            {"line_number": 3, "line": "token=should-not-print"},
                        ],
                    }
                ],
                "h5ad_metadata": [
                    {
                        "path": "/data/work/final.h5ad",
                        "sha256": "c" * 64,
                        "shape": [4, 5],
                        "duplicate_barcode_count": 1,
                    }
                ],
            }
            out_path = root / "g5-provenance-v95-out.json"
            err_path = root / "g5-provenance-v95-err.log"
            command_path = root / "g5-provenance-v95-command.txt"
            out_path.write_text(json.dumps(v95_data), encoding="utf-8")
            err_path.write_text("no error\n", encoding="utf-8")
            command_path.write_text(
                "readonly command; token=should-not-print\n", encoding="utf-8"
            )
            before = {
                path.name: path.read_bytes()
                for path in (out_path, err_path, command_path)
            }

            os.environ["G5_V96_ROOT"] = str(root)
            try:
                spec = importlib.util.spec_from_file_location(
                    "dcs_provenance_v96_readout", SCRIPT
                )
                module = importlib.util.module_from_spec(spec)
                self.assertIsNotNone(spec.loader)
                spec.loader.exec_module(module)
                with contextlib.redirect_stdout(io.StringIO()):
                    module.main()
            finally:
                os.environ.pop("G5_V96_ROOT", None)

            result_path = root / "g5-provenance-v96-out.json"
            result = json.loads(result_path.read_text(encoding="utf-8"))
            self.assertTrue(result["v95_json_summary"]["json_valid"])
            self.assertEqual(result["v95_json_summary"]["file_entry_count"], 1)
            key_lines = result["v95_json_summary"]["key_lines"]
            self.assertEqual(key_lines[0]["line"], "--in_label_col cell_type")
            rendered = json.dumps(result, ensure_ascii=False)
            self.assertNotIn("should-not-print", rendered)
            self.assertIn("[REDACTED_SENSITIVE_LINE]", rendered)
            after = {
                path.name: path.read_bytes()
                for path in (out_path, err_path, command_path)
            }
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
