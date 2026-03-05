from __future__ import annotations

import re
from typing import List

from bs4 import BeautifulSoup, Tag

from ..core import constants as C
from ..models.models import DownloadFile, IssueEntry


def _extract_view_state(soup: BeautifulSoup) -> str:
    """Pull the javax.faces.ViewState hidden input value from a page.

    Returns an empty string when the element is absent so callers never
    receive ``None``.
    """
    tag = soup.find("input", attrs={"name": C.VIEW_STATE_NAME})
    if tag and isinstance(tag, Tag):
        value = tag.get("value", "")
        return value if isinstance(value, str) else ""
    return ""


class IssueParser:
    """Stateless parser for the state gazette's listing pages.

    All public methods satisfy the ``PageParser`` protocol.
    """

    def parse_entries(self, soup: BeautifulSoup) -> List[IssueEntry]:
        """Parse all issue entries from a listing page."""
        entries: List[IssueEntry] = []

        data_table = soup.find("table", id=C.TABLE_ID)
        if not data_table:
            return entries

        tbody = data_table.find("tbody", id=C.TBODY_ID)
        if not tbody:
            return entries

        for row in tbody.find_all("tr", recursive=False):
            entry = self._parse_row(row)
            if entry is not None:
                entries.append(entry)

        return entries

    def parse_download_files(self, soup: BeautifulSoup) -> List[DownloadFile]:
        """Parse download file links from the download modal panel."""
        files: List[DownloadFile] = []

        tbody = soup.find(
            "tbody",
            id=re.compile(C.DOWNLOAD_TBODY_PATTERN),
        )
        if not tbody:
            return files

        for a_tag in tbody.find_all("a", href=re.compile(C.DOWNLOAD_HREF_PATTERN)):
            url = self._normalise_url(a_tag["href"])
            filename = a_tag.get_text(strip=True)
            files.append(DownloadFile(url=url, filename=filename))

        return files

    def parse_total_results(self, soup: BeautifulSoup) -> int:
        """Extract total results count from the 'Намерени резултати' span."""
        mark = soup.find(
            "span",
            class_=C.RESULTS_SPAN_CLASS,
            string=C.RESULTS_TEXT_RE,
        )
        if mark:
            match = C.RESULTS_NUMBER_RE.search(mark.get_text())
            if match:
                return int(match.group(1))
        return 0

    def parse_total_pages(self, soup: BeautifulSoup) -> int:
        """Count total pages from the page-selector dropdown."""
        select = soup.find("select", id=C.SELECT_PAGE_ID)
        if select:
            return len(select.find_all("option"))
        return 0

    @staticmethod
    def _parse_row(row: Tag) -> IssueEntry | None:
        """Parse a single <tr> row and return a IssueEntry or None."""
        td = row.find("td")
        if not td:
            return None

        text = td.get_text(" ", strip=True)
        match = C.ISSUE_RE.search(text)
        if not match:
            return None

        number = int(match.group(1))
        date_str: str = match.group(2)
        extra_type: str = match.group(3) or ""
        year = int(date_str.rsplit(".", 1)[-1])

        id_obj = IssueParser._extract_id_obj(td)
        download_link_id = IssueParser._extract_download_link_id(td)

        return IssueEntry(
            number=number,
            date=date_str,
            year=year,
            id_obj=id_obj,
            extra_type=extra_type,
            _download_link_id=download_link_id,
        )

    @staticmethod
    def _extract_id_obj(td: Tag) -> str:
        """Extract the idObj parameter from the 'Съдържание' link onclick."""
        link = td.find("a", id=re.compile(C.LINK_CONTENT_ID_SUFFIX + "$"))
        if not link:
            return ""
        onclick: str = link.get("onclick", "")
        params = dict(C.ONCLICK_PARAM_RE.findall(onclick))
        return params.get("idObj", "")

    @staticmethod
    def _extract_download_link_id(td: Tag) -> str:
        """Extract the HTML element id of the download trigger link."""
        dl_link = td.find("a", id=re.compile(C.LINK_DOWNLOAD_ID_SUFFIX + "$"))
        if not dl_link:
            return ""
        element_id = dl_link.get("id", "")
        return element_id if isinstance(element_id, str) else ""

    @staticmethod
    def _normalise_url(raw_url: str) -> str:
        """Ensure a URL is absolute."""
        if raw_url.startswith("http"):
            return raw_url
        return C.BASE_HOST + raw_url.lstrip("./")
