"""Inspect headers; source samples are written to internal only."""
import argparse
import csv
import sys
from pathlib import Path
from lib.config import load_config
from lib.io import detect_encoding, read_header
from lib.pipeline import open_context


def main(argv=None):
    parser = argparse.ArgumentParser(description="원본 헤더 확인")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run")
    args = parser.parse_args(argv)
    try:
        cfg = load_config(args.config)
        ctx = open_context(cfg, args.run)
        lines, missing = [], False
        for kind in ("pay", "shop"):
            path = Path(cfg["paths"][kind])
            encoding = detect_encoding(path, cfg["encoding_candidates"])
            header = read_header(path, encoding)
            public = ["%s encoding=%s bytes=%d" % (kind, encoding, path.stat().st_size), str(header)]
            for logical, physical in cfg["columns"][cfg["columns"]["active"]][kind].items():
                okay = physical in header
                missing = missing or not okay
                public.append("%s -> %s: %s" % (logical, physical, "OK" if okay else "MISSING"))
            print("\n".join(public))
            lines.extend(public)
            with path.open(encoding=encoding, newline="") as handle:
                reader = csv.reader(handle)
                next(reader)
                for _ in range(3):
                    lines.append(repr(next(reader, [])))
        ctx.write_internal("\n".join(lines), "headers.txt")
        ctx.finish("headers", {"missing_mapping": missing})
        print("run=" + str(ctx.root))
        return int(missing)
    except (OSError, ValueError, KeyError) as exc:
        print("헤더 오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
