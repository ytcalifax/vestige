from __future__ import annotations

from typing import Optional

import requests
from bs4 import BeautifulSoup

from ..core import constants as C
from ..scraping.parsers import _extract_view_state


class RequestsTransport:
    """Concrete HTTP transport backed by ``requests``.

    Satisfies the ``PageFetcher`` protocol.

    Parameters
    ----------
    session:
        Optional pre-configured ``requests.Session``.  If omitted a new
        session is created and the default headers are applied.
    """

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self._session: requests.Session = session or requests.Session()
        self._session.headers.update(C.DEFAULT_HEADERS)
        self._view_state: str = ""
        self._initialised: bool = False


    def fetch_page(self, page: int) -> BeautifulSoup:
        """Fetch a listing page by 1-based page number."""
        if not self._initialised:
            self._init_session()
        return self._post_page(page)

    def fetch_download(self, id_obj: str, idcl: str) -> BeautifulSoup:
        """Fetch the download modal for a given issue id."""
        return self._post_download(id_obj=id_obj, idcl=idcl)

    def _init_session(self) -> None:
        """GET the listing page to obtain cookies and the initial ViewState."""
        response = self._session.get(C.BASE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        self._view_state = _extract_view_state(soup)
        self._initialised = True

    def _post_page(self, page: int) -> BeautifulSoup:
        """POST the navigation form to retrieve a specific page."""
        page_str = str(page)
        data = {
            C.FIELD_ACTIVE_TAB: C.VALUE_ACTIVE_TAB,
            C.FIELD_NOT_FIRST: C.VALUE_NOT_FIRST,
            C.FIELD_JSP61: "",
            C.FIELD_JSP67: "",
            C.FIELD_JSP69: "",
            C.FIELD_FROM_DATE: "",
            C.FIELD_TO_DATE: "",
            C.FIELD_PERIOD: "",
            C.FIELD_SELECT_PAGE_TOP: page_str,
            C.FIELD_SELECT_PAGE: page_str,
            C.FIELD_FORM_SUBMIT: C.VALUE_FORM_SUBMIT,
            C.FIELD_LINK_HIDDEN: "",
            C.FIELD_DATE_IZD: "",
            C.FIELD_IDCL: C.VALUE_CHANGE_PAGE_CMD,
            C.FIELD_ID_: "",
            C.FIELD_ID_OBJ: "",
            C.FIELD_RAZDEL: "",
            C.FIELD_BROI: "",
            C.FIELD_VIEW_STATE: self._view_state,
        }
        return self._post(data)

    def _post_download(self, id_obj: str, idcl: str) -> BeautifulSoup:
        """POST the form to trigger the download modal for a given issue."""
        data = {
            C.FIELD_ACTIVE_TAB: C.VALUE_ACTIVE_TAB,
            C.FIELD_NOT_FIRST: C.VALUE_NOT_FIRST,
            C.FIELD_JSP61: "",
            C.FIELD_JSP67: "",
            C.FIELD_JSP69: "",
            C.FIELD_FROM_DATE: "",
            C.FIELD_TO_DATE: "",
            C.FIELD_PERIOD: "",
            C.FIELD_SELECT_PAGE_TOP: str(C.FIRST_PAGE),
            C.FIELD_SELECT_PAGE: str(C.FIRST_PAGE),
            C.FIELD_FORM_SUBMIT: C.VALUE_FORM_SUBMIT,
            C.FIELD_LINK_HIDDEN: "",
            C.FIELD_DATE_IZD: "",
            C.FIELD_IDCL: idcl,
            C.FIELD_ID_: id_obj,
            C.FIELD_ID_OBJ: "",
            C.FIELD_RAZDEL: "",
            C.FIELD_BROI: "",
            C.FIELD_VIEW_STATE: self._view_state,
        }
        return self._post(data)

    def _post(self, data: dict) -> BeautifulSoup:
        """Execute a POST request, update ViewState, and return parsed HTML."""
        response = self._session.post(C.BASE_URL, data=data)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        self._view_state = _extract_view_state(soup)
        return soup

