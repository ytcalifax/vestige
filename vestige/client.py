from __future__ import annotations

from typing import List, Optional

from .core import constants as C
from .core.interfaces import PageFetcher, PageParser
from .models.models import PageResult
from .network.transport import RequestsTransport
from .scraping.parsers import IssueParser


class DVClient:
    """Client for the Държавен вестник (Bulgarian State Gazette) listing.

    Parameters
    ----------
    transport:
        Concrete implementation of ``PageFetcher``.  Defaults to
        ``RequestsTransport`` which uses a live ``requests.Session``.
        Pass a stub/mock here in tests.
    parser:
        Concrete implementation of ``PageParser``.  Defaults to
        ``IssueParser``.  Pass a stub/mock here in tests.
    """

    def __init__(
        self,
        transport: Optional[PageFetcher] = None,
        parser: Optional[PageParser] = None,
    ) -> None:
        self._transport: PageFetcher = transport or RequestsTransport()
        self._parser: PageParser = parser or IssueParser()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_page(
        self,
        page: int = C.FIRST_PAGE,
        *,
        fetch_downloads: bool = True,
    ) -> PageResult:
        """Fetch one page of the issue listings.

        Parameters
        ----------
        page:
            1-based page number.
        fetch_downloads:
            When ``True`` (default) an additional HTTP request is made
            per entry to resolve the PDF / RTF download URLs.

        Returns
        -------
        PageResult
        """
        soup = self._transport.fetch_page(page)

        entries = self._parser.parse_entries(soup)
        total_results = self._parser.parse_total_results(soup)
        total_pages = self._parser.parse_total_pages(soup)

        if fetch_downloads:
            for entry in entries:
                if entry.id_obj and entry._download_link_id:
                    dl_soup = self._transport.fetch_download(
                        entry.id_obj,
                        entry._download_link_id,
                    )
                    entry.download_urls = self._parser.parse_download_files(dl_soup)

        return PageResult(
            page=page,
            total_results=total_results,
            total_pages=total_pages,
            entries=entries,
        )

    def get_all_pages(
        self,
        *,
        fetch_downloads: bool = True,
        max_pages: Optional[int] = None,
    ) -> List[PageResult]:
        """Fetch all (or up to *max_pages*) pages of the listing.

        Parameters
        ----------
        fetch_downloads:
            Forwarded to each ``get_page`` call.
        max_pages:
            When provided, stop after this many pages even if more
            exist on the server.

        Returns
        -------
        List[PageResult]
        """
        first = self.get_page(C.FIRST_PAGE, fetch_downloads=fetch_downloads)
        results: List[PageResult] = [first]

        limit = (
            first.total_pages
            if max_pages is None
            else min(max_pages, first.total_pages)
        )

        for page_num in range(C.FIRST_PAGE + 1, limit + 1):
            results.append(self.get_page(page_num, fetch_downloads=fetch_downloads))

        return results
