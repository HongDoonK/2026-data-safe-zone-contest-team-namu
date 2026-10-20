"""4차 방문 입력 코드 인쇄본 만들기 — docs/topics/T2_visit4_plan.md의 셀을 그대로 옮긴다(코드는 손대지 않는다).

출력: docs/report/T2_4차_입력코드.html  (A4 인쇄용. 셀마다 줄 번호, 억제 줄 노란 바탕, 현장에서 바꿀 값 빨간 글자)
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "docs" / "topics" / "T2_visit4_plan.md"
DST = ROOT / "docs" / "report" / "T2_4차_입력코드.html"
KEEP = ("## 2.", "## 3.", "## 4.", "## 5.", "## 5-2.", "## 6.", "## 7.", "## 8.", "## 9.")
md = SRC.read_text(encoding="utf-8")


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", t)
    return t


def table(lines):
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines if not re.match(r"^\|[-| ]+\|$", l.strip())]
    out = "<table><tr>" + "".join(f"<th>{inline(c)}</th>" for c in rows[0]) + "</tr>"
    out += "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows[1:])
    return out + "</table>"


def prose(block):
    out, buf = [], []
    for l in block.strip().splitlines() + [""]:
        if l.startswith("|"):
            buf.append(l)
            continue
        if buf:
            out.append(table(buf))
            buf = []
        if l.strip() and l.strip() != "---":
            cls = ' class="why"' if l.startswith(">") else ""
            out.append(f"<p{cls}>{inline(l.lstrip('> ').lstrip('- '))}</p>")
    return "\n".join(out)


def code_html(code):
    rows = []
    for i, l in enumerate(code.rstrip("\n").split("\n"), 1):
        e = html.escape(l)
        e = re.sub(r"(여기에_[^&\"]+)", r'<span class="ph">\1</span>', e)
        cls = "sup" if ("np.nan" in l and "=" in l and "fillna" not in l) else ""
        rows.append(f'<tr class="{cls}"><td class="n">{i}</td><td class="c">{e or "&nbsp;"}</td></tr>')
    return '<table class="code">' + "".join(rows) + "</table>", i


# 섹션(## …)을 나누고, 그 안의 셀(### 셀 …)을 코드·설명으로 나눈다
secs = re.split(r"(?m)^(?=## )", md)
body, n_cells, toc = [], 0, []
for s in secs:
    head = s.splitlines()[0] if s.strip() else ""
    if not head.startswith(KEEP):
        continue
    title = head[3:]
    parts = re.split(r"(?m)^(?=### )", s)
    body.append(f'<h2>{inline(title)}</h2>')
    intro = "\n".join(parts[0].splitlines()[1:])
    if intro.strip():
        body.append(f'<div class="intro">{prose(intro)}</div>')
    for p in parts[1:]:
        h = p.splitlines()[0][4:]
        m = re.search(r"```python\n(.*?)```", p, re.S)
        if not m:
            body.append(f'<h3>{inline(h)}</h3>' + prose("\n".join(p.splitlines()[1:])))
            continue
        name = re.match(r"셀 (\S+)", h).group(1)
        tbl, n = code_html(m.group(1))
        h = re.sub(r"\(\d+줄", f"({n}줄", h)
        rest = p[m.end():]
        n_cells += 1
        toc.append(name)
        body.append(f'''<div class="cell"><div class="ch"><span class="box">☐</span> {inline(h)}</div>
{tbl}<div class="note">{prose(rest)}</div>
<div class="field">현장 값: ________________________________________________</div></div>''')

shrink = re.search(r"(?ms)^## 10\. 축소 경로\n(.*?)(?=^## )", md).group(1)
stop = re.search(r"\*\*중단 규칙\*\*[^\n]*", md).group(0)
css = """
@page { size: A4; margin: 12mm 11mm; }
body { font-family: 'Malgun Gothic', sans-serif; font-size: 10.5pt; color: #1a1a1a; margin: 0 auto; max-width: 190mm; }
h1 { font-size: 17pt; margin: 0 0 4px; color: #0d366b; }
h2 { font-size: 13pt; color: #fff; background: #1c5cab; padding: 5px 9px; margin: 18px 0 8px; break-after: avoid; }
h3 { font-size: 11pt; color: #1c5cab; margin: 12px 0 4px; }
.lead { color: #52514e; margin: 0 0 10px; }
.rules { border: 1.5px solid #1c5cab; padding: 8px 12px; margin: 8px 0 12px; background: #f4f8fd; }
.rules p { margin: 3px 0; }
.legend span { display: inline-block; padding: 1px 6px; margin-right: 8px; }
.cell { border: 1px solid #b9c7da; margin: 10px 0; break-inside: avoid; }
.ch { background: #eef4fc; padding: 5px 8px; font-weight: bold; color: #0d366b; }
.box { font-size: 13pt; margin-right: 4px; }
table.code { border-collapse: collapse; width: 100%; font-family: Consolas, 'D2Coding', monospace; font-size: 9.6pt; }
table.code td { padding: 1px 6px; vertical-align: top; white-space: pre-wrap; word-break: break-all; }
td.n { width: 22px; color: #8a8a8a; text-align: right; border-right: 1px solid #ddd; user-select: none; }
tr.sup td.c { background: #fff2b3; font-weight: bold; }
.ph { color: #b8312f; font-weight: bold; }
.note { padding: 4px 9px 2px; font-size: 9.6pt; }
.note p { margin: 3px 0; }
p.why { color: #52514e; }
.field { padding: 4px 9px 7px; color: #52514e; font-size: 9.6pt; }
.intro p { margin: 3px 0; color: #52514e; }
table { border-collapse: collapse; margin: 6px 0; font-size: 9.6pt; }
th, td { border: 1px solid #c8c8c8; padding: 3px 6px; text-align: left; }
th { background: #eef4fc; }
code { font-family: Consolas, monospace; font-size: 9.4pt; background: #f2f2f2; padding: 0 3px; }
@media screen { body { padding: 16px; } }
"""
doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>4차 방문 입력 코드</title><style>{css}</style></head><body>
<h1>T2 4차 방문 입력 코드 (2026-10-16)</h1>
<p class="lead">계획서 <code>docs/topics/T2_visit4_plan.md</code>의 셀 {n_cells}개를 순서대로 옮겼다. 가짜 자료로 전 셀을 처음부터 끝까지 실행해 오류 없음, X1 전부 "통과"(2026-10-15).</p>
<div class="rules">
<p class="legend"><span style="background:#fff2b3"><b>노란 줄</b></span>억제 줄 — 빠뜨리면 3차 같은 억제 누락이 된다. 치고 나서 인쇄본과 한 번 더 대조
&nbsp; <span class="ph">빨간 글자</span> 현장에서 F0·F1·K1 결과로 바꿀 값</p>
<p><b>순서</b>: {" → ".join(toc)}</p>
<p>{inline(stop)}</p>
<p><b>3차 노트북(2026_10_02.ipynb)이 남아 있으면</b> M1·M2는 그 셀을 실행한다(15분 절약). <b>Q7·Q10을 건너뛰면</b> X1은 그 파일 줄을 찍지 않는다(고칠 것 없음).</p>
<p><b>X1이 "통과"를 찍지 않은 파일은 반출 신청하지 않는다.</b> 최댓값·상위 분위수·개별 계정은 출력하지 않는다(노트북째 반출된다).</p>
</div>
<h3>시간이 모자랄 때 (축소 경로)</h3>
{prose(shrink)}
{"".join(body)}
</body></html>"""
DST.write_text(doc, encoding="utf-8")
print("ok", DST.name, "| 셀", n_cells, "|", " ".join(toc))
