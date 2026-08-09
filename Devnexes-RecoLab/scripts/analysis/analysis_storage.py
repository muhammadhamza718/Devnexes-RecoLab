"""Analysis result storage manager for Day 5 Afternoon.

Handles persistence, formatting, and retrieval of analysis artifacts in
data/evaluation/advanced_analysis/ directory.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Add scripts directory to path for path_utils import
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from path_utils import get_validated_project_root

# Base path definitions
PROJECT_ROOT = get_validated_project_root()
ANALYSIS_DIR = PROJECT_ROOT / "data" / "evaluation" / "advanced_analysis"


class AnalysisStorage:
    """Storage infrastructure for Day 5 Afternoon advanced analysis."""

    CATEGORIES = {
        "error_analysis": ANALYSIS_DIR / "error_analysis",
        "edge_case_analysis": ANALYSIS_DIR / "edge_case_analysis",
        "bias_analysis": ANALYSIS_DIR / "bias_analysis",
        "limitations": ANALYSIS_DIR / "limitations",
        "visualizations": ANALYSIS_DIR / "visualizations",
    }

    def __init__(self, base_dir: Path | str | None = None) -> None:
        """Initialize storage infrastructure, creating directories if needed."""
        self.base_dir = Path(base_dir) if base_dir else ANALYSIS_DIR
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create all required subdirectories safely."""
        self.base_dir.mkdir(parents=True, exist_ok=True)
        for cat_dir in self.CATEGORIES.values():
            cat_dir.mkdir(parents=True, exist_ok=True)

    def get_category_dir(self, category: str) -> Path:
        """Get directory path for a specific analysis category."""
        if category not in self.CATEGORIES:
            valid_cats = list(self.CATEGORIES.keys())
            raise ValueError(f"Unknown category '{category}'. Must be one of {valid_cats}")
        path = self.base_dir / category
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_result(
        self,
        category: str,
        name: str,
        data: dict[str, Any] | list[Any],
        add_timestamp: bool = True,
    ) -> Path:
        """Save analysis result as structured JSON.

        Args:
            category: Subdirectory category name.
            name: Base filename (without extension).
            data: Dictionary or list payload to save.
            add_timestamp: Whether to append timestamp to filename.

        Returns:
            Path to saved JSON file.
        """
        cat_dir = self.get_category_dir(category)

        if add_timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{ts}.json"
        else:
            filename = f"{name}.json"

        file_path = cat_dir / filename

        # Add storage metadata wrapper if data is a dict
        if isinstance(data, dict):
            payload = {
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "category": category,
                    "name": name,
                },
                "data": data,
            }
        else:
            payload = data

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, default=str)

        print(f"Saved [{category}] result to: {file_path}")
        return file_path

    def save_markdown(
        self,
        category: str,
        name: str,
        content: str,
        add_timestamp: bool = False,
    ) -> Path:
        """Save text/markdown report."""
        cat_dir = self.get_category_dir(category)
        if add_timestamp:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{ts}.md"
        else:
            filename = f"{name}.md"

        file_path = cat_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Saved [{category}] report to: {file_path}")
        return file_path

    def load_result(self, category: str, name: str) -> dict[str, Any] | list[Any]:
        """Load specific result file by category and exact or pattern name."""
        cat_dir = self.get_category_dir(category)
        matches = sorted(cat_dir.glob(f"{name}*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not matches:
            raise FileNotFoundError(f"No result found matching '{name}' in '{category}'")

        latest_path = matches[0]
        with open(latest_path, "r", encoding="utf-8") as f:
            content = json.load(f)

        if isinstance(content, dict) and "data" in content and "metadata" in content:
            return content["data"]
        return content

    def list_results(self, category: str | None = None) -> list[Path]:
        """List all result paths in a category or across all categories."""
        if category:
            cat_dir = self.get_category_dir(category)
            return sorted(cat_dir.glob("*"))

        all_paths = []
        for cat_dir in self.CATEGORIES.values():
            all_paths.extend(sorted(cat_dir.glob("*")))
        return all_paths
