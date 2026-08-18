"""Intentionally problematic source used only by the analyzer demo.

The Flask application never imports this module. Every issue in this file is
deliberate, deterministic, and covered by integration tests.
"""


DEMO_API_KEY = "demo-only-not-a-real-secret"


def buildDemoChecklist(raw_items: list[str]) -> list[str]:
    """Build a deliberately overlong checklist for rule demonstrations."""

    # TODO: Replace this intentionally verbose demo during a live walkthrough.
    checklist: list[str] = []
    normalized_items: list[str] = []

    for raw_item in raw_items:
        normalized_item = raw_item.strip()

        if not normalized_item:
            continue

        normalized_items.append(normalized_item)

    if not normalized_items:
        normalized_items.append("No review items supplied")

    heading = "SecureCode Analyzer review"
    checklist.append(heading)
    checklist.append("=" * len(heading))

    item_number = 1

    for normalized_item in normalized_items:
        checklist.append(
            f"{item_number}. {normalized_item}"
        )
        item_number += 1

    checklist.append("")
    checklist.append("Static analysis checks")
    checklist.append("- inspect source files")
    checklist.append("- review reported rules")
    checklist.append("- confirm expected locations")
    checklist.append("")
    checklist.append("Dependency checks")
    checklist.append("- parse pinned requirements")
    checklist.append("- query advisory metadata")
    checklist.append("- review fixed versions")

    try:
        int("not-a-number")
    except ValueError:
        pass

    checklist.append("")
    checklist.append("Demo safeguards")
    checklist.append("- no real credentials")
    checklist.append("- no production imports")
    checklist.append("- no vulnerable runtime package")

    pending_count = len(normalized_items)
    summary = (
        f"Prepared {pending_count} review "
        "item(s) for the demo."
    )

    checklist.append("")
    checklist.append(summary)

    footer = "End of controlled analyzer demo"
    checklist.append(footer)

    return checklist
