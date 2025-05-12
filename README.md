# 🧵 Studio Sarte – Public String Art Stub

This repository contains the **public-facing stub** of the proprietary String Art generation engine developed by Blink Technologies for Studio Sarte.  
It provides the **exact same interface** as the full version, but does **not expose any internal logic or algorithmic details**.

---

## 🔧 Installation

Create a virtual environment (recommended):

```bash
python3 -m venv venv
source venv/bin/activate
````

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

Import the public API function:

```python
from stringart_public import generate_string_art
```

Run it on a local image:

```python
result = generate_string_art("example.jpg")
for version in result["versions"]:
    print(version["coordinates"][:10])     # list of nail indices
    print(version["preview_b64"][:100])    # base64 string (PNG preview)
```

Each call returns:

```python
{
  "versions": [
    { "coordinates": [...], "preview_b64": "..." },
    { "coordinates": [...], "preview_b64": "..." },
    { "coordinates": [...], "preview_b64": "..." },
    { "coordinates": [...], "preview_b64": "..." }
  ]
}
```

---

## 🛠 Notes

* The engine is **deterministic**: same image = same result.
* This stub version generates results based on the **image hash**, preserving the interface while hiding proprietary logic.
* Plotting uses matplotlib to render a circular string art preview.


