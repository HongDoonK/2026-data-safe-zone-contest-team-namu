"""PowerPoint COM으로 1920×1080(px) 슬라이드를 그리는 도구 모음. 좌표·크기는 px로 받아 pt(×0.75)로 바꾼다.

디자인 시스템(2026-10-20 팀 지정, 같은 날 웜 브라운 팔레트로 교체): 배경 #FAF8F5, 주색 #E63946(능금 레드),
보조 #F4A261(햇살 앰버), 글자·선 #2B2320(감영 브라운).
기존 이름은 역할 그대로 1:1 매핑해 둔다: NAVY→브라운, AMBER→레드, TEAL→앰버. 옛 경고색(CORAL)은 팔레트에서 빠져
경고·알림은 레드, ‘확인 필요’ 같은 범주는 브라운 중간 농도(UNDEC)로 쓴다. 옅은 색은 다섯 색의 투명도 변형만 쓴다.
제목·강조 수치 = 수성돋움체, 본문 = Pretendard.
레이아웃(같은 날 보고서형으로 개정): 카드·바탕 상자·칩·그림자 없음. 구분은 1px 선 rgba(43,35,32,.15)(HAIR)만,
강조는 글자 굵기·크기·레드로만. 표는 세로선·칸 바탕 없이 가로선만 쓴다.
"""
import re

import win32com.client as w32

PX = 0.75
TITLE_FONT = "Suseong Dotum"   # 수성돋움체(대구 수성구 전용서체). 글꼴 파일의 영문 이름 — 캔바·다른 PC에서도 같은 이름으로 잡힌다
BODY_FONT = "Pretendard"
HEAD_FONT = "Pretendard Medium"   # 머리글 소제목(핵심 메시지 한 줄). 정적 TTF라 가족 이름이 따로 있다
MONO_FONT = "Consolas"

BG, WHITE = "#FAF8F5", "#FFFFFF"
AMBER, TEAL, NAVY = "#E63946", "#F4A261", "#2B2320"      # 주색(레드) · 보조(앰버) · 글자·선(브라운)
CORAL = AMBER                                             # 경고·알림 = 주색 레드


def _hex(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def mix(color, alpha, base=WHITE):
    """color를 alpha 불투명도로 base 위에 얹은 색."""
    c, b = _hex(color), _hex(base)
    return "#%02X%02X%02X" % tuple(round(alpha * x + (1 - alpha) * y) for x, y in zip(c, b))


def rgb(h):
    r, g, b = _hex(h)
    return r + (g << 8) + (b << 16)


BORDER = mix(NAVY, 0.12)                 # 도형 기본 테두리
HAIR = mix(NAVY, 0.15, BG)               # 구분선 1px rgba(43,35,32,.15) — 영역 나눔·표의 행 사이
HEADRULE = mix(NAVY, 0.45, BG)           # 표 머리글 위아래 선(행 사이 선보다 한 단계 진하게)
INK = NAVY
INK2 = mix(NAVY, 0.78, BG)               # 본문 보조
MUTED = mix(NAVY, 0.55, BG)              # 설명·출처
FAINT = mix(NAVY, 0.30, BG)
UNDEC = mix(NAVY, 0.45)                  # ‘확인 필요’·판단 불가 범주
COLOR = {"a": AMBER, "t": TEAL, "c": CORAL, "n": NAVY, "m": MUTED, "w": WHITE, "i": INK2}
THEME = [NAVY, WHITE, NAVY, BG, AMBER, TEAL, UNDEC, mix(AMBER, 0.5), mix(TEAL, 0.5), mix(NAVY, 0.25), AMBER, NAVY]

MSO = dict(rect=1, rrect=5, oval=9, chevron=52, pentagon=51, rtri=8)


def est_w(text, size):
    """글자 폭 대략값(px). 한글 1.0, 영문·숫자 0.56, 공백 0.3, 기호 0.5 × 크기."""
    w = 0.0
    for ch in text:
        o = ord(ch)
        if 0xAC00 <= o <= 0xD7A3 or 0x3130 <= o <= 0x318F:
            w += 1.0
        elif ch == " ":
            w += 0.3
        elif ch.isdigit():
            w += 0.58
        elif ch.isascii() and ch.isalpha():
            w += 0.56
        else:
            w += 0.5
    return w * size


_MARK = re.compile(r"\*\*(.+?)\*\*|\{([atcnmwib]+):(.+?)\}")


def parse(text):
    """'**굵게**', '{a:주황}', '{ab:주황 굵게}' 표시를 풀어 (본문, [(시작, 길이, 꼴)])로."""
    out, spans, pos = [], [], 0
    for m in _MARK.finditer(text):
        out.append(text[pos:m.start()])
        start = sum(len(s) for s in out)
        if m.group(1) is not None:
            seg, flags = m.group(1), "b"
        else:
            flags, seg = m.group(2), m.group(3)
        out.append(seg)
        spans.append((start, len(seg), flags))
        pos = m.end()
    out.append(text[pos:])
    return "".join(out).replace("\n", "\r"), spans


class Deck:
    def __init__(self):
        self.app = w32.Dispatch("PowerPoint.Application")
        self.pres = self.app.Presentations.Add(WithWindow=0)
        self.pres.PageSetup.SlideWidth = 1920 * PX
        self.pres.PageSetup.SlideHeight = 1080 * PX
        for master in (self.pres.SlideMaster, self.pres.NotesMaster):   # 테마 기본색에서도 푸른색·검정 제거
            scheme = master.Theme.ThemeColorScheme
            for i, c in enumerate(THEME, 1):
                scheme.Colors(i).RGB = rgb(c)

    def slide(self):
        sl = self.pres.Slides.Add(self.pres.Slides.Count + 1, 12)   # ppLayoutBlank
        sl.FollowMasterBackground = 0
        sl.Background.Fill.Solid()
        sl.Background.Fill.ForeColor.RGB = rgb(BG)
        return sl

    # ---- 글자 -------------------------------------------------------------------------------
    @staticmethod
    def _style_runs(tr, size, color, font, bold, spans, legacy=None):
        """tr = TextRange2(전체 꼴), legacy = 옛 TextRange(부분 꼴: Characters는 옛 쪽만 동적 호출이 된다)."""
        f = tr.Font
        f.Name, f.NameFarEast, f.NameComplexScript = font, font, font
        f.Size = size * PX
        f.Bold = -1 if bold else 0
        f.Fill.Visible = -1
        f.Fill.Solid()
        f.Fill.ForeColor.RGB = rgb(color)
        for start, length, flags in spans:
            r = legacy.Characters(start + 1, length)
            for fl in flags:
                if fl == "b":
                    r.Font.Bold = -1
                elif fl in COLOR:
                    r.Font.Color.RGB = rgb(COLOR[fl])

    def text(self, sl, x, y, w, h, text, size=22, color=INK, font=BODY_FONT, bold=False, align="l",
             anchor="t", lsp=1.3, after=0, bullet=False, indent=22, name=None, raw=False, link=None):
        """link = (글자 안의 표시 문자열, 주소): 그 부분에 하이퍼링크(PDF에서도 눌림). 색은 테마 링크색(THEME 11번)."""
        s = sl.Shapes.AddTextbox(1, x * PX, y * PX, w * PX, h * PX)
        self._fill_text(s, text, size, color, font, bold, align, anchor, lsp, after, bullet, indent, raw)
        if link:
            sub, url = link
            i = s.TextFrame2.TextRange.Text.find(sub)
            if i >= 0:
                s.TextFrame.TextRange.Characters(i + 1, len(sub)).ActionSettings(1).Hyperlink.Address = url
        if name:
            s.Name = name
        return s

    def _fill_text(self, s, text, size, color, font, bold, align, anchor, lsp, after, bullet, indent, raw=False):
        tf = s.TextFrame2
        tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
        tf.WordWrap = -1
        tf.AutoSize = 0
        tf.VerticalAnchor = {"t": 1, "m": 3, "b": 4}[anchor]
        plain, spans = (text.replace("\n", "\r"), []) if raw else parse(text)
        tr = tf.TextRange
        tr.Text = plain
        self._style_runs(tr, size, color, font, bold, spans, s.TextFrame.TextRange)
        pf = tr.ParagraphFormat
        pf.Alignment = {"l": 1, "c": 2, "r": 3}[align]
        pf.LineRuleWithin = -1
        pf.SpaceWithin = lsp
        pf.SpaceAfter = after * PX
        pf.SpaceBefore = 0
        if bullet:
            pf.Bullet.Visible = -1
            pf.Bullet.Character = 8226
            pf.Bullet.Font.Fill.ForeColor.RGB = rgb(MUTED)
            pf.LeftIndent = indent * PX
            pf.FirstLineIndent = -indent * PX
        else:
            pf.Bullet.Visible = 0
            pf.LeftIndent = 0
            pf.FirstLineIndent = 0

    def title_text(self, sl, x, y, w, h, text, size=46, color=INK, align="l", anchor="t", lsp=1.12):
        # 수성돋움체는 Regular 한 굵기뿐이고 자체로 두꺼운 제목용이라, PowerPoint 가짜 굵게(번짐)를 쓰지 않는다
        return self.text(sl, x, y, w, h, text, size=size, color=color, font=TITLE_FONT, bold=False,
                         align=align, anchor=anchor, lsp=lsp)

    # ---- 도형 -------------------------------------------------------------------------------
    def shape(self, sl, kind, x, y, w, h, fill=WHITE, line=BORDER, lw=1.0, radius=10, dash=False, name=None):
        s = sl.Shapes.AddShape(MSO[kind], x * PX, y * PX, w * PX, h * PX)
        if kind == "rrect":
            s.Adjustments.SetItem(1, min(0.5, radius / max(1, min(w, h))))
        if fill is None:
            s.Fill.Visible = 0
        else:
            s.Fill.Visible = -1
            s.Fill.Solid()
            s.Fill.ForeColor.RGB = rgb(fill)
            s.Fill.Transparency = 0
        if line is None:
            s.Line.Visible = 0
        else:
            s.Line.Visible = -1
            s.Line.ForeColor.RGB = rgb(line)
            s.Line.Weight = lw * PX
            s.Line.DashStyle = 4 if dash else 1
        s.Shadow.Visible = 0
        tf = s.TextFrame2
        tf.MarginLeft = tf.MarginRight = tf.MarginTop = tf.MarginBottom = 0
        if name:
            s.Name = name
        return s

    def box_text(self, s, text, size=22, color=INK, font=BODY_FONT, bold=False, align="c", anchor="m",
                 lsp=1.2, pad=(0, 0, 0, 0)):
        """도형 안 글자(캔바에서 도형과 함께 움직인다)."""
        tf = s.TextFrame2
        tf.WordWrap = -1
        tf.AutoSize = 0
        tf.MarginLeft, tf.MarginTop, tf.MarginRight, tf.MarginBottom = (p * PX for p in pad)
        tf.VerticalAnchor = {"t": 1, "m": 3, "b": 4}[anchor]
        plain, spans = parse(text)
        tr = tf.TextRange
        tr.Text = plain
        self._style_runs(tr, size, color, font, bold, spans, s.TextFrame.TextRange)
        pf = tr.ParagraphFormat
        pf.Alignment = {"l": 1, "c": 2, "r": 3}[align]
        pf.LineRuleWithin = -1
        pf.SpaceWithin = lsp
        pf.SpaceAfter = 0
        pf.SpaceBefore = 0
        pf.Bullet.Visible = 0
        return s

    def line(self, sl, x1, y1, x2, y2, color=HAIR, w=1.0, dash=False, arrow=False):
        s = sl.Shapes.AddLine(x1 * PX, y1 * PX, x2 * PX, y2 * PX)
        s.Line.ForeColor.RGB = rgb(color)
        s.Line.Weight = w * PX
        s.Line.DashStyle = 4 if dash else 1
        if arrow:
            s.Line.EndArrowheadStyle = 2
            s.Line.EndArrowheadLength = 2
            s.Line.EndArrowheadWidth = 2
        return s

    def pic(self, sl, path, x, y, w=None, h=None):
        s = sl.Shapes.AddPicture(str(path), 0, -1, x * PX, y * PX)
        ar = s.Height / s.Width
        if w is not None:
            s.LockAspectRatio = -1
            s.Width = w * PX
        elif h is not None:
            s.LockAspectRatio = -1
            s.Height = h * PX
        return s, ar

    def notes(self, sl, text):
        sl.NotesPage.Shapes.Placeholders(2).TextFrame.TextRange.Text = text

    # ---- 표 ---------------------------------------------------------------------------------
    def table(self, sl, x, y, col_w, rows, row_h=44, head_h=None, head=True, size=19, head_size=16, aligns=None,
              colors=None, bolds=None, fonts=None, sizes=None, pad=14):
        """선만 쓰는 표: 칸 바탕·세로선 없음. 머리글 위아래 HEADRULE, 행 사이 HAIR. 바깥 양끝 칸은 바깥 여백 0(본문과 줄 맞춤).
        rows[0]이 머리글(head=True). colors/bolds/fonts/sizes: (r, c) -> 값 함수, r은 rows 기준 0부터(None이면 기본)."""
        nr, nc = len(rows), len(col_w)
        hh = head_h or row_h
        total = hh + (nr - 1) * row_h if head else nr * row_h
        s = sl.Shapes.AddTable(nr, nc, x * PX, y * PX, sum(col_w) * PX, total * PX)
        t = s.Table
        t.ApplyStyle("{2D5ABB26-0587-4C30-8999-92F81FD0307C}", False)   # No Style, No Grid
        t.FirstRow = 0
        t.HorizBanding = 0
        for c, cw in enumerate(col_w, 1):
            t.Columns(c).Width = cw * PX
        for r in range(1, nr + 1):
            is_head = head and r == 1
            t.Rows(r).Height = (hh if is_head else row_h) * PX
            for c in range(1, nc + 1):
                cell = t.Cell(r, c)
                sh = cell.Shape
                sh.Fill.Visible = 0
                sides = [(3, HEADRULE if is_head else HAIR)] + ([(1, HEADRULE)] if is_head else [])   # 3 아래, 1 위
                for side, color in sides:
                    bd = cell.Borders(side)
                    bd.Visible = -1
                    bd.ForeColor.RGB = rgb(color)
                    bd.Weight = 1 * PX
                tf = sh.TextFrame2
                tf.MarginLeft = (0 if c == 1 else pad) * PX
                tf.MarginRight = (0 if c == nc else pad) * PX
                tf.MarginTop = tf.MarginBottom = 4 * PX
                tf.VerticalAnchor = 3
                ri, ci = r - 1, c - 1
                plain, spans = parse(str(rows[ri][ci]))
                tr = tf.TextRange
                tr.Text = plain
                if is_head:
                    col, bold, font, sz = INK2, True, BODY_FONT, head_size
                else:
                    col = (colors(ri, ci) if colors else None) or INK
                    bold = bool(bolds(ri, ci)) if bolds else False
                    font = (fonts(ri, ci) if fonts else None) or BODY_FONT
                    sz = (sizes(ri, ci) if sizes else None) or size
                self._style_runs(tr, sz, col, font, bold, spans, sh.TextFrame.TextRange)
                pf = tr.ParagraphFormat
                pf.Alignment = {"l": 1, "c": 2, "r": 3}[aligns[ci] if aligns else "l"]
                pf.LineRuleWithin = -1
                pf.SpaceWithin = 1.15
        return s

    # ---- 저장 -------------------------------------------------------------------------------
    def save(self, path, png_dir=None, png_w=1600):
        self.pres.SaveAs(str(path))
        if png_dir:
            for i in range(1, self.pres.Slides.Count + 1):
                self.pres.Slides(i).Export(str(png_dir / f"s{i:02d}.png"), "PNG", png_w, int(png_w * 1080 / 1920))

    def close(self):
        self.pres.Close()
