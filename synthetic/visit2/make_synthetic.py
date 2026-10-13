"""SYNTHETIC fixed patterns only. No attempt to reproduce real distributions."""
import argparse
import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def make(out, rows):
    out = Path(out).resolve()
    allowed = [ROOT / "synthetic/visit2", ROOT / "tests/visit2/fixtures"]
    if not any(out == base or base in out.parents for base in allowed):
        raise ValueError("SYNTHETIC output must remain in synthetic/visit2 or tests/visit2/fixtures")
    if rows < 48:
        raise ValueError("rows must be at least 48 for all fixed traps")
    cfg = json.loads((ROOT / "analysis/visit2/config/visit2.json").read_text(encoding="utf-8"))
    out.mkdir(parents=True, exist_ok=True)
    pay_keys = list(cfg["columns"]["en"]["pay"])
    shop_keys = list(cfg["columns"]["en"]["shop"])
    # A 48-row repeated pattern, not a sampled or fitted distribution.
    pattern = []
    methods = ["SYN_MEAL_A", "SYN_MEAL_B", "SYN_GENERAL", "SYN_OTHER", "SYN_EMPTY_ROLE", ""]
    for i in range(48):
        item = {"shop_id": "SYN_SHOP_%04d" % (i % 6),
                "cust_id": "SYN_CUST_%04d" % (i % 12),
                "pay_gbn": methods[(i // 6) % 6], "card_pay_gbn": ["완료", "취소", "기타"][i % 3],
                "dest_pay_gbn": "SYN_APP", "app_time": "20240%d%02d%02d" % (i % 3 + 1, i % 7 + 15, i % 24),
                "tot_amt": "1000", "app_amt": "1000"}
        pattern.append(item)
    pattern[0]["pay_gbn"] = " SYN_MEAL_A  "
    pattern[0]["shop_id"] = " SYN_SHOP_0000  "
    pattern[1]["app_time"] = "202401151"
    pattern[2]["app_time"] = "ABCDEFGHIJ"
    pattern[3]["shop_id"] = "SYN_SHOP_9999"
    pattern[4]["pay_gbn"] = "SYN_MEAL_A_X"
    if rows > 48:
        # Exhaustive fixed grid for exercising all time axes. This is a test
        # coverage pattern, not a model of the real payment distribution.
        dense = []
        for monday in (datetime(2024, 1, 1), datetime(2024, 7, 1), datetime(2024, 9, 2)):
            for day in range(7):
                for hour in range(24):
                    for shop in range(36):
                        for group in ("meal", "general"):
                            date = monday + timedelta(days=day, hours=hour)
                            dense.append({"shop_id": "SYN_SHOP_%04d" % shop,
                                          "cust_id": "SYN_CUST_%04d" % shop,
                                          "pay_gbn": "SYN_MEAL_A" if group == "meal" else "SYN_GENERAL",
                                          "card_pay_gbn": "완료", "dest_pay_gbn": "SYN_APP",
                                          "app_time": date.strftime("%Y%m%d%H"), "tot_amt": "1000", "app_amt": "1000"})
        pattern.extend(dense)
    shops = []
    for i in range(30 if rows > 48 else 6):
        shops.append({"shop_id": "SYN_SHOP_%04d" % i, "gungu": "SYNTHETIC_구%d" % (i // 15),
                      "dong": "SYNTHETIC_동%d동" % (i // 5) if rows > 48 else ["SYNTHETIC_비산1동", "SYNTHETIC_비산동"][i % 2],
                      "child_able": ["Y", "N", ""][i % 3], "good_able": "N", "store_status": "SYN_100",
                      "closed_at": "", "service_closed": "N"})
    shops.append(dict(shops[0]))
    for language in ("en", "ko"):
        for kind, keys, items in (("PAY", pay_keys, None), ("SHOP", shop_keys, shops)):
            mapping = cfg["columns"][language][kind.lower()]
            target = out / ("SYNTHETIC_%s_%s.csv" % (kind, language))
            with target.open("w", newline="", encoding="utf-8-sig") as handle:
                writer = csv.writer(handle)
                writer.writerow([mapping[k] for k in keys])
                if items is None:
                    for i in range(rows):
                        writer.writerow([pattern[i % len(pattern)][k] for k in keys])
                else:
                    writer.writerows([[item[k] for k in keys] for item in items])
        local_cfg = json.loads(json.dumps(cfg))
        local_cfg["run_label"] = "SYNTHETIC"
        local_cfg["columns"]["active"] = language
        local_cfg["paths"] = {"pay": str(out / ("SYNTHETIC_PAY_%s.csv" % language)),
                              "shop": str(out / ("SYNTHETIC_SHOP_%s.csv" % language)),
                              "out_root": str(out / "SYNTHETIC_out")}
        local_cfg["meal_pay_values"] = ["SYN_MEAL_A", "SYN_MEAL_B"]
        local_cfg["reference_exports"] = None
        local_cfg["chunksize"] = 3 if rows <= 48 else 100000
        local_cfg["id_patterns"] = [r"SYN_(?:SHOP|CUST)_[0-9]{4}"]
        (out / ("SYNTHETIC_config_%s.json" % language)).write_text(
            json.dumps(local_cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    print("SYNTHETIC generated: rows=%d, headers=en/ko, seed=20260918 (fixed pattern)" % rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=2000000)
    parser.add_argument("--out", default=str(ROOT / "synthetic/visit2"))
    args = parser.parse_args()
    try:
        make(args.out, args.rows)
    except (ValueError, OSError) as exc:
        print("FAIL SYNTHETIC: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
