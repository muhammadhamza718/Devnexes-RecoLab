"""Headless smoke test for the RecoLab Streamlit UI using streamlit.testing.

Covers Task-012 (core functionality), Task-013 (session persistence) and
Task-014 (error handling). Run from the project root:

    python scripts/smoke_ui_test.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamlit.testing.v1 import AppTest  # noqa: E402

APP = Path(__file__).resolve().parents[1] / "streamlit_app.py"

RESULTS = []


def check(name: str, condition: bool) -> None:
    RESULTS.append((name, condition))
    print(f"{'PASS' if condition else 'FAIL'}  {name}")


# ---------------------------------------------------------------------------
# Task-012: core functionality
# ---------------------------------------------------------------------------
at = AppTest.from_file(str(APP), default_timeout=300)
at.run()

check("app starts without exceptions", not at.exception)
check("title rendered", any("RecoLab" in str(el.value) for el in at.title))
# The app auto-selects the first user on first render.
check("first user auto-selected", at.session_state["selected_user_id"] == 1)
check("initial state: no recommendations", at.session_state["recommendations"] == [])

# User dropdown defaults to the first user (id 1).
check("user dropdown present", len(at.selectbox) >= 2)
check("profile shown for user 1", at.session_state["user_profile"].get("rating_count") == 185)

# Generate recommendations with the default model (Hybrid) - heavy fit.
at.button[0].click()
at.run()
check("generate does not raise", not at.exception)
recs = at.session_state["recommendations"]
check("recommendations stored", len(recs) > 0)
check("rows enriched with titles", all(r.get("title") for r in recs))
check("rows enriched with explanations", all(r.get("explanation") for r in recs))

# ---------------------------------------------------------------------------
# Task-013: session persistence across reruns
# ---------------------------------------------------------------------------
first_rows = list(at.session_state["recommendations"])
# Touching an unrelated widget must not wipe recommendations.
at.text_input[0].set_value("1")
at.run()
check("recommendations survive a rerun", at.session_state["recommendations"] == first_rows)

# Switch model to Content (no full CF refit) and regenerate.
at.radio[0].set_value("Content")
at.run()
check("model switch clears stale recommendations", at.session_state["recommendations"] == [])
at.button[0].click()
at.run()
content_recs = at.session_state["recommendations"]
check("content model generates", len(content_recs) > 0)
check("content rows have explanations", all(r.get("explanation") for r in content_recs))

# ---------------------------------------------------------------------------
# Task-014: error handling
# ---------------------------------------------------------------------------
at.text_input[0].set_value("99999999")
at.run()
check("unknown user does not crash", not at.exception)
check("unknown user shows sidebar warning", len(at.warning) > 0)

print()
failed = [name for name, ok in RESULTS if not ok]
print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
if failed:
    print("FAILED:", failed)
    sys.exit(1)
