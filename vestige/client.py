from __future__ import annotations

import asyncio
from typing import List, Optional

from .core import constants as C
from .core.interfaces import AsyncPageFetcher, PageParser
from .models.models import PageResult
from .network.transport import AsyncRequestsTransport
from .scraping.parsers import IssueParser


class DVClient:
    """Client for the Държавен вестник (Bulgarian State Gazette) listing.

    Parameters
    ----------
    transport:
        Concrete implementation of ``AsyncPageFetcher``. Defaults to
        ``AsyncRequestsTransport``. Pass a stub/mock here in tests.
    parser:
        Concrete implementation of ``PageParser``. Defaults to
        ``IssueParser``. Pass a stub/mock here in tests.
    """

    def __init__(
        self,
        transport: Optional[AsyncPageFetcher] = None,
        parser: Optional[PageParser] = None,
    ) -> None:
        self._transport: AsyncPageFetcher = transport or AsyncRequestsTransport()
        self._parser: PageParser = parser or IssueParser()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_page(
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
            When ``True`` (default) all download URL fetches are fired
            concurrently via ``asyncio.gather``.

        Returns
        -------
        PageResult
        """
        tree = await self._transport.fetch_page(page)

        entries = self._parser.parse_entries(tree)
        total_results = self._parser.parse_total_results(tree)
        total_pages = self._parser.parse_total_pages(tree)

        if fetch_downloads:
            eligible = [e for e in entries if e.id_obj and e._download_link_id]
            view_state = self._transport._view_state

            async def _fetch_dl(entry) -> None:
                dl_tree = await self._transport.fetch_download_with_state(
                    entry.id_obj, entry._download_link_id, view_state
                )
                entry.download_urls = self._parser.parse_download_files(dl_tree)

            await asyncio.gather(*[_fetch_dl(e) for e in eligible])

        return PageResult(
            page=page,
            total_results=total_results,
            total_pages=total_pages,
            entries=entries,
        )

    async def get_all_pages(
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
            When provided, stop after this many pages even if more exist.

        Returns
        -------
        List[PageResult]
        """
        first = await self.get_page(C.FIRST_PAGE, fetch_downloads=fetch_downloads)
        results: List[PageResult] = [first]

        limit = (
            first.total_pages
            if max_pages is None
            else min(max_pages, first.total_pages)
        )

        for page_num in range(C.FIRST_PAGE + 1, limit + 1):
            results.append(
                await self.get_page(page_num, fetch_downloads=fetch_downloads)
            )

        return results

    async def aclose(self) -> None:
        """Release the underlying transport's HTTP client."""
        await self._transport.aclose()
