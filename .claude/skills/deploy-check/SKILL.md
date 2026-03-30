---
name: deploy-check
description: Run pre-deployment verification checks for PluginDB — validates data, tests, and Docker build before pushing
---

## Pre-Deploy Verification

Run all checks in sequence. Stop and report if any step fails.

### Step 1: Uncommitted Changes

```bash
git status --short
```

Report any uncommitted or untracked files. Warn the user but don't block — they may want to commit after verification.

### Step 2: Validate Seed Data

```bash
python -m plugindb.seed --validate
```

Must exit cleanly with no errors. This catches schema violations, invalid categories/formats/price_types, and data integrity issues.

### Step 3: Rebuild Database

```bash
python -m plugindb.seed
```

Ensures the SQLite database is in sync with seed.json. Must succeed.

### Step 4: Full Test Suite

```bash
python -m pytest tests/ -v --tb=short
```

All tests must pass. Report the total count and any failures with details.

### Step 5: Docker Build (if Docker available)

```bash
docker build -t plugindb-check .
```

Only run if `docker` is available. Tests the multi-stage build (builder → seeder → runtime). Report success/failure but don't block if Docker isn't installed locally.

### Results Summary

Report a checklist:

- [ ] Git status clean
- [ ] Seed validation passed
- [ ] Database rebuilt
- [ ] All N tests passed
- [ ] Docker build succeeded (or skipped)

If all checks pass, confirm the project is ready to deploy. If any fail, summarize what needs fixing.
