# stringart_public/engine.py
"""
Blink Technologies - minimal public interface for Studio Sarte.
"""
from base64 import b64encode
from pathlib import Path
import stringart_public._core.string_art as string_art


def generate_string_art(image_path: str) -> dict:
    """
    Simulate 4 versions of the string art output for integration.
    Returns:
        dict with key 'versions' and value: list of 4 dicts, each containing:
        - 'coordinates': list of nail indices
        - 'preview_b64': base64-encoded preview image
    """
    versions = []

    for i in range(4):
        sa = string_art.StringArt(image_path, seed_suffix=str(i))
        coords = sa.process()

        tmp = Path(f"preview_{i}.png")
        sa.plot(output_path=tmp, show=False)
        preview_b64 = b64encode(tmp.read_bytes()).decode()
        tmp.unlink(missing_ok=True)

        versions.append({
            "coordinates": coords["nail_indices"],
            "preview_b64": preview_b64
        })

    return {"versions": versions}
