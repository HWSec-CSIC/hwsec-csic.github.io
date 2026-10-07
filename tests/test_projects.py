"""Project calendar boundaries and migrated source data."""

from datetime import date
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from project_dates import project_duration, project_period, project_status, validate_project_dates


class ProjectDateTests(unittest.TestCase):
    def setUp(self):
        self.project = {"startDate": "2026-02-28", "endDate": "2026-03-02"}

    def test_status_includes_start_and_end_calendar_days(self):
        for day, expected in [(date(2026, 2, 27), "upcoming"),
                              (date(2026, 2, 28), "ongoing"),
                              (date(2026, 3, 1), "ongoing"),
                              (date(2026, 3, 2), "ongoing"),
                              (date(2026, 3, 3), "completed")]:
            with self.subTest(day=day):
                self.assertEqual(project_status(self.project, day), expected)

    def test_a_single_day_project_and_valid_leap_day(self):
        leap = {"startDate": "2028-02-29", "endDate": "2028-02-29"}
        validate_project_dates(leap)
        self.assertEqual(project_status(leap, date(2028, 2, 29)), "ongoing")
        self.assertEqual(project_status(leap, date(2028, 3, 1)), "completed")
        self.assertEqual(project_duration(leap), "29 Feb 2028")
        self.assertEqual(project_period(leap), "29 Feb 2028")

    def test_invalid_dates_are_rejected_with_the_field_location(self):
        for value in ("2026-02-29", "2026-13-01", "2026-04-31", "20260228", "2026-2-28", "", None):
            with self.subTest(value=value):
                invalid = dict(self.project, startDate=value)
                with self.assertRaisesRegex(ValueError, r"projects.json.projects\[0\].startDate"):
                    validate_project_dates(invalid, "projects.json.projects[0]")

    def test_dates_must_be_paired_and_in_chronological_order(self):
        for invalid in ({"startDate": "2026-01-01"}, {"endDate": "2026-01-01"}):
            with self.assertRaisesRegex(ValueError, "both startDate and endDate"):
                validate_project_dates(invalid)
        with self.assertRaisesRegex(ValueError, "on or after startDate"):
            validate_project_dates({"startDate": "2026-01-02", "endDate": "2026-01-01"})

    def test_dates_override_manual_status_and_legacy_active_is_supported(self):
        dated = dict(self.project, status="completed")
        self.assertEqual(project_status(dated, date(2026, 3, 1)), "ongoing")
        self.assertEqual(project_status({"status": "active"}, date(2099, 1, 1)), "ongoing")
        for status in ("upcoming", "ongoing", "completed"):
            self.assertEqual(project_status({"status": status}, date(2026, 1, 1)), status)
        for invalid in ({}, {"status": "current"}):
            with self.assertRaises(ValueError):
                validate_project_dates(invalid)

    def test_period_override_does_not_change_status_or_generated_duration(self):
        dated = dict(self.project, period="A custom programme label")
        self.assertEqual(project_period(dated), "A custom programme label")
        self.assertEqual(project_duration(dated), "28 Feb 2026 – 2 Mar 2026")
        self.assertEqual(project_status(dated, date(2026, 3, 3)), "completed")
        self.assertEqual(project_period(self.project), "28 Feb 2026 – 2 Mar 2026")
        legacy = {"status": "active", "details": [{"label": "Duration", "value": "1 Jan 2025 – 31 Dec 2028"}]}
        self.assertEqual(project_period(legacy), "1 Jan 2025 – 31 Dec 2028")
        self.assertEqual(project_duration(legacy), "1 Jan 2025 – 31 Dec 2028")

    def test_year_only_sources_show_full_calendar_bounds_with_precision_annotation(self):
        yearly = {"startDate": "2025-01-01", "endDate": "2026-12-31", "datePrecision": "year"}
        self.assertEqual(project_period(yearly), "1 Jan 2025 – 31 Dec 2026 (year-based dates)")
        self.assertEqual(project_duration(yearly), "1 Jan 2025 – 31 Dec 2026 (year-based dates)")
        self.assertEqual(project_status(yearly, date(2026, 12, 31)), "ongoing")
        self.assertEqual(project_status(yearly, date(2027, 1, 1)), "completed")
        for invalid in ({"startDate": "2025-02-01", "endDate": "2026-12-31", "datePrecision": "year"},
                        {"startDate": "2025-01-01", "endDate": "2026-11-30", "datePrecision": "year"},
                        {"status": "ongoing", "datePrecision": "year"},
                        dict(yearly, datePrecision="month")):
            with self.assertRaisesRegex(ValueError, "datePrecision"):
                validate_project_dates(invalid)

    def test_all_nine_projects_have_dates_and_retain_the_supplied_duration(self):
        data = json.loads((ROOT / "assets/docs/projects.json").read_text())
        expected = {
            "q-fence": "1 Nov 2025 – 31 Oct 2028",
            "decide": "1 Jan 2025 – 31 Dec 2028",
            "qubip": "1 Sep 2023 – 31 Aug 2026",
            "sqprim": "1 Jul 2023 – 31 Aug 2025",
            "goit": "1 Sep 2022 – 28 Feb 2025",
            "spirs": "1 Oct 2021 – 30 Sep 2024",
            "cryptopic": "1 Nov 2025 – 30 Oct 2028",
            "ares": "1 Sep 2021 – 31 Oct 2025",
            "technoquantum": "1 Jan 2025 – 31 Dec 2026 (year-based dates)",
        }
        self.assertEqual({project["id"] for project in data["projects"]}, set(expected))
        for project in data["projects"]:
            with self.subTest(project=project["id"]):
                validate_project_dates(project)
                self.assertNotIn("status", project)
                self.assertFalse(any(detail["label"] == "Duration" for detail in project["details"]))
                self.assertEqual(project_duration(project), expected[project["id"]])
                self.assertEqual(project_period(project), expected[project["id"]])
        ongoing = {project["id"] for project in data["projects"]
                   if project_status(project, date(2026, 10, 6)) == "ongoing"}
        self.assertEqual(ongoing, {"q-fence", "decide", "cryptopic", "technoquantum"})


if __name__ == "__main__":
    unittest.main()
