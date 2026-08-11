#!/bin/sh
# One-time setup for a fresh clone: point git at the repo's hooks so the
# QA gate runs before every commit. Safe to run repeatedly.
git config core.hooksPath .githooks
chmod +x .githooks/* 2>/dev/null
echo "✓ Git hooks enabled (core.hooksPath = .githooks)."
echo "  The pre-commit QA gate (tools/qa.py) will now run on every commit."
