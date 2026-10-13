"""Synthetic technical tests; these do not assert real image or story quality."""
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image, ImageDraw

from anchor_audit import audit


class AnchorAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.contract = {
            "schemaVersion": 1,
            "frame": {"width": 16, "height": 12, "pixelAspectRatio": "1:1"},
            "activePicture": {"x": 0, "y": 2, "width": 16, "height": 8},
            "matte": {"color": [0, 0, 0], "tolerance": 0},
            "fileNamePattern": r"^S[0-9]{2}-I[0-9]{2}__T[0-9]{6}__[a-z0-9-]+__[a-z0-9-]+\.(png|jpg|jpeg)$",
            "failOnExactDuplicates": True,
            "possibleDuplicateHammingDistance": 2,
        }

    def image(self, name, color, mark):
        image = Image.new("RGB", (16, 12), "black")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 2, 15, 9), fill=color)
        draw.rectangle(mark, fill="white")
        image.save(self.base / name)

    def test_matching_library_passes_technical_contract(self):
        self.image("S01-I01__T000000__first__test.png", "red", (1, 3, 3, 5))
        self.image("S01-I02__T002000__second__test.png", "blue", (12, 6, 14, 8))
        result = audit(self.contract, self.base)
        self.assertTrue(result["technicalPass"])
        self.assertEqual(result["imageCount"], 2)
        self.assertTrue(result["visualReviewRequired"])

    def test_inconsistent_matte_fails(self):
        self.image("S01-I01__T000000__first__test.png", "red", (1, 3, 3, 5))
        path = self.base / "S01-I01__T000000__first__test.png"
        image = Image.open(path).convert("RGB")
        image.putpixel((0, 0), (255, 0, 0))
        image.save(path)
        result = audit(self.contract, self.base)
        self.assertFalse(result["technicalPass"])
        self.assertIn("matte_contract", result["images"][0]["issues"])

    def test_exact_duplicate_fails(self):
        self.image("S01-I01__T000000__first__test.png", "red", (1, 3, 3, 5))
        source = Image.open(self.base / "S01-I01__T000000__first__test.png")
        source.save(self.base / "S01-I02__T002000__second__test.png")
        result = audit(self.contract, self.base)
        self.assertFalse(result["technicalPass"])
        self.assertEqual(len(result["exactDuplicates"]), 1)

    def test_bad_name_fails(self):
        self.image("anchor.png", "red", (1, 3, 3, 5))
        result = audit(self.contract, self.base)
        self.assertFalse(result["technicalPass"])
        self.assertIn("filename_contract", result["images"][0]["issues"])


if __name__ == "__main__":
    unittest.main()
