# SSO Merge Script Design

## Goal
Add a standalone script that combines Grok SSO text files into one output file without deduplication.

## Architecture
Implement a small CLI script under `scripts/` that scans a target directory for `sso_*.txt`, sorts by file name, skips the output file itself, and appends each line as-is into a merged file.

## Behavior
- Default input directory: `token_dir/grok`
- Default output file: `token_dir/grok/sso_merged.txt`
- No deduplication
- Preserve line order by sorted file name and in-file order
- Print file count and line count summary

## Testing
Add a unit test that creates temporary `sso_*.txt` files, runs the merge helper, and verifies the merged output preserves duplicates and ordering.
