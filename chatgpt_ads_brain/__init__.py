"""ChatGPT Ads local knowledge and operating tools."""

from pathlib import Path
import tomllib

__version__ = tomllib.loads((Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
