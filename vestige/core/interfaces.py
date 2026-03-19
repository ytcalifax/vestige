from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from selectolax.parser import HTMLParser

from ..models.models import DownloadFile, IssueEntry


@runtime_checkable
class PageFetcher(Protocol):
    """Contract for the HTTP transport layer.

    Any class that provides these two methods can be injected into
    ``DVClient`` in place of the default ``RequestsTransport``.
    """

    def fetch_page(self, page: int) -> HTMLParser:
        """Fetch a listing page by number and return its parsed HTML."""
        ...  # pragma: no cover

    def fetch_download(self, id_obj: str, idcl: str) -> HTMLParser:
        """Fetch the download modal for a given issue and return its parsed HTML."""
        ...  # pragma: no cover

    def fetch_download_with_state(
        self, id_obj: str, idcl: str, view_state: str
    ) -> HTMLParser:
        """Thread-safe download fetch using an explicit ViewState snapshot.

        Does not read or mutate ``self._view_state``.
        """
        ...  # pragma: no cover


@runtime_checkable
class PageParser(Protocol):
    """Contract for the HTML parsing layer.

    Any class that provides these methods can be injected into
    ``DVClient`` in place of the default ``IssueParser``.
    """

    def parse_entries(self, tree: HTMLParser) -> List[IssueEntry]:
        """Parse all IssueEntry items from a listing page."""
        ...  # pragma: no cover

    def parse_download_files(self, tree: HTMLParser) -> List[DownloadFile]:
        """Parse all DownloadFile items from a download modal page."""
        ...  # pragma: no cover

    def parse_total_results(self, tree: HTMLParser) -> int:
        """Return the total number of results reported by the server."""
        ...  # pragma: no cover

    def parse_total_pages(self, tree: HTMLParser) -> int:
        """Return the total number of pages reported by the server."""
        ...  # pragma: no cover
