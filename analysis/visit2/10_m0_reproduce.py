"""M0 offline entry point."""
import argparse
import sys
from lib.config import load_config, load_discovery_config, meal_values_configured
from lib.m0 import run
from lib.pipeline import open_context


def main(argv=None):
    parser = argparse.ArgumentParser(description="M0 1차 반출 재현")
    parser.add_argument("--config", required=True)
    parser.add_argument("--run")
    parser.add_argument("--meal-values")
    args = parser.parse_args(argv)
    try:
        if args.meal_values:
            cfg = load_discovery_config(args.config)
            cfg["meal_pay_values"] = [v.strip() for v in args.meal_values.split(",") if v.strip()]
            if not meal_values_configured(cfg):
                raise ValueError("급식 값 목록이 비었습니다")
        else:
            cfg = load_config(args.config)
        return run(open_context(cfg, args.run))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("M0 오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
