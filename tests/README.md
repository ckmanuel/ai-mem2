# Tests

`test_pre_commit_scan.py` covers the secret scanner. `test_search.py` covers
`scripts/search.sh`. `test_tools.py` covers `redact()`, `paste_pack.sh`, and
`doctor.sh`.

Run with:

```sh
python3 -m pytest tests/ -v
```

Or without pytest:

```sh
python3 tests/test_pre_commit_scan.py
python3 tests/test_search.py
python3 tests/test_tools.py
```

## Fixtures

`fixtures/` contains sample strings used by the tests:

- `fixtures/should_match.txt` — strings that contain real token shapes
  the scanner should catch (github_pat_, ghp_, sk-, AKIA, etc.). One
  per line.
- `fixtures/should_not_match.txt` — strings that look like tokens but
  aren't (md5, sha1, sha256, UUID, version strings, URLs, paths). The
  scanner should NOT flag these.
