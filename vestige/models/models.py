from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class DownloadFile:
    """A single downloadable file (PDF / RTF) for a given issue.

    Frozen because a file reference never changes once discovered.
    """

    url: str
    filename: str

    def __repr__(self) -> str:
        return f"DownloadFile(filename={self.filename!r}, url={self.url!r})"


@dataclass
class IssueEntry:
    """One issue of the State Gazette.

    Mutable so that ``urls`` can be populated lazily after the
    entry is first parsed from the listing page.
    """

    number: int
    date: str
    year: int
    id_obj: str
    type: str = ""

    # Internal transport detail — not part of the public API.
    _download_link_id: str = field(default="", repr=False)
    urls: List[DownloadFile] = field(default_factory=list)

    def __post_init__(self):
        object.__setattr__(self, 'type', self._normalize_type(self.type))

    @staticmethod
    def _normalize_type(value: str) -> str:
        if value == "извънреден":
            return "special"
        else:
            return "regular"

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
            "number": self.number,
            "date": self.date,
            "year": self.year,
            "id_obj": self.id_obj,
            "type": self.type,
            "urls": [
                {"url": f.url, "filename": f.filename}
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
