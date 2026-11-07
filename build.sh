#!/usr/bin/env bash
# Render build step: install, collect static files, migrate, seed.
set -o errexit
set -o pipefail

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# D's seed command (grader accounts + demo data). It must be safe to run on
# every deploy. Skipped until the command exists.
if python manage.py help seed >/dev/null 2>&1; then
  python manage.py seed
else
  echo "No seed command yet; skipping."
fi
