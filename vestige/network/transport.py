from __future__ import annotations

from typing import Optional, Tuple
import httpx
from selectolax.parser import HTMLParser

from ..core import constants as C
from ..scraping.parsers import _extract_view_state


class AsyncRequestsTransport:
    """Async HTTP transport backed by ``httpx``.

    Satisfies the ``AsyncPageFetcher`` protocol.

    Uses a single ``httpx.AsyncClient`` for the lifetime of the object.
    HTTP/2 is requested; if the server does not support it httpx falls
    back to HTTP/1.1 transparently.

    Call ``await transport.aclose()`` when done to release connections.
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient = httpx.AsyncClient(
            headers=C.DEFAULT_HEADERS,
            http2=True,
            follow_redirects=True,
        )
        self._view_state: str = ""
        self._initialised: bool = False

    async def fetch_page(self, page: int) -> HTMLParser:
        """Fetch a listing page by 1-based page number."""
        if not self._initialised:
            await self._init_session()
        return await self._post_page(page)

    async def fetch_download(self, id_obj: str, idcl: str) -> Tuple[Optional[HTMLParser], Optional[str]]:
        """Fetch the download modal or redirect URL for a given issue id."""
        return await self._post_download(id_obj=id_obj, idcl=idcl)

    async def fetch_download_with_state(
        self, id_obj: str, idcl: str, view_state: str
    ) -> Tuple[Optional[HTMLParser], Optional[str]]:
        """Concurrent-safe fetch: uses explicit ViewState, never mutates self._view_state."""
        data = self._build_download_data(id_obj=id_obj, idcl=idcl, view_state=view_state)

        # Override follow_redirects=False specifically for the download POST
        request = self._client.build_request("POST", C.BASE_URL, data=data)
        response = await self._client.send(request, follow_redirects=False)

        # Intercept single-file direct downloads (302 Redirect)
        if response.status_code in (301, 302, 303, 307, 308):
            return None, response.headers.get("Location")

        response.raise_for_status()
        return HTMLParser(response.content), None

    async def aclose(self) -> None:
        """Close the underlying httpx client and release connections."""
        await self._client.aclose()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _init_session(self) -> None:
        """GET the listing page to obtain cookies and the initial ViewState."""
        response = await self._client.get(C.BASE_URL)
        response.raise_for_status()
        tree = HTMLParser(response.content)
        self._view_state = _extract_view_state(tree)
        self._initialised = True

    async def _post_page(self, page: int) -> HTMLParser:
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
        return await self._post(data)

    async def _post_download(self, id_obj: str, idcl: str) -> Tuple[Optional[HTMLParser], Optional[str]]:
        """POST the form to trigger the download modal for a given issue."""
        data = self._build_download_data(
            id_obj=id_obj, idcl=idcl, view_state=self._view_state
        )
        request = self._client.build_request("POST", C.BASE_URL, data=data)
        response = await self._client.send(request, follow_redirects=False)

        if response.status_code in (301, 302, 303, 307, 308):
            return None, response.headers.get("Location")

        response.raise_for_status()
        tree = HTMLParser(response.content)
        self._view_state = _extract_view_state(tree)
        return tree, None

    def _build_download_data(self, id_obj: str, idcl: str, view_state: str) -> dict:
        """Construct the POST body for a download modal request."""
        return {
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
            C.FIELD_VIEW_STATE: view_state,
        }

    async def _post(self, data: dict) -> HTMLParser:
        """Execute a POST, update ViewState, and return parsed HTML."""
        response = await self._client.post(C.BASE_URL, data=data)
        response.raise_for_status()
        tree = HTMLParser(response.content)
        self._view_state = _extract_view_state(tree)
        return tree