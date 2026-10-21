"""T2 기획서 겸 발표자료(30쪽) — 팀 나무. PowerPoint로 그린 뒤 PDF·PPTX로 내보내 캔바로 가져간다.

실행: anaconda python build_deck.py [--only 1,13,16] [--png DIR] [--pdf]
수치는 반출 결과·결과 문서·대시보드 자료(analysis/outside/out_dashboard)에 있는 값만 쓴다(CLAUDE.md).
문체: 명사형 종결·개조식, 추상 형용사 금지, 장식 이모지 금지(팀 지정 2026-10-20).
레이아웃(2026-10-20 개정, 보고서형): 카드·바탕 상자·칩·원형 번호·화살표 도형 없이 여백과 1px 구분선(HAIR)으로 나누고,
강조는 글자 굵기·크기·레드로만 한다. 비교·절차는 가로선만 쓰는 표로 쓴다.
용어: 팀 대시보드 ‘한계와 용어 → 용어 풀이’의 쉬운 이름(처방 → 해결방안·개선 대상, 1순위 → 우선 점검,
결합 단위 → 동네 묶음, LQ → 급식 비중 지수, 레짐 → 시기, 증빙 → 부록, R1~R7 → 이유 이름).
멈춤 → 공백(숫자로 보이는 빈 곳, 판정을 거친 곳만 사각지대), 착시 → 사각지대 아님·잘못 뽑히는 동,
‘A × B’ → ‘A·B별’·‘A마다 B’, 계정 → 이용자(급식카드로 결제한 대구로 앱 회원, 세는 말 ‘명’)(팀 지정 2026-10-20).
머리글(2026-10-21, 팀 지정 ‘인간 디자이너 위계’): 대제목 = 장 번호 + 핵심 낱말, 소제목 = 핵심 메시지 한 줄.
긴 분석 문장·수치를 제목에 넣지 않고, 수치와 산출 근거는 본문 캡션(차트 머리 아래, 표 아래, 수치 설명)으로 내린다.
줄표(—·–) 금지(팀 지정 2026-10-21): 두 마디는 콜론(뒤가 앞을 풀어 줄 때)·쉼표 이음(뒤가 앞의 결과일 때)·괄호(참고)로 잇고,
빈 칸 표시는 ‘없음’, 두 이름 잇기는 가운뎃점(행정동·법정동). 빌드 끝에 쪽 글자를 다시 읽어 남은 줄표를 WARN으로 알린다.
"""
import argparse
import json
from pathlib import Path

from deck_lib import (AMBER, BG, HAIR, HEAD_FONT, INK, INK2, MONO_FONT, MUTED, NAVY, TEAL, TITLE_FONT, UNDEC, Deck, est_w,
                      mix)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSET = HERE / "assets"
DASH = ROOT / "analysis" / "outside" / "out_dashboard"
GITHUB = "github.com/HongDoonK/2026-data-safe-zone-contest-team-namu"   # 팀 저장소(2026-10-21 공개). 표지·27·30쪽
GITHUB_LINK = (GITHUB, "https://" + GITHUB)                              # 주소 글자에 거는 하이퍼링크

# 대시보드 자료 속 옛 용어 → 쉬운 이름(용어 풀이). 긴 표현부터 바꾼다
PLAIN = [("처방 필요 4곳", "개선 대상 4곳"), ("처방 + 확인 필요", "개선 대상 + 확인 필요"),
         ("처방이 필요한 곳", "개선이 필요한 곳"), ("처방 4", "개선 대상 4"), ("1순위", "우선 점검"),
         ("(R3)", ""), ("(R7)", ""), ("행정동 × 연령대", "행정동·연령대별"), ("요일×시간", "요일·시간대별"),
         ("동×시기", "동·시기별"), ("방학 이용 계정은", "방학 이용자는"), ("계정 명의자 연령대", "이용자 연령대"),
         ("배달 1건, 계정", "배달 1건, 이용자"), ("참고: 판정 없이 17곳 전체", "참고: 판정 없이 17곳 전체(겉보기)"),
         ("행정동–법정동", "행정동·법정동")]


def plain(s):
    for a, b in PLAIN:
        s = s.replace(a, b)
    return s


def load(name):
    d = json.load(open(DASH / f"{name}.json", encoding="utf-8"))
    rows = d if isinstance(d, list) else d.get("rows", d)
    return [{k: plain(v) if isinstance(v, str) else v for k, v in r.items()} for r in rows]


LABELS = json.load(open(ASSET / "maps_labels.json", encoding="utf-8"))

CHAPTERS = [("00", "요약", "한 장 요약"), ("01", "문제 정의", "문제 정의"), ("02", "데이터와 방법", "데이터와 방법"),
            ("03", "결과 · 시간", "결과 1 · 시간"), ("04", "결과 · 공간", "결과 2 · 공간"),
            ("05", "결과 · 제도", "결과 3 · 제도"), ("06", "해결방안과 효과", "해결방안과 효과"), ("07", "한계", "한계"),
            ("08", "부록", "부록")]

X0, X1 = 348, 1856
W = X1 - X0
TOP, BOT = 236, 1012
NAVY_L = mix(NAVY, 0.22)       # 차트 보조 막대
TEAL_M = mix(TEAL, 0.7)        # 차트 ‘전환’ 막대
AXIS = mix(NAVY, 0.4, BG)      # 차트 기준선
KIND_NAME = {"confirmed": "개선 대상", "undecided": "확인 필요", "exclude_nb": "제외 · 옆 동네",
             "exclude_need": "제외 · 필요 적음"}
KIND_INK = {"confirmed": AMBER, "undecided": UNDEC, "exclude_nb": INK2, "exclude_need": INK2}
WARN = []


# ---- 공통 틀 ------------------------------------------------------------------------------------
def frame(d, sl, ch, cat, head, page, source=None):
    """머리글 두 단계. 대제목 = 장 번호 + 핵심 낱말(수성돋움체 60px, 일반 16:9 슬라이드의 30pt에 해당),
    소제목 = 쪽 전체를 꿰는 메시지 한 줄(Pretendard Medium 34px, 17pt에 해당). 수치·근거는 본문에 둔다."""
    chap = CHAPTERS[ch][0]
    if est_w(f"{chap}  {cat}", 60) > W:
        WARN.append(f"{page}쪽 대제목 길이 {est_w(f'{chap}  {cat}', 60):.0f}px > {W}")
    if est_w(head, 34) > W:
        WARN.append(f"{page}쪽 소제목 길이 {est_w(head, 34):.0f}px > {W}")
    if "—" in head:
        WARN.append(f"{page}쪽 소제목에 줄표(—)")
    vline(d, sl, 300, 48, 1032)                    # 목차와 본문을 가르는 세로선 하나
    for i, (no, short, _) in enumerate(CHAPTERS):
        y = 92 + 100 * i
        if i == ch:                                 # 지금 장: 작은 사각 점 + 굵은 레드
            d.shape(sl, "rect", 40, y + 10, 10, 10, fill=AMBER, line=None)
            d.text(sl, 64, y, 228, 30, f"{no}  {short}", size=19, color=AMBER, bold=True)
        else:
            d.text(sl, 64, y, 228, 30, f"{no}  {short}", size=19, color=MUTED)
    d.text(sl, 64, 1000, 228, 28, "팀 나무", size=16, color=MUTED, bold=True)
    d.title_text(sl, X0, 40, W, 76, f"{{a:{chap}}}  {cat}", size=60)
    d.text(sl, X0, 124, W, 48, head, size=34, font=HEAD_FONT, color=INK)
    hline(d, sl, X0, X1, 194)
    d.text(sl, X1 - 120, 1026, 120, 26, f"{page:02d} / 30", size=16, color=MUTED, align="r")
    if source:
        d.text(sl, X0, 1026, W - 160, 26, source, size=15, color=MUTED)


def hline(d, sl, x1, x2, y):
    d.line(sl, x1, y, x2, y, color=HAIR, w=1)


def vline(d, sl, x, y1, y2):
    d.line(sl, x, y1, x, y2, color=HAIR, w=1)


def kicker(d, sl, x, y, w, text, color=AMBER):
    """소제목 위 작은 표지 — 칩(바탕 도형) 대신 색 글자."""
    d.text(sl, x, y, w, 26, text, size=16, color=color, bold=True)


def head(d, sl, x, y, w, text, size=22, right=None):
    """소제목. right = 같은 줄 오른쪽 끝의 작은 설명."""
    d.text(sl, x, y, w, size * 1.5, text, size=size, color=INK, bold=True)
    if right:
        d.text(sl, x + w - 300, y + (size - 16) / 2, 300, 26, right, size=16, color=MUTED, align="r")


def stat(d, sl, x, y, w, big, label, sub=None, color=INK, size=60, sub_h=90):
    """숫자 묶음: 큰 숫자 + 굵은 설명 + 보충. 색 막대 없이 크기·색으로만 강조."""
    d.title_text(sl, x, y, w, size * 1.2, big, size=size, color=color)
    lines = max(1, -(-int(est_w(label, 20) * 1.05) // int(w)))
    d.text(sl, x, y + size * 1.2 + 4, w, 26 * lines + 8, label, size=20, color=INK, bold=True, lsp=1.25)
    if sub:
        d.text(sl, x, y + size * 1.2 + 12 + 26 * lines, w, sub_h, sub, size=17, color=MUTED, lsp=1.32)


def stats_column(d, sl, x, y, w, items, step, size=50, sub_h=60):
    """세로로 쌓은 숫자 묶음, 사이는 가로선."""
    for i, (big, lab, sub, col) in enumerate(items):
        if i:
            hline(d, sl, x, x + w, y - 18)
        stat(d, sl, x, y, w, big, lab, sub, color=col, size=size, sub_h=sub_h)
        y += step


def bullets(d, sl, x, y, w, h, items, size=19, after=8, color=INK2, lsp=1.3):
    return d.text(sl, x, y, w, h, "\n".join(items), size=size, color=color, bullet=True, after=after, lsp=lsp)


def legend(d, sl, x_right, y, items):
    """차트 범례(오른쪽 끝 정렬): 작은 색 사각 + 이름. items는 오른쪽부터."""
    lx = x_right
    for col, lab in items:
        tw = est_w(lab, 16)
        lx -= tw + 34
        d.shape(sl, "rect", lx, y + 6, 14, 14, fill=col, line=None)
        d.text(sl, lx + 22, y, tw + 10, 26, lab, size=16, color=INK2)
        lx -= 18


def map_labels(d, sl, mx, my, mw, numbers=True, gu_size=17):
    mh = mw * LABELS["aspect"]
    shift = {"서구": (-34, 26), "중구": None, "남구": (0, 6)}
    for g in LABELS["gu"]:
        if g["name"] in shift and shift[g["name"]] is None:
            continue
        dx, dy = shift.get(g["name"], (0, 0))
        px, py = g["pos"]
        d.text(sl, mx + px * mw - 50 + dx, my + py * mh - 12 + dy, 100, 24, g["name"], size=gu_size, color=MUTED,
               bold=True, align="c")
    if numbers:                                     # 지도 번호(16쪽 판정표 번호) — 위치 표시라 남긴다
        for t in LABELS["targets"]:
            px, py = t["pos"]
            cx, cy = mx + px * mw, my + py * mh
            s = d.shape(sl, "oval", cx - 12, cy - 12, 24, 24, fill=NAVY, line=None)
            d.box_text(s, str(t["no"]), size=13, color="#FFFFFF", bold=True)
    return mh


def code_block(d, sl, x, y, w, title, code, size=17, note=None):
    """코드: 어두운 상자 없이 왼쪽 세로선 하나 + 고정폭 글자. 세로선은 코드 줄 수만큼. 반환: 블록 아래 끝 y."""
    d.text(sl, x, y, w, 30, title, size=19, color=INK, bold=True)
    body_h = (code.count("\n") + 1) * size * 1.32 * 1.25 + 8
    vline(d, sl, x, y + 46, y + 46 + body_h)
    d.text(sl, x + 24, y + 50, w - 24, body_h, code, size=size, color=INK, font=MONO_FONT, lsp=1.32, raw=True)
    bottom = y + 46 + body_h
    if note:
        d.text(sl, x + 24, bottom + 14, w - 24, 50, note, size=16, color=MUTED, lsp=1.3)
        bottom += 64
    return bottom


# ---- 1. 표지 ------------------------------------------------------------------------------------
def s01(d, sl):
    d.text(sl, 160, 236, 1060, 30, "2026 데이터안심구역 경진대회 · 아이디어 기획서 겸 발표자료", size=20, color=MUTED,
           bold=True)
    d.title_text(sl, 160, 318, 1100, 260, "아동급식카드는\n어디서 멈추는가", size=104, lsp=1.08)
    d.text(sl, 160, 626, 1000, 100,
           "공공배달앱 ‘대구로’ 급식카드 결제 341,216건으로 본\n시간·공간·제도의 공백과 방학 점검표",
           size=30, color=INK2, lsp=1.35)
    hline(d, sl, 160, 1060, 836)
    d.text(sl, 160, 860, 300, 44, "팀 나무", size=30, color=INK, bold=True)
    d.text(sl, 330, 864, 700, 40, "김동훈 · 나선엽 · 이승혁 · 정다현", size=26, color=INK2)
    d.text(sl, 160, 918, 900, 32, "분석 기간 2023-06~2025-06 · 데이터안심구역 방문 4회  |  2026. 10.", size=19,
           color=MUTED)
    d.text(sl, 160, 952, 1060, 64, f"분석 코드·문서·작업 기록 전체 GitHub 공개\v{GITHUB}", size=19, color=MUTED, lsp=1.35,
           link=GITHUB_LINK)
    rows = load("monthly")
    gx, gy, gw, gh = 1290, 300, 470, 470
    d.text(sl, gx, gy - 64, gw, 30, "월별 급식카드 결제 건수", size=20, color=INK, bold=True)
    mx = max(r["meal"] for r in rows)
    bw = gw / len(rows)
    for i, r in enumerate(rows):
        h = gh * r["meal"] / mx
        col = AMBER if r["regime"] == "방학" else (TEAL_M if r["regime"] == "전환" else NAVY_L)
        d.shape(sl, "rect", gx + i * bw + 2, gy + gh - h, bw - 4, h, fill=col, line=None)
    d.line(sl, gx, gy + gh, gx + gw, gy + gh, color=AXIS, w=1)
    d.text(sl, gx, gy + gh + 10, 150, 24, "2023-06", size=15, color=MUTED)
    d.text(sl, gx + gw - 150, gy + gh + 10, 150, 24, "2025-06", size=15, color=MUTED, align="r")
    lx = gx
    for col, lab in ((AMBER, "방학 1·2·8월"), (TEAL_M, "전환 7·12월"), (NAVY_L, "학기")):
        d.shape(sl, "rect", lx, gy + gh + 53, 14, 14, fill=col, line=None)
        d.text(sl, lx + 22, gy + gh + 47, 160, 26, lab, size=16, color=INK2)
        lx += 160
    d.text(sl, gx, gy + gh + 86, gw, 26, "방학 6개월 = 전체 결제의 55.3%", size=17, color=INK, bold=True)
    d.notes(sl, "표지. 팀 나무: 김동훈·나선엽·이승혁·정다현.\n"
                "오른쪽 그래프는 실제 월별 급식카드 결제 건수(2차 반출). 레드 = 방학 달. 첫 발견: 결제가 방학에 몰림.\n"
                "분석 코드와 문서, 작업 기록은 모두 GitHub에 공개.")


# ---- 2. 한 장 요약 --------------------------------------------------------------------------------
def s02(d, sl):
    frame(d, sl, 0, "한 장 요약", "멈추는 곳은 가게 없는 동이 아니라 판정으로 걸러낸 4개 동", 2,
          "숫자 출처: 2~4차 반출 결과 · 시나리오 숫자는 가정 아래 계산 · 이용자 수는 아동 수와 다름")
    lw = 880
    kicker(d, sl, X0, TOP, lw, "이야기 한 줄")
    d.text(sl, X0, TOP + 34, lw, 76,
           "가게를 더 모으는 사업보다, 방학마다 같은 로그로 덜 쓰는 동을 다시 판정해 필요한 몇 곳에 해결방안 집중",
           size=25, color=INK, bold=True, lsp=1.3)
    hline(d, sl, X0, X0 + lw, TOP + 132)
    cols = [(280, "99.9%", "급식 주문 가게가 이미 닿는 아이 비율", "가게 모집·활성화 효과\n방학 월 이용자 +0명\n(가장 후한 가정 +35명)", AMBER),
            (280, "65%", "겉보기 부족분 중 사각지대 아닌 10곳 몫", "우선 점검 17곳 부족분\n월 1,337건 중 870건", INK),
            (260, "4곳", "개선 대상 동 · 모두 배달형", "회복 시 그 동네 이용자\n약 10명 → 16~22명 (가정)", INK)]
    cx, y = X0, TOP + 158
    for i, (w, big, lab, sub, col) in enumerate(cols):
        if i:
            vline(d, sl, cx - 15, y, y + 220)
        stat(d, sl, cx, y, w - 10, big, lab, sub, color=col, size=60, sub_h=80)
        cx += w + 30
    hline(d, sl, X0, X0 + lw, TOP + 404)
    rows = [["시간", "방학(1·2·8월) 결제 55.3% · 방학 이용자 수 학기의 4.9배 · 23시 이후 급식 결제 사실상 0"],
            ["공간", "우선 점검 17곳 → 사각지대 아님 10 · 개선 대상 4 · 확인 필요 3 (13곳은 두 방학 연속 하위 25%)"],
            ["제도", "방학 이용자 99.5%가 하루 1만 원 넘게 카드 결제한 날이 있음\v최소주문 면제 가게가 앱 목록에 표시 안 됨"]]
    d.table(sl, X0, TOP + 404, [96, lw - 96], rows, head=False, row_h=(BOT - TOP - 404) / 3, size=19,
            bolds=lambda r, c: c == 0)
    vline(d, sl, X0 + lw + 30, TOP, BOT)
    rx = X0 + lw + 60
    rw = X1 - rx
    head(d, sl, rx, TOP, rw, "해결방안 3가지", right="담당 · 시점")
    items = [("1", "방학 정기 배달편 + 배달 가능 급식 가게 우선 노출", "운영사 · 배달형 3곳 시범(북구 학정동·검단동, 논공 금포리)"),
             ("2", "앱 목록에 ‘급식카드 최소주문 면제’ 표시", "대구시·운영사 · 대구 전역, 시범 없이 시행"),
             ("3", "운영사 재공모 협약에 ‘방학 급식 사각지대 점검표’ 제출 조항", "대구시 · 2026-11 협약 → 2027-03 1회차")]
    iy = TOP + 58
    for no, h_, sub in items:
        lines = 1 if est_w(h_, 20) * 0.9 < rw - 36 else 2      # est_w는 넉넉하게 잡는 값
        d.text(sl, rx, iy, 30, 30, no, size=22, color=AMBER, bold=True)
        d.text(sl, rx + 36, iy + 1, rw - 36, 60, h_, size=20, color=INK, bold=True, lsp=1.25)
        d.text(sl, rx + 36, iy + 8 + 26 * lines, rw - 36, 50, sub, size=17, color=MUTED, lsp=1.3)
        iy += 132
    hline(d, sl, rx, X1, TOP + 470)
    head(d, sl, rx, TOP + 494, rw, "데이터 연계", size=20)
    d.text(sl, rx, TOP + 540, rw, 110,
           "**미개방**  대구로 결제·가맹점·배달·고객, KCB 소득\n**공개**  주민등록 인구, 행정동·법정동 대응표, 경계\n"
           "**현장**  대구로 앱 점검, 구청·시청 확인", size=17, color=INK2, lsp=1.6)
    d.text(sl, rx, TOP + 660, rw, 40, "→ 동네 묶음 71곳(법정동 ↔ 행정동)으로 연결", size=17, color=INK, bold=True)
    d.text(sl, rx, TOP + 712, rw, 56, "분석 규모: 급식카드 결제 341,216건 · 25개월 · 법정동 181곳\v"
           "진단 → 이유 7가지 판정 → 해결방안·방학 점검표", size=16, color=MUTED, lsp=1.35)
    d.notes(sl, "한 장 요약. 결론: 가게를 더 모으는 것보다 방학마다 덜 쓰는 동을 판정해 필요한 몇 곳에 해결방안을 모으는 장치.\n"
                "숫자 셋: 가게는 이미 99.9%의 아이에게 닿음(모집 효과 0), 겉보기 부족분의 65%는 사각지대가 아닌 곳, 개선이 필요한 곳은 4개 동.\n"
                "해결방안 셋: 방학 정기 배달편, 앱 목록 면제 표시, 운영사 협약에 점검표 조항.")


# ---- 3. 배경 -----------------------------------------------------------------------------------
def s03(d, sl):
    frame(d, sl, 1, "문제 정의: 지원 구조", "급식카드 배달 결제는 열렸지만, 쟁점은 실제로 주문하느냐", 3,
          "대구로 급식카드 배달 결제 2023-06-01 시행(경북매일, 2023-05-31) · 배달비 지원 누적(매일신문, 2024-02-29)")
    rows = [["단계", "내용", "확인"],
            ["1  신청", "학기·방학별로 아침·점심·저녁 끼니를 골라 신청", "동구청 아동청소년과 확인 · 2026-10-08 · 대구 공통"],
            ["2  결제", "끼니 구분 없이 하루 한도 금액까지 결제 · 대구로 앱 배달 주문 가능, 배달비 지원 중",
             "동구청 확인 · 배달비 누적 약 6천 명·2억 7천만 원"],
            ["3  단가", "2026년 1끼 1만 원 · 하루 한도는 신청한 끼니 수만큼(두 끼면 2만 원)", "대구시청 복지과 문의 · 2026-10-15"]]
    head(d, sl, X0, TOP, W, "대구 아동급식카드 지원 구조", size=20, right="2023-06부터 대구로 배달 결제")
    d.table(sl, X0, TOP + 44, [170, 820, W - 990], rows, row_h=96, head_h=46, size=20,
            bolds=lambda r, c: c == 0, colors=lambda r, c: MUTED if c == 2 else INK,
            sizes=lambda r, c: 17 if c == 2 else 20)
    y = TOP + 420
    lw = 580
    kicker(d, sl, X0, y, lw, "기존 시각", color=MUTED)
    d.text(sl, X0, y + 38, lw, 90, "급식 가맹점이 주변에 있으면 이용 가능", size=27, color=INK2, bold=True, lsp=1.3)
    bullets(d, sl, X0, y + 112, lw, 160, ["평가 지표 = 가맹점 수, 공급 지도", "방학·시간대·한도는 지표 밖"], size=19)
    vline(d, sl, X0 + lw + 40, y, y + 230)
    rx = X0 + lw + 80
    kicker(d, sl, rx, y, X1 - rx, "이 분석의 시각")
    d.text(sl, rx, y + 38, X1 - rx, 90, "결제 로그로 방학에 실제 주문이 일어나는지 동 단위 확인", size=27, color=INK,
           bold=True, lsp=1.3)
    bullets(d, sl, rx, y + 112, X1 - rx, 200,
            ["덜 쓰는 동 → 이유 7가지 판정 → 담당별 해결방안", "같은 로그로 방학마다 다시 점검(점검표, 22쪽)",
             "기대효과 단위 = 방학 한 달 이용자 수"], size=19)
    d.notes(sl, "배경. 2023년 6월부터 대구로 앱에서 급식카드 배달 결제가 된다.\n"
                "지원 구조: 끼니를 골라 신청, 결제는 하루 한도로만 막힘, 2026년 1끼 1만 원(구청·시청 확인).\n"
                "기존 평가는 가맹점 수였다. 우리는 결제 로그로 실제 주문이 일어나는지를 동 단위로 본다.")


# ---- 4. 질문 -----------------------------------------------------------------------------------
def s04(d, sl):
    frame(d, sl, 1, "문제 정의: 세 축과 질문", "‘어디서 멈추는가’를 세 축으로 나눠, 한 축이 약해도 나머지 축으로 결론 유지", 4)
    axes = [("시간", "언제 멈추나", "학기·방학 시기, 요일, 시각", "월별·시간대 결제(1·2차 반출)"),
            ("공간", "어디서 멈추나", "법정동 181곳, 동네 묶음 71곳", "동·시기별 결제, 아동 인구, KCB 소득(3·4차)"),
            ("제도", "무엇이 막나", "신청 유형, 하루 한도, 최소주문", "결제 금액(4차), 앱 점검, 구청·시청 확인")]
    lw = 600
    y = TOP
    for i, (name, q, scope, data) in enumerate(axes):
        if i:
            hline(d, sl, X0, X0 + lw, y - 24)
        d.title_text(sl, X0, y, 120, 60, name, size=40)
        d.text(sl, X0 + 120, y + 12, lw - 120, 34, q, size=22, color=INK2, bold=True)
        d.text(sl, X0, y + 80, lw, 34, scope, size=20, color=INK, bold=True)
        d.text(sl, X0, y + 122, lw, 60, f"자료: {data}", size=17, color=MUTED, lsp=1.3)
        y += 256
    vline(d, sl, X0 + lw + 40, TOP, BOT)
    rx = X0 + lw + 80
    rw = X1 - rx
    head(d, sl, rx, TOP, rw, "분석 질문", right="답하는 쪽")
    qs = [("1", "아이들은 언제 급식카드로 배달을 시키나", "10~12쪽"),
          ("2", "실제로 덜 쓰는 동은 어디인가: 두 기준으로 선정", "13~16쪽"),
          ("3", "덜 쓰는 이유는 무엇인가: 후보 7가지를 데이터로 판정", "16~19쪽"),
          ("4", "무엇을 하면 더 쓰나: 누가, 얼마나", "20~22쪽")]
    qy = TOP + 72
    for i, (no, q, pages) in enumerate(qs):
        if i:
            hline(d, sl, rx, X1, qy - 30)
        d.title_text(sl, rx, qy, 60, 60, no, size=44, color=AMBER)
        d.text(sl, rx + 70, qy + 6, rw - 210, 80, q, size=23, color=INK, bold=True, lsp=1.3)
        d.text(sl, X1 - 120, qy + 12, 120, 28, pages, size=16, color=MUTED, align="r")
        qy += 172
    d.notes(sl, "질문을 세 축으로 나눈다. 시간(언제), 공간(어디서), 제도(무엇이 막나).\n"
                "분석 질문은 넷: 언제 쓰나, 실제로 덜 쓰는 동은 어디인가, 왜 덜 쓰나, 무엇을 하면 더 쓰나.")


# ---- 5. 분석 틀 --------------------------------------------------------------------------------
def s05(d, sl):
    frame(d, sl, 1, "문제 정의: 분석 틀", "진단 → 이유 판정 → 해결방안, 판정 규칙은 결과 확인 전에 고정", 5,
          "판정 규칙 문서 docs/topics/T2_reason_rules.md (결정 기록 D-019)")
    rows = [["단계", "하는 일", "결과물"],
            ["1  진단", "시간: 시기·시각 분포\n공간: 방학 급식 비중 지수, 아동 1천 명당 이용", "우선 점검 17곳"],
            ["2  이유 판정", "이유 7가지마다 해당·아님·판단 불가\n근거: KCB 소득, 배달, 앱 점검, 이웃 비교", "제외 · 개선 대상 · 확인 필요"],
            ["3  해결방안·시나리오", "유형별 담당과 확인 지표\n가게 늘리기(A) 대 이용 회복(B)", "같은 단위 비교: 방학 월 이용자 수"]]
    d.table(sl, X0, TOP, [300, 760, W - 1060], rows, row_h=110, head_h=46, size=20,
            bolds=lambda r, c: c in (0, 2))
    y = TOP + 450
    principles = [("원칙 1", "판정 규칙은 반출물 확인 전 고정", "2026-10-13 문서화·버전 기록(git)\n문턱 = 대구 분포 25%·중앙값", 520),
                  ("원칙 2", "진단 숫자와 시나리오 숫자 분리", "시나리오는 ‘가정 하’ 표시\n결론 문장에 섞지 않음", 440),
                  ("원칙 3", "판단 불가는 ‘?’로 유지", "숨기지 않고\n다음 회차 점검 항목으로 넘김", 428)]
    x = X0
    for i, (tag, h_, body, w) in enumerate(principles):
        if i:
            vline(d, sl, x - 30, y, y + 200)
        kicker(d, sl, x, y, w, tag)
        d.text(sl, x, y + 40, w, 80, h_, size=24, color=INK, bold=True, lsp=1.3)
        d.text(sl, x, y + 96, w, 110, body, size=19, color=INK2, lsp=1.45)
        x += w + 60
    d.notes(sl, "분석은 세 단계. 진단에서 덜 쓰는 동을 고르고, 이유 7가지를 판정하고, 유형별로 해결방안과 효과를 낸다.\n"
                "판정 규칙은 4차 반출물을 보기 전에 고정했다. 시나리오 숫자는 가정 아래 계산이라 진단 결론과 섞지 않는다.")


# ---- 6. 데이터 연계 ----------------------------------------------------------------------------
def s06(d, sl):
    frame(d, sl, 2, "데이터와 방법: 자료 연결", "결제 로그에 소득·배달·인구·현장 확인을 동네 단위로 연결", 6,
          "가점 대상: 상호제공 데이터(KCB 행정동 소득) 연계 · 분석 기간 2023-06~2025-06")
    cols = [(520, "미개방 상호제공 4종(대구로 3 + KCB) · 데이터안심구역", AMBER,
             [("대구로 결제", "급식 341,216건 · 일반 3,612,950건\n2023-06~2025-06, 결제 → 가맹점 법정동"),
              ("대구로 가맹점", "22,086곳 · 급식카드 등록 10,781곳\n등록·영업 상태, 주소(법정동)"),
              ("대구로 배달·고객", "배달 시간·배달팁 · 이용자 연령대\n4차 반출(일부 결함, 25쪽)"),
              ("KCB 행정동 소득", "2023년 4분기 · 행정동 150개(군위 포함)\n30·40대 소득 구간 → 필요의 대리 지표")]),
            (430, "공개 3종", INK,
             [("주민등록 연령별 인구", "6~18세 · 행정동별 · 25개월 (행정안전부)"),
              ("행정동·법정동 대응표", "2025-06-30 기준 (행정안전부)"),
              ("법정동·리 경계", "2026-09 (국가공간정보포털) · 지도, 이웃 동")]),
            (438, "현장 확인 2종", INK,
             [("대구로 앱 점검", "우선 점검 13곳·대조 3곳, ‘1인분’ 목록 (2026-10-15)"),
              ("구청·시청 확인", "신청 유형·하루 한도·2026 단가 (10-08·10-15)")])]
    x = X0
    for i, (w, tag, col, items) in enumerate(cols):
        if i:
            vline(d, sl, x - 30, TOP, TOP + 540)
        kicker(d, sl, x, TOP, w, tag, color=col)
        y = TOP + 44
        for name, body in items:
            d.text(sl, x, y, w, 30, name, size=21, color=INK, bold=True)
            d.text(sl, x, y + 38, w, 70, body, size=17, color=INK2, lsp=1.35)
            y += 124
        x += w + 60
    y = TOP + 580
    hline(d, sl, X0, X1, y)
    kicker(d, sl, X0, y + 30, 300, "연결 키")
    d.title_text(sl, X0, y + 64, 520, 60, "동네 묶음 71곳", size=44)
    d.text(sl, X0 + 580, y + 34, W - 580, 120,
           "가맹점 주소의 법정동과 인구·소득의 행정동을 공식 대응표로 묶은 단위\n면적 배분 없이 묶음 · 진단은 법정동 181곳",
           size=19, color=INK2, lsp=1.45)
    d.notes(sl, "데이터 연계. 안심구역의 미개방 상호제공 데이터(대구로 결제·가맹점·배달·고객, KCB 소득)에\n"
                "공개 데이터(인구, 대응표, 경계)와 현장 확인(앱 점검, 구청·시청)을 붙였다.\n"
                "가맹점은 법정동, 인구·소득은 행정동이라 둘을 이은 동네 묶음 71곳을 연결 키로 쓴다.")


# ---- 7. 전처리 ---------------------------------------------------------------------------------
def s07(d, sl):
    frame(d, sl, 2, "데이터와 방법: 전처리", "같은 정의 5단계를 모든 반출에 똑같이 적용", 7,
          "급식 정의·기간 판정: 2·3차 방문 확정 · 반출 가림 규칙은 센터 반출 기준")
    rows = [["단계", "정의", "결과", "근거"],
            ["1  급식 정의", "결제수단 ‘아동급식카드’ · 결제 완료 · 중복 제거 없음", "341,216건", "2차 방문 확정"],
            ["2  기간", "2023-06~2025-06", "25개월", "미리 정한 기간 판정 규칙으로 3차 방문 확정"],
            ["3  시기", "방학 1·2·8월 · 전환 7·12월 · 학기 나머지", "6 · 4 · 15개월", "방학 = 학교급식이 없는 달"],
            ["4  공간", "결제 → 가맹점 법정동, 인구·소득(행정동)과 연결", "71곳", "동네 묶음, 면적 배분 없음"],
            ["5  반출 가림", "결제 5건·고객 5명·가맹점 3곳 미만 가림 + 역산 칸 보완 가림", "자동 검사", "반출 전 자동 검사 통과 파일만 신청"]]
    d.table(sl, X0, TOP, [210, 640, 230, W - 1080], rows, row_h=76, head_h=46, size=19,
            bolds=lambda r, c: c == 0, fonts=lambda r, c: TITLE_FONT if c == 2 else None,
            sizes=lambda r, c: 26 if c == 2 else (17 if c == 3 else 19),
            colors=lambda r, c: AMBER if (r == 1 and c == 2) else (MUTED if c == 3 else INK))
    y = TOP + 480
    notes = [(X0, 700, "주의 1", "결제 위치 = 가맹점 소재지 (아이 집 아님)",
              ["옆 동네 가게 이용 판정으로 보정", "4차 집→가게 이동표는 결함으로 11% 표본만 반출 → 이웃 동 비교로 대체"]),
             (X0 + 760, W - 760, "주의 2", "이용자 = 대구로 앱 회원 (아동 수 아님)", ["형제 카드 합산·보호자 명의 가능", "효과 단위 = 방학 한 달 이용자 수"])]
    vline(d, sl, X0 + 730, y, BOT)
    for x, w, tag, h_, items in notes:
        kicker(d, sl, x, y, w, tag)
        d.text(sl, x, y + 38, w, 34, h_, size=22, color=INK, bold=True)
        bullets(d, sl, x, y + 92, w, 150, items, size=18)
    d.notes(sl, "전처리 다섯 단계. 급식 결제 = 결제수단이 아동급식카드이고 결제 완료된 건, 2023년 6월부터 25개월.\n"
                "시기는 방학·전환·학기. 공간은 가맹점 법정동을 행정동과 이어 동네 묶음 71곳.\n"
                "반출 때는 작은 칸과 역산되는 칸을 가리고, 저장 파일을 다시 읽어 자동 검사했다.")


# ---- 8. 지표와 판정 ----------------------------------------------------------------------------
def s08(d, sl):
    frame(d, sl, 2, "데이터와 방법: 지표와 판정", "두 기준으로 우선 점검 동네를 고르고, 덜 쓰는 이유는 7가지로 판정", 8,
          "선정 규칙 결정 기록 D-015~017 · 이유 판정 D-019 · 급식 비중 지수 분모 = 4차 동·시기별 일반 결제")
    rows = [["단계", "정의", "결과"],
            ["방학 급식 비중 지수", "동의 방학 급식 결제 ÷ 동의 일반 배달 결제\n대구 평균 = 1", "법정동 181곳"],
            ["덜 쓰는 동네 후보", "등록 급식 가게 3곳 이상\n+ 방학 급식 비중 지수 하위 25%", "37곳"],
            ["우선 점검 동네", "후보 중 아동 1천 명당 방학 이용이\n중앙값 미만", "17곳"],
            ["이유 판정", "이유 7가지마다 해당·아님·판단 불가\n문턱 = 대구 분포 25%·중앙값", "제외 10 · 개선 대상 4\n확인 필요 3"]]
    d.table(sl, X0, TOP, [230, 420, 210], rows, row_h=86, head_h=46, size=18,
            bolds=lambda r, c: c in (0, 2), colors=lambda r, c: AMBER if (c == 2 and r == 3) else INK)
    d.text(sl, X0, TOP + 414, 860, 60, "일반 배달 대비와 아동 수 대비가 모두 낮은 동만 우선 점검\v"
           "기준 하나로 고르면 잘못 뽑히는 동(직장 배달이 많은 동 등)을 차단", size=17, color=INK2, lsp=1.35)
    vline(d, sl, X0 + 890, TOP, TOP + 500)
    rx = X0 + 920
    rw = X1 - rx
    head(d, sl, rx, TOP, rw, "덜 쓰는 이유 7가지", size=20)
    reasons = [["필요", "도움이 필요한 집이 원래 적다", "제외"],
               ["옆 동네", "옆 동네 가게에서 사 먹는다", "제외"],
               ["가게", "급식 주문을 받는 가게가 적다", "해결방안"],
               ["1끼 값", "1끼 값으로 시킬 수 있는 가게가 적다", "해결방안"],
               ["배달", "배달이 적거나 오래 걸린다", "해결방안"],
               ["안내·신청", "몰라서 못 쓰거나 신청 끼니가 안 맞는다", "남은 이유로 추정"],
               ["다른 경로", "다른 방법으로 먹는다(지역아동센터 등)", "참고만"]]
    grp_ink = {"제외": INK2, "해결방안": AMBER, "남은 이유로 추정": MUTED, "참고만": MUTED}
    d.table(sl, rx, TOP + 46, [118, rw - 278, 160], reasons, head=False, row_h=62, size=17,
            bolds=lambda r, c: c == 0 or (c == 2 and reasons[r][2] == "해결방안"),
            colors=lambda r, c: grp_ink[reasons[r][2]] if c == 2 else (INK if c == 0 else INK2))
    y = TOP + 560
    hline(d, sl, X0, X1, y)
    head(d, sl, X0, y + 22, 600, "묶는 순서 (판정 규칙 D-019)", size=20)
    steps = ["옆 동네 → 제외", "필요 적음 → 제외", "가게·1끼 값·배달 → 개선 대상", "모두 아님 → 안내·신청으로 추정", "그 밖 → 확인 필요"]
    sw = W / len(steps)
    for i, s in enumerate(steps):
        d.text(sl, X0 + i * sw, y + 70, sw - 24, 60, f"{{a:{i + 1}}}  {s}", size=18, color=INK, bold=True, lsp=1.25)
    d.text(sl, X0, y + 150, W, 40, "사각지대가 아닌 곳(옆 동네·필요 적음)을 먼저 빼야 예산이 새지 않음(21쪽 65%)",
           size=18, color=INK2)
    d.notes(sl, "덜 쓰는 동은 두 기준으로 고른다. 일반 배달 대비로만 보면 직장 배달이 많은 동이 낮게 나와서, 아이 수 대비로도 낮은 곳만 우선 점검 동네로 본다.\n"
                "우선 점검 17곳의 이유를 7가지로 판정하고, 옆 동네에서 시키거나 필요가 적은 곳을 먼저 뺀다.")


# ---- 9. 신뢰성 ---------------------------------------------------------------------------------
def s09(d, sl):
    frame(d, sl, 2, "데이터와 방법: 신뢰성", "규칙은 반출 전에 고정하고, 사후 개정 2건은 개정 전 결과와 함께 공개", 9,
          "결정 기록 docs/DECISIONS.md (D-015~D-019) · 판정 코드 analysis/outside/90_reason_table.py")
    rows = [["날짜", "한 일", "내용"],
            ["10-12~15", "가짜 자료 사전 검증", "센터 입력 셀과 밖의 판정·시나리오 코드를 가짜 자료로 처음부터 끝까지 실행"],
            ["10-13", "판정 규칙 고정", "이유 7가지 문턱·묶는 순서·대조 동 10곳 문서화, 버전 기록(D-019)"],
            ["10-16", "반출 전 자동 검사", "저장 파일을 다시 읽어 5 미만 칸 검사 → 통과 파일만 반출 신청"],
            ["10-16 밤", "결함 대체 규칙 적용", "4차 결함 3건을 미리 정한 규칙대로 처리(가게 이유는 판단 불가, 옆 동네 이유는 이웃 동 비교)"]]
    d.table(sl, X0, TOP, [170, 330, W - 500], rows, row_h=66, head_h=46, size=19, bolds=lambda r, c: c in (0, 1))
    y2 = TOP + 370
    lw = 880
    kicker(d, sl, X0, y2, lw, "공개")
    d.text(sl, X0, y2 + 34, lw, 34, "결과 확인 후 바꾼 규칙 2건", size=22, color=INK, bold=True)
    items = [("1", "1끼 값 기준: 목록 최소주문 → 급식카드 결제 기준 최소주문",
              "앱 점검 중 ‘급식카드 주문 시 최소주문 미적용’ 가게 확인 → 면제 가게는 0원으로"),
             ("2", "‘지역 공통 장벽’ 표시 추가",
              "같은 구 대조 동도 1끼 가능 가게가 똑같이 적으면 동별 해결방안 대신 구 단위 장벽으로 표시")]
    iy = y2 + 92
    for no, h_, body in items:
        d.text(sl, X0, iy, 40, 34, no, size=22, color=AMBER, bold=True)
        d.text(sl, X0 + 44, iy, lw - 44, 34, h_, size=20, color=INK, bold=True)
        d.text(sl, X0 + 44, iy + 40, lw - 44, 70, body, size=17, color=INK2, lsp=1.35)
        iy += 124
    d.text(sl, X0 + 44, iy + 6, lw - 44, 30, "두 건 모두 개정 전 판정을 결정 기록에 함께 보존", size=17, color=MUTED)
    vline(d, sl, X0 + lw + 40, y2, y2 + 360)
    x2 = X0 + lw + 80
    w2 = X1 - x2
    d.text(sl, x2, y2 + 34, w2, 34, "판단 불가는 숨기지 않음", size=22, color=INK, bold=True)
    d.title_text(sl, x2, y2 + 86, 200, 80, "?", size=72, color=UNDEC)
    bullets(d, sl, x2, y2 + 186, w2, 200, ["다른 경로·안내: 동별 자료 없음", "가게: 4차 반출 결함", "→ 다음 회차 점검 항목으로 넘김"],
            size=19)
    d.notes(sl, "신뢰성 장치. 판정 규칙을 4차 반출물을 보기 전에 고정해 버전 기록을 남겼다.\n"
                "센터에서 입력할 코드를 가짜 자료로 끝까지 돌려 봤고, 반출 전에 저장 파일을 다시 읽어 가림 누락을 자동 검사했다.\n"
                "앱 점검 중 결과를 보고 바꾼 규칙 2건은 바꾸기 전 결과와 함께 공개한다.")


# ---- 10. 시간 1 --------------------------------------------------------------------------------
def s10(d, sl):
    frame(d, sl, 3, "결과 · 시간: 방학 집중", "급식카드 배달 결제는 학교급식이 없는 방학에 몰림", 10,
          "2차 반출 월별 표 · 아동 6~18세 대구 합계 269,326 → 264,685명(주민등록, 2024-01 → 2025-01) · 이용자 수는 아동 수와 다름")
    rows = load("monthly")
    cw = 1000
    head(d, sl, X0, TOP, 600, "월별 급식카드 결제 건수", size=20)
    legend(d, sl, X0 + cw, TOP + 2, ((NAVY_L, "학기"), (TEAL_M, "전환 7·12월"), (AMBER, "방학 1·2·8월")))
    gx, gy, gw, gh = X0 + 70, TOP + 80, cw - 70, 400
    vmax = 45000
    for t in (10000, 20000, 30000, 40000):
        yy = gy + gh - gh * t / vmax
        hline(d, sl, gx, gx + gw, yy)
        d.text(sl, gx - 70, yy - 12, 60, 24, f"{t // 10000}만", size=14, color=MUTED, align="r")
    bw = gw / len(rows)
    for i, r in enumerate(rows):
        h = gh * r["meal"] / vmax
        col = AMBER if r["regime"] == "방학" else (TEAL_M if r["regime"] == "전환" else NAVY_L)
        d.shape(sl, "rect", gx + i * bw + 5, gy + gh - h, bw - 10, h, fill=col, line=None)
        if r["month"] in ("2023-08", "2024-01", "2024-02", "2024-08", "2025-01", "2025-02"):
            d.text(sl, gx + i * bw - 16, gy + gh - h - 26, bw + 32, 22, f"{r['meal'] / 10000:.1f}만", size=13,
                   color=AMBER, bold=True, align="c")
        if r["month"].endswith(("-01", "-06")) or i == len(rows) - 1:
            d.text(sl, gx + i * bw - 20, gy + gh + 10, bw + 40, 22, r["month"][2:], size=13, color=MUTED, align="c")
    d.line(sl, gx, gy + gh, gx + gw, gy + gh, color=AXIS, w=1)
    vline(d, sl, X0 + cw + 30, TOP, TOP + 560)
    rx = X0 + cw + 60
    stats_column(d, sl, rx, TOP, X1 - rx,
                 [("55.3%", "급식 결제 중 방학 1·2·8월 몫", "25개월 중 6개월에 절반 넘게", AMBER),
                  ("4.9배", "방학 월평균 이용자 ÷ 학기", "3,785명 대 779명", INK),
                  ("16.3", "아동 1천 명당 1월 이용자 수", "13.5(2024) → 16.3(2025), 같은 기간 아동 −1.7%", INK)], step=192)
    y = TOP + 600
    hline(d, sl, X0, X1, y)
    kicker(d, sl, X0, y + 26, 600, "제도의 경계 · 사각지대 아님", color=MUTED)
    d.text(sl, X0, y + 64, W, 90,
           "학교급식 시간인 학기 평일 11시에는 급식 비중이 일반 결제의 {ab:0.65배}. ‘공백’이 아니라 제도의 경계로 따로 보고, 해결방안 대상에서 제외",
           size=20, color=INK, lsp=1.4)
    d.notes(sl, "급식카드 배달 결제의 55%가 방학 6개월에 몰린다. 방학 월평균 이용자는 학기의 약 4.9배.\n"
                "같은 기간(2024년 1월 → 2025년 1월) 아동은 1.7% 줄었는데 아동 1천 명당 1월 이용자 수는 13.5명에서 16.3명으로 늘었다.\n"
                "학기 평일 점심이 얇은 것은 학교급식 시간이라 사각지대가 아니라 제도의 경계로 따로 본다.")


# ---- 11. 시간 2 --------------------------------------------------------------------------------
def s11(d, sl):
    frame(d, sl, 3, "결과 · 시간: 시간대", "급식 결제만 23시에 끊기고, 점심·오후 비중은 일반 결제보다 높음", 11,
          "2차 반출 시간대·요일·시기별 파일 · 이용시간 06~23시 규칙(구청 안내)과 일치")
    rows = load("hourly")
    cw = 1040
    head(d, sl, X0, TOP, 600, "시간대별 결제 비중 (%, 25개월 합)", size=20)
    legend(d, sl, X0 + cw, TOP + 2, ((NAVY_L, "일반 결제"), (AMBER, "급식카드")))
    gx, gy, gw, gh = X0 + 60, TOP + 80, cw - 60, 600
    vmax = 20
    for t in (5, 10, 15, 20):
        yy = gy + gh - gh * t / vmax
        hline(d, sl, gx, gx + gw, yy)
        d.text(sl, gx - 60, yy - 12, 50, 24, f"{t}%", size=14, color=MUTED, align="r")
    gwid = gw / len(rows)
    for i, r in enumerate(rows):
        x = gx + i * gwid
        for j, (v, col) in enumerate(((r["meal_pct"], AMBER), (r["general_pct"], NAVY_L))):
            h = max(1.5, gh * v / vmax)
            d.shape(sl, "rect", x + 6 + j * (gwid - 12) / 2, gy + gh - h, (gwid - 12) / 2 - 2, h, fill=col, line=None)
        d.text(sl, x - 6, gy + gh + 10, gwid + 12, 22, r["hour"], size=13 if len(r["hour"]) > 2 else 14,
               color=AMBER if r["hour"] == "23~05" else MUTED, align="c", bold=r["hour"] == "23~05")
    d.line(sl, gx, gy + gh, gx + gw, gy + gh, color=AXIS, w=1)
    last = gx + (len(rows) - 1) * gwid
    d.text(sl, last - 150, gy + gh - 280, gwid + 150, 60, "23~05시\n급식 0.00% · 일반 2.44%", size=15, color=AMBER,
           bold=True, align="r", lsp=1.25)
    vline(d, sl, X0 + cw + 30, TOP, BOT)
    rx = X0 + cw + 60
    stats_column(d, sl, rx, TOP, X1 - rx,
                 [("11건", "23~05시 급식 결제, 25개월 합", "같은 시간 일반 결제 88,244건\v22시 급식 14,730건 → 23시 이후 절벽", AMBER),
                  ("18.6%", "방학 11~12시 급식 결제 비중", "학기 12.4% · 일반은 14.3% → 15.6%", INK),
                  ("36.3%", "저녁 17~19시 급식 결제 비중", "일반 45.4%보다 낮아 저녁 피크가 얇음", INK),
                  ("+10%", "주말 하루 평균 급식 결제(평일 대비)", "일반 +43%보다 작아 급식은 평일 쪽", INK)],
                 step=(BOT - TOP + 18) / 4, size=40, sub_h=40)
    d.notes(sl, "시간대에서 두 가지. 급식만 23시에 끊긴다: 25개월 동안 23시~05시 급식 결제는 11건, 일반은 자정에도 계속.\n"
                "방학에는 점심 비중이 학기 12.4%에서 18.6%로 오른다. 저녁 피크는 일반보다 얇다.")


# ---- 12. 시간 3 --------------------------------------------------------------------------------
def s12(d, sl):
    frame(d, sl, 3, "결과 · 시간: 달성군 학기", "달성군만 학기 이용이 유독 적음: 학교 점심이 아니라 군 단위 차이", 12,
          "3차 반출 동·시기별 파일 · 결제 위치 = 가맹점 소재지(남구는 다른 구로 배달한 몫 포함 가능) · 시간대 비중: 2차 반출 · "
          "달성군 지원: 경북매일·아주경제 2024-08-01")
    rows = sorted(load("gu"), key=lambda r: -r["ratio"])
    cw = 860
    head(d, sl, X0, TOP, 600, "아동 1천 명당 월 급식 결제 (건)", size=20)
    legend(d, sl, X0 + cw, TOP + 2, ((NAVY_L, "학기"), (AMBER, "방학")))
    d.text(sl, X0, TOP + 32, cw, 26, "가맹점 소재 군구 기준 · 방학 ÷ 학기 배수 순 · 달성군은 학기 이용이 방학의 1/25",
           size=16, color=MUTED)
    gx, gy = X0 + 100, TOP + 66
    gw = cw - 100 - 170
    vmax = 360
    rh = (BOT - gy) / len(rows)
    for i, r in enumerate(rows):
        y = gy + i * rh
        hl = r["gu"] == "달성군"
        d.text(sl, X0, y + 12, 90, 30, r["gu"], size=19, color=AMBER if hl else INK, bold=hl)
        for j, (v, col) in enumerate(((r["vacation"], AMBER), (r["semester"], NAVY_L))):
            w = max(2, gw * v / vmax)
            d.shape(sl, "rect", gx, y + 6 + j * 26, w, 22, fill=col, line=None)
            d.text(sl, gx + w + 8, y + 4 + j * 26, 90, 24, f"{v:.1f}", size=14, color=MUTED)
        d.text(sl, X0 + cw - 120, y + 10, 120, 34, f"{r['ratio']:.1f}배", size=22, color=AMBER if hl else INK,
               align="r", font=TITLE_FONT)
        if i < len(rows) - 1:
            hline(d, sl, X0, X0 + cw, y + rh - 6)
    vline(d, sl, X0 + cw + 30, TOP, BOT)
    rx = X0 + cw + 60
    rw = X1 - rx
    kicker(d, sl, rx, TOP, rw, "달성군 남부 5개 읍면")
    d.text(sl, rx, TOP + 34, rw, 34, "논공·유가·구지·옥포·현풍", size=21, color=INK, bold=True)
    d.title_text(sl, rx, TOP + 76, rw, 70, "1/66~1/85", size=50, color=AMBER)
    d.text(sl, rx, TOP + 150, rw, 30, "방학 대비 배수 · 학기 아동 1천 명당 월 0.3~1.8건", size=18, color=INK2)
    hline(d, sl, rx, X1, TOP + 206)
    d.text(sl, rx, TOP + 228, rw, 30, "학교 점심 때문만은 아님", size=20, color=INK, bold=True)
    d.text(sl, rx, TOP + 268, rw, 140,
           "학기에도 평일 저녁·주말 점심엔 카드를 씀\v(학기 주말 점심 급식 비중이 일반의 1.2배)\n"
           "같은 학기 아동 1천 명당: 다른 구 12.7~89.0건,\v달성군 2.6건, 북부 읍(화원·다사)도 3.9건",
           size=18, color=INK2, lsp=1.4, after=8)
    hline(d, sl, rx, X1, TOP + 430)
    kicker(d, sl, rx, TOP + 452, rw, "해석 (추정)", color=MUTED)
    d.text(sl, rx, TOP + 486, rw, 100,
           "군 전체가 학기에 거의 안 씀\v→ 동네가 아니라 군의 지원·신청 방식 차이\v"
           "달성군은 여름방학 지원 대상을 따로 정해 발표(2024 보도)", size=18, color=INK2, lsp=1.4)
    hline(d, sl, rx, X1, TOP + 600)
    kicker(d, sl, rx, TOP + 622, rw, "해결방안 대신 확인")
    d.text(sl, rx, TOP + 656, rw, 30, "달성군청: 학기 지원 방식 · 학기 신청 인원", size=19, color=INK, bold=True)
    d.text(sl, rx, TOP + 696, rw, 70, "다른 경로(지역아동센터 등)로 먹으면 사각지대 아님\n학기 지원이 비어 있으면 군 정책 과제로 보고",
           size=17, color=INK2, lsp=1.35)
    d.notes(sl, "학기에는 어느 구나 덜 쓴다. 학기 평일 점심은 학교급식이고, 학기에 카드를 쓰는 끼니는 평일 저녁과 주말 점심이다"
                "(학기 주말 점심 급식 비중이 일반의 1.2배).\n"
                "그런데 같은 학기끼리 비교해도 달성군은 아동 1천 명당 2.6건으로 다른 구(12.7~89.0건)보다 훨씬 적고, "
                "북부 읍(화원·다사)도 3.9건이다. 남부 5개 읍면은 방학의 66~85분의 1이고, 학기에 쓰는 이용자 자체가 거의 없다.\n"
                "학교 점심으로는 설명되지 않는 군 단위 차이다. 달성군은 여름방학 지원 대상을 따로 정해 발표한다(2024 보도). "
                "학기에 다른 경로로 먹는지, 학기 지원이 비어 있는지는 결제 로그로 가릴 수 없어 군청 확인 항목으로 둔다.\n"
                "그래서 ‘학기 이용 회복’ 숫자는 효과로 쓰지 않는다. 비교 기준에 따라 대구 중앙값이면 +39.8명, "
                "달성군 북부면 +4.8명으로 8배 차이가 난다.")


# ---- 13. 공간 1: 지도 ----------------------------------------------------------------------------
def s13(d, sl):
    frame(d, sl, 4, "결과 · 공간: 지도", "방학에 덜 쓰는 동은 권역이 아니라 동 단위로 흩어져, 동 하나씩 판정", 13,
          "공간 뭉침 지수(Moran’s I): 동네 묶음 70곳(아동 300명 이상), 9,999회 순열 검정 · 지도는 우선 점검 위치만 표시(지표 값 비공개, 반출 공표 규칙)")
    mw = 580
    d.pic(sl, ASSET / "map_targets.png", X0, TOP, w=mw)
    map_labels(d, sl, X0, TOP, mw)
    vline(d, sl, X0 + mw + 40, TOP, BOT)
    rx = X0 + mw + 80
    rw = X1 - rx
    half = (rw - 60) / 2
    for i, (tag, col, big, p, body) in enumerate([
            ("학기 이용", MUTED, "I 0.53", "p < 0.001 · 강하게 뭉침", "달성군·북구 외곽에 낮은 이용이 권역으로 모임\n→ 지역 단위 원인(지원·신청 방식, 12쪽)"),
            ("방학 이용", AMBER, "I −0.02", "p 0.49 · 뭉치지 않음", "권역 단위 해결방안 불가\n→ 동마다 이유를 따로 판정(16쪽)")]):
        x = rx + i * (half + 60)
        if i:
            vline(d, sl, x - 30, TOP, TOP + 330)
        kicker(d, sl, x, TOP, half, tag, color=col)
        d.title_text(sl, x, TOP + 34, half, 90, big, size=72)
        d.text(sl, x, TOP + 130, half, 30, p, size=20, color=INK, bold=True)
        d.text(sl, x, TOP + 172, half, 150, body, size=19, color=INK2, lsp=1.35)
    hline(d, sl, rx, X1, TOP + 360)
    d.text(sl, rx, TOP + 386, rw, 34, "우선 점검 17곳 = 두 기준 모두 낮은 동", size=24, color=INK, bold=True)
    d.text(sl, rx, TOP + 432, rw, 120,
           "일반 배달 대비 방학 급식 비중 지수 하위 25% {b:+} 아동 1천 명당 이용 중앙값 미만\n지도 번호 = 16쪽 판정표 번호", size=20,
           color=INK2, lsp=1.4)
    hline(d, sl, rx, X1, TOP + 548)
    kicker(d, sl, rx, TOP + 574, rw, "두 번째 기준으로 거른 20곳 중 대표 예")
    d.text(sl, rx, TOP + 612, rw, 130,
           "달서구 서부(신당·호산 등 4곳): 일반 배달 대비로만 낮음(직장 배달이 많은 곳으로 추정)\v"
           "→ 아동 수 대비로는 중앙값의 약 2.2배\n"
           "기준 하나로만 골랐다면 우선 점검에 잘못 들어갔을 곳", size=19, color=INK2, lsp=1.4)
    d.notes(sl, "지도. 학기 이용은 권역 단위로 강하게 뭉친다(I 0.53). 방학은 뭉치지 않는다(I −0.02).\n"
                "그래서 방학 사각지대는 권역 단위 해결방안이 아니라 동 하나씩 이유를 판정해야 한다.\n"
                "일반 배달 대비로만 고르면 달서구 서부가 낮게 나오지만 아이 수 대비로는 많이 쓰는 곳이라 걸렀다. "
                "이렇게 두 번째 기준으로 거른 곳이 모두 20곳이다(37곳 → 17곳).")


# ---- 14. 공간 2: 선정·재현성 --------------------------------------------------------------------------
def s14(d, sl):
    frame(d, sl, 4, "결과 · 공간: 우선 점검 선정", "우선 점검 동네는 일시적으로 낮은 곳이 아님: 대부분 두 방학 연속 하위", 14,
          "3·4차 반출(동·시기별, 방학 반기) · 앞 반기 2023-08·2024-01·02 / 뒤 반기 2024-08·2025-01·02")
    fn = load("funnel")
    cw = 900
    rows = [["곳 수", "선정 단계"]] + [[f"{r['n']}", r["stage"]] for r in fn]
    last = len(rows) - 1
    d.table(sl, X0, TOP, [160, cw - 160], rows, row_h=100, head_h=46, size=21,
            fonts=lambda r, c: TITLE_FONT if c == 0 else None, sizes=lambda r, c: 40 if c == 0 else 21,
            colors=lambda r, c: AMBER if r == last else INK, bolds=lambda r, c: c == 1 and r == last)
    d.text(sl, X0, TOP + 46 + 100 * last + 22, cw, 30,
           "분모를 4차 동·시기별 일반 결제로 바꿔 다시 계산하니 북구 읍내동이 들어오고 화원읍 설화리가 빠짐", size=16, color=INK2)
    vline(d, sl, X0 + cw + 40, TOP, BOT)
    rx = X0 + cw + 80
    stats_column(d, sl, rx, TOP, X1 - rx,
                 [("0.785", "두 반기 동 순위 상관", "방학 급식 비중 지수 순위, 156개 동(등록 3곳 이상)", INK),
                  ("13 / 17", "우선 점검 중 두 반기 모두 하위 25%", "덜 쓰는 곳은 일시적이지 않음", AMBER),
                  ("4 / 4", "개선 대상 동 모두 연속", "시범 대상 선정 근거(22쪽)", INK)], step=262, size=56)
    d.notes(sl, "선정 단계. 비교 가능한 법정동 181곳 → 방학 비중 하위 25% 37곳 → 아이 수로 봐도 적은 우선 점검 17곳 → 판정 후 개선 대상 4곳.\n"
                "재현성: 방학 앞·뒤 반기의 동 순위 상관 0.785, 우선 점검 17곳 중 13곳은 두 반기 모두 하위 25%.")


# ---- 15. 공간 3: 공급 점검 -----------------------------------------------------------------------
def s15(d, sl):
    frame(d, sl, 4, "결과 · 공간: 공급 점검", "급식 주문 가게가 이미 거의 모든 아이에게 닿아, 가게를 더 모아도 효과 없음", 15,
          "공급 점검 코드 80 · 아동 266,222명 · 동네 묶음 71곳 · 후보 법정동 290곳 · 시나리오 = 가정 아래 계산")
    lw = 500
    d.text(sl, X0, TOP, lw, 30, "급식 가게가 닿는 아이 비율", size=20, color=INK, bold=True)
    d.title_text(sl, X0, TOP + 40, lw, 120, "99.9%", size=104, color=AMBER)
    d.text(sl, X0, TOP + 172, lw, 96, "공급 점검(MCLP) 기준: 방학에 실제 급식 주문을 받은 가게\v"
           "맞닿은 동까지 닿음 · KCB 소득으로 필요 반영\v가게 문턱 1~50곳 모두 0.999", size=17, color=INK2, lsp=1.35)
    d.text(sl, X0, TOP + 290, lw, 30, "가장 빡빡한 설정에서도", size=19, color=INK, bold=True)
    rows = [["닿는 범위 · 가게 문턱", "닿는 비율"], ["맞닿은 동까지 · 1~50곳", "99.9%"], ["같은 동네 묶음 안만 · 1곳", "99.9%"],
            ["같은 동네 묶음 안만 · 20곳", "98.5%"], ["같은 동네 묶음 안만 · 50곳", "89.3%"]]
    d.table(sl, X0, TOP + 332, [330, 170], rows, row_h=60, head_h=44, size=18, aligns=["l", "r"],
            bolds=lambda r, c: c == 1)
    vline(d, sl, X0 + lw + 30, TOP, BOT)
    mx = X0 + lw + 60
    mw = 440
    d.text(sl, mx, TOP, mw, 30, "가게는 있는데 주문이 없음", size=20, color=INK, bold=True)
    d.title_text(sl, mx, TOP + 40, mw, 90, "631곳", size=72)
    d.text(sl, mx, TOP + 136, mw, 70, "급식카드 등록·영업 중인데 급식 결제가 없는 가게\n(3차, 영업·서비스 유지)", size=18,
           color=INK2, lsp=1.35)
    d.text(sl, mx, TOP + 230, mw, 160, "공급 부족이 아니라 이용 쪽 문제\n→ 가게 수 대신 이유 판정(16쪽)과\n해결방안(20쪽)", size=20,
           color=INK, bold=True, lsp=1.4)
    vline(d, sl, mx + mw + 30, TOP, TOP + 440)
    rx = mx + mw + 60
    rw = X1 - rx
    d.text(sl, rx, TOP, rw, 30, "외곽 예외 6곳", size=20, color=INK, bold=True)
    d.text(sl, rx, TOP + 38, rw, 30, "공급 점검 후보로 유지 (결정 기록 D-018)", size=17, color=MUTED)
    d.text(sl, rx, TOP + 84, rw, 80, "가창면 · 하빈면 · 공산동\n안심2동 · 검단동 · 파동", size=20, color=INK, bold=True, lsp=1.45)
    d.text(sl, rx, TOP + 190, rw, 200,
           "실제 주문받는 가게 기준 공급과 주문 흐름 자료가 4차 결함으로 일부만 반출 → 공급형 해결방안 판정 보류, 다음 회차", size=18,
           color=INK2, lsp=1.4)
    y = TOP + 470
    hline(d, sl, mx, X1, y)
    kicker(d, sl, mx, y + 26, 600, "시나리오 A · 가정 아래 계산")
    d.text(sl, mx, y + 62, X1 - mx, 34, "가게 모집·활성화 → 방학 월 이용자 수", size=21, color=INK, bold=True)
    d.title_text(sl, mx, y + 110, 220, 90, "+0", size=78)
    d.text(sl, mx + 220, y + 130, X1 - mx - 220, 100, "가장 후한 가정에서도 최대 +35명 · 대구 방학 월평균 3,785명 대비",
           size=18, color=INK2, lsp=1.4)
    d.notes(sl, "공급 점검. 방학에 실제 급식 주문을 받은 가게가 이미 도움이 필요한 정도를 반영한 아이의 99.9%에 닿는다.\n"
                "등록·영업 중인데 급식 결제가 없는 가게도 631곳 있다. 공급 부족이 아니라 이용 쪽 문제.\n"
                "그래서 가게를 더 모으는 시나리오 A의 효과는 0(가장 후한 가정에서도 35명).")


# ---- 16. 공간 4: 판정표 --------------------------------------------------------------------------
def s16(d, sl):
    frame(d, sl, 4, "결과 · 공간: 판정표", "옆 동네 이용·필요 적음을 먼저 빼고, 남은 곳만 해결방안·현장 확인", 16,
          "● 해당  ○ 아님  ? 판단 불가 · 다른 경로·안내는 동별 자료 없음, 가게는 4차 반출 결함으로 판단 불가 · 판정 규칙은 반출 전 고정(D-019)")
    tg = load("targets")
    rows = [["번호", "구", "동", "필요", "다른 경로", "가게", "1끼 값", "배달", "안내·신청", "옆 동네", "판정"]] + [
        [t["no"], t["gu"], t["dong"], t["R1"], t["R2"], t["R3"], t["R4"], t["R5"], t["R6"], t["R7"], KIND_NAME[t["kind"]]]
        for t in tg]
    sym_col = {"●": NAVY, "○": mix(NAVY, 0.45), "?": mix(NAVY, 0.30)}

    def colors(r, c):
        if 3 <= c <= 9:
            return sym_col.get(rows[r][c], INK)
        return KIND_INK[tg[r - 1]["kind"]] if c == 10 else INK

    col_w = [60, 84, 160, 72, 94, 72, 84, 72, 94, 84, 160]
    d.table(sl, X0, TOP - 4, col_w, rows, row_h=40, head_h=44, size=17, head_size=15,
            aligns=["c", "l", "l"] + ["c"] * 7 + ["l"], colors=colors,
            bolds=lambda r, c: (c == 10 and tg[r - 1]["kind"] in ("confirmed", "undecided")) or
            (3 <= c <= 9 and rows[r][c] == "●"))
    rx = X0 + sum(col_w) + 60
    vline(d, sl, rx - 30, TOP, BOT)
    rw = X1 - rx
    items = [("사각지대 아님", "10곳", INK, "옆 동네 가게 이용 5 · 필요 가구 적음 5\n→ 조치 없이 다음 회차 관찰"),
             ("개선 대상 · 배달형", "4곳", AMBER, "배달 자체가 적거나 오래 걸림(배달팁 아님)\n→ 운영사: 방학 정기 배달편"),
             ("확인 필요", "3곳", UNDEC, "이유 판정 불가 항목 남음\n→ 구청 현장 확인 후 다음 회차")]
    y = TOP
    for i, (lab, n, col, desc) in enumerate(items):
        if i:
            hline(d, sl, rx, X1, y - 22)
        d.text(sl, rx, y, rw, 30, lab, size=20, color=INK, bold=True)
        d.title_text(sl, rx, y + 38, rw, 70, n, size=56, color=col)
        d.text(sl, rx, y + 116, rw, 96, desc, size=17, color=INK2, lsp=1.35)
        y += 262
    d.notes(sl, "판정표. 우선 점검 17곳마다 이유 7가지를 해당·아님·판단 불가로 판정했다.\n"
                "먼저 사각지대가 아닌 곳을 뺀다: 옆 동네 가게에서 사 먹는 곳 5곳, 도움이 필요한 집이 원래 적은 곳 5곳.\n"
                "남은 7곳 중 4곳은 배달 여건이 걸려 개선 대상(배달형), 3곳은 이유를 확정하지 못해 구청 현장 확인으로 넘긴다.")


# ---- 17. 제도 1: 앱 점검 -----------------------------------------------------------------------
def s17(d, sl):
    frame(d, sl, 5, "결과 · 제도: 앱 점검", "급식카드 최소주문 면제 가게는 있지만 앱 목록에는 표시 안 됨", 17,
          "앱 점검 기록(팀, 2026-10-15 17:26~17:53, 가게 상세 18:01~20:58) · 1끼 값 기준 개정(결과 확인 후, 9쪽)")
    steps = ["동별 실제 주소 입력", "‘1인분’ · 가까운 순", "상위 10곳 최소주문 기록", "상세 화면 면제 문구 확인"]
    sw = W / len(steps)
    for i, s in enumerate(steps):
        d.text(sl, X0 + i * sw, TOP, sw - 20, 30, f"{{a:{i + 1}}}  {s}", size=19, color=INK, bold=True)
    y = TOP + 66
    hline(d, sl, X0, X1, y)
    y += 30
    sw2 = 340
    stat(d, sl, X0, y, sw2, "64곳", "기록한 가게", "우선 점검 13곳·대조 3곳 주소의\v‘1인분’ 목록 상위 10곳 · 2026-10-15",
         size=56, sub_h=56)
    vline(d, sl, X0 + sw2 + 30, y, y + 240)
    stat(d, sl, X0 + sw2 + 60, y, sw2, "5 / 13", "상세 확인 가게 중 면제", "‘최소주문 미적용’ 문구 확인", color=AMBER, size=56,
         sub_h=50)
    vline(d, sl, X0 + 2 * sw2 + 90, y, y + 240)
    x3 = X0 + 2 * sw2 + 120
    kicker(d, sl, x3, y, X1 - x3, "목록 표시: 없음")
    d.text(sl, x3, y + 36, X1 - x3, 90, "면제 여부는 가게 상세 화면 문구로만 확인 가능\n1인분 목록에는 최소주문 금액만 노출",
           size=21, color=INK, bold=True, lsp=1.35)
    d.text(sl, x3, y + 148, X1 - x3, 90,
           "→ 해결방안: 목록에 ‘급식카드 최소주문 면제’ 표시. 대구 전역, 비용이 작고 해가 없어 시범 없이 시행", size=18,
           color=INK2, lsp=1.4)
    y2 = y + 280
    hline(d, sl, X0, X1, y2)
    y2 += 30
    lw = 600
    d.text(sl, X0, y2, lw, 30, "우선 점검 17곳의 1끼 값 판정", size=20, color=INK, bold=True)
    d.text(sl, X0, y2 + 44, lw, 40, "해당 {b:2}  ·  아님 {b:7}  ·  판단 불가 {b:8}", size=24, color=INK)
    d.text(sl, X0, y2 + 100, lw, 120,
           "판단 불가 8 = 면제 여부 미확인 4 + 앱 점검 안 한 동 4\n해당 2곳(옥포 본리리, 지묘동)은 옆 동네 이용으로 최종 제외",
           size=17, color=INK2, lsp=1.4)
    d.text(sl, X0, y2 + 176, lw, 50, "기준 = 카드 한 끼 값(1만 원)만으로 주문할 수 있는가\v한 끼만 신청했거나 돈을 더 낼 수 없는 아이 기준(18쪽)",
           size=16, color=MUTED, lsp=1.35)
    vline(d, sl, X0 + lw + 30, y2, y2 + 220)
    x2 = X0 + lw + 60
    w2 = 430
    kicker(d, sl, x2, y2, w2, "지역 공통 장벽 · 5곳")
    d.text(sl, x2, y2 + 36, w2, 100, "화원 명곡리·본리리, 옥포 본리리,\n북구 칠성동2가·침산동", size=19, color=INK, bold=True,
           lsp=1.35)
    d.text(sl, x2, y2 + 116, w2, 120, "같은 구 대조 동도 1끼 가능 가게가 똑같이 적음\n→ 동이 아니라 구 단위 가격 장벽", size=17,
           color=INK2, lsp=1.4)
    vline(d, sl, x2 + w2 + 30, y2, y2 + 220)
    x3 = x2 + w2 + 60
    kicker(d, sl, x3, y2, X1 - x3, "목록 자체가 짧은 곳", color=INK)
    d.text(sl, x3, y2 + 36, X1 - x3, 60, "동구 지묘동 · 옥포 본리리", size=19, color=INK, bold=True)
    d.text(sl, x3, y2 + 80, X1 - x3, 150, "주소 기준 1인분 목록에 가게 3곳뿐\n→ 집 근처보다 옆 동네에서 주문", size=17,
           color=INK2, lsp=1.4)
    d.notes(sl, "앱 점검. 우선 점검 13곳과 대조 3곳의 실제 주소로 ‘1인분’ 목록 상위 10곳을 기록했다.\n"
                "급식카드로 주문하면 최소주문을 면제하는 가게가 있지만, 목록에는 표시되지 않고 상세 화면 문구로만 보인다.\n"
                "가격 장벽은 특정 동이 아니라 구 단위로 깔려 있다(대조 동도 같음).")


# ---- 18. 제도 2: 결제 금액 ---------------------------------------------------------------------
def s18(d, sl):
    frame(d, sl, 5, "결과 · 제도: 결제 금액", "쓰는 아이는 1끼 값에 막히지 않음: 여러 끼·형제 카드를 합쳐 카드로 결제", 18,
          "4차 반출 하루 결제 금액표(결제 원장 직접 집계, 정상 파일) · 주문 합계 분포: 3차 반출 · 하루 한도는 신청한 끼니 수만큼(대구시청 복지과)")
    rows = load("maxday")
    cw = 940
    head(d, sl, X0, TOP, 700, "방학 중 하루 최대 카드 승인액별 이용자 수", size=20)
    d.text(sl, X0, TOP + 32, cw, 26, "방학에 결제한 이용자 6,223명 · 금액 = 급식카드 승인액(본인이 더 낸 돈은 빠짐)",
           size=16, color=MUTED)
    gx, gy, gw, gh = X0 + 60, TOP + 80, cw - 60, 400
    vmax = 2400
    for t in (500, 1000, 1500, 2000):
        yy = gy + gh - gh * t / vmax
        hline(d, sl, gx, gx + gw, yy)
        d.text(sl, gx - 64, yy - 12, 54, 24, f"{t:,}", size=14, color=MUTED, align="r")
    bw = gw / len(rows)
    for i, r in enumerate(rows):
        low = i < 3
        h = max(3, gh * r["accounts"] / vmax)
        d.shape(sl, "rect", gx + i * bw + 8, gy + gh - h, bw - 16, h, fill=AMBER if low else (TEAL_M if i >= 6 else NAVY_L),
                line=None)
        d.text(sl, gx + i * bw - 4, gy + gh - h - 26, bw + 8, 22, f"{r['accounts']:,}", size=14,
               color=AMBER if low else INK2, bold=low, align="c")
        d.text(sl, gx + i * bw - 4, gy + gh + 10, bw + 8, 22, r["bin"], size=14, color=MUTED, align="c")
    d.line(sl, gx, gy + gh, gx + gw, gy + gh, color=AXIS, w=1)
    d.text(sl, gx, gy + gh + 44, gw, 50,
           "{ab:1만 원 이하는 31명(0.5%)}뿐이고, 나머지 99.5%는 하루 1만 원 넘게 결제한 날이 있음\v"
           "2.4만 원 초과 4,911명(78.9%) · 3만 원 초과 2,260명(36.3%, 카드 한 장의 하루 한도를 넘는 금액)", size=16,
           color=INK2, lsp=1.35)
    vline(d, sl, X0 + cw + 30, TOP, TOP + 580)
    rx = X0 + cw + 60
    stats_column(d, sl, rx, TOP, X1 - rx,
                 [("18,626원", "결제 1건 평균 카드 승인액", "승인액 합 6,355,520,400원 ÷ 341,216건", INK),
                  ("82.9%", "하루 1회만 결제한 날", "이용자별 결제일 284,110일 중 235,512일", INK),
                  ("8.4%", "주문 합계 3만 원 이상 (급식카드)", "일반 결제는 24.4%, 급식 주문은 카드 한도 근처에서 끊김",
                   AMBER)], step=200)
    y = TOP + 620
    hline(d, sl, X0, X1, y)
    lw = 720
    kicker(d, sl, X0, y + 24, lw, "1만 원 넘는 결제의 출처 · 추정", color=MUTED)
    bullets(d, sl, X0, y + 58, lw, 110,
            ["여러 끼를 한 번에: 하루 한도는 신청한 끼니 수만큼, 하루 1회 결제 82.9%",
             "형제 카드: 3만 원 초과는 카드 한 장으로 안 되는 금액(36.3%)",
             "본인 돈 추가: 승인액에는 없지만, 주문 합계가 3만 원에서 끊겨 흔하지 않아 보임"], size=17, after=4)
    vline(d, sl, X0 + lw + 30, y + 24, BOT)
    rx2 = X0 + lw + 60
    kicker(d, sl, rx2, y + 24, X1 - rx2, "그래서 1끼 값 점검의 뜻")
    d.text(sl, rx2, y + 58, X1 - rx2, 110,
           "기준은 ‘카드 한 끼 값만으로 한 끼’: 한 끼만 신청했거나 돈을 더 낼 수 없는 아이 기준\v"
           "쓰는 아이는 막히지 않음, 막힌 아이는 로그에 없음\v"
           "→ 운영 회차 지표 = 신규 이용자 수, 1건 1만 원 이하 결제 비중", size=17, color=INK, lsp=1.35)
    d.notes(sl, "결제 금액으로 본 한도. 여기 금액은 급식카드 승인액이라 본인이 더 낸 돈은 들어 있지 않다.\n"
                "방학에 쓴 이용자 6,223명 중 하루 최대 승인액이 1만 원 이하인 이용자는 31명(0.5%). 하루 한도가 신청한 끼니 수만큼이라 "
                "여러 끼를 한 번에 주문하고(하루 1회 결제 83%), 3만 원을 넘는 날은 카드 한 장으로는 안 되는 금액이라 형제 카드를 함께 쓰는 것으로 "
                "보인다(36.3%).\n"
                "돈을 더 얹어 시키는지는 승인액에 안 나온다. 다만 주문 합계 분포가 3만 원에서 끊기고(3만 원 이상 급식 8.4%, 일반 24.4%), "
                "평균 주문 합계 21,794원이 승인액 18,626원과 할인 3,167원의 합과 맞아 흔하지 않아 보인다(건별 확인은 못 함).\n"
                "그래서 1끼 값 점검은 지금 쓰는 아이가 아니라 한 끼만 신청했거나 돈을 더 낼 수 없는 아이를 기준으로 한다. "
                "그런 아이는 로그에 안 나와서 운영 회차에서는 신규 이용자 수를 본다.")


# ---- 19. 제도 3: 사례 -------------------------------------------------------------------------
CHECKS = {"달성군 화원읍 일대": "방학 신규 이용자 수(처음 쓴 이용자), 1건 1만 원 이하 결제 비중\n대조: 달성군 다른 읍",
          "북구 검단동·학정동, 논공 금포리": "이용자 수, 아동 1천 명당 결제, 평균 배달 시간,\n배달 가능 급식 가게 수",
          "동구 지묘동": "다음 회차 이동표(배달 주소 기준),\n동별 급식카드 대상 아동 수"}


def s19(d, sl):
    frame(d, sl, 5, "결과 · 제도: 대표 사례", "가격은 구 단위, 배달은 동 단위, 나머지는 사각지대 아님", 19,
          "판정표(4차 결과) · 앱 점검 2026-10-15 · 시범 설계 docs/topics/T2_pilot_design.md")
    cases = [(520, "가격형 · 구 단위", INK, "달성군 화원읍 일대",
              ["대상 동(명곡리·본리리)과 많이 쓰는 대조 동(구라리) 모두 1인분 목록 10곳 중 1끼(1만 원) 가능 급식 가게 3곳 수준",
               "동별 판정 대신 ‘지역 공통 장벽’ 표시"],
              "시범 B(탐색): 면제·1만 원 이하 1인 메뉴 가게 모집, 목록 면제 표시", "대구시·구 + 운영사"),
             (500, "배달형 · 동 단위", AMBER, "북구 검단동·학정동, 논공 금포리",
              ["대구로 배달 자체가 적음(세 곳), 배달 시간이 김(금포리) · 배달팁은 걸리지 않음",
               "세 곳 모두 방학 앞·뒤 반기 연속 하위 25%",
               "배달형 4곳 중 화원 본리리는 시범 B 지역 안이라 B로 평가"],
              "시범 A: 방학 정기 배달편(점심·저녁 묶음 배달)\n배달 가능 급식 가게 우선 노출", "운영사"),
             (368, "사각지대 아님 · 해결방안 제외", MUTED, "동구 지묘동",
              ["필요·1끼 값·배달 모두 해당", "그러나 옆 동네 가게에서 주문"],
              "조치 없이 다음 회차 관찰\n(판정 없이 17곳 전체에 사업하면\n포함될 곳)", "없음")]
    x = X0
    for i, (w, tag, col, place, facts, plan, owner) in enumerate(cases):
        if i:
            vline(d, sl, x - 30, TOP, TOP + 660)
        kicker(d, sl, x, TOP, w, tag, color=col)
        d.text(sl, x, TOP + 36, w, 80, place, size=25, color=INK, bold=True, lsp=1.25)
        bullets(d, sl, x, TOP + 112, w, 200, facts, size=18, after=10)
        hline(d, sl, x, x + w, TOP + 300)
        d.text(sl, x, TOP + 320, 200, 26, "해결방안", size=16, color=MUTED, bold=True)
        d.text(sl, x, TOP + 350, w, 120, plan, size=19, color=INK, bold=True, lsp=1.35)
        hline(d, sl, x, x + w, TOP + 470)
        d.text(sl, x, TOP + 490, 200, 26, "확인 지표", size=16, color=MUTED, bold=True)
        d.text(sl, x, TOP + 520, w, 80, CHECKS[place], size=18, color=INK2, lsp=1.35)
        d.text(sl, x, TOP + 620, w, 30, f"담당: {owner}", size=17, color=INK, bold=True)
        x += w + 60
    d.notes(sl, "사례 세 묶음. 화원읍 일대는 대상·대조 동 모두 1끼로 시킬 가게가 적어 구 단위 가격 장벽(시범 B, 탐색).\n"
                "북구 검단동·학정동, 논공 금포리는 배달 자체가 적거나 오래 걸리는 배달형(시범 A). "
                "배달형 4곳 중 화원 본리리는 시범 B 지역 안이라 두 처방이 겹쳐 B로 평가한다.\n"
                "지묘동은 여러 이유가 걸리지만 옆 동네에서 주문하는 곳이라 해결방안 대상에서 뺐다.")


# ---- 20. 해결방안 표 ------------------------------------------------------------------------------
def s20(d, sl):
    frame(d, sl, 6, "해결방안: 유형별 조치", "담당·조치·확인 지표를 판정 유형에 고정", 20,
          "배달비 지원: 매일신문 2024-02-29 · 유형 설계: 점검표 설계 docs/topics/T2_checkup_tool.md §6")
    rows = [["유형", "걸린 이유", "담당", "조치", "확인 지표", "이번 분석"],
            ["배달형", "배달", "운영사", "방학 정기 배달편(점심·저녁 묶음), 배달 가능 급식 가게 우선 노출", "방학 결제, 배달 시간", "4곳"],
            ["가격형", "1끼 값", "대구시·구\n+ 운영사", "최소주문 면제 가게·1만 원 이하 1인 메뉴 확대, 앱 목록 면제 표시",
             "1끼 가능 가게 수, 신규 이용자 수", "공통 장벽 5곳"],
            ["공급형", "가게", "운영사", "쉬는 등록 가게 다시 살리기, 가맹점 모집(공급 점검 순서)", "주문받는 가게 수", "판단 불가"],
            ["안내형", "안내·신청", "구청", "방학 전 보호자·아이 모두에게 안내, 신청 끼니 점검", "신청 유형 비중", "자료 없음"],
            ["확인 필요", "판단 불가", "구청", "현장 확인 질문지 → 다음 회차 판정", "다음 회차 유형", "3곳"],
            ["사각지대 아님", "옆 동네·필요", "없음", "조치 없음, 다음 회차 관찰", "이동표, 대상 아동 수", "10곳"]]
    d.table(sl, X0, TOP, [170, 150, 140, 560, 300, 188], rows, row_h=96, head_h=46, size=18,
            aligns=["l", "l", "l", "l", "l", "c"], bolds=lambda r, c: c in (0, 5),
            colors=lambda r, c: AMBER if (r == 1 and c in (0, 5)) else INK)
    d.text(sl, X0, BOT - 102, W, 30,
           "배달형: 배달비는 이미 지원 중(누적 약 6천 명·2억 7천만 원) → 쟁점은 비용이 아니라 배달이 오느냐",
           size=16, color=MUTED)
    d.text(sl, X0, BOT - 64, W, 50,
           "안내형: 이용자 약 3분의 1이 10대(4차 11% 표본, 참고) → 안내 대상은 보호자와 아이 모두 · 공급형은 4차 결함으로 이번 회차 판정 불가",
           size=16, color=MUTED, lsp=1.35)
    d.notes(sl, "해결방안은 판정 유형에 고정한다. 배달형은 운영사가 방학 정기 배달편으로, 가격형은 시·구와 운영사가 면제 가게와 1인 메뉴로.\n"
                "배달비는 이미 지원 중이라 배달형의 문제는 비용이 아니라 배달이 오느냐다.\n"
                "사각지대가 아닌 10곳은 조치하지 않고 다음 회차에 관찰한다.")


# ---- 21. 시나리오 ------------------------------------------------------------------------------
def s21(d, sl):
    frame(d, sl, 6, "해결방안: 기대효과", "진짜 공백은 작고 몇 곳에 있어, 큰 사업 대신 판정한 곳에 정확히", 21,
          "시나리오 코드 85·80 · 기대 이용 모형: 동네 묶음 70곳, R² 0.746 · 이용자 수는 아동 수와 다름")
    rows = load("scenario")
    cw = 940
    head(d, sl, X0, TOP, 700, "늘어나는 방학 월 이용자 수 (하한~상한)", size=20)
    d.text(sl, X0, TOP + 32, cw, 26, "단위: 방학 한 달 이용자 수(대구 월평균 3,785명) · 가정 아래 계산이라 진단 결과와 분리",
           size=16, color=MUTED)
    gx, gw = X0 + 380, cw - 380 - 110
    vmax = 170
    top = TOP + 80
    rh = (BOT - TOP - 130) / len(rows)
    for t in (0, 50, 100, 150):
        xx = gx + gw * t / vmax
        d.line(sl, xx, top - 10, xx, top + rh * len(rows), color=HAIR, w=1)
        d.text(sl, xx - 30, top + rh * len(rows) + 6, 60, 22, str(t), size=14, color=MUTED, align="c")
    for i, r in enumerate(rows):
        y = top + i * rh
        ref = r["option"].startswith("참고")
        grp_b = r["group"].startswith("B")
        col = mix(NAVY, 0.18) if ref else (AMBER if grp_b and "상한" not in r["group"] else
                                           UNDEC if "상한" in r["group"] else mix(NAVY, 0.3))
        d.text(sl, X0, y + 8, 360, 60, r["option"], size=18, color=INK2 if ref else INK, bold=not ref, lsp=1.2)
        lo, hi = r["lo"], r["hi"]
        x0 = gx + gw * lo / vmax
        w = max(6, gw * (hi - lo) / vmax)
        d.shape(sl, "rect", x0, y + 16, w, 22, fill=col, line=None)
        lab = f"{hi:g}" if lo == hi else f"{lo:g}~{hi:g}"
        d.text(sl, x0 + w + 10, y + 12, 130, 30, lab, size=18, color=INK, bold=True)
        if i == 2:
            hline(d, sl, X0, X0 + cw, y + rh - 4)
    vline(d, sl, X0 + cw + 30, TOP, BOT)
    rx = X0 + cw + 60
    rw = X1 - rx
    vals = {g["kind"]: g["gap"] for g in load("gap")}
    total = sum(vals.values())
    excl = vals["exclude_need"] + vals["exclude_nb"]
    kicker(d, sl, rx, TOP, rw, "진짜 공백은 작음")
    d.text(sl, rx, TOP + 34, rw, 30, f"우선 점검 17곳 겉보기 부족분 월 {total:,.0f}건 중", size=18, color=INK2)
    d.title_text(sl, rx, TOP + 70, 200, 80, f"{vals['confirmed']:,.0f}건", size=64, color=AMBER)
    d.text(sl, rx + 170, TOP + 96, rw - 170, 40, "= 판정으로 확정한 공백(개선 대상 4곳)", size=18, color=INK, bold=True)
    d.text(sl, rx, TOP + 160, rw, 30, f"사각지대 아님 {excl:,.0f}건({excl / total:.0%}) · 확인 필요 {vals['undecided']:,.0f}건",
           size=17, color=INK2)
    hline(d, sl, rx, X1, TOP + 214)
    kicker(d, sl, rx, TOP + 238, rw, "그 동네에선 1.6~2.1배")
    d.title_text(sl, rx, TOP + 272, rw, 60, "10명 → 16~22명", size=40, color=INK)
    d.text(sl, rx, TOP + 334, rw, 120,
           "개선 대상 4곳 방학 월 이용자\v기대 이용의 50~100% 회복 시 {ab:+57~114%}\v"
           "다른 기대 모형으로는 최대 +26.7~40.8명\v(주 모형이 가장 작게 잡음)", size=17, color=INK2, lsp=1.35)
    hline(d, sl, rx, X1, TOP + 466)
    kicker(d, sl, rx, TOP + 490, rw, "헛수고를 막는 효과")
    d.text(sl, rx, TOP + 524, rw, 70, "판정 없이 17곳 전체에 사업하면\v부족분의 약 3분의 2를 사각지대 아닌 곳에서 추적",
           size=18, color=INK, bold=True, lsp=1.35)
    d.text(sl, rx, TOP + 602, rw, 90, "가게 모집은 0명 → 큰 사업 대신 매 방학 같은 로그로 다시 판정\v(점검표 · 회차당 1~2인일 추정, 22쪽)",
           size=17, color=INK2, lsp=1.35)
    d.notes(sl, "숫자가 작은 것이 결론이다. 같은 단위(방학 한 달 이용자 수)로 비교했다.\n"
                "가게를 더 모으는 사업은 0명(가장 후한 가정에서도 35명). 우선 점검 17곳의 겉보기 부족분 월 1,337건 중 "
                "판정으로 확정한 공백은 개선 대상 4곳의 98건뿐이고, 870건(65%)은 사각지대가 아닌 곳의 몫, 369건은 확인 필요다.\n"
                "그 4곳만 보면 방학 월 이용자가 약 10명에서 16~22명으로 는다(+5.9~11.8명, +57~114%). 기대 이용을 가장 작게 잡는 "
                "주 모형 기준이고, 다른 모형(가까운 10개 단위, 일반 배달 뺀 모형)으로는 최대 +26.7~40.8명이다.\n"
                "판정 없이 17곳 전체에 사업하면 부족분의 약 3분의 2를 사각지대가 아닌 곳에서 쫓게 된다. "
                "그래서 큰 사업 대신 매 방학 같은 로그로 다시 판정해 몇 곳에 정확히 쓰는 점검표를 제안한다.")


# ---- 22. 점검표·로드맵 ---------------------------------------------------------------------------
def s22(d, sl):
    frame(d, sl, 6, "해결방안: 점검표 제도화", "운영사 재공모 협약에 ‘방학 급식 사각지대 점검표’ 제출 조항을 넣음", 22,
          "점검표 docs/topics/T2_checkup_tool.md · 시범 docs/topics/T2_pilot_design.md · 일정과 시범 지역은 제안")
    lw = 700
    d.text(sl, X0, TOP, lw, 30, "점검 절차 · 매 방학 종료 후 30일 이내", size=20, color=INK, bold=True)
    steps = [["단계", "할 일", "내용"],
             ["0", "자료 점검(자동)", "4차 실제 오류 5종을 점검 항목화: 합계 대조, 기간, 취소율, 코드 연결, 가림"],
             ["1", "덜 쓰는 동", "회차 문턱 + 첫 회 문턱 고정(개선 추적), 지속성 표시"],
             ["2", "이유 7가지 판정", "판정 규칙(D-019) 그대로, 가린 칸 두 번 판정"],
             ["3", "유형·담당 배정", "운영사·구청·시 (20쪽 해결방안 표)"],
             ["4", "추적", "다음 회차 지표로 효과 확인"]]
    d.table(sl, X0, TOP + 44, [70, 190, lw - 260], steps, row_h=62, head_h=44, size=17, head_size=15,
            aligns=["c", "l", "l"], bolds=lambda r, c: c in (0, 1), colors=lambda r, c: AMBER if c == 0 else INK)
    y2 = TOP + 430
    hline(d, sl, X0, X0 + lw, y2)
    kicker(d, sl, X0, y2 + 24, lw, "협약 조항안")
    d.text(sl, X0, y2 + 60, lw, 210,
           "“운영자는 매 방학 종료 후 30일 이내에 ‘방학 급식 사각지대 점검표’(법정동별 이용 지표, 이유 판정, 개선 대상)를 작성하여 시에 제출한다. "
           "공개본은 동 단위 집계로 작성하며 5건 미만 칸은 가린다.”", size=18, color=INK, lsp=1.42)
    d.text(sl, X0, y2 + 220, lw, 30, "+ 협약 종료 시 동 단위 집계 인계 조항 · 이번 분석(0회차) = 첫 기준선", size=16, color=INK2,
           bold=True)
    d.text(sl, X0, y2 + 262, lw, 56, "시점: 현 운영사 협약 2026-12 종료 · 새 운영사 2027-01부터 3년\v"
           "(공모 10/12~11/10, 아이뉴스24 2026-10-11)", size=16, color=MUTED, lsp=1.35)
    vline(d, sl, X0 + lw + 40, TOP, BOT)
    rx = X0 + lw + 80
    rw = X1 - rx
    d.text(sl, rx, TOP, rw, 30, "로드맵", size=20, color=INK, bold=True)
    tl = [["시점", "할 일"], ["2026-11", "협약 조항"], ["2027-01·02", "시범 전 기준 측정"], ["2027-03", "1회차 점검표"],
          ["2027-08~", "시범 1년차"], ["2028-03", "중간 판정"], ["2029-03", "최종 판정"]]
    d.table(sl, rx, TOP + 44, [180, rw - 180], tl, row_h=38, head_h=40, size=16, head_size=15,
            bolds=lambda r, c: c == 0, colors=lambda r, c: AMBER if (r in (1, 3, 6) and c == 0) else INK)
    d.text(sl, rx, TOP + 322, rw, 30, "2027-04~07 준비: 정기 배달편 설계 · 화원읍 면제·1인 메뉴 가게 모집 · 목록 면제 표시", size=16,
           color=MUTED, lsp=1.3)
    y3 = TOP + 380
    hline(d, sl, rx, X1, y3)
    kicker(d, sl, rx, y3 + 22, 200, "시범 A · 배달형")
    d.text(sl, rx + 160, y3 + 20, rw - 160, 30, "북구 학정동·검단동, 논공 금포리", size=19, color=INK, bold=True)
    rows = [["판정 기간", "구별 가능한 최소 증가", "기대 증가(시나리오 B)"], ["방학 3개월(1년)", "+75%", "+47~95%"],
            ["방학 6개월(2년)", "+49%", "+47~95%"]]
    d.table(sl, rx, y3 + 64, [240, 250, rw - 490], rows, row_h=42, head_h=40, size=17, head_size=15,
            aligns=["l", "c", "c"], bolds=lambda r, c: c == 1)
    d.text(sl, rx, y3 + 198, rw, 60, "자연 변동(반기 표준편차 0.200, 약 238건) 기준 → 처음부터 2년 판정 설계 · 시범 B(화원읍, 배달형 본리리 포함)는 가격형 탐색",
           size=16, color=INK2, lsp=1.3)
    y4 = y3 + 270
    hline(d, sl, rx, X1, y4)
    d.text(sl, rx, y4 + 20, rw, 30, "비용 · 확산", size=19, color=INK, bold=True)
    d.text(sl, rx, y4 + 56, rw, 80,
           "새 자료 수집 없음 · 집계표 → 판정·시나리오·지도 노트북 PC 약 1분 · 회차당 1~2인일(추정)\n급식카드 + 공공배달앱을 쓰는 다른 지자체 · 매장 결제 결합 시 앱 밖 이용까지",
           size=16, color=INK2, lsp=1.4)
    d.notes(sl, "실행. 현 운영사 협약이 2026년 말 끝나고 새 운영사가 2027년부터 3년 운영한다. 협약에 점검표 제출 한 줄을 넣자.\n"
                "매 방학 끝나고 30일 안에 같은 로그로 덜 쓰는 동, 이유, 개선 대상을 뽑아 시에 낸다.\n"
                "시범 A(배달형 3곳)는 효과가 작을 수 있어 처음부터 2년 판정으로 설계했다.")


# ---- 23. 한계 ----------------------------------------------------------------------------------
def s23(d, sl):
    frame(d, sl, 7, "한계와 대응", "지표는 배달 경로 접근성의 하한이고, 판단 불가와 사후 개정은 숨기지 않고 기록", 23,
          "설계서 §7.1 주장 범위 한정 · 결정 기록 D-019 · 4차 결함 처리 docs/topics/T2_export_1016_results.md")
    rows = [["한계", "대응"],
            ["대구로는 사용처 중 하나: 편의점·일반음식점 매장 결제는 미관측",
             "지표 = 배달 경로 접근성의 하한 · 기대효과는 ‘식당 한 끼로 가는 경로 회복’으로 한정 · 운영 회차에서 시 보유 매장 결제 결합"],
            ["덜 쓰는 동의 편의점 대체 가능성: ‘다른 경로’ 이유(지역아동센터 정원)로 미포착", "‘다른 경로’는 ‘?’로 유지, 판정 근거로 쓰지 않음"],
            ["결제 위치는 아이 집이 아님", "옆 동네 이용 판정으로 보정 · 4차 이동표 결함 → 이웃 동 비교(약)로 대체"],
            ["필요 = 성인(30·40대) 소득 대리", "‘간접’ 근거로 표시 · 운영 회차에서 동별 급식카드 대상 아동 수로 교체"],
            ["배달형 판정은 부분 설명",
             "배달 여건은 아동 수 대비 이용이 적은 이유만 설명(일반 배달도 함께 줄어 급식 비중 지수는 설명 못 함) · 시범 A로 확인"],
            ["앱 점검 = 2026-10 화면", "2026년 단가(1만 원) 기준 ‘지금 남은 장벽’으로만 해석"],
            ["본인이 더 낸 돈은 안 보임", "금액은 카드 승인액 · 주문 합계 분포로 간접 확인(3만 원에서 끊김) · 운영 회차에서 ‘카드 + 다른 결제’ 비율 확인"],
            ["이용자 수는 아동 수와 다름", "효과 단위 = 방학 한 달 이용자 수 · 이용자 = 대구로 앱 회원(형제 카드 합산·보호자 명의 가능)"],
            ["4차 반출 결함 3건", "미리 정한 대체 규칙으로 판정 · 가게 이유는 전부 판단 불가 · 재반출 시 수정 목록(약 1시간) 보유"],
            ["결과 확인 후 바꾼 규칙 2건", "개정 전 판정 함께 공개(9쪽)"]]
    d.table(sl, X0, TOP, [620, W - 620], rows, row_h=72, head_h=46, size=18, bolds=lambda r, c: c == 0,
            colors=lambda r, c: AMBER if (r <= 2 and c == 0) else INK)
    d.notes(sl, "한계. 가장 큰 것은 대구로가 급식카드 사용처 중 하나라는 점. 편의점·일반음식점 매장 결제는 보지 못했다.\n"
                "그래서 지표는 배달 경로 접근성의 하한이고, 기대효과는 결식 감소가 아니라 식당 한 끼로 가는 경로 회복으로 말한다.\n"
                "배달형 4곳의 배달 여건은 아동 수 대비 이용이 적은 이유는 설명하지만, 배달이 나쁘면 일반 배달도 함께 줄어 "
                "급식 비중 지수가 낮은 이유까지는 설명하지 못한다. 그래서 판정 규칙대로 ‘부분 설명’으로 두고 시범 A로 확인한다.\n"
                "판단 불가와 사후 개정은 숨기지 않고 기록했다.")


# ---- 24~30. 부록 -------------------------------------------------------------------------------
def s24(d, sl):
    frame(d, sl, 8, "부록 1: 활용 데이터", "미개방 4종·공개 3종·현장 확인을 가맹점 법정동과 행정동으로 연결", 24)
    src = load("sources")
    rows = [["구분", "데이터", "제공", "기간", "단위", "쓰임"]] + [
        [r["kind"], r["data"], r["provider"], r["period"].replace(" 월별", "\n월별"), r["unit"], r["use"]] for r in src]
    d.table(sl, X0, TOP, [190, 220, 300, 200, 220, W - 1130], rows, row_h=84, head_h=46, size=17,
            bolds=lambda r, c: c in (0, 1), colors=lambda r, c: AMBER if (c == 0 and rows[r][0] == "미개방 상호제공") else INK)
    d.notes(sl, "부록 1. 활용 데이터 목록. 미개방 상호제공은 대구로 플랫폼(결제·가맹점·배달·고객)과 KCB 소득.\n"
                "공개는 인구, 대응표, 경계. 현장은 구청·시청 확인과 앱 점검.")


def s25(d, sl):
    frame(d, sl, 8, "부록 2: 방문과 반출", "데이터안심구역 방문 4회·반출 4회의 기록과 4차 결함 처리", 25,
          "반출 가림: 결제 5건·고객 5명·가맹점 3곳 미만 + 역산 칸 보완 가림 · 반출 전 자동 검사")
    vs = load("visits")
    rows = [["회차", "날짜", "한 일", "반출물", "발견"]] + [[v["step"], v["date"], v["did"], v["got"], v["found"]] for v in vs]
    d.table(sl, X0, TOP, [130, 200, 330, 330, W - 990], rows, row_h=58, head_h=44, size=15, head_size=14,
            bolds=lambda r, c: c == 0, colors=lambda r, c: INK2 if rows[r][0] == "현장 확인" else INK)
    y = TOP + 44 + 58 * (len(rows) - 1) + 40
    d.text(sl, X0, y, W, 30, "4차 반출 결함 3건과 처리 (현장 손입력 오류 · 미리 정한 대체 규칙)", size=19, color=INK, bold=True)
    df = load("defects")
    rows2 = [["항목", "원인", "영향", "처리"]] + [[r["item"], r["what"], r["hit"], r["handled"]] for r in df]
    d.table(sl, X0, y + 44, [190, 420, 420, W - 1030], rows2, row_h=58, head_h=44, size=14, head_size=14,
            bolds=lambda r, c: c == 0)
    d.text(sl, X0, y + 44 + 44 + 58 * (len(rows2) - 1) + 24, W, 30,
           "반출물 폴더 9_11 · 9_18 · 10_2 · 10_16: 회차별 반출 파일과 노트북", size=16, color=MUTED)
    d.notes(sl, "부록 2. 방문은 9월 11일, 9월 18일, 10월 2일, 10월 16일 네 번. 반출도 네 번.\n"
                "4차 반출에는 현장 손입력 오류 3건이 있었고, 미리 정한 대체 규칙으로 처리했다.")


def s26(d, sl):
    frame(d, sl, 8, "부록 3: 센터 안 코드", "급식 정의·반출 전 가림·자동 검사, 현장 손입력 오류도 점검 항목으로", 26,
          "전체 셀: 4차 방문 입력 코드 인쇄본 docs/report/T2_4차_입력코드.html · 반출 노트북 함께 제출")
    code1 = ("for ch in pd.read_csv(PAY, usecols=[...], dtype=str,\n"
             "                      chunksize=1_000_000):\n"
             "    ch = ch.apply(lambda s: s.str.strip())\n"
             "    mr.append(ch[(ch[C_GBN].isin(MEAL)) &\n"
             "                 (ch[C_STAT] == DONE)])\n"
             "m = pd.concat(mr)\n"
             "m = m[(m.ym >= \"202306\") & (m.ym <= \"202506\")]\n"
             "# 4차 현장: mr.append 줄이 for 밖으로 → 11%만 집계")
    code2 = ("gd[gd < 5] = np.nan\n"
             "gd.loc[gd.isna().any(axis=1)] = np.nan   # 한 칸 가리면 동 전체\n\n"
             "for f in sorted(glob.glob(\"EXPORT_v4_*.csv\")):\n"
             "    e = pd.read_csv(f, encoding=\"utf-8-sig\")\n"
             "    low = int((e[cols] < lim).sum().sum())\n"
             "    print(\"통과\" if low == 0 else \"※ 억제 누락\", low, f)")
    lw = 740
    rx = X0 + lw + 60
    rw = X1 - rx
    b1 = code_block(d, sl, X0, TOP, lw, "급식 결제 정의", code1)
    b2 = code_block(d, sl, rx, TOP, rw, "반출 전 가림 · 자동 검사", code2,
                    note="자동 검사: 저장한 파일을 다시 읽어 5 미만 칸을 셈 → ‘통과’ 파일만 반출 신청")
    y = max(b1, b2) + 40
    vline(d, sl, X0 + lw + 30, TOP, y + 200)
    hline(d, sl, X0, X0 + lw, y)
    kicker(d, sl, X0, y + 24, lw, "4차 현장 오류")
    d.text(sl, X0, y + 60, lw, 200,
           "mr.append(...)가 for 밖으로 나가 마지막 덩어리만 집계 → 38,854건(11%)\n→ 점검표 0단계 ‘급식 결제 합 = 원장 합’으로 차단",
           size=17, color=INK, lsp=1.42)
    hline(d, sl, rx, X1, y)
    kicker(d, sl, rx, y + 24, rw, "4차 자동 검사 결과", color=INK)
    bullets(d, sl, rx, y + 62, rw, 220,
            ["CSV 11개 모두 ‘통과’ (5 미만 칸 0)", "노트북 출력의 가림 전 표 2건은 반출됨 → 그 값은 인용하지 않음",
             "→ 점검표 0단계에 ‘출력에 가림 전 표 없음’ 추가"], size=17, after=8)
    d.notes(sl, "부록 3. 센터 안에서 실행한 코드. 급식 결제 정의와 반출 전 가림·자동 검사.\n"
                "4차 현장에서 급식 결제 정의 코드 한 줄 들여쓰기 오류가 있었고, 이를 점검표의 자동 점검 항목으로 바꿨다.")


def s27(d, sl):
    frame(d, sl, 8, "부록 4: 센터 밖 코드", "반출 집계에서 판정표·시나리오·지도까지, 노트북에서 1분 안에 다시 계산", 27,
          "가짜 자료로 전 과정 회귀 점검 · 코드와 결정은 버전 기록(git)")
    nodes = [("10", "군구 아동 대비", "구별 이용"), ("20", "행정동 아동", "144곳 · 25개월"), ("30", "행정동·법정동", "동네 묶음 71곳"),
             ("40", "동네 지표·진단", "후보 37 · 우선 점검 17"), ("50·55", "지도·군집", "Moran’s I · LISA"), ("70", "이웃 점검", "옆 동네 판정"),
             ("80", "공급 점검(MCLP)", "공급 기준선·후보"), ("85", "시나리오 B", "가게 대 이용 회복"), ("90", "판정표", "이유 7가지"),
             ("95", "앱 점검 기록", "1끼 가능 가게"), ("97", "점검표 지도", "첫 회 시안"), ("98", "팀 대시보드", "공유 자료")]
    hl = {"80", "85", "90"}
    half = (W - 60) / 2
    for k in range(2):
        rows = [["코드", "단계", "출력"]] + [list(n) for n in nodes[k * 6:(k + 1) * 6]]
        d.table(sl, X0 + k * (half + 60), TOP, [110, 300, half - 410], rows, row_h=62, head_h=44, size=18, head_size=15,
                fonts=lambda r, c: TITLE_FONT if c == 0 else None, sizes=lambda r, c: 24 if c == 0 else 18,
                colors=lambda r, c, rows=rows: AMBER if (c == 0 and rows[r][0] in hl) else (MUTED if c == 2 else INK),
                bolds=lambda r, c: c == 1)
    vline(d, sl, X0 + half + 30, TOP, TOP + 44 + 6 * 62)
    y = TOP + 470
    hline(d, sl, X0, X1, y)
    d.text(sl, X0, y + 24, W, 30, "입력과 출력", size=19, color=INK, bold=True)
    d.text(sl, X0, y + 62, W, 80,
           "입력: 반출 집계 CSV(가림 적용) + 공개 인구·대응표·경계 + 앱 점검 기록 → 출력: 판정표(공개본 = 기호·유형만), 시나리오 표, 지도, 대시보드 자료\v"
           "실행 시간(노트북 PC): 판정 11초 · 공급 점검 약 30초 · 시나리오 약 6초 · 지도 5초 · 코드 analysis/outside/10~98",
           size=17, color=INK2, lsp=1.4)
    hline(d, sl, X0, X1, y + 160)
    kicker(d, sl, X0, y + 184, W, "전 과정 공개")
    d.text(sl, X0, y + 220, W, 70,
           f"분석 코드 · 센터 입력 코드 · 결정 기록 · 반출 결과 문서 · 작업 기록 전체를 GitHub 저장소에 공개\v{GITHUB}",
           size=19, color=INK, bold=True, lsp=1.35, link=GITHUB_LINK)
    d.notes(sl, "부록 4. 센터 밖 분석 과정. 반출 집계에서 출발해 인구, 대응표, 진단, 지도·군집, 이웃 점검, 공급 점검, 시나리오, 판정표까지 번호 순서로 이어진다.\n"
                "집계 표에서 판정·시나리오·지도까지 노트북 PC로 약 1분. 코드와 문서, 작업 기록은 모두 GitHub에 공개.")


def s28(d, sl):
    frame(d, sl, 8, "부록 5: 판정 코드", "가려진 칸은 최솟값·최댓값으로 두 번 판정해 같을 때만 확정", 28)
    code = ("def judge_one(x, hit, ok, bad):\n"
            "    if pd.isna(x):\n"
            "        return \"?자료\"\n"
            "    if bad == \"low\":\n"
            "        return \"●\" if x <= hit else (\"○\" if x >= ok else \"?경계\")\n"
            "    return \"●\" if x >= hit else (\"○\" if x <= ok else \"?경계\")\n\n"
            "def merge2(a, b, conflict=\"?억제\"):\n"
            "    # 가린 칸을 0과 (가림 문턱 − 1)로 채운 두 판정\n"
            "    return a if a == b else conflict")
    lw = 860
    b = code_block(d, sl, X0, TOP, lw, "핵심 함수 (요약) · analysis/outside/90_reason_table.py · 판정 규칙 D-019", code)
    hline(d, sl, X0, X0 + lw, b + 30)
    d.text(sl, X0, b + 54, lw, 30, "이번 분석 결과: 우선 점검 17곳 · 이유별 판정 수", size=19, color=INK, bold=True)
    cnt = [["판정", "필요", "다른 경로", "가게", "1끼 값", "배달", "안내·신청", "옆 동네"],
           ["● 해당", 6, 0, 0, 2, 9, 0, 5], ["○ 아님", 6, 0, 0, 7, 2, 0, 9], ["? 경계", 4, 0, 0, 0, 6, 0, 3],
           ["? 면제 미확인", 0, 0, 0, 4, 0, 0, 0], ["? 가림", 1, 0, 0, 0, 0, 0, 0], ["? 자료 없음", 0, 17, 17, 4, 0, 17, 0]]
    d.table(sl, X0, b + 98, [160] + [100] * 7, cnt, row_h=40, head_h=40, size=15, head_size=14,
            aligns=["l"] + ["c"] * 7, colors=lambda r, c: (mix(NAVY, 0.3) if (c and cnt[r][c] == 0) else INK),
            bolds=lambda r, c: c == 0 or (c and cnt[r][c] != 0))
    vline(d, sl, X0 + lw + 30, TOP, BOT)
    rx = X0 + lw + 60
    rw = X1 - rx
    rules = [("1", "문턱", "대구 분포 하위 25%면 해당, 중앙값 반대편이면 아님, 사이는 경계(?)"),
             ("2", "가린 칸", "0과 (가림 문턱 − 1)로 채워 두 번 판정"),
             ("3", "확정", "두 판정이 같을 때만 확정, 다르면 판단 불가(? 가림)"),
             ("4", "묶기", "제외(옆 동네·필요 적음) → 개선 대상(가게·1끼 값·배달) → 남은 이유 추정(안내·신청) → 확인 필요")]
    y = TOP
    hh = (BOT - TOP) / len(rules)
    for i, (no, h_, body) in enumerate(rules):
        if i:
            hline(d, sl, rx, X1, y - 20)
        d.text(sl, rx, y, rw, 34, f"{{a:{no}}}  {h_}", size=22, color=INK, bold=True)
        d.text(sl, rx, y + 46, rw, hh - 70, body, size=18, color=INK2, lsp=1.4)
        y += hh
    d.notes(sl, "부록 5. 판정 코드의 핵심. 반출 자료에는 작은 칸이 가려져 있다.\n"
                "가린 칸을 가장 불리한 값과 가장 유리한 값으로 채워 두 번 판정하고, 두 판정이 같을 때만 확정한다.")


def s29(d, sl):
    frame(d, sl, 8, "부록 6: 분석 기술", "모든 출력은 가림을 적용한 집계에서 계산", 29)
    rows = [["기법", "용도", "설정"],
            ["입지계수(급식 비중 지수, LQ)", "일반 배달 대비 급식 비중", "방학 기준, 대구 평균 = 1, 분모 = 4차 동·시기별 일반 결제"],
            ["Moran’s I · LISA", "공간 군집(뭉침)", "KNN 6 / Queen, 9,999회 순열"],
            ["퍼지 인접", "이웃 동, 닿는 범위", "경계 틈 5m 허용"],
            ["MCLP 부분 커버 탐욕 선택", "공급 점검: 가게 활성화·모집 위치(시나리오 A)", "(1 − 1/e) 보장, 문턱 격자 1~50곳"],
            ["로그 선형 기대 모형", "비슷한 조건 동의 기대 이용(시나리오 B)", "자기 단위 빼고 예측, 동네 묶음 70곳, R² 0.746"],
            ["가린 칸 두 번 판정", "가림이 있어도 판정", "0과 (가림 문턱 − 1)"],
            ["반기 자연 변동", "시범 효과의 최소 구별 크기", "방학 앞·뒤 반기 d의 표준편차, 양측 5%·검정력 80% → 표준편차의 2.8배"],
            ["결합 단위(동네 묶음)", "행정동·법정동 불일치 해결", "연결 성분 71곳"]]
    d.table(sl, X0, TOP, [380, 480, W - 860], rows, row_h=84, head_h=46, size=18, bolds=lambda r, c: c == 0)
    d.text(sl, X0, TOP + 46 + 84 * (len(rows) - 1) + 20, W, 30, "도구: Python(pandas, geopandas, libpysal, esda)",
           size=16, color=MUTED)
    d.notes(sl, "부록 6. 분석 기술. 이용 비중은 입지계수, 공간 군집은 Moran과 LISA, 이웃은 퍼지 인접.\n"
                "시나리오는 MCLP 부분 커버 탐욕 선택과 로그 선형 기대 모형, 시범 판정은 반기 자연 변동으로 설계.")


def s30(d, sl):
    frame(d, sl, 8, "부록 7: 출처", "모든 숫자와 확인 사항의 출처를 부서·매체·날짜까지 기록", 30)
    # \v = 같은 항목 안 줄바꿈(글머리 없이 이어짐)
    cols = [("데이터", ["대구로 플랫폼 데이터: 결제·가맹점·배달·고객\v(경북대 첨단정보통신융합산업기술원, 상호제공)",
                        "행정동 단위 소득 관련 통계\v(한국데이터산업진흥원·KCB, 상호제공)",
                        "주민등록 연령별 인구현황 (행정안전부, 2023-06~2025-06)",
                        "행정동·법정동 대응표 (행정안전부, 2025-06-30 기준)",
                        "법정동·리 경계 (국가공간정보포털, 2026-09)"], 540),
            ("확인 기록", ["동구청 아동청소년과 전화 확인 (2026-10-08)\v신청 유형, 하루 한도",
                           "대구시청 복지과 문의 (2026-10-15)\v2026년 1끼 1만 원, 대구 공통",
                           "대구로 앱 점검 (팀, 2026-10-15)\v1인분 목록, 가게 상세 화면 · 기록 시각 보존"], 430),
            ("보도", ["경북매일 (2023-05-31)\v대구로 급식카드 배달 결제 6월 1일 시행",
                      "매일신문 (2024-02-29)\v대구로 급식 배달비 지원 누적",
                      "경북매일·아주경제 (2024-08-01)\v달성군 여름방학 아동급식 지원",
                      "아이뉴스24 (2026-10-11)\v대구로 운영사 재공모, 2027년부터 3년"], 418)]
    x = X0
    ch = 360
    for i, (h_, items, w) in enumerate(cols):
        if i:
            vline(d, sl, x - 30, TOP, TOP + ch)
        d.text(sl, x, TOP, w, 34, h_, size=23, color=INK, bold=True)
        bullets(d, sl, x, TOP + 52, w, ch - 52, items, size=18, after=14, lsp=1.4)
        x += w + 60
    y = TOP + ch + 50
    hline(d, sl, X0, X1, y)
    d.text(sl, X0, y + 24, 600, 32, "재현 자료 · 전 과정 GitHub 공개", size=21, color=INK, bold=True)
    d.text(sl, X1 - 900, y + 28, 900, 28, GITHUB, size=19, color=AMBER, bold=True, align="r", link=GITHUB_LINK)
    items = [("분석 코드", "analysis/outside/10~98 (Python)"), ("센터 입력 코드", "docs/report/T2_4차_입력코드.html"),
             ("결정 기록", "docs/DECISIONS.md (D-012~D-020)"), ("반출 결과", "docs/topics/T2_export_*_results.md (1~4차)")]
    cw = (W - 3 * 60) / 4
    for i, (k, v) in enumerate(items):
        cx = X0 + i * (cw + 60)
        if i:
            vline(d, sl, cx - 30, y + 80, y + 170)
        d.text(sl, cx, y + 84, cw, 28, k, size=17, color=INK, bold=True)
        d.text(sl, cx, y + 118, cw, 60, v, size=15, color=INK2, lsp=1.3)
    d.text(sl, X0, y + 200, W, 30, "분석 코드·센터 입력 코드·결정 기록·반출 결과 문서·작업 기록(git) 전체를 같은 저장소에 공개",
           size=17, color=INK2)
    d.notes(sl, "부록 7. 출처. 데이터 출처와 전화·문의 확인 기록, 보도, 앱 점검 일시.\n"
                "분석 코드·센터 입력 코드·결정 기록·반출 결과 문서·작업 기록 전체를 GitHub에 공개.")


SLIDES = {i: globals()[f"s{i:02d}"] for i in range(1, 31)}


def scrub_theme(path):
    """테마 효과 스타일에 남은 기본 검정 그림자색(#000000)을 브라운으로 바꾼다(도형에는 그림자를 쓰지 않음)."""
    import shutil
    import zipfile
    tmp = Path(str(path) + ".tmp")
    with zipfile.ZipFile(path) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
        for item in zi.infolist():
            data = zi.read(item.filename)
            if item.filename.startswith("ppt/theme/"):
                data = data.replace(b'srgbClr val="000000"', b'srgbClr val="' + NAVY.lstrip("#").encode() + b'"')
            zo.writestr(item, data)
    shutil.move(tmp, path)


def dash_check(path):
    """저장한 PPTX의 쪽 글자를 다시 읽어 줄표(—·–)가 남은 곳을 알린다(노트·코드 주석은 보지 않음)."""
    import re
    import zipfile
    with zipfile.ZipFile(path) as z:
        pages = {int(m.group(1)): n for n in z.namelist() if (m := re.match(r"ppt/slides/slide(\d+)\.xml$", n))}
        for p in sorted(pages):
            for t in re.findall(r"<a:t>([^<]*)</a:t>", z.read(pages[p]).decode("utf-8")):
                if "—" in t or "–" in t:
                    print("WARN", f"{p}쪽 줄표:", t[:40])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default=str(HERE / "T2_기획서_나무.pptx"))
    ap.add_argument("--png", default="")
    ap.add_argument("--pdf", action="store_true")
    a = ap.parse_args()
    only = [int(x) for x in a.only.split(",") if x] or sorted(SLIDES)
    d = Deck()
    try:
        for n in only:
            sl = d.slide()
            SLIDES[n](d, sl)
        png = Path(a.png) if a.png else None
        if png:
            png.mkdir(parents=True, exist_ok=True)
        d.save(Path(a.out), png)
        if a.pdf:
            d.pres.SaveAs(str(Path(a.out).with_suffix(".pdf")), 32)
        print("saved", a.out, "| slides", len(only))
        for w in WARN:
            print("WARN", w)
    finally:
        d.close()
    scrub_theme(Path(a.out))
    dash_check(Path(a.out))


if __name__ == "__main__":
    main()
