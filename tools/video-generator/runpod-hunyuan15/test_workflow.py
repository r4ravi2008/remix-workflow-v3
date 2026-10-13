import argparse
import unittest

from run_hunyuan15 import build_prompt


class WorkflowTests(unittest.TestCase):
    def args(self, **changes):
        values = dict(prompt="Quiet lateral tracking", negative_prompt="singing", frames=49,
                      steps=20, seed=20260922, output_prefix="test", width=1280,
                      height=528, sr_width=1936, sr_height=800, crf=16,
                      stage="base", save_latent=True, tiled_vae=True, latent=None)
        values.update(changes)
        return argparse.Namespace(**values)

    def assert_links_resolve(self, graph):
        for node in graph.values():
            for value in node["inputs"].values():
                if isinstance(value, list) and len(value) == 2 and isinstance(value[1], int):
                    self.assertIn(value[0], graph)

    def test_base_has_no_sr_models(self):
        graph = build_prompt(self.args(), "anchor.png")
        self.assert_links_resolve(graph)
        self.assertEqual(graph["117"]["inputs"]["samples"], ["125", 0])
        self.assertEqual(graph["117"]["inputs"]["temporal_size"], 4096)
        self.assertNotIn("111", graph)
        self.assertIn("151", graph)

    def test_refine_reuses_latent(self):
        graph = build_prompt(self.args(stage="sr", latent="saved.latent"), "anchor.png")
        self.assert_links_resolve(graph)
        self.assertNotIn("12", graph)
        self.assertNotIn("151", graph)
        self.assertEqual(graph["109"]["inputs"]["samples"], ["150", 0])

    def test_refine_requires_latent(self):
        with self.assertRaises(ValueError):
            build_prompt(self.args(stage="sr"), "anchor.png")

    def test_full_and_legacy_decode(self):
        graph = build_prompt(self.args(stage="full", tiled_vae=False), "anchor.png")
        self.assert_links_resolve(graph)
        self.assertEqual(graph["117"]["class_type"], "VAEDecode")
        self.assertEqual(graph["109"]["inputs"]["width"], 1936)


if __name__ == "__main__":
    unittest.main()
