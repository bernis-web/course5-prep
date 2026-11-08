import sys
import unittest
from pathlib import Path

import numpy as np

SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from build_transductive_bundles import (  # noqa: E402
    BundleBuildError,
    CellRecord,
    SPECIES_PREFIXES,
    canonical_species,
    direction_bundles,
    level_mapping,
    load_mapping_rows,
    prefixed_barcode,
    validate_cells,
)


class MappingNamespaceTests(unittest.TestCase):
    def test_species_names_are_canonicalized_and_prefixed(self):
        self.assertEqual(canonical_species("Homo_sapiens"), "human")
        self.assertEqual(canonical_species("Mus_musculus"), "mouse")
        self.assertEqual(canonical_species("Danio_rerio"), "zebrafish")
        self.assertEqual(prefixed_barcode("human", "AAAC-1"), "hu|AAAC-1")
        self.assertEqual(prefixed_barcode("mouse", "AAAC-1"), "mo|AAAC-1")
        self.assertEqual(prefixed_barcode("zebrafish", "AAAC-1"), "zf|AAAC-1")
        with self.assertRaises(BundleBuildError):
            canonical_species("lamprey")

    def test_level_mapping_is_direction_safe_and_excludes_unmapped(self):
        rows = [
            {
                "source_species": "human",
                "source_label": "Endothelial cell",
                "coarse_level": "endothelial",
                "fine_mapped_label": "endothelial cell",
                "mapping_status": "active",
            },
            {
                "source_species": "mouse",
                "source_label": "Endothelial cell",
                "coarse_level": "endothelial",
                "fine_mapped_label": "endothelial cell",
                "mapping_status": "active",
            },
            {
                "source_species": "mouse",
                "source_label": "Proliferating cell",
                "coarse_level": "other",
                "fine_mapped_label": "unmapped",
                "mapping_status": "unmapped",
            },
        ]
        mapping = level_mapping(rows, {"human", "mouse"}, "coarse")
        self.assertEqual(mapping["Endothelial cell"], "endothelial")
        self.assertNotIn("Proliferating cell", mapping)

    def test_conflicting_mappings_are_rejected(self):
        rows = [
            {
                "source_species": "human",
                "source_label": "Valve",
                "coarse_level": "fibroblast",
                "fine_mapped_label": "human valve",
                "mapping_status": "active",
            },
            {
                "source_species": "mouse",
                "source_label": "Valve",
                "coarse_level": "fibroblast",
                "fine_mapped_label": "mouse valve",
                "mapping_status": "active",
            },
        ]
        with self.assertRaises(BundleBuildError):
            level_mapping(rows, {"human", "mouse"}, "fine")

    def test_real_mapping_file_loads(self):
        root = Path(__file__).resolve().parents[1]
        rows = load_mapping_rows(root / "config" / "heart-celltype-map-v1.tsv")
        self.assertEqual(len(rows), 38)
        self.assertEqual(SPECIES_PREFIXES["zebrafish"], "zf")


class DirectionBundleTests(unittest.TestCase):
    def _cells(self):
        return [
            CellRecord("hu|E1", "human", "Endothelial cell", 0),
            CellRecord("mo|E1", "mouse", "Endothelial cell", 1),
            CellRecord("zf|E2", "zebrafish", "Endothelial cell", 2),
            CellRecord("zf|P1", "zebrafish", "Proliferating cell", 3),
        ]

    def _embedding(self):
        return np.array(
            [
                [1.0, 0.0],
                [0.0, 1.0],
                [0.9, 0.1],
                [0.1, 0.9],
            ],
            dtype=float,
        )

    def _mapping_rows(self):
        return [
            {
                "source_species": "human",
                "source_label": "Endothelial cell",
                "coarse_level": "endothelial",
                "fine_mapped_label": "endothelial cell",
                "mapping_status": "active",
            },
            {
                "source_species": "mouse",
                "source_label": "Endothelial cell",
                "coarse_level": "endothelial",
                "fine_mapped_label": "endothelial cell",
                "mapping_status": "active",
            },
            {
                "source_species": "zebrafish",
                "source_label": "Endothelial cell",
                "coarse_level": "endothelial",
                "fine_mapped_label": "endothelial cell",
                "mapping_status": "active",
            },
            {
                "source_species": "zebrafish",
                "source_label": "Proliferating cell",
                "coarse_level": "other",
                "fine_mapped_label": "unmapped",
                "mapping_status": "unmapped",
            },
        ]

    def test_directions_are_complete_and_ordered(self):
        descriptions = direction_bundles(self._cells(), self._embedding(), self._mapping_rows())
        self.assertEqual(
            sorted(descriptions),
            [
                "hu->mo", "hu->zf", "mo->hu",
                "mo->zf", "zf->hu", "zf->mo",
            ],
        )
        item = descriptions["hu->mo"]
        self.assertEqual(item["reference_species"], "human")
        self.assertEqual(item["query_species"], "mouse")
        self.assertEqual(item["exact"]["n_reference"], 1)
        self.assertEqual(item["exact"]["n_query"], 1)
        self.assertIn("Endothelial cell", item["coarse"]["mapping"])

    def test_fish_direction_reports_unmapped_exclusions(self):
        descriptions = direction_bundles(self._cells(), self._embedding(), self._mapping_rows())
        fish_item = descriptions["hu->zf"]
        self.assertEqual(fish_item["exact"]["n_query"], 2)
        self.assertEqual(fish_item["coarse"]["n_query"], 1)
        self.assertEqual(fish_item["fine"]["n_unmapped_query"], 1)
        self.assertNotIn("zf|P1", fish_item["coarse"]["selected_cells"])
        self.assertNotIn("zf|P1", fish_item["fine"]["selected_cells"])
        self.assertIn("zf|P1", fish_item["exact"]["selected_cells"])

    def test_validate_cells_rejects_duplicate_prefixed_barcodes(self):
        with self.assertRaises(BundleBuildError):
            validate_cells(
                ["human", "human"],
                ["AAAC-1", "AAAC-1"],
                ["A", "B"],
            )

    def test_embedding_shape_must_match_cells(self):
        with self.assertRaises(BundleBuildError):
            direction_bundles(self._cells(), self._embedding()[:2], self._mapping_rows())


if __name__ == "__main__":
    unittest.main()
