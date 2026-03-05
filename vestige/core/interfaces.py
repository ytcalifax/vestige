from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from bs4 import BeautifulSoup

from ..models.models import DownloadFile, IssueEntry


@runtime_checkable
class PageFetcher(Protocol):
    """Contract for the HTTP transport layer.

    Any class that provides these two methods can be injected into
    ``DVClient`` in place of the default ``RequestsTransport``.
    """

    def fetch_page(self, page: int) -> BeautifulSoup:
        """Fetch a listing page by number and return its parsed HTML."""
        ...  # pragma: no cover

    def fetch_download(self, id_obj: str, idcl: str) -> BeautifulSoup:
        """Fetch the download modal for a given issue and return its parsed HTML."""
        ...  # pragma: no cover


@runtime_checkable
class PageParser(Protocol):
    """Contract for the HTML parsing layer.

    Any class that provides these methods can be injected into
    ``DVClient`` in place of the default ``IssueParser``.
    """

    def parse_entries(self, soup: BeautifulSoup) -> List[IssueEntry]:
        """Parse all IssueEntry items from a listing page."""
        ...  # pragma: no cover

    def parse_download_files(self, soup: BeautifulSoup) -> List[DownloadFile]:
        """Parse all DownloadFile items from a download modal page."""
        ...  # pragma: no cover

    def parse_total_results(self, soup: BeautifulSoup) -> int:
        """Return the total number of results reported by the server."""
        ...  # pragma: no cover

    def parse_total_pages(self, soup: BeautifulSoup) -> int:
        """Return the total number of pages reported by the server."""
        ...  # pragma: no cover
