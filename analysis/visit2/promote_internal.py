"""Manually promote only the specified dong-name inventory after approval."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from lib.pipeline import emit, open_context


def main(argv=None):
    parser = argparse.ArgumentParser(description="센터 확인 후 동 이름 목록 수동 승격")
    parser.add_argument("--run", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args(argv)
    try:
        if not args.reason.strip():
            raise ValueError("센터 확인 사항과 승격 사유를 입력하세요")
        if args.file != "m4_dong_names.csv":
            raise ValueError("수동 승격은 m4_dong_names.csv에만 허용됩니다")
        root = Path(args.run).resolve()
        manifest = json.loads((root / "export/run_manifest.json").read_text(encoding="utf-8"))
        cfg = manifest["config"]
        cfg["_config_path"] = str(Path(__file__).resolve().parent / "config/visit2.json")
        ctx = open_context(cfg, root)
        source = root / "internal" / args.file
        if source.resolve().parent != root / "internal":
            raise ValueError("internal 밖 파일은 승격할 수 없습니다")
        frame = pd.read_csv(source, encoding="utf-8-sig", dtype={"gungu": str, "dong": str})
        if set(frame.columns) != {"gungu", "dong", "len_chars"}:
            raise ValueError("승격 대상의 열 구조가 동 이름 목록과 다릅니다")
        if frame[["gungu", "dong"]].isna().any().any() or frame.duplicated(["gungu", "dong"]).any():
            raise ValueError("동 이름 목록의 키가 비었거나 중복입니다")
        if not pd.to_numeric(frame.len_chars, errors="coerce").eq(frame.dong.str.len()).all():
            raise ValueError("동 이름 길이 검증 실패")
        emit(ctx, frame, "m4_dong_names", ["gungu", "dong"], "shop", n_col=None, shop_col=None, cust_col=None)
        ctx.manual_actions.append({"file": args.file, "reason": args.reason.strip(), "time": datetime.now().isoformat()})
        ctx.finish("promote_internal", {"file": args.file})
        print("동 이름 목록 승격 완료. 반출 점검을 다시 실행하세요")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("수동 승격 오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
