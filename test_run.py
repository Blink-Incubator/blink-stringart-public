# test_run.py
from stringart_public import generate_string_art

results = generate_string_art("example.jpeg")

for i, variant in enumerate(results["versions"], 1):
    print(f"Variant {i}:")
    print("  Coordinates:", variant["coordinates"][:10])
    print("  Preview (base64, first 100 chars):", variant["preview_b64"][:100])
    print()