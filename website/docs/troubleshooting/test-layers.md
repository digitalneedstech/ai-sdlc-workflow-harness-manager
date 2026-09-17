---
title: Test layers
description: One tester after all children. Playwright implements qa-test-cases 1:1. Devops requires FEATURE_SIGNOFF.
---

## Symptom

Tester writes markdown only (`TESTS: cases-only`) or devops runs before automated e2e.

## Cause

BA must plan layers early; tester must execute them **once** at feature level; devops must require `qa-signoff.md`.

## Do not

- Mark tester SUCCESS without `FEATURE_SIGNOFF: passed` when `skip_tester: false`
- Run tester-agent per child spec or between waves
- Recreate `features/{slug}/e2e/` — specs and PNGs live in `automation-tests/`
- Let devops substitute health checks for required e2e
- Let Playwright invent scenarios from Must ACs instead of implementing `qa-test-cases.md` 1:1

Which classes run tester is in `tester-policy.md`, copied into `route.md` `skip_tester`. Override: `RUN_TESTER: true|false`. Target URL lives in the test-plan Target block, not in harness source.
