"""Offline M1 entry point; meal values may still be unset."""
import argparse
import sys

from lib.config import load_discovery_config
from lib.m1 import run
from lib.pipeline import open_context


def main(argv=None):
    parser = argparse.ArgumentParser(description="M1 지급구분 의미 확인")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run")
    args = parser.parse_args(argv)
    try:
        ctx = open_context(load_discovery_config(args.config), args.run)
        result = run(ctx)
        return 2 if result["incomplete"] else 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("M1 오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
