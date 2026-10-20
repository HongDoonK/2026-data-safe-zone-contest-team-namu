"""팀 대시보드 Artifact(https://claude.ai/artifact/WDeywrTBi5jcg3Ec7v31zc)에 쓸 문서를 만든다.

입력: 같은 폴더 index.html, ../out_dashboard/*.json 을 올린 자리(BLOB)
출력: store/ 아래 dash_meta.json, datasets_<id>.json, files_index.json  → ArtifactData batch 의 file_path 로 쓴다.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "store"
OUT.mkdir(exist_ok=True)
AT = datetime.now(timezone.utc).isoformat(timespec="seconds")
BY = "Claude (팀 공유용 정리)"

BLOB = {
    "facts": "f62d420589a4f65e6b065380bf51d628", "monthly": "3e75bf48b8f9654b869160588a6bd594",
    "hourly": "a951bda90709b5d4702327716bdbb565", "gu": "db45510e5d91ad55cd8c6799f0e6ac9a",
    "visits": "175e26a44699a4c1d97ba5743f7bdb4b", "sources": "4b5861093cb3bcca65d6cbeb9a03e680",
    "defects": "a8da92f0d1bc9de684910597af95be89", "funnel": "a67287a5541ebd2c9921cb42218dd8dc",
    "reasons": "5f858399e12494fe7e00e79004ba7ef7", "targets": "ab653f025c13740169972629d8e599ac",
    "gap": "224ffa85910a05e671036cb4b13fa3ef", "scenario": "8b39750b7e17016f7e49de628d490940",
    "daycount": "84a73f5cfa82b930c0e682be02e825d5", "maxday": "cc2f1afc31988be986c3a4ed4064ed68",
    "variation": "0954318d85870bb2b2f43aef3aa14964", "mde": "4301c96c87bee166419e7122878771dd",
    "pilot": "aebc6272aa9298e13762e314ef7ddb72", "solutions": "05d40bc1ba1d2d631cd797b4d47a1e17",
    "glossary": "dc2e59ba99577e90ebaa894d2d46d5f0", "geo": "ac1465feee3f7b3fa953215090f6b856",
}
META = {
    "facts": ("핵심 수치 모음", "본문과 카드에 쓰는 낱개 수치. 행마다 source 열에 출처(반출 파일, 결과 문서, 문의·보도)가 있다. 동 단위 지표 값은 넣지 않았다."),
    "monthly": ("월별 급식·일반 결제", "2차 반출 EXPORT_m2_month_group.csv(2026-09-18 방문). 급식 = 아동급식카드 · 결제 완료, 일반 = 승인 시각이 있는 그 밖의 완료 결제. 2023-06~2025-06."),
    "hourly": ("시간대별 급식·일반 결제", "2차 반출 EXPORT_m2_hour_edge_meal.csv(급식)와 EXPORT_m2_general_regime_dow_hour.csv(일반)를 시간대별로 합친 값. 23~05시는 한 칸."),
    "gu": ("구별 아이 1천 명당 결제", "3차 반출 동×시기 결제(우리 규칙으로 다시 가린 본)를 구로 합쳐 주민등록 6~18세로 나눈 값(analysis/outside/out/gungu_per_child.csv). 결제는 가게 위치 기준."),
    "visits": ("방문·반출 기록", "팀 방문 기록과 반출 결과 문서(docs/topics/T2_export_*.md) 요약."),
    "sources": ("활용 데이터 목록", "기획서 증빙의 데이터 목록과 같은 내용."),
    "defects": ("4차 반출 결함과 처리", "4차 반출 노트북과 CSV 대조 결과(docs/topics/T2_export_1016_results.md §1·§3)."),
    "funnel": ("동네 좁히기 단계", "3차 반출 동 키, 4차 분모로 다시 계산한 U2·1순위, 이유 판정 결과(analysis/outside/out_V4FBK)."),
    "reasons": ("이유 7가지 판정 수", "1순위 17곳의 이유별 판정 기호 집계(out_V4FBK/reason_table_INTERNAL.csv). 규칙은 결정 기록 D-019."),
    "targets": ("1순위 동네 판정표", "공표용: 유형·기호·두 반기 지속성만 담았다. 지표 값은 없다(out_V4FBK, 97_summary.txt)."),
    "gap": ("겉보기 부족분 유형별", "1순위 동네의 기대 이용 − 실제 이용(방학 한 달 결제)을 판정 유형별로 더한 값(out_V4FBK 시나리오 B)."),
    "scenario": ("시나리오 A·B 비교", "방학 한 달에 늘어나는 이용 계정. 가정 아래 계산(out_V4FBK/scenario_AB_compare.csv)."),
    "daycount": ("하루 결제 횟수", "4차 반출 노트북 출력: 계정-일 284,110의 하루 급식 결제 횟수."),
    "maxday": ("방학 하루 최대 결제", "4차 반출 노트북 출력: 방학에 결제한 계정 6,223의 하루 최대 승인액 구간별 계정 수."),
    "variation": ("방학 반기 자연 변동", "4차 반출 EXPORT_v4_dong_vac_half.csv로 계산한 동별 반기 변화의 로그 표준편차(반기 결제 규모 구간별)."),
    "mde": ("시범 판정 가능 크기", "자연 변동으로 계산한 구별 가능한 최소 증가(docs/topics/T2_pilot_design.md §4)."),
    "pilot": ("시범 운영 일정", "docs/topics/T2_pilot_design.md §3."),
    "solutions": ("유형별 처방", "docs/topics/T2_checkup_tool.md §6. 배달비 지원 보도(매일신문 2024-02-29)를 반영했다."),
    "glossary": ("용어 풀이", "문서에 나오는 코드(Q1, R3 등)를 쉬운 이름으로 바꾼 표."),
    "geo": ("법정동 경계와 점검 결과", "국가공간정보포털 법정동·리 경계(2026-09, EPSG:5186, 25m 단순화)와 1순위 유형. 동 단위는 유형만 담았다."),
}


def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


dump("dash_meta.json", {"title": "아동급식카드는 어디서 멈추는가"})
for k, blob in BLOB.items():
    title, desc = META[k]
    dump(f"datasets_{k}.json", {"title": title, "description": desc,
                                "source": {"kind": "file", "url": f"/_blob/{blob}", "name": f"{k}.json", "format": "json"},
                                "updated": {"at": AT, "by": BY}, "fixed": True})
html = (HERE / "index.html").read_text(encoding="utf-8")
dump("files_index.json", {"text": html})
print("ok", len(BLOB), "datasets | index.html", round(len(html.encode("utf-8")) / 1024, 1), "KB")
