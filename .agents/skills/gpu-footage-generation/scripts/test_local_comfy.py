import unittest

import local_comfy as lc


def links(graph):
    for node_id, node in graph.items():
        for value in node["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                yield node_id, value[0]


class GraphTests(unittest.TestCase):
    def assert_closed(self, graph):
        for node_id, target in links(graph):
            self.assertIn(target, graph, f"{node_id} links to missing node {target}")

    def test_flux_chains_every_reference_on_both_conditionings(self):
        graph, out = lc.flux_graph("p", ["a/x.png", "a/y.png"], 1360, 768, 7, "a/job")
        self.assert_closed(graph)
        refs = [n for n in graph.values() if n["class_type"] == "ReferenceLatent"]
        self.assertEqual(len(refs), 4)
        guider = graph["14"]["inputs"]
        self.assertEqual(graph[guider["positive"][0]]["class_type"], "ReferenceLatent")
        self.assertEqual(graph[guider["negative"][0]]["class_type"], "ReferenceLatent")
        self.assertEqual(graph[out]["class_type"], "SaveImage")

    def test_flux_without_references_uses_plain_conditioning(self):
        graph, _ = lc.flux_graph("p", [], 1024, 1024, 1, "a/job")
        self.assert_closed(graph)
        self.assertEqual(graph["14"]["inputs"]["positive"], ["4", 0])

    def test_flux_img2img_starts_from_encoded_init_with_split_sigmas(self):
        graph, _ = lc.flux_graph("p", ["a/s.png"], 1360, 768, 1, "a/job", 8, init="a/src.png", denoise=0.5)
        self.assert_closed(graph)
        self.assertEqual(graph["15"]["inputs"]["latent_image"], ["92", 0])
        self.assertEqual(graph["15"]["inputs"]["sigmas"], ["93", 1])
        self.assertEqual(graph["93"]["inputs"]["denoise"], 0.5)

    def test_flux_masked_img2img_protects_unmasked_pixels(self):
        graph, _ = lc.flux_graph("p", [], 1360, 768, 1, "a/job", 16, init="a/c.png", denoise=0.8, mask="a/m.png")
        self.assert_closed(graph)
        self.assertEqual(graph["15"]["inputs"]["latent_image"], ["95", 0])
        self.assertEqual(graph["95"]["inputs"]["mask"], ["94", 0])

    def test_ltx_single_image_guides_first_frame_at_full_strength(self):
        graph, out = lc.ltx_graph("p", "a/x.png", None, 1024, 576, 121, 3, "a/job")
        self.assert_closed(graph)
        guides = [n for n in graph.values() if n["class_type"] == "LTXVAddGuide"]
        self.assertEqual([(g["inputs"]["frame_idx"], g["inputs"]["strength"]) for g in guides], [(0, 1.0)])
        self.assertEqual(graph[out]["class_type"], "SaveVideo")

    def test_ltx_first_last_guides_both_ends(self):
        graph, _ = lc.ltx_graph("p", "a/x.png", "a/y.png", 1024, 576, 97, 3, "a/job", 0.7)
        self.assert_closed(graph)
        guides = sorted((n["inputs"]["frame_idx"], n["inputs"]["strength"]) for n in graph.values() if n["class_type"] == "LTXVAddGuide")
        self.assertEqual(guides, [(-1, 0.7), (0, 0.7)])
        self.assertEqual(graph["48"]["inputs"]["positive"], ["33", 0])

    def test_ltx_audio_conditioning_is_held_fixed_and_allows_mouths(self):
        graph, _ = lc.ltx_graph("p", "a/x.png", None, 1024, 576, 121, 3, "a/job", audio="a/v.wav", audio_start=69.375)
        self.assert_closed(graph)
        self.assertEqual(graph["61"]["inputs"]["start_index"], 69.375)
        self.assertAlmostEqual(graph["61"]["inputs"]["duration"], 121 / 24, places=3)
        self.assertEqual(graph["63"]["inputs"]["value"], 0.0)
        self.assertEqual(graph["41"]["inputs"]["audio_latent"], ["64", 0])
        self.assertNotIn("singing, open mouth", graph["6"]["inputs"]["text"])


if __name__ == "__main__":
    unittest.main()
