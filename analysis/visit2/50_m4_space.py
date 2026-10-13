"""M4 offline entry point."""
import argparse
import sys
from lib.config import load_config
from lib.m4 import run
from lib.pipeline import open_context


def main(argv=None):
    parser = argparse.ArgumentParser(description="M4 공간 공표 가능성")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run")
    args = parser.parse_args(argv)
    try:
        return run(open_context(load_config(args.config), args.run))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("M4 오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
