"""팀 공유용 HTML 보고서 빌드 — 템플릿에 지도 3장(base64)과 1순위 22곳 표를 채운다.

입력: docs/report/team_report_1008.template.html, fig/v2_*.png, out/u2_denominator_check_INTERNAL.csv, out/neighbor_check_INTERNAL.csv
출력: docs/report/T2_팀보고_20261012.html (한 파일, 외부 이미지 없음)
"""
import base64
import io
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TPL = ROOT / "docs/report/team_report_1008.template.html"
DST = ROOT / "docs/report/T2_팀보고_20261012.html"


def img_uri(p, width=2000):
    im = Image.open(p).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# 지도 1과 같은 번호: 경계가 있는 1순위 동을 일반 배달 많은 순으로 번호, 경계 없는 동은 "–"
# 표 순서: 이웃 점검 판정(먼저 → 다음 → 나중 → 확인 불가) 안에서 지도 번호 순
chk = pd.read_csv(HERE / "out/u2_denominator_check_INTERNAL.csv").set_index("dong")
nbr = pd.read_csv(HERE / "out/neighbor_check_INTERNAL.csv").set_index("dong")
p1 = chk[chk.robust.str.startswith("견고")].sort_values("gen", ascending=False)
NOMAP = {"달성군|현풍읍중리"}
no, n = {}, 0
for k in p1.index:
    if k not in NOMAP:
        n += 1
        no[k] = n
GROUP = {"주변도 함께 적음": (1, "먼저", "c1", "함께 적음"), "중간": (2, "다음", "c2", "평균보다 조금 적음"),
         "옆 동네가 대신할 가능성 큼": (3, "나중", "c3", "많이 씀 (대신 주문 가능)")}
rows = []
for k in sorted(p1.index, key=lambda k: (GROUP.get(nbr.at[k, "verdict"], (4,))[0], no.get(k, 99))):
    gu, dong = k.split("|")
    g = GROUP.get(nbr.at[k, "verdict"])
    order = f'<span class="chip {g[2]}">{g[1]}</span>' if g else '<span class="chip c0">확인 불가</span>'
    nb = g[3] if g else "주소 표기 불완전"
    rows.append(f'<tr><td>{order}</td><td class="n">{no.get(k, "–")}</td><td>{gu}</td><td>{dong}</td><td>{nb}</td></tr>')
print("1순위", len(rows), "| 판정", nbr.verdict.value_counts().to_dict())

html = TPL.read_text(encoding="utf-8")
html = html.replace("{{ROWS}}", "".join(rows))
for i, f in enumerate(["v2_map1_vacation_use.png", "v2_map2_per_child.png", "v2_map3_clusters.png"], 1):
    html = html.replace(f"{{{{IMG{i}}}}}", img_uri(HERE / "fig" / f))
assert "{{" not in html
# 로컬 파일로 돌려볼 수 있게 문서 골격을 붙인다(메신저·메일로 받은 사람이 브라우저로 바로 연다)
head, rest = html.split("</style>", 1)
html = ('<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + head + "body { margin: 0; }\nimg { max-width: 100%; }\n</style>\n</head>\n<body>\n" + rest + "\n</body>\n</html>\n")
DST.write_text(html, encoding="utf-8")
print(DST, round(DST.stat().st_size / 1e6, 2), "MB")
