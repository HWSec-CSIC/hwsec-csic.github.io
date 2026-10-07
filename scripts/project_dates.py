"""Calendar-based project metadata shared by the static builder and its tests.

Date bounds are inclusive. A source that only supplied years is represented by
January 1 / December 31 bounds with datePrecision="year"; this is a calendar-year
assumption for status calculation, not a claim about exact contractual dates.
"""

from __future__ import annotations

from datetime import date
import re

STATUSES = ("upcoming", "ongoing", "completed")
STATUS_LABELS = {"upcoming": "Upcoming", "ongoing": "Ongoing", "completed": "Completed"}
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _date(value: object, location: str) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError(f"{location}: use a valid ISO date such as 2026-10-06.")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{location}: use a valid ISO date such as 2026-10-06.") from error


def validate_project_dates(project: dict, location: str = "project") -> None:
    """Validate a date pair, or a legacy manually maintained status."""
    has_start, has_end = "startDate" in project, "endDate" in project
    if has_start != has_end:
        raise ValueError(f"{location}: supply both startDate and endDate.")
    if has_start:
        start = _date(project["startDate"], location + ".startDate")
        end = _date(project["endDate"], location + ".endDate")
        if end < start:
            raise ValueError(f"{location}.endDate: must be on or after startDate.")
    elif project.get("status") not in (*STATUSES, "active"):
        raise ValueError(f"{location}: supply startDate/endDate or a legacy status (upcoming, ongoing, completed).")
    if "status" in project and project["status"] not in (*STATUSES, "active"):
        raise ValueError(f"{location}.status: use upcoming, ongoing or completed.")
    precision = project.get("datePrecision", "day")
    if precision not in ("day", "year"):
        raise ValueError(f"{location}.datePrecision: use day or year.")
    if precision == "year":
        if not has_start or project["startDate"][5:] != "01-01" or project["endDate"][5:] != "12-31":
            raise ValueError(f"{location}.datePrecision: year precision requires January 1 / December 31 bounds.")


def project_status(project: dict, on_date: date | None = None) -> str:
    """Resolve status for a local calendar date; supplied dates override status."""
    validate_project_dates(project)
    if "startDate" not in project:
        return "ongoing" if project["status"] == "active" else project["status"]
    today = on_date if on_date is not None else date.today()
    if not isinstance(today, date):
        raise TypeError("on_date must be a datetime.date.")
    if today < _date(project["startDate"], "project.startDate"):
        return "upcoming"
    if today > _date(project["endDate"], "project.endDate"):
        return "completed"
    return "ongoing"


def project_period(project: dict) -> str:
    """Full calendar range for cards/features, with an optional display override."""
    if project.get("period"):
        return project["period"]
    return project_duration(project)


def project_duration(project: dict) -> str:
    """Human-readable range generated from the same data used for status."""
    if "startDate" not in project:
        return next((item["value"] for item in project.get("details", [])
                     if item["label"].casefold() == "duration"), "")
    validate_project_dates(project)
    start = _date(project["startDate"], "project.startDate")
    end = _date(project["endDate"], "project.endDate")
    def label(value: date) -> str:
        return f"{value.day} {MONTHS[value.month - 1]} {value.year}"
    duration = label(start) if start == end else f"{label(start)} – {label(end)}"
    if project.get("datePrecision") == "year":
        duration += " (year-based dates)"
    return duration
