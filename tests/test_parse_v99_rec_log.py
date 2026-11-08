"""Fixture dry-run for parse_v99_rec_log_v1.py (R1 recovery log parser).

Builds a synthetic R1-protocol log with known SHA values and verifies the
parser's full path: tsv b64 reconstruction, metrics/confusion byte-exact
recovery, CONFDUP identity, PREDMETA/PREDPLAN accounting, and the
Windows-illegal '->' filename sanitisation map.
"""
import base64
import gzip
import hashlib
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def sha(b):
    return hashlib.sha256(b).hexdigest()


def build_fixture(tmp: Path):
    metrics_bytes = json.dumps({"human->mouse": {"coarse": {"acc": 0.5}}}, indent=1).encode()
    conf_bytes = json.dumps({"CM=>CM": 3, "CM=>FB": 1}, sort_keys=True).encode()
    rows = [
        {"prefixed_barcode": "mo|A", "truth": "CM", "prediction": "CM", "included": True,
         "confidence": 0.9, "exclusion_reason": "", "neighbor_barcodes": ["hu|X"]},
        {"prefixed_barcode": "mo|B", "truth": "CM", "prediction": "FB", "included": True,
         "confidence": 0.6, "exclusion_reason": "", "neighbor_barcodes": []},
        {"prefixed_barcode": "mo|C", "truth": "CM", "prediction": "CM", "included": True,
         "confidence": 0.7, "exclusion_reason": "", "neighbor_barcodes": []},
        {"prefixed_barcode": "mo|D", "truth": "CM", "prediction": "CM", "included": True,
         "confidence": 0.8, "exclusion_reason": "", "neighbor_barcodes": []},
    ]
    pred_bytes = json.dumps(rows).encode()
    compact = [[r["prefixed_barcode"], r["truth"], r["prediction"],
                1 if r["included"] else 0, r["confidence"], r["exclusion_reason"]] for r in rows]
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9, mtime=0) as g:
        g.write(json.dumps(compact, separators=(",", ":"), ensure_ascii=False).encode())
    gz = buf.getvalue()
    pred_b64 = base64.b64encode(gz).decode()
    tsv_bytes = (
        f"{sha(metrics_bytes)}  metrics.json\n"
        f"{sha(conf_bytes)}  confusion/coarse_human->mouse.json\n"
        f"{sha(pred_bytes)}  predictions/coarse_human->mouse.json\n"
        f"{'f' * 64}  sha256.tsv\n"
    ).encode()

    lines = [
        "===HASHVER===",
        f"HASHVER|metrics.json|{sha(metrics_bytes)}|{len(metrics_bytes)}",
        f"HASHVER|confusion/coarse_human->mouse.json|{sha(conf_bytes)}|{len(conf_bytes)}",
        f"HASHVER|predictions/coarse_human->mouse.json|{sha(pred_bytes)}|{len(pred_bytes)}",
        f"HASHVER|sha256.tsv|{sha(tsv_bytes)}|{len(tsv_bytes)}",
        "SHATSVB64|" + base64.b64encode(tsv_bytes).decode(),
        "===METRICS===", metrics_bytes.decode(), "===END_METRICS===",
        "===CONF|confusion/coarse_human->mouse.json===", conf_bytes.decode(), "===END_CONF===",
        "CONFDUP|confusion/fine_human->mouse.json|=confusion/coarse_human->mouse.json|True",
        "===PREDMETA===",
        f"PREDMETA|predictions/coarse_human->mouse.json|{len(pred_bytes)}|{sha(pred_bytes)}|4|4|0.750000",
        f"PREDPLAN|predictions/coarse_human->mouse.json|{len(pred_b64)}|{sha(gz)}",
        "===END===",
    ]
    log = tmp / "r1_fixture.log"
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log, metrics_bytes, conf_bytes, tsv_bytes, gz


class ParserFixtureTests(unittest.TestCase):
    def test_full_parse_path(self):
        import tempfile

        import parse_v99_rec_log_v1 as parser

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            log, metrics_bytes, conf_bytes, tsv_bytes, gz = build_fixture(tmp)
            parser_raw = (ROOT / "scripts" / "parse_v99_rec_log_v1.py").read_text(encoding="utf-8")
            parser_raw = parser_raw.replace(
                r'RAW = Path(r"D:\projects\course5-prep\results\pilot-v1\saturn-v99\raw")',
                f'RAW = Path({str(tmp)!r})')
            parser_raw = parser_raw.replace(
                '"metrics.json": "d1081cfd2489bf2afd30af7706fadf2d08b90390c26d38a766ea97b54b3dc261",',
                f'"metrics.json": "{sha(metrics_bytes)}",')
            parser_raw = parser_raw.replace(
                '"sha256.tsv": "c84dd3780cb0db09f54ef4020a4e1e6ad91aef72433c949079634f6fcc35d687",',
                f'"sha256.tsv": "{sha(tsv_bytes)}",')
            mod_path = tmp / "parser_under_test.py"
            mod_path.write_text(parser_raw, encoding="utf-8")

            import importlib.util
            spec = importlib.util.spec_from_file_location("parser_under_test", mod_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            old_argv = sys.argv
            try:
                sys.argv = ["parser_under_test.py", str(log)]
                rc = mod.main()
            finally:
                sys.argv = old_argv
            self.assertEqual(rc, 0)

            out = tmp / "recovered-20261001"
            self.assertIn((out / "metrics.json").read_bytes(), (metrics_bytes, metrics_bytes + b"\n"))
            self.assertIn(
                (out / "confusion" / "coarse_human_to_mouse.json").read_bytes(),
                (conf_bytes, conf_bytes + b"\n"))
            self.assertEqual((out / "sha256.tsv").read_bytes(), tsv_bytes)
            rep = json.loads((out / "_r1-verification.json").read_text(encoding="utf-8"))
            self.assertTrue(rep["confusion_all_ok"])
            self.assertTrue(rep["confdup_all_true"])
            self.assertTrue(rep["predmeta_sha_ok"])
            self.assertEqual(rep["predmeta_count"], 1)
            self.assertEqual(rep["predplan"]["predictions/coarse_human->mouse.json"], len(base64.b64encode(gz).decode()))
            self.assertEqual(rep["local_name_map"]["confusion/coarse_human->mouse.json"],
                             "confusion/coarse_human_to_mouse.json")


if __name__ == "__main__":
    unittest.main()
