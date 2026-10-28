import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
from nodes import ACECoverLatent


class FakeVAE:
    def __init__(self, result=None):
        self.waveform = None
        self.result = {"samples": "latent"} if result is None else result

    def encode(self, waveform):
        self.waveform = waveform
        return self.result


class ACECoverLatentTests(unittest.TestCase):
    def test_passes_waveform_to_vae(self):
        vae = FakeVAE()
        result = ACECoverLatent().encode({"waveform": "audio", "sample_rate": 44100}, vae)
        self.assertEqual(result, ({"samples": "latent"},))
        self.assertEqual(vae.waveform, "audio")

    def test_rejects_unknown_vae_result(self):
        with self.assertRaisesRegex(TypeError, "LATENT"):
            ACECoverLatent().encode({"waveform": "audio", "sample_rate": 44100}, FakeVAE({}), 0)

    def test_requires_comfy_audio_metadata(self):
        with self.assertRaisesRegex(ValueError, "sample_rate"):
            ACECoverLatent().encode({"waveform": "audio"}, FakeVAE())


if __name__ == "__main__":
    unittest.main()
