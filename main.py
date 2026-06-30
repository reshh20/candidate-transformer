import argparse
import json
import sys
from src.pipeline import run_pipeline, run_pipeline_with_config


def main():
    parser = argparse.ArgumentParser(
        description="Multi-Source Candidate Data Transformer — turns messy candidate data into clean profiles."
    )
    parser.add_argument(
        "--csv", required=True,
        help="Path to the recruiter CSV input file."
    )
    parser.add_argument(
        "--config", required=False,
        help="Path to a JSON config file to reshape the output. If omitted, the full default canonical record is returned."
    )
    parser.add_argument(
        "--out", required=True,
        help="Path to write the output JSON file."
    )

    args = parser.parse_args()

    try:
        if args.config:
            result = run_pipeline_with_config(args.csv, args.config)
        else:
            result = run_pipeline(args.csv)
    except Exception as e:
        print(f"Error: pipeline failed to run — {e}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
    except Exception as e:
        print(f"Error: failed to write output file — {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Done. Wrote {len(result)} candidate profile(s) to {args.out}")


if __name__ == "__main__":
    main()