"""Seed the database with grader accounts and demo data.  Owner: D.

`build.sh` runs this on every Render deploy, so it MUST be safe to run any
number of times.  Everything below uses get_or_create / update_or_create and
never `create`, so a second run changes nothing.

It deliberately makes no network calls: a deploy must not fail because an
external API is slow, and the course requires that tests never touch real
external services.  Real College Scorecard rows come from a separate command,
`import_scorecard`, which a human runs on purpose.

    python manage.py seed
"""

import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Institution, Shortlist, ShortlistItem

SAMPLE_DATA = Path(__file__).resolve().parent.parent.parent / "data" / "sample_institutions.json"

# Grader accounts.  Fake addresses, passwords used nowhere else, no 2FA.
# These exact values go in the assignment's "notes" field.
GRADER_ACCOUNTS = [
    {
        "username": "admin",
        "email": "admin@example.com",
        "password": "compass-admin-demo-2026",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "username": "student",
        "email": "student@example.com",
        "password": "compass-student-demo-2026",
        "is_staff": False,
        "is_superuser": False,
    },
]

DEMO_SHORTLIST_NAME = "Fall 2027 applications"
DEMO_SHORTLIST_PICKS = [
    (900001, "In-state tuition, strong retention. Safety."),
    (900003, "Best earnings outcome on the list. Target."),
    (900010, "Reach. Need to check aid before applying."),
]


class Command(BaseCommand):
    help = "Create grader accounts and demo data. Safe to run repeatedly."

    @transaction.atomic
    def handle(self, *args, **options):
        users = self._seed_users()
        created, updated = self._seed_institutions()
        self._seed_demo_shortlist(users["student"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {len(users)} accounts, "
                f"{created} institutions created, {updated} updated."
            )
        )
        self.stdout.write(
            "Sample institutions are stored with data_release='SAMPLE'. "
            "Run `python manage.py import_scorecard` for real federal data."
        )

    def _seed_users(self):
        User = get_user_model()
        users = {}
        for spec in GRADER_ACCOUNTS:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "email": spec["email"],
                    "is_staff": spec["is_staff"],
                    "is_superuser": spec["is_superuser"],
                },
            )
            # Re-apply on every run so a changed password or flag is restored,
            # and so the account still works after a database reset.
            user.email = spec["email"]
            user.is_staff = spec["is_staff"]
            user.is_superuser = spec["is_superuser"]
            user.set_password(spec["password"])
            user.save()
            users[spec["username"]] = user
            self.stdout.write(f"  {'created' if created else 'updated'} user {user.username}")
        return users

    def _seed_institutions(self):
        payload = json.loads(SAMPLE_DATA.read_text(encoding="utf-8"))
        created = updated = 0
        for row in payload["institutions"]:
            fields = {k: v for k, v in row.items() if k != "unitid"}
            fields["data_release"] = Institution.SAMPLE
            _, was_created = Institution.objects.update_or_create(
                unitid=row["unitid"], defaults=fields
            )
            created += was_created
            updated += not was_created
        return created, updated

    def _seed_demo_shortlist(self, student):
        shortlist, _ = Shortlist.objects.get_or_create(
            user=student, name=DEMO_SHORTLIST_NAME
        )
        for position, (unitid, note) in enumerate(DEMO_SHORTLIST_PICKS):
            institution = Institution.objects.filter(unitid=unitid).first()
            if institution is None:
                continue
            ShortlistItem.objects.update_or_create(
                shortlist=shortlist,
                institution=institution,
                defaults={"note": note, "position": position},
            )
