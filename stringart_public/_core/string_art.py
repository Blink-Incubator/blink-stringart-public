"""
Blink Technologies - public stub for Studio Sarte
-------------------------------------------------
Deterministic, minimal string-art generator:
    • Same public interface as the real engine
    • Preview is derived from image hash
"""

from pathlib import Path
from hashlib import sha256
from base64 import b64encode
from typing import Dict, List
import numpy as np
import matplotlib.pyplot as plt


class StringArt:

    def __init__(self, image_path: str, num_nails: int = 200, seed_suffix: str = "") -> None:
        self.image_path = image_path
        self.num_nails = num_nails
        self.seed_suffix = seed_suffix
        self._nail_sequence: List[int] | None = None

    # Deterministic pseudo-random sequence generation
    def process(self) -> Dict:
        file_bytes = Path(self.image_path).read_bytes() + self.seed_suffix.encode()
        seed = int(sha256(file_bytes).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)

        self._nail_sequence = rng.integers(1, self.num_nails + 1, 400).tolist()
        return {
            "nail_indices": self._nail_sequence,
            "count": len(self._nail_sequence),
        }

    # Draws sequence
    def plot(self, output_path: str | None = None, show: bool = False):
        if self._nail_sequence is None:
            raise RuntimeError("Call process() before plot().")

        # Pre-compute nail coordinates on unit circle
        theta = np.linspace(0, 2 * np.pi, self.num_nails, endpoint=False)
        nail_x = np.cos(theta)
        nail_y = np.sin(theta)

        fig, ax = plt.subplots(figsize=(5, 5))
        ax.set_aspect("equal")
        ax.axis("off")
        ax.plot(nail_x.tolist() + [nail_x[0]],
                nail_y.tolist() + [nail_y[0]],
                color="k", linewidth=0.5)

        for a, b in zip(self._nail_sequence[:-1], self._nail_sequence[1:]):
            ax.plot([nail_x[a - 1], nail_x[b - 1]],
                    [nail_y[a - 1], nail_y[b - 1]],
                    color=(0, 0, 0, 0.06))

        if output_path:
            fig.savefig(output_path, dpi=150, bbox_inches="tight")

        if show:
            plt.show()

        return fig
