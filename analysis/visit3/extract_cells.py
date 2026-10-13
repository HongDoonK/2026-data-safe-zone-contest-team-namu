"""Extract literal code fences; compare Unicode including line endings."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs/topics/T2_visit3_plan.md"
HERE = Path(__file__).resolve().parent
ORDER = ["S1", "P1", "P1b", "P2", "P3", "M1", "M2", "M3", "M4", "M5", "M6", "A1", "A2", "A3", "A4"]
LINES = [9, 13, 1, 6, 12, 8, 13, 10, 9, 13, 12, 15, 7, 9, 4]


def extract():
    text = PLAN.read_bytes().decode("utf-8")
    section = text[text.index("## 2. 공통 설정"):text.index("## 6. 반출 패키지")]
    blocks = re.findall(r"```python\r?\n(.*?)```", section, flags=re.S)
    if len(blocks) != len(ORDER):
        raise ValueError("Expected exactly 15 Python fences, got %d" % len(blocks))
    return dict(zip(ORDER, blocks))


def check():
    blocks = extract()
    return [{"cell": c, "lines": len(blocks[c].splitlines()), "expected_lines": n,
             "synced": (HERE / "cells" / (c + ".py")).is_file() and
             (HERE / "cells" / (c + ".py")).read_bytes() == blocks[c].encode("utf-8"),
             "sha256": hashlib.sha256(blocks[c].encode("utf-8")).hexdigest()}
            for c, n in zip(ORDER, LINES)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Initial extraction only; refuses to overwrite")
    args = parser.parse_args()
    if args.write:
        (HERE / "cells").mkdir(parents=True, exist_ok=True)
        for cell, source in extract().items():
            path = HERE / "cells" / (cell + ".py")
            if path.exists() and path.read_bytes() != source.encode("utf-8"):
                raise ValueError("Existing cell differs: " + cell)
            path.write_bytes(source.encode("utf-8"))
    results = check()
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if not all(r["synced"] and r["lines"] == r["expected_lines"] for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
