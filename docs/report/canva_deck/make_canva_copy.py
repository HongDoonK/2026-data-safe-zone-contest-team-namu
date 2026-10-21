"""캔바 가져오기용 PPTX 사본.

캔바는 PPTX를 가져올 때 브랜드 키트에 올린 글꼴을 쓰지 않는다. 라이브러리에 없는 글꼴(Pretendard, Suseong Dotum)은
전부 같은 대체 글꼴 하나로 바뀌어, 제목과 본문을 '모두 변경'으로 따로 되돌릴 수 없다(2026-10-20 확인).
사본에서는 네 글꼴 이름을 캔바 라이브러리에 있는 서로 다른 글꼴로 바꿔 둔다.
가져온 뒤 캔바에서 제목 하나 → Suseong Dotum → 모두 변경, 본문 하나 → Pretendard → 모두 변경,
머리글 소제목 하나(나눔명조로 보임) → Pretendard Medium → 모두 변경(2026-10-21 머리글 개정으로 추가).
PowerPoint·PDF는 원본(T2_기획서_나무.pptx)을 그대로 쓴다.

사용: python make_canva_copy.py
"""
import collections
import re
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "T2_기획서_나무.pptx"
DST = HERE / "T2_기획서_나무_캔바용.pptx"
FONT_MAP = {"Suseong Dotum": "Black Han Sans", "Pretendard": "Noto Sans KR", "Pretendard Medium": "Nanum Myeongjo",
            "Consolas": "Roboto Mono"}

count = collections.Counter()
with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(DST, "w", zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)
        if item.filename.endswith(".xml"):
            text = data.decode("utf-8")
            for old, new in FONT_MAP.items():
                pat = f'typeface="{old}"'
                count[old] += text.count(pat)
                text = text.replace(pat, f'typeface="{new}"')
            data = text.encode("utf-8")
        zout.writestr(item, data)

with zipfile.ZipFile(DST) as z:
    used = collections.Counter(f for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n)
                               for f in re.findall(r'typeface="([^"]+)"', z.read(n).decode("utf-8")))
print("바꾼 수:", dict(count))
print("사본 슬라이드의 글꼴:", dict(used))
print("→", DST.name)
