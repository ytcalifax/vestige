from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import re

@dataclass(frozen=True)
class DownloadFile:
    """A single downloadable file (PDF / RTF) for a given issue.

    Frozen because a file reference never changes once discovered.
    """

    url: str
    filename: str

    def __repr__(self) -> str:
        return f"DownloadFile(filename={self.filename!r}, url={self.url!r})"

    def extension(self) -> str:
        """Return the file extension (without leading dot), lower-cased, or empty string.

        This is computed from the filename and is used when serialising to JSON.
        """
        import os

        _, ext = os.path.splitext(self.filename or "")
        return ext.lstrip('.').lower() if ext else ""


@dataclass
class IssueEntry:
    """One issue of the State Gazette.

    Mutable so that ``urls`` can be populated lazily after the
    entry is first parsed from the listing page.
    """

    number: int
    date: str
    year: int
    type: str = ""
    urls: List[DownloadFile] = field(default_factory=list)

    # Internal transport details — not part of the public API.
    _id_obj: str = field(default="", repr=False)
    _download_link_id: str = field(default="", repr=False)


    def __post_init__(self):
        object.__setattr__(self, 'type', self._normalize_type(self.type))

    @staticmethod
    def _normalize_type(value: str) -> str:
        if value == "извънреден":
            return "special"
        else:
            return "regular"

    @staticmethod
    def _normalize_date(value: str) -> str:
        """Normalise various scraped date formats to ISO YYYY-MM-DD.

        Handles common dot-separated Bulgarian numeric dates like '8.1.2026'
        or '08.01.2026', as well as already ISO-formatted dates. If parsing
        fails, returns the original string unchanged.
        """
        if not value:
            return value

        v = value.strip()
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v

        # Common dot-separated numeric date: d.m.Y or dd.mm.Y
        if "." in v:
            parts = [p.strip() for p in v.split('.') if p.strip()]
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                day, month, year = parts
                day = day.zfill(2)
                month = month.zfill(2)
                # normalise 2-digit year -> assume 2000s
                if len(year) == 2:
                    year = f"20{year}"
                try:
                    dt = datetime(int(year), int(month), int(day))
                    return dt.strftime("%Y-%m-%d")
                except Exception:
                    pass

        # Try common slash-separated or space-separated formats
        for fmt in ("%d/%m/%Y", "%d %m %Y", "%Y/%m/%d", "%Y.%m.%d"):
            try:
                dt = datetime.strptime(v, fmt)
                return dt.strftime("%Y-%m-%d")
            except Exception:
                continue
        return value

    def __repr__(self) -> str:
        extra = f", type={self.type!r}" if self.type else ""
        dl = f", files={len(self.urls)}" if self.urls else ""
        return (
            f"IssueEntry(number={self.number}, date={self.date!r}, "
            f"year={self.year}{extra}{dl})"
        )

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dictionary representation."""
        return {
            "issue": self.number,
            "date": self._normalize_date(self.date),
            "year": self.year,
            "type": self.type,
            "files": [
                {"url": f.url, "filename": f.filename, "extension": f.extension()}
                for f in self.urls
            ],
        }


@dataclass(frozen=True)
class PageResult:
    """Result of fetching one page of the issue listing.

    Frozen because the metadata for a fetched page is fixed.
    """

    page: int
    total_results: int
    total_pages: int
    entries: List[IssueEntry]

    def __repr__(self) -> str:
        return (
            f"PageResult(page={self.page}, "
            f"total_results={self.total_results}, "
            f"total_pages={self.total_pages}, "
            f"entries={len(self.entries)})"
        )

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dictionary representation."""
        return {
            "page": self.page,
            "total_results": self.total_results,
            "total_pages": self.total_pages,
            "entries": [e.to_dict() for e in self.entries],
        }
