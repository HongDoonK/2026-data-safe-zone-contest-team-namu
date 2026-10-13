"""SYNTHETIC: deterministic edge cases and repetition, NOT realistic distributions."""
import argparse
import csv
import io
import json
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAY_COLS = "SHOP_ID CUST_ID PAY_GBN TOT_AMT ETC_AMT DISC_AMT MILEAGE_AMT DEST_PAY_GBN CARD_PAY_GBN CARD_APP_TIME CARD_APP_AMT PACK_DISC_AMT SHOP_DISC_AMT GOOD_DISC_AMT CHILD_DISC_AMT".split()
SHOP_COLS = "SHOP_ID GUNGU_NM DONG_NM CHILD_ABLE_YN GOOD_ABLE_YN STORE_STATUS CLOSED_AT SERVICE_CLOSED".split()
SEED = 1002


def months():
    return ["%04d%02d" % (y, m) for y in range(2022, 2026) for m in range(1, 13)
            if "%04d%02d" % (y, m) <= "202506"]


def build():
    root = HERE.parents[1]
    with (root / "9_18_데이터분석 결과물/EXPORT_m1_values.csv").open(encoding="utf-8-sig", newline="") as stream:
        codes = [r["PAY_GBN"] for r in csv.DictReader(stream)]
    assert len(codes) == 19
    shops, rows = [], []
    groups = [("중구", "SYNTHETIC_정상동", 3), ("남구", "SYNTHETIC_정상동", 3),
              ("중구", "SYNTHETIC_k1동", 3), ("중구", "SYNTHETIC_급식0동", 6),
              ("중구", "SYNTHETIC_희소동", 1), ("중구", "SYNTHETIC_2가맹동", 2),
              ("", "SYNTHETIC_군구결측", 3), ("북구", "", 3), ("강서구", "SYNTHETIC_오류구", 2)]
    ids = []
    for gidx, (gu, dong, count) in enumerate(groups):
        group = []
        for j in range(count):
            sid = "SYNTHETIC_S%02d_%d" % (gidx, j)
            status = ["01", "02", "03"][j % 3]
            shops.append(dict(zip(SHOP_COLS, [sid, gu, dong, "Y", "N", status,
                                               "202501" if status == "03" else "", "N" if j % 2 == 0 else "Y"])))
            group.append(sid)
        ids.append(group)

    def add(code, ym, group=0, count=1, disc="0", total="8000", status="완료"):
        for j in range(count):
            r = dict.fromkeys(PAY_COLS, "0")
            r.update(SHOP_ID=ids[group][j % len(ids[group])], CUST_ID="SYNTHETIC_C%d" % (j % 7),
                     PAY_GBN=code, TOT_AMT=total, CARD_PAY_GBN=status,
                     CARD_APP_TIME=ym + "0112" if ym else "", CHILD_DISC_AMT=disc,
                     CARD_APP_AMT=str(int(total) - int(disc)) if total.lstrip("-").isdigit() and disc.isdigit() else "",
                     DEST_PAY_GBN="앱결제")
            rows.append(r)

    for ym in months():
        add("카드", ym, count=4)
        if ym <= "202307":
            add("행복페이", ym, count=3)
        if ym >= "202306":
            add("대구로페이", ym, count=2)
            add("아동급식카드", ym, count=6, disc="2500")
    for group in [1, 6, 7]:
        for ym in ["202401", "202407", "202409"]:
            add("아동급식카드", ym, group, 6, "1500")
    for ym, count in [("202401", 2), ("202407", 6), ("202409", 6)]:
        add("아동급식카드", ym, 2, count, "1000")
    add("아동급식카드", "202409", 4, 2, "500")
    for group in range(len(groups)):
        add("카드", "202409", group, len(ids[group]) * 2)
    for code in codes:
        if code not in ["카드", "행복페이", "대구로페이", "아동급식카드"]:
            no_time = code in ["현금", "모바일상품권", "결제수단없음(마일리지/쿠폰등)"]
            add(code, "" if no_time else "202409", count=2)
    add("아동급식카드", "", count=2, disc="500", status="취소")
    add("카드", "", count=1)
    add("행복페이", "", count=1)
    add("카드", "202409", count=1, total="bad_amount", status="")
    # Thirty 500-won bins plus malformed/empty/negative values, enumerated, not modelled.
    for bin_id in range(30):
        add("아동급식카드", "202409", count=6, disc="500", total=str(bin_id * 500))
    add("카드", "202409", count=1, total="500000")
    add("아동급식카드", "202409", count=1, total="-250")
    add("아동급식카드", "202409", count=1, total="")
    add("아동급식카드", "202409", count=1, total="not_numeric")
    rows[-1]["CHILD_DISC_AMT"] = "not_numeric"
    for idx in [0, 12, 51]:
        for column in ["PAY_GBN", "SHOP_ID", "CUST_ID", "CARD_PAY_GBN", "TOT_AMT"]:
            rows[idx][column] = " " + rows[idx][column] + " "
    shops[0]["CHILD_ABLE_YN"] = " Y "
    random.Random(SEED).shuffle(rows)
    assert 300 <= len(rows) < 1000
    return shops, rows, codes


def write_rows(path, columns, rows, count=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    header = buf.getvalue()
    buf.seek(0)
    buf.truncate(0)
    writer.writerows(rows)
    body = buf.getvalue()
    if count is None:
        count = len(rows)
    whole, remainder = divmod(count, len(rows))
    with path.open("w", encoding="utf-8", newline="") as target:
        target.write(header)
        for _ in range(whole):
            target.write(body)
        target.write("".join(body.splitlines(True)[:remainder]))
    return path


def make(size="small", count=None):
    shops, rows, codes = build()
    base = HERE / "data_SYNTHETIC"
    shop = write_rows(base / "SYNTHETIC_shop.csv", SHOP_COLS, shops)
    pay = write_rows(base / ("SYNTHETIC_pay_%s.csv" % size), PAY_COLS, rows, count)
    manifest = {"label": "SYNTHETIC", "seed": SEED, "rows": count or len(rows), "template_rows": len(rows),
                "pay": str(pay), "shop": str(shop), "codes": codes,
                "generation": "fixed edge-case enumeration repeated; no real distribution estimate"}
    (base / ("SYNTHETIC_%s_manifest.json" % size)).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return pay, shop, manifest


def p0_fixtures():
    shops, rows, _ = build()
    base = HERE / "data_SYNTHETIC"
    paths = {}
    for name in ["A", "B", "C1", "C2"]:
        data = [dict(r) for r in rows]
        if name == "B":
            # Explicit rare marker counts 1 vs 2; every pre month, both years' vacation share rises.
            for ym in months()[:17]:
                count = 2 if ym[4:6] in ["01", "02", "08"] else 1
                happy = [r for r in data if r["PAY_GBN"].strip() == "행복페이" and r["CARD_APP_TIME"].startswith(ym)]
                for r in happy[:count]:
                    r["CHILD_DISC_AMT"] = "500"
                # Keep marker proportion exactly 1% in the dated pre-period.
                # Repeating a positive row here would make B overlap C1's "common" case.
                target = 200 if count == 2 else 100
                data.extend([dict(happy[-1]) for _ in range(target - len(happy))])
        elif name == "C1":
            for r in data:
                if r["PAY_GBN"].strip() == "카드":
                    r["CHILD_DISC_AMT"] = "500"
        elif name == "C2":
            for r in data:
                if r["PAY_GBN"].strip() == "아동급식카드" and "202306" <= r["CARD_APP_TIME"][:6] <= "202312":
                    r["CHILD_DISC_AMT"] = "0"
        paths[name] = write_rows(base / ("SYNTHETIC_P0_%s.csv" % name), PAY_COLS, data)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", choices=["small", "large", "timing"], default="small")
    parser.add_argument("--rows", type=int)
    args = parser.parse_args()
    default = {"small": None, "large": 1200000, "timing": 8000000}[args.size]
    print(json.dumps(make(args.size, args.rows or default)[2], ensure_ascii=False, indent=2))
