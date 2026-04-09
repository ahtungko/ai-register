import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from util.sso_merge import DEFAULT_GROK_DIR, DEFAULT_OUTPUT_FILE, merge_grok_sso_files


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge Grok SSO files into a single output file.")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_GROK_DIR,
        help="Directory containing Grok SSO files. Defaults to token_dir/grok.",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help="Merged output path. Defaults to token_dir/grok/sso_merged.txt.",
    )
    args = parser.parse_args()

    result = merge_grok_sso_files(args.input_dir, args.output_file)
    print(f"Processed {result.files_processed} files and wrote {result.lines_written} lines.")


if __name__ == "__main__":
    main()
