"""M3 offline entry point."""
import argparse
import sys
from lib.config import load_config
from lib.m3 import run
from lib.pipeline import open_context


def main(argv=None):
    parser = argparse.ArgumentParser(description="M3 가맹점 결합")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run")
    args = parser.parse_args(argv)
    try:
        return run(open_context(load_config(args.config), args.run))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("M3 오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
