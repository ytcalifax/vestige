from __future__ import annotations

import re
from typing import List, Optional

from selectolax.parser import HTMLParser, Node

from ..core import constants as C
from ..models.models import DownloadFile, IssueEntry

def _extract_view_state(tree: HTMLParser) -> str:
    """Pull the javax.faces.ViewState hidden input value from a page.

    Returns an empty string when the element is absent so callers never
    receive ``None``.
    """
    node = tree.css_first(f'input[name="{C.VIEW_STATE_NAME}"]')
    if node is None:
        return ""
    return node.attributes.get("value", "") or ""


class IssueParser:
    """Stateless parser for the state gazette's listing pages.

    All public methods satisfy the ``PageParser`` protocol.
    """

    def parse_entries(self, tree: HTMLParser) -> List[IssueEntry]:
        """Parse all issue entries from a listing page."""
        entries: List[IssueEntry] = []
        data_table = tree.css_first(f'table[id="{C.TABLE_ID}"]')
        if data_table is None:
            return entries
        tbody = data_table.css_first(f'tbody[id="{C.TBODY_ID}"]')
        if tbody is None:
            return entries
        for row in tbody.css("tr"):
            entry = self._parse_row(row)
            if entry is not None:
                entries.append(entry)
        return entries

    def parse_download_files(
        self,
        tree: Optional[HTMLParser],
        direct_url: Optional[str] = None,
        issue: Optional[int] = None,
        year: Optional[int] = None,
    ) -> List[DownloadFile]:
        """Parse download file links from the modal panel or process direct link.

        When a direct URL is provided (redirect to file) and both `issue` and
        `year` are supplied, build the filename as "{issue}_{YYYY}.pdf" where
        YYYY is the full four-digit year. If the scraped `year` appears to be
        two-digit (e.g. 26) it is interpreted as 2000+ (-> 2026) for filename
        construction. If issue/year are missing we fallback to the previous
        behaviour and use the file id when available.
        """

        # Scenario 1: Intercepted a 302 Redirect to a direct download
        if direct_url:
            url = self._normalise_url(direct_url)
            if issue is not None and year is not None:
                # Ensure a four-digit year for the filename. If the scraped
                # year is two-digit (e.g. 26) assume 2000s (-> 2026).
                year_full = year if year >= 100 else 2000 + year
                year_str = str(year_full).zfill(4)
                return [DownloadFile(url=url, filename=f"{issue}_{year_str}.pdf")]
            match = re.search(r"idFileAtt=(\d+)", direct_url)
            file_id = match.group(1) if match else "direct"

            return [DownloadFile(url=url, filename=f"Issue_Document_{file_id}.pdf")]

        # Scenario 2: Processing the modal popup HTML tree
        files: List[DownloadFile] = []
        if tree is None:
            return files

        tbody = tree.css_first(
            'tbody[id^="broi_form:_idJsp"][id$=":tbody_element"]'
        )
        if tbody is None:
            return files

        for a_tag in tbody.css('a[href*="fileUploadShowing"]'):
            href = a_tag.attributes.get("href", "") or ""
            url = self._normalise_url(href)
            filename = a_tag.text(strip=True)
            files.append(DownloadFile(url=url, filename=filename))

        return files

    def parse_total_results(self, tree: HTMLParser) -> int:
        """Extract total results count from the 'Намерени резултати' span."""
        for node in tree.css(f"span.{C.RESULTS_SPAN_CLASS}"):
            text = node.text()
            if C.RESULTS_TEXT_RE.search(text):
                match = C.RESULTS_NUMBER_RE.search(text)
                if match:
                    return int(match.group(1))
        return 0

    def parse_total_pages(self, tree: HTMLParser) -> int:
        """Count total pages from the page-selector dropdown."""
        select = tree.css_first(f'select[id="{C.SELECT_PAGE_ID}"]')
        if select is not None:
            return len(select.css("option"))
        return 0

    @staticmethod
    def _parse_row(row: Node) -> IssueEntry | None:
        """Parse a single <tr> row and return an IssueEntry or None."""
        td = row.css_first("td")
        if td is None:
            return None
        text = td.text(separator=" ", strip=True)
        match = C.ISSUE_RE.search(text)
        if not match:
            return None
        number = int(match.group(1))
        datestr: str = match.group(2)
        extra_type: str = match.group(3) or ""
        year = int(datestr.rsplit(".", 1)[-1])
        id_obj = IssueParser._extract_id_obj(td)
        download_link_id = IssueParser._extract_download_link_id(td)
        return IssueEntry(
            number=number,
            date=datestr,
            year=year,
            type=extra_type,
            _id_obj=id_obj,
            _download_link_id=download_link_id,
        )

    @staticmethod
    def _extract_id_obj(td: Node) -> str:
        """Extract the idObj parameter from the content link onclick."""
        link = td.css_first(f'a[id$="{C.LINK_CONTENT_ID_SUFFIX}"]')
        if link is None:
            return ""
        onclick = link.attributes.get("onclick", "") or ""
        params = dict(C.ONCLICK_PARAM_RE.findall(onclick))
        return params.get("idObj", "")

    @staticmethod
    def _extract_download_link_id(td: Node) -> str:
        """Extract the HTML element id of the download trigger link."""
        dl_link = td.css_first(f'a[id$="{C.LINK_DOWNLOAD_ID_SUFFIX}"]')
        if dl_link is None:
            return ""
        return dl_link.attributes.get("id", "") or ""

    @staticmethod
    def _normalise_url(raw_url: str) -> str:
        """Ensure a URL is absolute."""
        if raw_url.startswith("http"):
            return raw_url
        return C.BASE_HOST + raw_url.lstrip("/")