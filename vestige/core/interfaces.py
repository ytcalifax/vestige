from __future__ import annotations

from typing import List, Protocol, runtime_checkable

from selectolax.parser import HTMLParser

from ..models.models import DownloadFile, IssueEntry


@runtime_checkable
class AsyncPageFetcher(Protocol):
    """Contract for the async HTTP transport layer."""

    async def fetch_page(self, page: int) -> HTMLParser:
        """Fetch a listing page by number and return its parsed HTML."""
        ...  # pragma: no cover

    async def fetch_download(self, id_obj: str, idcl: str) -> HTMLParser:
        """Fetch the download modal for a given issue and return its parsed HTML."""
        ...  # pragma: no cover

    async def fetch_download_with_state(
        self, id_obj: str, idcl: str, view_state: str
    ) -> HTMLParser:
        """Concurrent-safe download fetch using an explicit ViewState snapshot."""
        ...  # pragma: no cover

    async def aclose(self) -> None:
        """Release the underlying HTTP client."""
        ...  # pragma: no cover


@runtime_checkable
class PageParser(Protocol):
    """Contract for the HTML parsing layer (remains synchronous)."""

    def parse_entries(self, tree: HTMLParser) -> List[IssueEntry]:
        ...  # pragma: no cover

    def parse_download_files(self, tree: HTMLParser) -> List[DownloadFile]:
        ...  # pragma: no cover

    def parse_total_results(self, tree: HTMLParser) -> int:
        ...  # pragma: no cover

    def parse_total_pages(self, tree: HTMLParser) -> int:
        ...  # pragma: no cover
