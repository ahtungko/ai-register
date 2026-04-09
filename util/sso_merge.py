from dataclasses import dataclass
from pathlib import Path

DEFAULT_GROK_DIR = Path("token_dir") / "grok"
DEFAULT_OUTPUT_FILE = DEFAULT_GROK_DIR / "sso_merged.txt"


@dataclass(frozen=True)
class MergeResult:
    files_processed: int
    lines_written: int


def _sso_candidate_files(base_dir: Path, output_file: Path) -> list[Path]:
    target_resolved = output_file.resolve()
    candidates: list[Path] = []

    for path in base_dir.iterdir():
        if not path.is_file() or not path.name.startswith("sso_"):
            continue

        if path.resolve() == target_resolved:
            continue

        candidates.append(path)

    return sorted(candidates, key=lambda p: p.name)


def merge_grok_sso_files(
    grok_dir: Path | str | None = None,
    output_file: Path | str | None = None,
) -> MergeResult:
    base_dir = Path(grok_dir or DEFAULT_GROK_DIR)
    if not base_dir.is_dir():
        raise FileNotFoundError(f"Grok directory not found: {base_dir}")

    target_file = Path(output_file or DEFAULT_OUTPUT_FILE)
    target_file.parent.mkdir(parents=True, exist_ok=True)

    candidates = _sso_candidate_files(base_dir, target_file)
    line_count = 0

    with target_file.open("w", encoding="utf-8", newline="") as merged:
        for candidate in candidates:
            with candidate.open("r", encoding="utf-8", newline="") as source:
                for line in source:
                    merged.write(line)
                    line_count += 1

    return MergeResult(files_processed=len(candidates), lines_written=line_count)
