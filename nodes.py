"""Small, deliberately conservative nodes for ACE-Step cover workflows.

The official ACE-Step ComfyUI workflow already implements image-to-image-style
audio variation: audio is encoded by the selected VAE and given to KSampler as
its latent input.  This node makes that connection explicit without copying or
patching model internals.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ACECoverLatent:
    """Encode reference audio with the loaded ACE VAE for native KSampler use."""

    CATEGORY = "audio/ACE-Step"
    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)
    FUNCTION = "encode"
    DESCRIPTION = (
        "Encodes reference AUDIO with the connected VAE. Connect the LATENT to "
        "KSampler.latent_image and choose the amount of preservation with the "
        "native KSampler denoise setting."
    )

    @classmethod
    def INPUT_TYPES(cls) -> dict[str, dict[str, dict[str, Any]]]:
        return {
            "required": {
                "audio": ("AUDIO",),
                "vae": ("VAE",),
            },
            "optional": {
                "max_seconds": (
                    "FLOAT",
                    {
                        "default": 0.0,
                        "min": 0.0,
                        "max": 600.0,
                        "step": 0.1,
                        "tooltip": "0 keeps the complete file; a positive value trims only the tail.",
                    },
                ),
            },
        }

    def encode(self, audio: Mapping[str, Any], vae: Any, max_seconds: float = 0.0):
        if not isinstance(audio, Mapping):
            raise TypeError("ACECoverLatent expected ComfyUI AUDIO metadata (a mapping).")
        if "waveform" not in audio or "sample_rate" not in audio:
            raise ValueError("AUDIO must contain 'waveform' and 'sample_rate'. Use ComfyUI LoadAudio.")
        encode = getattr(vae, "encode", None)
        if not callable(encode):
            raise TypeError("The connected VAE does not expose encode(waveform); it cannot be used for cover mode.")

        waveform = audio["waveform"]
        sample_rate = audio["sample_rate"]
        if not isinstance(sample_rate, (int, float)) or sample_rate <= 0:
            raise ValueError("AUDIO sample_rate must be a positive number.")

        # ComfyUI AUDIO is a torch waveform shaped [batch, channels, samples].
        # Ellipsis preserves all leading dimensions and avoids importing torch.
        if max_seconds > 0:
            frames = max(1, round(float(max_seconds) * sample_rate))
            try:
                waveform = waveform[..., :frames]
            except (IndexError, TypeError) as error:
                raise TypeError("AUDIO waveform does not support ComfyUI tensor-style slicing.") from error

        latent = encode(waveform)
        if not isinstance(latent, Mapping) or "samples" not in latent:
            raise TypeError(
                "VAE.encode did not return ComfyUI LATENT data (a mapping containing 'samples'). "
                "This extension intentionally does not adapt unknown VAE APIs."
            )
        return (latent,)


NODE_CLASS_MAPPINGS = {"ACECoverLatent": ACECoverLatent}
NODE_DISPLAY_NAME_MAPPINGS = {"ACECoverLatent": "ACE-Step Cover Latent (VAE)"}
