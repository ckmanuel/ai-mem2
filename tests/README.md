# Tests for pre_commit_scan.py

Run with:

```sh
python3 -m pytest tests/ -v
```

Or without pytest:

```sh
python3 tests/test_pre_commit_scan.py
```

## Fixtures

`fixtures/` contains sample strings used by the tests:

- `fixtures/should_match.txt` — strings that contain real token shapes
  the scanner should catch (github_pat_, ghp_, sk-, AKIA, etc.). One
  per line.
- `fixtures/should_not_match.txt` — strings that look like tokens but
  aren't (md5, sha1, sha256, UUID, version strings, URLs, paths). The
  scanner should NOT flag these.
